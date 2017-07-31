from django.db import models

class RegisteredUser(models.Model):
    registration_datetime = models.DateTimeField(auto_now=True)

    email = models.EmailField(unique=True)
    referred_by = models.ForeignKey("RegisteredUser", null=True, default=None, related_name='registered_users')
    referral_code = models.CharField(max_length=8, null=True, default=None)

