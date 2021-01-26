import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from qazline.models import VideoMaterial, ImageMaterial, AssignmentMaterial, QuizMaterial, Image


def _delete_file(path):
    """ Deletes file from filesystem. """
    if os.path.isfile(path):
        os.remove(path)


@receiver(post_delete, sender=Image)
def delete_file(sender, instance, *args, **kwargs):
    # TODO Check if this condition is needed
    if instance.image:
        _delete_file(instance.image.path)


def delete_related_material(sender, instance, **kwargs):
    deleted_material = instance
    deleted_material.subject.delete()


post_delete.connect(delete_related_material, sender=VideoMaterial)
post_delete.connect(delete_related_material, sender=ImageMaterial)
post_delete.connect(delete_related_material, sender=AssignmentMaterial)
post_delete.connect(delete_related_material, sender=QuizMaterial)
