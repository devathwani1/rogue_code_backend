# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("challenges", "0006_dailyplanitem_solve"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="questionplan",
            name="version",
        ),
    ]
