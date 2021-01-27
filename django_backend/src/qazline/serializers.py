from rest_framework import serializers

from qazline.models import (
    Lesson, Subject, Material, VideoMaterial, AssignmentMaterial, ImageMaterial, Image, QuizMaterial, Task,
)


class SubjectSerializer(serializers.ModelSerializer):
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())

    class Meta:
        model = Subject
        fields = ('number', 'title', 'lesson')


class ReadOnlySubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ('number', 'title',)
        read_only_fields = ('number', 'title',)


class LessonSerializer(serializers.ModelSerializer):
    subjects = ReadOnlySubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'number', 'title', 'subjects',
        )


class MaterialSerializer(serializers.ModelSerializer):
    subject_title = serializers.CharField(max_length=50, write_only=True)
    lesson = serializers.IntegerField(write_only=True)
    subject_number = serializers.IntegerField(write_only=True)

    class Meta:
        abstract = True
        model = Material
        fields = ('lesson', 'subject_number', 'subject_title', 'topic',)

    def create(self, validated_data):
        subject_title = validated_data.pop('subject_title')
        subject_number = validated_data.pop('subject_number')
        lesson_id = validated_data.pop('lesson')
        subject = Subject.objects.create(number=subject_number, title=subject_title, lesson_id=lesson_id)
        validated_data['subject'] = subject

    def update(self, instance, validated_data):
        subject_title = validated_data.pop('subject_title', None)
        subject_number = validated_data.pop('subject_number', None)
        lesson_id = validated_data.pop('lesson', None)
        subject = instance.subject
        if subject_number:
            subject.number = subject_number
        if subject_title:
            subject.title = subject_title
        if lesson_id:
            subject.lesson_id = lesson_id
        subject.save()
        instance = super().update(instance, validated_data)
        return instance

    def validate_lesson(self, value):
        if not Lesson.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f'Cannot create material, cause lesson with pk: {value} does not exist')
        return value


class VideoMaterialSerializer(MaterialSerializer):

    def create(self, validated_data):
        super().create(validated_data)
        instance = VideoMaterial.objects.create(**validated_data)
        return instance

    class Meta:
        model = VideoMaterial
        fields = MaterialSerializer.Meta.fields + ('url',)


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Image
        fields = ('image', 'description',)
        read_only_fields = ('image', 'description',)


class ImageMaterialSerializer(MaterialSerializer):

    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False), write_only=True,
    )
    descriptions = serializers.ListField(
        child=serializers.CharField(max_length=255, allow_blank=True), write_only=True,
    )

    class Meta:
        model = ImageMaterial
        fields = MaterialSerializer.Meta.fields + ('images', 'descriptions',)

    def create(self, validated_data):
        super().create(validated_data)
        images = validated_data.pop('images')
        descriptions = validated_data.pop('descriptions')
        instance = ImageMaterial.objects.create(**validated_data)
        self._save_image(images, descriptions, instance)
        return instance

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        descriptions = validated_data.pop('descriptions', None)
        self._save_image(images, descriptions, instance)
        instance = super().update(instance, validated_data)
        return instance

    def validate(self, attrs):
        # TODO review this part
        if not self.partial:
            attrs = super().validate(attrs)
            images = attrs.get('images', None)
            descriptions = attrs.get('descriptions', None)
            if not images:
                raise serializers.ValidationError('Images are not provided')
            if not descriptions:
                raise serializers.ValidationError('Descriptions are not provided')
            if len(images) != len(descriptions):
                raise serializers.ValidationError('Number of images must be the same as number of image descriptions')
        return attrs

    def to_representation(self, instance):
        self.fields['images'] = ImageSerializer(many=True)
        return super().to_representation(instance)

    @staticmethod
    def _save_image(images, descriptions, instance):
        if images and descriptions:
            for image, description in zip(images, descriptions):
                Image.objects.create(image=image, description=description, image_material=instance)


class AssignmentMaterialSerializer(MaterialSerializer):

    class Meta:
        model = AssignmentMaterial
        fields = MaterialSerializer.Meta.fields + ('task',)

    def create(self, validated_data):
        super().create(validated_data)
        instance = AssignmentMaterial.objects.create(**validated_data)
        return instance


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('question', 'answers', 'task_type',)
        read_only_fields = ('task_type',)


class QuizMaterialSerializer(MaterialSerializer):
    tasks = TaskSerializer(many=True)

    class Meta:
        model = QuizMaterial
        fields = MaterialSerializer.Meta.fields + ('tasks',)

    def create(self, validated_data):
        super().create(validated_data)
        tasks = validated_data.pop('tasks')
        instance = QuizMaterial.objects.create(**validated_data)
        for task in tasks:
            self._create_task(task, instance)
        return instance

    def update(self, instance, validated_data):
        tasks = validated_data.pop('tasks', None)
        if tasks:
            for task in tasks:
                self._create_task(task, instance)
        instance = super().update(instance, validated_data)
        return instance

    @staticmethod
    def _create_task(task, quiz_material_instance):
        question = task['question']
        answers = task['answers']
        instance = Task.objects.create(
            question=question, answers=answers, quiz_material=quiz_material_instance
        )
        instance.save()


