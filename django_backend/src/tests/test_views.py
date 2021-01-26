import json

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from tests.setup import TestViewSetUp
from qazline.views import (
    VideoMaterialViewSet, AssignmentMaterialViewSet, SubjectMaterialDetailView, SubjectListView,
    ImageMaterialViewSet, QuizMaterialViewSet,
)
from qazline.models import (
    Subject, VideoMaterial, AssignmentMaterial, Lesson, ImageMaterial, QuizMaterial, Task,
)


class ViewsTest(TestViewSetUp):

    request_factory = APIRequestFactory()

    # def test_lesson_list_return_correct_response(self):
    #     lesson_url = reverse('lesson-list')
    #     request = self.request_factory.get(lesson_url)
    #     view = LessonViewSet.as_view({'get': 'list'})
    #     response = view(request)
    #     expected_response_json = json.dumps([{
    #         'number': 1,
    #         'title': 'Sample lesson #1',
    #         'subjects': [
    #             {'number': 1, 'title': 'Assignment subject'},
    #             {'number': 2, 'title': 'Video subject'}
    #         ]
    #     }])
    #     expected_response_json = expected_response_json.encode('utf-8')
    #     response.render()
    #     self.assertEqual(response.content, expected_response_json)

    def test_subject_list_view_return_200_response(self):
        subject_url = reverse('subject-list')
        request = self.request_factory.get(subject_url)
        view = SubjectListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_subject_detail_view_returns_200_response(self):
        subject = Subject.objects.get(title='Assignment subject')
        subject_url = reverse('subject-material-detail', kwargs={'pk': subject.pk})
        request = self.request_factory.get(subject_url)
        view = SubjectListView.as_view()
        response = view(request, pk=subject.pk)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_subject_detail_view_not_found_response(self):
        pk = 9999999999999999999
        subject_url = reverse('subject-material-detail', kwargs={'pk': pk})
        request = self.request_factory.get(subject_url)
        view = SubjectMaterialDetailView.as_view()
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_video_view_creates_video_material(self):
        subject_title = 'Video subject'
        subject_number = self.get_last_subject_number()
        url = 'https://youtube.com/aaaa'
        topic = 'AAAAA'
        lesson_pk = Lesson.objects.first().pk
        video_json = json.dumps({
            'lesson': lesson_pk,
            'subject_title': subject_title,
            'subject_number': subject_number,
            'url': url,
            'topic': topic,
        })
        video_url = reverse('video-material-list')
        request = self.request_factory.post(video_url, video_json, content_type='application/json')
        view = VideoMaterialViewSet.as_view({'post': 'create'})
        response = view(request)
        try:
            video = VideoMaterial.objects.get(url=url, topic=topic)
        except VideoMaterial.DoesNotExist:
            video = None
        if video:
            subject = video.subject
        else:
            subject = None
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg='Video is not posted')
        self.assertIsNotNone(subject, msg='Subject is not created')

    def test_subject_view_returns_video_response(self):
        video = VideoMaterial.objects.first()
        subject = video.subject
        subject_url = reverse('subject-material-detail', kwargs={'pk': subject.pk})
        request = self.request_factory.get(subject_url)
        view = SubjectMaterialDetailView.as_view()
        response = view(request, pk=subject.pk)
        expected_response = {
                'topic': video.topic,
                'url': video.url
        }
        self.assertEqual(response.data, expected_response)

    def test_video_updates_subject_title_of_video_material(self):
        patched_subject_title = 'New subject title'
        video = VideoMaterial.objects.get(url='http://sample_video.com')
        pk = video.pk
        request_json = json.dumps({
            'subject_title': patched_subject_title,
        })
        video_url = reverse('video-material-detail', kwargs={'pk': pk})
        request = self.request_factory.patch(video_url, request_json, content_type='application/json')
        view = VideoMaterialViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=pk)
        subject = video.subject
        video.refresh_from_db()
        self.assertEqual(subject.title, patched_subject_title)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_video_updates_video_material_url(self):
        video = VideoMaterial.objects.get(url='http://updated_video.com')
        pk = video.pk
        new_video_url = 'http://youtube.com'
        request_json = json.dumps({
            'url': new_video_url,
        })
        video_url = reverse('video-material-detail', kwargs={'pk': pk})
        request = self.request_factory.patch(video_url, request_json, content_type='application/json')
        view = VideoMaterialViewSet.as_view({'patch': 'partial_update'})
        view(request, pk=pk)
        video.refresh_from_db()
        self.assertEqual(video.url, new_video_url)

    def test_video_updates_subject_lesson_of_video_material(self):
        video = VideoMaterial.objects.get(url='http://sample_video.com')
        pk = video.pk
        lesson_pk = Lesson.objects.order_by('-pk').first().pk
        request_json = json.dumps({
            'lesson': lesson_pk,
        })
        video_url = reverse('video-material-detail', kwargs={'pk': pk})
        request = self.request_factory.patch(video_url, request_json, content_type='application/json')
        view = VideoMaterialViewSet.as_view({'patch': 'partial_update'})
        view(request, pk=pk)
        video.refresh_from_db()
        ls_pk = video.subject.lesson.pk
        self.assertEqual(lesson_pk, ls_pk)

    def test_image_view_creates_image_material_with_one_image(self):
        subject_title ='Image subject'
        subject_number = self.get_last_subject_number()
        topic = 'just topic'
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open('tests/test.jpeg', 'rb').read(),
            content_type='image/jpeg'
        )
        image_description = 'Image decription'
        lesson_pk = Lesson.objects.first().pk
        request_dict = {
            'lesson': lesson_pk,
            'subject_title': subject_title,
            'subject_number': subject_number,
            'topic': topic,
            'images': image,
            'descriptions': image_description
        }
        image_url = reverse('image-material-list')
        request = self.request_factory.post(image_url, request_dict, format='multipart')
        view = ImageMaterialViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_image_view_creates_image_material_with_multiple_images(self):
        subject_title = 'Image subject'
        subject_number = self.get_last_subject_number()
        topic = 'just topic'
        images = []
        descriptions = []
        for i in range(3):
            image = SimpleUploadedFile(
                name=f'test_image_{i}.jpg',
                content=open('tests/test.jpeg', 'rb').read(),
                content_type='image/jpeg'
            )
            descriptions.append(f'image description {i}')
            images.append(image)
        lesson_pk = Lesson.objects.first().pk
        request_dict = {
            'lesson': lesson_pk,
            'subject_title': subject_title,
            'subject_number': subject_number,
            'topic': topic,
            'images': images,
            'descriptions': descriptions
        }
        image_url = reverse('image-material-list')
        request = self.request_factory.post(image_url, request_dict, format='multipart')
        view = ImageMaterialViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_image_view_add_image_in_image_material(self):
        image_material = ImageMaterial.objects.get(topic='Put image topic')
        pk = image_material.pk
        new_image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=open('tests/test.jpeg', 'rb').read(),
            content_type='image/jpeg'
        )
        new_description = 'Put image'
        request_dict = {
            'images': new_image_file,
            'descriptions': new_description,
        }
        image_url = reverse('image-material-detail', kwargs={'pk': pk})
        request = self.request_factory.patch(image_url, request_dict, format='multipart')
        view = ImageMaterialViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=pk)
        image_material.refresh_from_db()
        n_images = image_material.images.count()
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(2, n_images)

    def test_image_updates_subject_title_of_image_material(self):
        patched_subject_title = 'New subject title'
        image_material = ImageMaterial.objects.get(topic='Update image subject')
        pk = image_material.pk
        request_json = json.dumps({
            'subject_title': patched_subject_title,
        })
        image_url = reverse('image-material-detail', kwargs={'pk': pk})
        request = self.request_factory.patch(image_url, request_json, content_type='application/json')
        view = ImageMaterialViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=pk)
        subject = image_material.subject
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(subject.title, patched_subject_title)

    def test_assignment_view_creates_assignment_material(self):
        subject_title = 'Assignment subject'
        subject_number = self.get_last_subject_number()
        topic = 'Topic'
        task = 'Sample task'
        lesson_pk = Lesson.objects.first().pk
        request_json = json.dumps({
            '' 'lesson': lesson_pk,
            'subject_title': subject_title,
            'subject_number': subject_number,
            'topic': topic,
            'task': task,
        })
        assignment_url = reverse('assignment-material-list')
        request = self.request_factory.post(assignment_url, request_json, content_type='application/json')
        view = AssignmentMaterialViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_subject_view_returns_assignment_material_respone(self):
        assignment = AssignmentMaterial.objects.first()
        subject = assignment.subject
        subject_url = reverse('subject-material-detail', kwargs={'pk': subject.pk})
        request = self.request_factory.get(subject_url)
        view = SubjectMaterialDetailView.as_view()
        response = view(request, pk=subject.pk)
        expected_response = {
            'topic': assignment.topic,
            'task': assignment.task,
        }
        self.assertEqual(response.data, expected_response)

    def test_assignment_updates_subject_title_of_assignment_material(self):
        patched_subject_title = 'New subject title'
        assignment = AssignmentMaterial.objects.get(task='sample task')
        pk = assignment.pk
        request_json = json.dumps({
            'subject_title': patched_subject_title,
        })
        assignment_url = reverse('assignment-material-detail', kwargs={'pk': pk})
        request = self.request_factory.patch(assignment_url, request_json, content_type='application/json')
        view = AssignmentMaterialViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=pk)
        subject = assignment.subject
        self.assertEqual(subject.title, patched_subject_title)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_assignment_updates_subject_lesson_of_assignment_material(self):
        assignment = AssignmentMaterial.objects.get(task='sample task')
        pk = assignment.pk
        lesson_pk = Lesson.objects.order_by('-pk').first().pk
        request_json = json.dumps({
            'lesson': lesson_pk,
        })
        assignment_url = reverse('assignment-material-detail', kwargs={'pk': pk})
        request = self.request_factory.patch(assignment_url, request_json, content_type='application/json')
        view = AssignmentMaterialViewSet.as_view({'patch': 'partial_update'})
        view(request, pk=pk)
        ls_pk = assignment.subject.lesson.pk
        self.assertEqual(lesson_pk, ls_pk)

    def test_quiz_view_creates_quiz_material_with_different_tasks(self):
        subject_title = 'Quiz subject'
        subject_number = self.get_last_subject_number()
        lesson_pk = Lesson.objects.first().pk
        topic = 'just topic'
        quiz_dict = {
            'lesson': lesson_pk,
            'subject_title': subject_title,
            'subject_number': subject_number,
            'topic': topic,
            'tasks': [],
        }
        single_choice_task = {
            'question': 'single choice task',
            'answers': [
                {'answer_text': 'first', 'correct': True},
                {'answer_text': 'second', 'correct': False},
                {'answer_text': 'third', 'correct': False},
            ],
        }
        multiple_choice_task = {
            'question': 'multiple choice task',
            'answers': [
                {'answer_text': 'first', 'correct': True},
                {'answer_text': 'second', 'correct': True},
                {'answer_text': 'third', 'correct': False},
            ],
        }
        fill_the_blank_task = {
            'question': 'fill the blank task _____',
            'answers': [
                {'answer_text': 'first'},
            ],
        }
        quiz_dict['tasks'].append(single_choice_task)
        quiz_dict['tasks'].append(multiple_choice_task)
        quiz_dict['tasks'].append(fill_the_blank_task)
        request_json = json.dumps(quiz_dict)
        quiz_url = reverse('quiz-material-list')
        request = self.request_factory.post(quiz_url, request_json, content_type='application/json')
        view = QuizMaterialViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        single_choice_task_instance = Task.objects.get(question='single choice task')
        multiple_choice_task_instance = Task.objects.get(question='multiple choice task')
        fill_the_blank_task_instance = Task.objects.get(question='fill the blank task _____')
        self.assertEqual(single_choice_task_instance.task_type, Task.TaskType.SINGLE_ANSWER)
        self.assertEqual(multiple_choice_task_instance.task_type, Task.TaskType.MULTIPLE_ANSWERS)
        self.assertEqual(fill_the_blank_task_instance.task_type, Task.TaskType.FILL_IN_THE_BLANK)

    def test_quiz_view_add_task_in_quiz_material(self):
        quiz_material = QuizMaterial.objects.get(topic='Add task')
        pk = quiz_material.pk
        quiz_dict = {'tasks': []}
        single_choice_task = {
            'question': 'question text',
            'answers': [
                {'answer_text': 'first', 'correct': True},
                {'answer_text': 'second', 'correct': False},
                {'answer_text': 'third', 'correct': False},
            ],
        }
        quiz_dict['tasks'].append(single_choice_task)
        quiz_url = reverse('quiz-material-detail', kwargs={'pk': pk})
        request_json = json.dumps(quiz_dict)
        request = self.request_factory.patch(quiz_url, request_json, content_type='application/json')
        view = QuizMaterialViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=pk)
        n_task = quiz_material.tasks.count()
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(2, n_task)

    def test_quiz_view_updates_subject_title_of_quiz_material(self):
        patched_subject_title = 'New subject title'
        quiz = QuizMaterial.objects.get(topic='Add task')
        pk = quiz.pk
        request_json = json.dumps({
            'subject_title': patched_subject_title,
        })
        quiz_url = reverse('quiz-material-detail', kwargs={'pk': pk})
        request = self.request_factory.patch(quiz_url, request_json, content_type='application/json')
        view = QuizMaterialViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=pk)
        subject = quiz.subject
        self.assertEqual(subject.title, patched_subject_title)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_quiz_view_updates_subject_lesson_of_quiz_material(self):
        quiz = QuizMaterial.objects.get(topic='Add task')
        pk = quiz.pk
        lesson_pk = Lesson.objects.order_by('-pk').first().pk
        request_json = json.dumps({
            'lesson': lesson_pk,
        })
        quiz_url = reverse('quiz-material-detail', kwargs={'pk': pk})
        request = self.request_factory.patch(quiz_url, request_json, content_type='application/json')
        view = QuizMaterialViewSet.as_view({'patch': 'partial_update'})
        view(request, pk=pk)
        ls_pk = quiz.subject.lesson.pk
        self.assertEqual(lesson_pk, ls_pk)

    def test_subject_view_returns_200_respone(self):
        quiz = QuizMaterial.objects.first()
        subject = quiz.subject
        subject_url = reverse('subject-material-detail', kwargs={'pk': subject.pk})
        request = self.request_factory.get(subject_url)
        view = SubjectMaterialDetailView.as_view()
        response = view(request, pk=subject.pk)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_quiz_view_raise_validation_error_on_invalid_answers_schema(self):
        subject_title = 'Quiz subject'
        subject_number = self.get_last_subject_number()
        lesson_pk = Lesson.objects.first().pk
        topic = 'just topic'
        quiz_dict = {
            'lesson': lesson_pk,
            'subject_title': subject_title,
            'subject_number': subject_number,
            'topic': topic,
            'tasks': [],
        }
        single_choice_task = {
            'question': 'single choice task',
            'answers': [
                # {'aaaa': 'first', 'correct': True},
                # {'aaaa': 'second', 'correct': False},
                {'answer_text': 'third', 'correct': False},
                {'answer_text': 'fourth' , 'correct': True, 'SSS': 'SSS'}
            ],
        }
        quiz_dict['tasks'].append(single_choice_task)
        request_json = json.dumps(quiz_dict)
        quiz_url = reverse('quiz-material-list')
        request = self.request_factory.post(quiz_url, request_json, content_type='application/json')
        view = QuizMaterialViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_quiz_view_raise_validation_error_on_invalid_answers_schema_add_task_in_quiz_material(self):
        quiz_material = QuizMaterial.objects.get(topic='Add task')
        pk = quiz_material.pk
        quiz_dict = {'tasks': []}
        single_choice_task = {
            'question': 'question text',
            'answers': [
                {'answer_text': 'first', 'correct': True},
                {'answer_text': 'second', 'correct': False},
                {'aaaaa': 'third', 'correct': False},
            ],
        }
        quiz_dict['tasks'].append(single_choice_task)
        quiz_url = reverse('quiz-material-detail', kwargs={'pk': pk})
        request_json = json.dumps(quiz_dict)
        request = self.request_factory.patch(quiz_url, request_json, content_type='application/json')
        view = QuizMaterialViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=pk)
        n_task = quiz_material.tasks.count()
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(1, n_task)


