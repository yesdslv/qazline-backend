from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, DestroyAPIView, RetrieveDestroyAPIView, RetrieveUpdateDestroyAPIView

from qazline.models import (
    Lesson, Subject, VideoMaterial, ImageMaterial, AssignmentMaterial, QuizMaterial, Image, Task,
)
from qazline.serializers import (
    VideoMaterialSerializer, AssignmentMaterialSerializer, SubjectSerializer, LessonSerializer,
    ImageMaterialSerializer, ImageSerializer, QuizMaterialSerializer, TaskSerializer
)


class LessonViewSet(ModelViewSet):
    queryset = Lesson.objects.prefetch_related(
        'subjects',
    ).all()
    serializer_class = LessonSerializer


class SubjectMaterialDetailView(RetrieveDestroyAPIView):

    def get_object(self):
        instance = get_object_or_404(Subject, pk=self.kwargs['pk'])
        if instance.has_video_material():
            obj = instance.videomaterial
        elif instance.has_image_material():
            obj = instance.imagematerial
        elif instance.has_assignment_material():
            obj = instance.assignmentmaterial
        elif instance.has_quiz_material():
            obj = instance.quizmaterial
        else:
            raise Exception
        return obj

    def get_serializer_class(self):
        instance = get_object_or_404(Subject, pk=self.kwargs['pk'])
        if instance.has_video_material():
            serializer = VideoMaterialSerializer
        elif instance.has_image_material():
            serializer = ImageMaterialSerializer
        elif instance.has_assignment_material():
            serializer = AssignmentMaterialSerializer
        elif instance.has_quiz_material:
            serializer = QuizMaterialSerializer
        else:
            raise Exception
        return serializer


class SubjectListView(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class VideoMaterialViewSet(ModelViewSet):
    queryset = VideoMaterial.objects.all()
    serializer_class = VideoMaterialSerializer


class ImageMaterialViewSet(ModelViewSet):
    queryset = ImageMaterial.objects.all()
    serializer_class = ImageMaterialSerializer


class ImageDeleteView(DestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class AssignmentMaterialViewSet(ModelViewSet):
    queryset = AssignmentMaterial.objects.all()
    serializer_class = AssignmentMaterialSerializer


class QuizMaterialViewSet(ModelViewSet):
    queryset = QuizMaterial.objects.all()
    serializer_class = QuizMaterialSerializer


class TaskRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class HelloView(APIView):
    def get(self, request, format=None):
        return Response('Hello from django!')


class VideoView(TemplateView):
    template_name = 'qazline/video.html'

