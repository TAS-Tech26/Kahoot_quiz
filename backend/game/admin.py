# admin.py


from django.contrib import admin
from django.utils import timezone

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
    readonly_fields = ('team_code', 'name', 'total_score')
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

    list_display = ('pin', 'quiz', 'event_name', 'started_at', 'ended_at', 'is_active')
    list_filter = ('started_at', 'event_name')

    search_fields = ('pin', 'event_name')

    inlines = [PlayerResultInline] # Clicking on a session lets you see the entire leaderboard

    actions = ['force_end_sessions']

    def is_active(self, obj):

        return obj.ended_at is None

    is_active.boolean = True

    @admin.action(description = "Force-close selected abandoned sessions")
    def force_end_sessions(self, request, queryset):
        updated = queryset.filter(ended_at__isnull = True).update(ended_at = timezone.now())

        self.message_user(request, f"Successfully closed {updated} abandoned session(s).")


@admin.register(PlayerResult)
class PlayerResultAdmin(admin.ModelAdmin):

    list_display = ('team_code', 'name', 'session_pin', 'total_score')
    list_filter = ('session__pin',)

    search_fields = ('team_code', 'name', 'session__pin')

    def session_pin(self, obj):

        return obj.session.pin
    
    session_pin.short_description = "Game PIN"

# Choice doesn't need its own implementation since it's fully managed inside Question model. 