# models.py


from django.conf import settings
from django.db import models
from django.db.models import JSONField


class Quiz(models.Model):

    title = models.CharField(max_length = 255)
    is_published = models.BooleanField(default = False)
    compiled_data = JSONField(null = True, blank = True) # Stores the entire quiz (Qs & choices) in a single block.
    created_at = models.DateTimeField(auto_now_add = True)
    is_active = models.BooleanField(default = True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, limit_choices_to = {'is_staff' : True})

    def compile_for_redis(self):
        """
        Postgres is slow, Redis is fast. Basically this func queries Postgres for all the Qs in the quiz, process & pre-packages them & they're stored in Redis for
        faster access as this quiz will happen in real-time.
        """

        payload = {'quiz_id' : self.id, 'title' : self.title, 'questions' : []}

        for q in self.questions.all().prefetch_related('choices').order_by('order'):
            payload['questions'].append({
                'id' : q.id,
                'text' : q.text,
                'time_limit' : q.time_limit,
                'media_url' : q.media_url,
                'media_type' : q.media_type,
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

    media_url = models.URLField(max_length = 500, null = True, blank = True)
    media_type = models.CharField(max_length = 10, choices = [('image', 'Image'), ('video', 'Video'), ('audio', 'Audio')], null = True, blank = True)

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
    event_name = models.CharField(max_length = 255)
    
    quiz = models.ForeignKey(Quiz, on_delete = models.CASCADE)


class PlayerResult(models.Model):

    name = models.CharField(max_length = 255)
    total_score = models.IntegerField(default = 0)
    correct_answers = models.IntegerField(default = 0)
    total_time = models.FloatField(default = 0.0)
    team_code = models.CharField(max_length = 10, db_index = True)
    
    session = models.ForeignKey(GameSession, on_delete = models.CASCADE)

    class Meta:

        constraints = [models.UniqueConstraint(fields = ['session', 'team_code'], name = 'unique_team_per_session')]
