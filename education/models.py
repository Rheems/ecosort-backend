from django.db import models
from django.conf import settings


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('glass', 'Glass'),
        ('metal', 'Metal'),
        ('organic', 'Organic'),
        ('ewaste', 'Ewaste'),
    ]

    # Who can access this category
    TRACK_CHOICES = [
        ('household', 'Household Only'),
        ('collector', 'Collector Only'),
        ('all', 'All Users'),
    ]

    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField()
    sorting_guide = models.TextField()
    tips = models.TextField(blank=True)
    track = models.CharField(max_length=20, choices=TRACK_CHOICES, default='all')
    collector_module_number = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class QuizQuestion(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    guide_section_ref = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.category.name} - {self.question[:50]}"


class QuizResult(models.Model):
    BADGE_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('none', 'None'),
        # Household badges
        ('plastic_complete', 'Plastic Complete'),
        ('glass_complete', 'Glass Complete'),
        ('metal_complete', 'Metal Complete'),
        ('paper_complete', 'Paper Complete'),
        ('organic_complete', 'Organic Complete'),
        ('ewaste_complete', 'Ewaste Complete'),
        ('full_sorter', 'Full Sorter'),
        # Collector badges
        ('metal_collector', 'Metal Collector'),
        ('organic_collector', 'Organic Collector'),
        ('ewaste_collector', 'Ewaste Collector'),
        ('full_collector', 'Full Collector'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    badge_awarded = models.CharField(max_length=20, choices=BADGE_CHOICES, default='none')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.category.name} - {self.score}"


class UserEducationProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Household guide progress
    plastic_guide_read = models.BooleanField(default=False)
    glass_guide_read = models.BooleanField(default=False)
    metal_guide_read = models.BooleanField(default=False)
    paper_guide_read = models.BooleanField(default=False)
    organic_guide_read = models.BooleanField(default=False)
    ewaste_guide_read = models.BooleanField(default=False)

    # Quiz passed
    plastic_quiz_passed = models.BooleanField(default=False)
    glass_quiz_passed = models.BooleanField(default=False)
    metal_quiz_passed = models.BooleanField(default=False)
    paper_quiz_passed = models.BooleanField(default=False)
    organic_quiz_passed = models.BooleanField(default=False)
    ewaste_quiz_passed = models.BooleanField(default=False)

    # Badges earned
    plastic_badge_earned = models.BooleanField(default=False)
    glass_badge_earned = models.BooleanField(default=False)
    metal_badge_earned = models.BooleanField(default=False)
    paper_badge_earned = models.BooleanField(default=False)
    organic_badge_earned = models.BooleanField(default=False)
    ewaste_badge_earned = models.BooleanField(default=False)

    # Master badges
    full_sorter_badge_earned = models.BooleanField(default=False)
    full_collector_badge_earned = models.BooleanField(default=False)

    # Streak
    daily_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    # Organic special field
    separation_method_informed = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} progress"


class EducationEvent(models.Model):
    EVENT_CHOICES = [
        ('GUIDE_VIEWED', 'Guide Viewed'),
        ('QUIZ_ANSWERED', 'Quiz Answered'),
        ('BADGE_AWARDED', 'Badge Awarded'),
        ('EWASTE_DISPOSAL_QUERY', 'Ewaste Disposal Query'),
    ]

    CHANNEL_CHOICES = [
        ('WHATSAPP', 'WhatsApp'),
        ('USSD', 'USSD'),
        ('MOBILE_APP', 'Mobile App'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('pidgin', 'Pidgin'),
    ]

    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module_id = models.CharField(max_length=20)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='MOBILE_APP')
    guide_completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Append-only — no updates or deletes
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} - {self.user} - {self.module_id}"