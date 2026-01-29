from django.test import TestCase
from rest_framework import serializers
from apps.challenges.serializers.questions import QuestionSerializer
from apps.challenges.models.questions import Question

class QuestionSerializerTest(TestCase):
    def test_valid_pattern(self):
        data = {
            "title": "Two Sum",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            "function_name": "twoSum",
            "parameters": [
                {"name": "nums", "type": "list(int)"},
                {"name": "target", "type": "int"}
            ],
            "return_type": "list(int)",
            "test_cases": [
                {
                    "input": [
                        {"name": "nums", "value": [2, 7, 11, 15]},
                        {"name": "target", "value": 9}
                    ],
                    "output": [0, 1]
                }
            ],
            "difficulty": "easy"
        }
        serializer = QuestionSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_parameters(self):
        data = {
            "title": "Invalid Params",
            "description": "...",
            "function_name": "test",
            "parameters": "not a list",
            "return_type": "int",
            "test_cases": [],
            "difficulty": "easy"
        }
        serializer = QuestionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('parameters', serializer.errors)

    def test_invalid_test_cases(self):
        data = {
            "title": "Invalid Test Cases",
            "description": "...",
            "function_name": "test",
            "parameters": [],
            "return_type": "int",
            "test_cases": [
                {"input": "not a list", "output": 1}
            ],
            "difficulty": "easy"
        }
        serializer = QuestionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('test_cases', serializer.errors)
