from rest_framework import serializers

from authentication.models import User
from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_name = serializers.SerializerMethodField()
    comic_book_title = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'

    def get_user_name(self, obj):
        return f"{obj.user}"

    def get_comic_book_title(self, obj):
        return f"{obj.comic_book.title}"
