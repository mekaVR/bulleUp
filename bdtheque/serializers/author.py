from rest_framework import serializers

from ..models import Author, AuthorFollow, ComicBook, ComicBookAuthor


class AuthorFollowSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = AuthorFollow
        fields = ['id', 'author_name']

    def get_author_name(self, obj):
        if obj.author.first_name:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return f"{obj.author.last_name}"


class ComicBookForAuthorDetailSerializer(serializers.ModelSerializer):
    comic_book_id = serializers.PrimaryKeyRelatedField(queryset=ComicBook.objects.all())
    comic_book_title = serializers.SerializerMethodField()

    class Meta:
        model = ComicBookAuthor
        fields = ['comic_book_id', 'comic_book_title']

    def get_comic_book_title(self, obj):
        return obj.comic_book.title


class AuthorListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'author_name', 'profile_picture']

    def get_author_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class AuthorDetailSerializer(serializers.ModelSerializer):
    comic_book = ComicBookForAuthorDetailSerializer(source='comicbookauthor_set', many=True, read_only=True)

    class Meta:
        model = Author
        fields = '__all__'
