# Generated by Django 5.1.4 on 2024-12-30 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_post_updated_at_alter_post_image_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='position',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]