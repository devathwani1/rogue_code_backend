from django.db import models
from .questions import Question

class QuestionParameter(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="parameters")
    name = models.CharField(max_length=100)
    type_schema = models.JSONField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.question.title} - {self.name}"

    class Meta:
        ordering = ['order']
