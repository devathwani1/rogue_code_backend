from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("challenges", "0009_userquestionlastattempt"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="image_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]

