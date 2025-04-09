from django.contrib import admin
from .models import *

admin.site.register(ComicBook)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Review)
admin.site.register(ComicBookAuthor)
admin.site.register(UserCollection)
admin.site.register(UserWishlist)