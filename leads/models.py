from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    is_organizer = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username
    
class Lead(models.Model):       
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    age = models.IntegerField(default=0)    
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent = models.ForeignKey("Agent",null=True, blank=True, on_delete=models.SET_NULL) 
    category = models.ForeignKey("Category", related_name="leads",on_delete=models.SET_NULL, null=True, blank=True)    
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number= models.CharField(max_length=20)
    email = models.EmailField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"   
    
class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.email
    
class Category(models.Model):
    name = models.CharField(max_length=30)
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.name 
    
def post_user_created_signal(sender, instance, created, **kwargs):
    print(instance, created)
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(post_user_created_signal, sender=User)