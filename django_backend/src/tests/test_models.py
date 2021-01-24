from mock import Mock

from django.db import IntegrityError
from django.core.files import File
from django.core.exceptions import ValidationError

from tests.setup import TestModelSetUp
from qazline.models import (
    Subject, VideoMaterial, ImageMaterial, AssignmentMaterial, QuizMaterial, Image, Task
)


class ModelsTest(TestModelSetUp):

    def test_only_one_material_children_can_be_assigned_to_subject(self):
        subject = Subject.objects.order_by('?').first()
        AssignmentMaterial.objects.create(topic='assignment', subject=subject)
        with self.assertRaises(IntegrityError):
            VideoMaterial.objects.create(topic='video', subject=subject, url='http://sample.com')
        with self.assertRaises(IntegrityError):
            file_mock = Mock(spec_set=File, name='image.jpg')
            image_material = ImageMaterial.objects.create(topic='image', subject=subject)
            Image.objects.create(image=file_mock, image_material=image_material)

    def test_delete_material_also_delete_subject(self):
        last_subject_number = Subject.objects.order_by('-number').first().number + 1
        subject = Subject.objects.create(number=last_subject_number, title='deleted subject title')
        video_material = VideoMaterial.objects.create(topic='video', url='http://sample.com', subject=subject)
        video_material.delete()
        with self.assertRaises(Subject.DoesNotExist):
            Subject.objects.get(title='deleted subject title')

    def test_create_fill_the_blank_task(self):
        last_subject_number = Subject.objects.order_by('-number').first().number + 1
        subject = Subject.objects.create(number=last_subject_number, title='task title')
        quiz_material = QuizMaterial.objects.create(topic='quiz', subject=subject)
        task = Task.objects.create(
            question='Hello my name is _____',
            answers=[{'answer_text': 'John'}],
            quiz_material=quiz_material,
        )
        self.assertIsNotNone(task.pk)
        self.assertEqual(task.task_type, Task.TaskType.FILL_IN_THE_BLANK)

    def test_assert_error_single_answer_task(self):
        # TODO write test for repeated answer_text in answers
        #  {'answers': [
        #    {'answer_text': 'John', 'correct': True},
        #    {'answer_text': 'John', 'correct': True},
        #  ]},
        pass

    def test_create_single_answer_task(self):
        last_subject_number = Subject.objects.order_by('-number').first().number + 1
        subject = Subject.objects.create(number=last_subject_number, title='task title')
        quiz_material = QuizMaterial.objects.create(topic='quiz', subject=subject)
        task = Task.objects.create(
            question='Hello my name is _____',
            answers=[
                {'answer_text': 'John', 'correct': True},
                {'answer_text': 'James', 'correct': False},
                {'answer_text': 'Jack', 'correct': False},
            ],
            quiz_material=quiz_material,
        )
        self.assertIsNotNone(task.pk)
        self.assertEqual(task.task_type, Task.TaskType.SINGLE_ANSWER)

    def test_create_multiple_answer_task(self):
        last_subject_number = Subject.objects.order_by('-number').first().number + 1
        subject = Subject.objects.create(number=last_subject_number, title='task title')
        quiz_material = QuizMaterial.objects.create(topic='quiz', subject=subject)
        task = Task.objects.create(
            question='Hello my name is _____',
            answers=[
                {'answer_text': 'John', 'correct': True},
                {'answer_text': 'James', 'correct': True},
                {'answer_text': 'Jack', 'correct': False},
            ],
            quiz_material=quiz_material,
        )
        self.assertIsNotNone(task.pk)
        self.assertEqual(task.task_type, Task.TaskType.MULTIPLE_ANSWERS)

    def test_create_raises_validation_error_on_invalid_number_of_correct_values(self):
        last_subject_number = Subject.objects.order_by('-number').first().number + 1
        subject = Subject.objects.create(number=last_subject_number, title='task title')
        quiz_material = QuizMaterial.objects.create(topic='quiz', subject=subject)
        with self.assertRaises(ValidationError):
            Task.objects.create(
                question='Hello my name is _____',
                answers=[
                    {'answer_text': 'John', 'correct': True},
                    {'answer_text': 'James', 'correct': True},
                    {'answer_text': 'Jack',},
                ],
                quiz_material=quiz_material,
            )

    def test_create_raises_validation_error_on_invalid_number_of_fill_the_blank_special_character(self):
        last_subject_number = Subject.objects.order_by('-number').first().number + 1
        subject = Subject.objects.create(number=last_subject_number, title='task title')
        quiz_material = QuizMaterial.objects.create(topic='quiz', subject=subject)
        with self.assertRaises(ValidationError):
            Task.objects.create(
                question='Hello my name is _____',
                answers=[
                    {'answer_text': 'John'},
                    {'answer_text': 'James'},
                ],
                quiz_material=quiz_material,
            )
