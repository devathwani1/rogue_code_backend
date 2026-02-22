from django.db import models
from .questions import Question

class TestCase(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="test_cases")
    input_data = models.JSONField()
    expected_output = models.JSONField()
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"TestCase for {self.question.title} ({'Hidden' if self.is_hidden else 'Public'})"
