import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.validators import ValidationError

from qazline.models import VideoMaterial, ImageMaterial, AssignmentMaterial, QuizMaterial, Image, Task

FILL_THE_BLANK_SPECIAL_CHARS = '_____'


def _delete_file(path):
    """ Deletes file from filesystem. """
    if os.path.isfile(path):
        os.remove(path)


@receiver(post_delete, sender=Image)
def delete_file(sender, instance, *args, **kwargs):
    if instance.image:
        _delete_file(instance.image.path)


def _define_task_type(task: Task):
    answers = task.answers
    question = task.question
    n_true_answer = 0
    n_values = 0
    for answer in answers:
        if 'correct' in answer:
            n_values += 1
            is_correct = answer['correct']
            if is_correct:
                n_true_answer += 1
    _is_valid_answers(answers, question, n_values)
    if n_values == 0:
        task_type = Task.TaskType.FILL_IN_THE_BLANK
    elif n_true_answer == 1:
        task_type = Task.TaskType.SINGLE_ANSWER
    else:
        task_type = Task.TaskType.MULTIPLE_ANSWERS
    return task_type


def _is_valid_answers(answers, question, n_values):
    if n_values != 0:
        # Check single choice and multipe choice question
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


@receiver(pre_save, sender=Task)
def set_task_type(sender, instance, *args, **kwargs):
    task_type = _define_task_type(instance)
    instance.task_type = task_type


def delete_related_material(sender, instance, **kwargs):
    deleted_material = instance
    deleted_material.subject.delete()


post_delete.connect(delete_related_material, sender=VideoMaterial)
post_delete.connect(delete_related_material, sender=ImageMaterial)
post_delete.connect(delete_related_material, sender=AssignmentMaterial)
post_delete.connect(delete_related_material, sender=QuizMaterial)
