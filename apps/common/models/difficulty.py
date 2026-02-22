from django.db import models

class Difficulty(models.Model):
    name = models.CharField(max_length=50, unique=True)
    mode_name = models.CharField(max_length=50, default='Easy')
    logo = models.TextField(help_text="SVG logo content", null=True, blank=True)
    days = models.PositiveIntegerField(help_text="Number of days for this level")
    number_of_questions = models.PositiveIntegerField(help_text="Expected number of questions for this level")

    class Meta:
        verbose_name_plural = "Difficulties"

    def __str__(self):
        return self.name
