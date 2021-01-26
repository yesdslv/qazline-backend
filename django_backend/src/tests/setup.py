import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from qazline.models import (
    Lesson, Subject, AssignmentMaterial, VideoMaterial, ImageMaterial, Image, QuizMaterial, Task,
)

BASE_DIR = settings.BASE_DIR
MEDIA_ROOT = f'{BASE_DIR}/test_media'


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestViewSetUp(APITestCase):

    def setUp(self):
        lesson = Lesson.objects.create(number=1, title='Sample lesson #1')
        assignment_subject = Subject.objects.create(number=1, lesson=lesson, title='Assignment subject')
        video_subject = Subject.objects.create(number=2, lesson=lesson, title='Video subject')
        image_subject = Subject.objects.create(number=3, lesson=lesson, title='Image subject')
        updated_video_subject = Subject.objects.create(number=4, lesson=lesson, title='Updated video subject')
        updated_image_subject = Subject.objects.create(number=5, lesson=lesson, title='Updated image subject')
        quiz_subject = Subject.objects.create(number=6, lesson=lesson, title='Quiz subject')
        AssignmentMaterial.objects.create(subject=assignment_subject, task='sample task')
        VideoMaterial.objects.create(subject=video_subject, url='http://sample_video.com')
        VideoMaterial.objects.create(subject=updated_video_subject, url='http://updated_video.com')
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=open('tests/test.jpeg', 'rb').read(),
            content_type='image/jpeg'
        )
        image_material = ImageMaterial.objects.create(subject=image_subject, topic='Put image topic')
        Image.objects.create(image=image_file, description='Image descritpion', image_material=image_material)
        image_material = ImageMaterial.objects.create(subject=updated_image_subject, topic='Update image subject')
        Image.objects.create(image=image_file, description='Image descritpion', image_material=image_material)
        quiz_material = QuizMaterial.objects.create(subject=quiz_subject, topic='Add task')
        Task.objects.create(
            question='Hello my name is',
            answers=[
                {'answer_text': 'John', 'correct': True},
                {'answer_text': 'James', 'correct': False},
                {'answer_text': 'Jack', 'correct': False},
            ],
            quiz_material=quiz_material,
        )

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(MEDIA_ROOT)


    @classmethod
    def get_last_subject_number(cls) -> int:
        last_subject_number = Subject.objects.order_by('-number').first().number
        subject_number = last_subject_number + 1
        return subject_number


class TestModelSetUp(APITestCase):

    def setUp(self):
        for i in range(1, 4):
            lesson = Lesson.objects.create(number=i, title=f'Sample lesson #{i}')
            # Create empty subjects
            for j in range(1, 4):
                Subject.objects.create(number=j, lesson=lesson, title=f'Subject #{j} from lesson #{i}')
