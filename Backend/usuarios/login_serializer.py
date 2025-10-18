from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    Email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)