from rest_framework import serializers
from .models import Category, QuizQuestion, QuizResult

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d']
        # correct_answer is excluded so users can't see it

class CategorySerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'sorting_guide', 'tips', 'questions']

class QuizSubmitSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.CharField()
    )  # e.g. {"1": "A", "2": "C", "3": "B"}

class QuizResultSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = QuizResult
        fields = ['id', 'category_name', 'score', 'total_questions', 'badge_awarded', 'completed_at']