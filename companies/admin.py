from django.contrib import admin
from .models import Company, Director, Listing, BoardMember, Exchange

admin.site.register(Company)
admin.site.register(Director)
admin.site.register(Listing)
admin.site.register(BoardMember)
admin.site.register(Exchange)

