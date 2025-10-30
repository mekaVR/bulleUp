from rest_framework import serializers

from ..models import ComicBook, ComicBookAuthor, Author
from .publisher import PublisherMiniSerializer
from .review import ReviewSerializer


class ComicBookAuthorSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = ComicBookAuthor
        fields = ['author_id', 'author_name', 'role']

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}" if obj.author.first_name else None


class ComicBookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComicBook
        fields = ['id', 'title', 'series', 'volume', 'cover_image']


class ComicBookDetailSerializer(serializers.ModelSerializer):
    authors = ComicBookAuthorSerializer(source='comicbookauthor_set', many=True, read_only=True)
    publisher = PublisherMiniSerializer(read_only=True)
    reviews = ReviewSerializer(read_only=True,  many=True)

    class Meta:
        model = ComicBook
        fields = '__all__'
