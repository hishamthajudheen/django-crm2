from django.contrib import admin
from .models import User, Lead, Agent, UserProfile, Category

admin.site.register(User)
admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Agent)
admin.site.register(Lead)