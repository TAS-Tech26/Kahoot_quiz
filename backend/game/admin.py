# admin.py


from django.contrib import admin

from .models import Choice, GameSession, PlayerResult, Question, Quiz

# INLINES (Allows managing nested data in 1 page)
class ChoiceInline(admin.TabularInline):

    model = Choice
    extra = 4 # Pre-populates 4 choices automatically for new Qs
    readonly_fields = ('id',)
    fields = ('text', 'is_correct')


class PlayerResultInline(admin.TabularInline):

    model = PlayerResult
    extra = 0 # Not pre-populating empty rows for players
    readonly_fields = ('player_id', 'full_name', 'contact_info', 'school_name', 'grade_level', 'total_score')
    can_delete = False # Prevent accidental deletion of student records during the event


# MODEL ADMINS (For configuring lists, searching, etc.)
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):

    list_display = ('id', 'has_compiled_data')

    def has_compiled_data(self, obj):

        return bool(obj.compiled_data)

    has_compiled_data.boolean = True
    has_compiled_data.short_description = 'Compiled'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = ('text', 'quiz', 'time_limit')
    list_filter = ('quiz',)

    search_fields = ('text',)

    inlines = [ChoiceInline] # Add/edit choices directly inside the Q view


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):

    list_display = ('pin', 'quiz', 'started_at', 'ended_at')
    list_filter = ('started_at',)

    search_fields = ('pin',)

    inlines = [PlayerResultInline] # Clicking on a session lets you see the entire leaderboard


@admin.register(PlayerResult)
class PlayerResultAdmin(admin.ModelAdmin):

    list_display = ('full_name', 'session_pin', 'total_score', 'school_name', 'grade_level')
    list_filter = ('grade_level', 'school_name', 'session__pin')

    search_fields = ('full_name', 'contact_info', 'school_name', 'session__pin')

    def session_pin(self, obj):

        return obj.session.pin
    
    session_pin.short_description = "Game PIN"

# Choice doesn't need its own implementation since it's fully managed inside Question model. 