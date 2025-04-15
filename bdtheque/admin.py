from django.contrib import admin
from .models import *

class ComicBookAdmin(admin.ModelAdmin):

     list_display = ('title','volume', 'series', 'ean', 'publisher', 'genre', 'category')


admin.site.register(ComicBook, ComicBookAdmin)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Review)
admin.site.register(ComicBookAuthor)
admin.site.register(UserCollection)
admin.site.register(UserWishlist)