from django.db import models
# import random
# import string

class UserManager(models.Manager):
    def authenticate(self, username, password):
        try:
            user = self.get(username=username, password=password)
            return user
        except User.DoesNotExist:
            return None

class User(models.Model):
    id = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=100)
    middleName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=255, blank=True, null=True)
    companyId = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    objects = UserManager()

class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=100)
    middleName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    objects = UserManager() 

class Slip(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confHR = models.BooleanField(default=False, blank=True, null=True)
    confhead = models.BooleanField(default=False, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    status = models.BooleanField(default=False)
    timeIn = models.DateTimeField()
    timeOut = models.DateTimeField()
    checkIn = models.DateTimeField(blank=True, null=True)
    checkInQR = models.CharField(max_length=255, blank=True, null=True)
    checkOut = models.DateTimeField(blank=True, null=True)
    checkOutQR = models.CharField(max_length=255, blank=True, null=True)
    reason = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)

class Code(models.Model):
    id = models.AutoField(primary_key=True)
    qr = models.CharField(max_length=255)
    user = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)