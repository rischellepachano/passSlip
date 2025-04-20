from django.contrib import admin
from .models import User, Slip, Code, Admin

admin.site.register(User)
admin.site.register(Slip)
admin.site.register(Code)
admin.site.register(Admin)

