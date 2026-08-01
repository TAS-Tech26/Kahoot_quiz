# urls.py


"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from game.views import create_game_session, export_event_scores, list_host_quizzes, verify_pin


urlpatterns = [
    path('admin/', admin.site.urls),

    path ('api/token/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),

    path('api/game/create/', create_game_session, name = 'create_session'),
    path('api/game/verify/<str:pin>', verify_pin, name = 'verify_pin'),
    path('api/quizzes/', list_host_quizzes, name = 'list_quizzes'),

    path('api/export-scores/<str:event_name>/', export_event_scores, name = 'export_scores')
]
