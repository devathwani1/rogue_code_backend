# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0002_alter_profile_difficulty"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="last_closed_ist_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
