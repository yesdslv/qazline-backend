# Generated by Django 3.0.5 on 2020-09-04 18:52

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qazline', '0003_auto_20200831_0928'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizMaterial',
            fields=[
                ('subject', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='qazline.Subject')),
                ('topic', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='image',
            name='image_material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='qazline.ImageMaterial'),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answers', django.contrib.postgres.fields.jsonb.JSONField()),
                ('type', models.CharField(choices=[('SA', 'Одиночный ответ'), ('MA', 'Множественный ответ'), ('FB', 'Заполнить пропуск')], default='SA', max_length=2)),
                ('quiz_material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='qazline.QuizMaterial')),
            ],
        ),
    ]
