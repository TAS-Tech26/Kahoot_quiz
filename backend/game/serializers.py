# serializers.py


from rest_framework import serializers

from .models import PlayerResult

import os, requests


class PlayerJoinSerializer(serializers.Serializer):

    full_name = serializers.CharField(max_length = 255, allow_blank = False, trim_whitespace = True)
    contact_info = serializers.CharField(max_length = 255, allow_blank = False, trim_whitespace = True)
    school_name = serializers.CharField(max_length = 255, allow_blank = True, trim_whitespace = True, required = False)
    grade_level = serializers.IntegerField(required = False) # Update this after confirming with EVM

    team_code = serializers.CharField(max_length = 10, allow_blank = True, required = False)

    def validate(self, data):
        session = self.context.get('session')

        if not session:

            raise serializers.ValidationError("Critical Error: Session context missing.")
        
        event_name = session.event_name

        if event_name == 'standard':
            if not data.get('school_name'):
        
                raise serializers.ValidationError({'school_name' : "School name is required for standard events."})
            if not data.get('grade_level'):
                    
                raise serializers.ValidationError({'grade_level' : "Grade level is required for standard events."})
        
            return data

        team_code = data.get('team_code')

        if not team_code:

            raise serializers.ValidationError({'team_code' : "Team code is required for tournament events."})

        # Only 1 device per team code per room
        if PlayerResult.objects.filter(session = session, team_code = team_code).exists():

            raise serializers.ValidationError({'team_code' : "This team code has already joined the lobby. Only 1 device is allowed."})

        hub_url = os.environ.get('HUB_SERVICE_URL')
        hub_secret_key = os.environ.get('HUB_SECRET_KEY')

        try:
            verify_response = requests.get(f'{hub_url}/api/admin/verify-team/{team_code}/{event_name}/', headers = {'X-Hub-Secret' : hub_secret_key}, timeout = 3)

            if not verify_response.ok:

                raise serializers.ValidationError({'team_code' : "Invalid team code. Please try again."})
        except requests.exceptions.RequestException:

            raise serializers.ValidationError({'team_code' : "Error occurred while verifying team code. Please try again."})

        return data