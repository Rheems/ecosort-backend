from django.db import models
from django.conf import settings

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('glass', 'Glass'),
        ('metal', 'Metal'),
        ('organic', 'Organic'),
        ('mixed', 'Mixed'),
    ]
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField()
    sorting_guide = models.TextField()
    tips = models.TextField(blank=True)
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

    def __str__(self):
        return f"{self.category.name} - {self.question[:50]}"


class QuizResult(models.Model):
    BADGE_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('none', 'None'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    badge_awarded = models.CharField(max_length=10, choices=BADGE_CHOICES, default='none')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.category.name} - {self.score}"

# Create your models here.
