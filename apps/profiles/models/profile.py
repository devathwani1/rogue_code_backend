from django.conf import settings
from django.db import models
from django.utils import timezone


class Profile(models.Model):

    class Difficulty(models.TextChoices):
        LOW = "low", "Low"
        STANDARD = "standard", "Standard"
        CRUSHING = "crushing", "Crushing"

    class Language(models.TextChoices):
        CPP = "cpp", "C++",
        PYTHON = "python", "Python",
        JAVA = "java", "Java",

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name="profile"
    )

    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        null=True,
        blank=True
    )

    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        null=True,
        blank=True
    )

    profile_id = models.AutoField(primary_key=True)
    lives = models.PositiveSmallIntegerField(default=3)
    streak = models.PositiveIntegerField(default=0)
    max_streak = models.PositiveIntegerField(default=0)

    challenge_day = models.PositiveIntegerField(default=1)
    is_rogue = models.BooleanField(default=False)
    
    joined_challenge_at = models.DateTimeField(null=True, blank=True)
    last_completed_at = models.DateTimeField(null=True, blank=True)

    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Profile {self.profile_id} - User: {self.user.username}"