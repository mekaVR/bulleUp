from rest_framework import serializers

from ..models import Publisher, PublisherFollow


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class PublisherMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'profile_picture']


class PublisherFollowSerializer(serializers.ModelSerializer):
    publisher_name = serializers.SerializerMethodField()

    class Meta:
        model = PublisherFollow
        fields = ['id', 'publisher_name']

    def get_publisher_name(self, obj):
        return f"{obj.publisher.name}"
