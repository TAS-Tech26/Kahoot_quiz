# authentication.py


from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

import jwt


User = get_user_model()


class HubJWTAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith("Bearer "):

            return None

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.HUB_SECRET_KEY, algorithms = ['HS256'])

            if payload.get('role') == 'host':
                user, _ = User.objects.get_or_create(username = payload['username'], defaults = {'is_staff' : True})
                
                return (user, token)
            elif 'team_code' in payload and 'event_name' in payload:
                class AuthenticatedTeam:

                    def __init__(self, team_code, event_name):
                        self.team_code = team_code
                        self.event_name = event_name
                        self.is_authenticated = True
                        self.is_staff = False

                return (AuthenticatedTeam(payload['team_code'], payload['event_name']), token)
            else:
                raise AuthenticationFailed("Unrecognised token payload structure.")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid cryptographic signature.")