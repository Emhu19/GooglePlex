# Generated by Django 5.1.4 on 2025-01-21 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PST', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('keywords', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.DeleteModel(
            name='WebPageFTS',
        ),
        migrations.AddIndex(
            model_name='webpage',
            index=models.Index(fields=['title'], name='PST_webpage_title_a51fc3_idx'),
        ),
        migrations.AddIndex(
            model_name='webpage',
            index=models.Index(fields=['keywords'], name='PST_webpage_keyword_b0c702_idx'),
        ),
    ]
