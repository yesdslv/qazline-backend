from django.urls import path
from rest_framework import routers

#
from qazline.views import (
    # LessonViewSet, SubjectViewSet, VideoViewSet, ImageViewSet, AssignmentViewSet,
    # VideoView,
    # AssignmentViewSet,
    SubjectMaterialDetailView,
    SubjectListView,
    LessonViewSet,
    VideoMaterialViewSet,
    ImageMaterialViewSet,
    AssignmentMaterialViewSet,
    QuizMaterialViewSet,
    ImageDeleteView,
    TaskRetrieveUpdateDestroyView,
)

#
#
router = routers.SimpleRouter()
router.register(r'lessons', LessonViewSet)
router.register(r'videos', VideoMaterialViewSet, basename='video-material')
router.register(r'images', ImageMaterialViewSet, basename='image-material')
router.register(r'assignments', AssignmentMaterialViewSet, basename='assignment-material')
router.register(r'quizzes', QuizMaterialViewSet, basename='quiz-material')


urlpatterns = [
    path('images/<int:pk>/', ImageDeleteView.as_view(), name='image-delete'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path(
        'lessons/<int:lesson_numeral>/subjects/<int:subject_numeral>/',
        SubjectMaterialDetailView.as_view(), name='subject-material-detail'
    ),
] + router.urls
