# serializers.py


from django.db import transaction
from rest_framework import serializers

from .models import Choice, Question, Quiz


class ChoiceSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required = False)

    class Meta:

        model = Choice
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required = False)
    choices = ChoiceSerializer(many = True)

    class Meta:

        model = Question
        fields = ['id', 'text', 'time_limit', 'media_url', 'media_type', 'choices']

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

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', [])

        with transaction.atomic():
            instance.title = validated_data.get('title', instance.title)
            instance.save(update_fields = ['title'])

            existing_q_ids = set(instance.questions.values_list('id', flat = True))
            incoming_q_ids = set()

            for index, q_data in enumerate(questions_data):
                choices_data = q_data.pop('choices', [])
                q_id = q_data.get('id')

                if q_id and q_id in existing_q_ids:
                    question = Question.objects.get(id = q_id, quiz = instance)

                    for attr, value in q_data.items():
                        setattr(question, attr, value)

                    question.order = index
                    question.save()

                    incoming_q_ids.add(q_id)
                else:
                    question = Question.objects.create(quiz = instance, order = index, **q_data)

                existing_c_ids = set(question.choices.values_list('id', flat = True))
                incoming_c_ids = set()

                for c_data in choices_data:
                    c_id = c_data.get('id')

                    if c_id and c_id in existing_c_ids:
                        choice = Choice.objects.get(id = c_id, question = question)

                        for attr, value in c_data.items():
                            setattr(choice, attr, value)

                        choice.save()

                        incoming_c_ids.add(c_id)
                    else:
                        Choice.objects.create(question = question, **c_data)

                choices_to_delete = existing_c_ids - incoming_c_ids

                if choices_to_delete:
                    Choice.objects.filter(id__in = choices_to_delete).delete()

            questions_to_delete = existing_q_ids - incoming_q_ids

            if questions_to_delete:
                Question.objects.filter(id__in = questions_to_delete).delete()

            instance.compile_for_redis()

        return instance