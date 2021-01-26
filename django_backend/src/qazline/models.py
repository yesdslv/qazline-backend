from functools import wraps
from datetime import datetime


from django.db import models, IntegrityError
from django.apps import apps
from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_image_file_extension, ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from qazline.managers import QazlineUserManager
from qazline.validators import JSONSchemaValidator, ANSWER_JSON_FIELD_SCHEMA

fs = FileSystemStorage(location='/media/photos')

FILL_THE_BLANK_SPECIAL_CHARS = '_____'


# Get subclasses of Material abstract model in qazline app
def get_subclasses():
    result = []
    for model in apps.get_app_config('qazline').get_models():
        if issubclass(model, Material) and model is not Material:
            result.append(model)
    return result


def get_path_for_image(instance, filename):
    base_name = str(datetime.now().timestamp()).replace('.', '')
    extension = filename.split('.')[-1]
    image_material_pk = instance.image_material.pk
    path = f'{image_material_pk}/{base_name}.{extension}'
    return path


def check_subject_existence(save):
    @wraps(save)
    def wrapper(self, *args, **kwargs):
        child_models = get_subclasses()
        subject = self.subject
        for child_model in child_models:
            if not isinstance(self, child_model):
                if child_model.objects.filter(subject=subject).exists():
                    raise IntegrityError(f'{subject} exist in {child_model.__name__.lower()} table')
        save(self, *args, **kwargs)
    return wrapper


class QazlineUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = QazlineUserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'  # pragma: no cover


class Lesson(models.Model):
    number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return f'#{self.number}: {self.title}'  # pragma: no cover


class Subject(models.Model):
    number = models.IntegerField()
    lesson = models.ForeignKey(Lesson, null=True, on_delete=models.SET_NULL, related_name='subjects')
    title = models.CharField(max_length=50)
    objects = models.Manager()

    class Meta:
        unique_together = ('number', 'lesson',)

    def __str__(self):
        return f'{self.title}'

    def has_video_material(self):
        return hasattr(self, 'videomaterial')

    def has_image_material(self):
        return hasattr(self, 'imagematerial')

    def has_assignment_material(self):
        return hasattr(self, 'assignmentmaterial')

    def has_quiz_material(self):
        return hasattr(self, 'quizmaterial')


class Material(models.Model):
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE, primary_key=True)
    topic = models.CharField(blank=True, max_length=255)

    class Meta:
        abstract = True

    @check_subject_existence
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class VideoMaterial(Material):
    url = models.URLField()


class ImageMaterial(Material):
    pass


class Image(models.Model):
    image_material = models.ForeignKey(ImageMaterial, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(validators=[validate_image_file_extension], upload_to=get_path_for_image)
    description = models.CharField(blank=True, max_length=255)


class AssignmentMaterial(Material):
    task = models.TextField(default='')


class QuizMaterial(Material):
    pass


class Task(models.Model):

    class TaskType(models.TextChoices):
        SINGLE_ANSWER = 'SA', 'Одиночный ответ'
        MULTIPLE_ANSWERS = 'MA', 'Множественный ответ'
        FILL_IN_THE_BLANK = 'FB', 'Заполнить пропуск'

    quiz_material = models.ForeignKey(QuizMaterial, on_delete=models.CASCADE, related_name='tasks')
    question = models.TextField()
    answers = models.JSONField(validators=[
        JSONSchemaValidator(limit_value=ANSWER_JSON_FIELD_SCHEMA),

    ])
    task_type = models.CharField(max_length=2, choices=TaskType.choices, default=TaskType.SINGLE_ANSWER)

    def save(self, *args, **kwargs):
        task_type = kwargs.get('task_type')
        if not task_type:
            task_type = self._define_task_type()
            self.task_type = task_type
        super().save(*args, **kwargs)

    def _define_task_type(self):
        answers = self.answers
        question = self.question
        n_true_answer = 0
        n_values = 0
        for answer in answers:
            if 'correct' in answer:
                n_values += 1
                is_correct = answer['correct']
                if is_correct:
                    n_true_answer += 1
        self._is_valid_answers(answers, question, n_values)
        if n_values == 0:
            task_type = Task.TaskType.FILL_IN_THE_BLANK
        elif n_true_answer == 1:
            task_type = Task.TaskType.SINGLE_ANSWER
        else:
            task_type = Task.TaskType.MULTIPLE_ANSWERS
        return task_type

    @staticmethod
    def _is_valid_answers(answers, question, n_values):
        # TODO Refactor check answer
        if n_values != 0:
            # Check single choice and multiple choice question
            if len(answers) != n_values:
                raise ValidationError({
                    'answers': 'In single-choice or multiple-choice tasks for not all answers are given correct values'
                })
        else:
            n_blank_spec_chars = question.count(FILL_THE_BLANK_SPECIAL_CHARS)
            if n_blank_spec_chars != len(answers):
                raise ValidationError({
                    'answers': 'Number of answers are different from number of fill the blank special character'
                })
