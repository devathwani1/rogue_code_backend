from django.db import models
from django.utils.text import slugify

class Question(models.Model):

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField()
    function_name = models.CharField(max_length=100)
    parameters = models.JSONField()
    return_type = models.CharField(max_length=100)
    test_cases = models.JSONField()

    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @staticmethod
    def get(slug: str):
        return Question.objects.get(slug=slug)
