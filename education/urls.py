from django.urls import path
from . import views

urlpatterns = [
    path('guides/', views.get_all_guides, name='all_guides'),
    path('guides/<str:category_name>/', views.get_category_guide, name='category_guide'),
    path('quiz/submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/results/', views.get_my_results, name='my_results'),
    path('progress/', views.get_education_progress, name='education_progress'),
]