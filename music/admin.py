from django.contrib import admin

# Register your models here.

# Admin functionality for the app

from .models import Album, Song

admin.site.register(Album)
admin.site.register(Song)