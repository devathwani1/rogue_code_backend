from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("challenges", "0010_question_image_url"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="image_url",
        ),
        migrations.AddField(
            model_name="question",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="question_images/"),
        ),
    ]

