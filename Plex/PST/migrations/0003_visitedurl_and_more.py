# Generated by Django 5.1.4 on 2025-01-22 08:20

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PST', '0002_webpage_delete_webpagefts_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitedURL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
            ],
        ),
        migrations.RemoveIndex(
            model_name='webpage',
            name='PST_webpage_title_a51fc3_idx',
        ),
        migrations.RemoveIndex(
            model_name='webpage',
            name='PST_webpage_keyword_b0c702_idx',
        ),
        migrations.AddField(
            model_name='webpage',
            name='content_length',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='webpage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='webpage',
            name='language',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='webpage',
            name='last_modified',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='webpage',
            name='meta_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='webpage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='webpage',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='webpage',
            name='keywords',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='webpage',
            name='title',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
