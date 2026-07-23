# serializers.py


from rest_framework import serializers


class PlayerJoinSerializer(serializers.Serializer):

    full_name = serializers.CharField(max_length = 255, allow_blank = False, trim_whitespace = True)
    contact_info = serializers.CharField(max_length = 255, allow_blank = False, trim_whitespace = True)
    school_name = serializers.CharField(max_length = 255, allow_blank = False, trim_whitespace = True)
    grade_level = serializers.IntegerField(min_value = 1, max_value = 20) # Update this after confirming with EVM