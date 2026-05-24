from rest_framework import serializers


class ApiErrorSerializer(serializers.Serializer):
    error = serializers.CharField()


class ScoreSubmissionRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    points = serializers.IntegerField()


class ScoreSubmissionResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    saved = serializers.BooleanField()


class ProfileImageUploadRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    image = serializers.ImageField()


class ProfileImageUploadResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    image_url = serializers.CharField()


class LeaderboardUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    points = serializers.IntegerField()
    profile_image = serializers.CharField(allow_null=True)


class ProfileImageResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    profile_image = serializers.CharField(allow_null=True)
    message = serializers.CharField(required=False)
