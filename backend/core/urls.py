# urls.py


from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from game.views import (
    create_game_session, create_quiz, delete_quiz, export_event_scores, list_host_quizzes, get_cloudinary_signature, get_quiz_detail, update_quiz, verify_pin
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),

    path('api/game/create/', create_game_session, name = 'create_session'),
    path('api/game/verify/<str:pin>/', verify_pin, name = 'verify_pin'),
    
    path('api/media/signature/', get_cloudinary_signature, name = 'cloudinary_signature'),

    path('api/quizzes/', list_host_quizzes, name = 'list_quizzes'),
    path('api/quizzes/<int:quiz_id>/', get_quiz_detail, name = 'get_quiz_detail'),
    path('api/quizzes/create/', create_quiz, name = 'create-quiz'),
    path('api/quizzes/<int:quiz_id>/update/', update_quiz, name = 'update_quiz'),
    path('api/quizzes/<int:quiz_id>/delete/', delete_quiz, name = 'delete_quiz'),

    path('api/export-scores/<str:event_name>/', export_event_scores, name = 'export_scores')
]
