# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0005_profile_last_closed_ist_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="xp",
        ),
    ]
