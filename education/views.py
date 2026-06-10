from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Sum
from .models import Category, QuizQuestion, QuizResult, UserEducationProgress, EducationEvent
from .serializers import CategorySerializer, QuizSubmitSerializer, QuizResultSerializer


# ── COLLECTOR SAFETY TRACK CATEGORIES ──
COLLECTOR_MODULES = ['metal', 'organic', 'ewaste']
HOUSEHOLD_MODULES = ['plastic', 'glass', 'metal', 'paper', 'organic', 'ewaste']


def get_user_modules(user):
    if user.user_type == 'collector':
        return COLLECTOR_MODULES
    return HOUSEHOLD_MODULES


def log_event(user, event_type, module_id, guide_completed=False, channel='MOBILE_APP', language='en'):
    EducationEvent.objects.create(
        event_type=event_type,
        user=user,
        module_id=module_id.upper(),
        language=language,
        channel=channel,
        guide_completed=guide_completed
    )


def get_or_create_progress(user):
    progress, _ = UserEducationProgress.objects.get_or_create(user=user)
    return progress


# ── GET ALL GUIDES (filtered by user type) ──
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_guides(request):
    if request.user.is_authenticated:
        modules = get_user_modules(request.user)
        categories = Category.objects.filter(name__in=modules)
    else:
        categories = Category.objects.all()

    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# ── GET SINGLE CATEGORY GUIDE ──
@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_guide(request, category_name):
    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    # Log guide view event
    if request.user.is_authenticated:
        log_event(request.user, 'GUIDE_VIEWED', category_name)

        # Update progress
        progress = get_or_create_progress(request.user)
        setattr(progress, f'{category_name}_guide_read', True)

        # Update streak
        today = timezone.now().date()
        if progress.last_activity_date != today:
            if progress.last_activity_date and (today - progress.last_activity_date).days == 1:
                progress.daily_streak += 1
            elif progress.last_activity_date and (today - progress.last_activity_date).days > 1:
                progress.daily_streak = 1
            else:
                progress.daily_streak = 1
            progress.last_activity_date = today

        # Special field for organic
        if category_name == 'organic':
            progress.separation_method_informed = True

        progress.save()

    serializer = CategorySerializer(category)
    return Response(serializer.data)


# ── SUBMIT QUIZ ──
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request):
    serializer = QuizSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    category_id = serializer.validated_data['category_id']
    answers = serializer.validated_data['answers']

    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if collector is allowed this module
    if request.user.user_type == 'collector' and category.name not in COLLECTOR_MODULES:
        return Response(
            {'error': f'Collectors only access Metal, Organic and E-waste modules'},
            status=status.HTTP_403_FORBIDDEN
        )

    questions = QuizQuestion.objects.filter(category=category)
    total = questions.count()
    score = 0
    feedback = []

    for question in questions:
        user_answer = answers.get(str(question.id), '').upper()
        is_correct = user_answer == question.correct_answer

        # Log each quiz answer event
        log_event(request.user, 'QUIZ_ANSWERED', category.name)

        if is_correct:
            score += 1
        else:
            feedback.append({
                'question': question.question,
                'your_answer': user_answer,
                'correct_answer': question.correct_answer,
                'guide_section_ref': question.guide_section_ref,
                'hint': f'Review the {category.name} sorting guide — section: {question.guide_section_ref}'
            })

    percentage = (score / total * 100) if total > 0 else 0

    # Determine badge based on user type
    badge = 'none'
    if percentage == 100:
        if request.user.user_type == 'collector':
            badge = f'{category.name}_collector'
        else:
            badge = f'{category.name}_complete'

    # Save quiz result
    result = QuizResult.objects.create(
        user=request.user,
        category=category,
        score=score,
        total_questions=total,
        badge_awarded=badge
    )

    # Update progress
    progress = get_or_create_progress(request.user)

    if percentage == 100:
        setattr(progress, f'{category.name}_quiz_passed', True)
        setattr(progress, f'{category.name}_badge_earned', True)

        # Log badge event
        log_event(request.user, 'BADGE_AWARDED', category.name, guide_completed=True)

    progress.save()

    # ── CHECK FULL SORTER BADGE (Household) ──
    full_sorter_unlocked = False
    if request.user.user_type != 'collector':
        household_badges = all([
            progress.plastic_badge_earned,
            progress.glass_badge_earned,
            progress.metal_badge_earned,
            progress.paper_badge_earned,
            progress.organic_badge_earned,
            progress.ewaste_badge_earned,
        ])
        if household_badges and not progress.full_sorter_badge_earned:
            progress.full_sorter_badge_earned = True
            progress.save()
            QuizResult.objects.create(
                user=request.user,
                category=category,
                score=total,
                total_questions=total,
                badge_awarded='full_sorter'
            )
            log_event(request.user, 'BADGE_AWARDED', 'FULL_SORTER', guide_completed=True)
            full_sorter_unlocked = True

    # ── CHECK FULL COLLECTOR BADGE (Collector) ──
    full_collector_unlocked = False
    if request.user.user_type == 'collector':
        collector_badges = all([
            progress.metal_badge_earned,
            progress.organic_badge_earned,
            progress.ewaste_badge_earned,
        ])
        if collector_badges and not progress.full_collector_badge_earned:
            progress.full_collector_badge_earned = True
            progress.save()
            QuizResult.objects.create(
                user=request.user,
                category=category,
                score=total,
                total_questions=total,
                badge_awarded='full_collector'
            )
            log_event(request.user, 'BADGE_AWARDED', 'FULL_COLLECTOR', guide_completed=True)
            full_collector_unlocked = True

    return Response({
        'score': score,
        'total': total,
        'percentage': percentage,
        'badge_awarded': badge,
        'full_sorter_unlocked': full_sorter_unlocked,
        'full_collector_unlocked': full_collector_unlocked,
        'feedback': feedback,
    }, status=status.HTTP_200_OK)


# ── GET MY QUIZ RESULTS ──
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_results(request):
    results = QuizResult.objects.filter(user=request.user).order_by('-completed_at')
    serializer = QuizResultSerializer(results, many=True)
    return Response(serializer.data)


# ── GET EDUCATION PROGRESS ──
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_education_progress(request):
    progress = get_or_create_progress(request.user)
    user = request.user

    if user.user_type == 'collector':
        modules = COLLECTOR_MODULES
        total_modules = 3
        full_badge = 'FULL_COLLECTOR'
        full_badge_earned = progress.full_collector_badge_earned
    else:
        modules = HOUSEHOLD_MODULES
        total_modules = 6
        full_badge = 'FULL_SORTER'
        full_badge_earned = progress.full_sorter_badge_earned

    module_statuses = []
    badges_earned = []
    completed = 0

    for module in modules:
        guide_read = getattr(progress, f'{module}_guide_read', False)
        quiz_passed = getattr(progress, f'{module}_quiz_passed', False)
        badge_earned = getattr(progress, f'{module}_badge_earned', False)

        if badge_earned:
            completed += 1
            if user.user_type == 'collector':
                badges_earned.append(f'{module}_collector')
            else:
                badges_earned.append(f'{module}_complete')

        module_statuses.append({
            'module': module,
            'guide_read': guide_read,
            'quiz_passed': quiz_passed,
            'badge_earned': badge_earned,
        })

    if full_badge_earned:
        badges_earned.append(full_badge)

    # Get verified kg from pickups
    from pickup.models import PickupRequest
    verified_kg = PickupRequest.objects.filter(
        user=user, status='completed'
    ).aggregate(total=Sum('weight_kg'))['total'] or 0

    return Response({
        'user_type': user.user_type,
        'total_modules': total_modules,
        'completed_modules': completed,
        'module_statuses': module_statuses,
        'badges_earned': badges_earned,
        'daily_streak': progress.daily_streak,
        'last_activity_date': progress.last_activity_date,
        'full_badge': full_badge,
        'full_badge_earned': full_badge_earned,
        'verified_kg': verified_kg,
        'separation_method_informed': progress.separation_method_informed,
    })