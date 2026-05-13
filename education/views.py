from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Category, QuizQuestion, QuizResult
from .serializer import CategorySerializer, QuizSubmitSerializer, QuizResultSerializer

# GET ALL 6 CATEGORY GUIDES
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_guides(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

# GET SINGLE CATEGORY GUIDE + QUIZ
@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_guide(request, category_name):
    try:
        category = Category.objects.get(name=category_name)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

# SUBMIT QUIZ
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

    questions = QuizQuestion.objects.filter(category=category)
    total = questions.count()
    score = 0
    feedback = []

    for question in questions:
        user_answer = answers.get(str(question.id), '').upper()
        is_correct = user_answer == question.correct_answer
        if is_correct:
            score += 1
        else:
            feedback.append({
                'question': question.question,
                'your_answer': user_answer,
                'correct_answer': question.correct_answer,
                'hint': f'Review the {category.name} sorting guide'
            })

    # Award badge
    percentage = (score / total * 100) if total > 0 else 0
    if percentage == 100:
        badge = 'gold'
    elif percentage >= 60:
        badge = 'silver'
    elif percentage >= 40:
        badge = 'bronze'
    else:
        badge = 'none'

    # Save result
    result = QuizResult.objects.create(
        user=request.user,
        category=category,
        score=score,
        total_questions=total,
        badge_awarded=badge
    )

    # Check if all 6 badges earned
    earned_badges = QuizResult.objects.filter(
        user=request.user
    ).exclude(badge_awarded='none').values_list('category__name', flat=True).distinct()

    full_sorter = len(set(earned_badges)) >= 6

    return Response({
        'score': score,
        'total': total,
        'percentage': percentage,
        'badge_awarded': badge,
        'full_sorter_unlocked': full_sorter,
        'feedback': feedback
    }, status=status.HTTP_200_OK)

# GET USER QUIZ RESULTS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_results(request):
    results = QuizResult.objects.filter(user=request.user).order_by('-completed_at')
    serializer = QuizResultSerializer(results, many=True)
    return Response(serializer.data)