# serializers.py


from django.db import transaction
from rest_framework import serializers

from .models import Choice, Question, Quiz


class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:

        model = Choice
        fields = ['text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):

    choices = ChoiceSerializer(many = True)

    class Meta:

        model = Question
        fields = ['text', 'time_limit', 'media_url', 'media_type', 'choices']

    def validate_choices(self, value):
        if len(value) < 2:

            raise serializers.ValidationError("A question must have at least 2 choices.")

        has_correct = any(c.get('is_correct') for c in value)

        if not has_correct:

            raise serializers.ValidationError("A question must have at least 1 correct choice.")

        return value

class QuizSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many = True)

    class Meta:

        model = Quiz
        fields = ['title', 'questions']

    def validate_questions(self, value):
        if not value or len(value) < 1:

            raise serializers.ValidationError("The quiz must contain at least 1 question.")

        return value

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')

        author = self.context['request'].user

        with transaction.atomic():
            quiz = Quiz.objects.create(author = author, **validated_data)

            for index, q_data in enumerate(questions_data):
                choices_data = q_data.pop('choices')

                question = Question.objects.create(quiz = quiz, order = index, **q_data)

                Choice.objects.bulk_create([Choice(question = question, **c_data) for c_data in choices_data])

            quiz.compile_for_redis()

        return quiz