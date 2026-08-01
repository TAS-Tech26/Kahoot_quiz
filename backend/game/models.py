# models.py


from django.conf import settings
from django.db import models
from django.db.models import JSONField

import uuid


class Quiz(models.Model):

    title = models.CharField(max_length = 255)
    is_published = models.BooleanField(default = False)
    compiled_data = JSONField(null = True, blank = True) # Stores the entire quiz (Qs & choices) in a single block.
    created_at = models.DateTimeField(auto_now_add = True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, limit_choices_to = {'is_staff' : True})

    def compile_for_redis(self):
        """
        Postgres is slow, Redis is fast. Basically this func queries Postgres for all the Qs in the quiz, process & pre-packages them & they're stored in Redis for
        faster access as this quiz will happen in real-time.
        """

        payload = {'quiz_id' : self.id, 'title' : self.title, 'questions' : []}

        for q in self.questions.all().order_by('order'):
            payload['questions'].append({
                'id' : q.id,
                'text' : q.text,
                'time_limit' : q.time_limit,
                'choices' : [{'id' : c.id, 'text' : c.text, 'is_correct' : c.is_correct} for c in q.choices.all()]
            })

        self.compiled_data = payload
        self.is_published = True
        self.save(update_fields = ['compiled_data', 'is_published'])

        return payload
    
    def __str__(self):

        return f"Quiz {self.id}"


class Question(models.Model):

    text = models.CharField(max_length = 500)
    time_limit = models.IntegerField(default = 10)
    order = models.IntegerField(default = 0)

    quiz = models.ForeignKey(Quiz, related_name = 'questions', on_delete = models.CASCADE)

    def __str__(self):

        return self.text[:50] # Shows the 1st 50 chars of the Q


class Choice(models.Model):

    text = models.CharField(max_length = 255)
    is_correct = models.BooleanField(default = False)

    question = models.ForeignKey(Question, related_name = 'choices', on_delete = models.CASCADE)

    def __str__(self):

        return f"{self.text} (Correct)" if self.is_correct else self.text


class GameSession(models.Model):

    pin = models.CharField(max_length = 6, unique = True, db_index = True)
    started_at = models.DateTimeField(auto_now_add = True)
    ended_at = models.DateTimeField(null = True, blank = True)
    final_leaderboard = JSONField(null = True, blank = True)
    event_name = models.CharField(max_length = 255, default = 'standard')
    
    quiz = models.ForeignKey(Quiz, on_delete = models.CASCADE)


class PlayerResult(models.Model):

    player_id = models.UUIDField(default = uuid.uuid4, editable = False, db_index = True)
    full_name = models.CharField(max_length = 255)
    contact_info = models.CharField(max_length = 255)
    total_score = models.IntegerField(default = 0)
    school_name = models.CharField(max_length = 255, null = True, blank = True)
    grade_level = models.IntegerField(null = True, blank = True)

    session = models.ForeignKey(GameSession, on_delete = models.CASCADE)
    team_code = models.CharField(max_length = 10, null = True, blank = True)