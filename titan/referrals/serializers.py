from django.db.models import Count
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from referrals.models import RegisteredUser


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=RegisteredUser.objects.all())])


class UserReferralSerializer(serializers.Serializer):
    email = serializers.EmailField()
    referral_count = serializers.SerializerMethodField()
    referral_code = serializers.CharField()
    wait_list_position = serializers.SerializerMethodField()
    total_registered = serializers.SerializerMethodField()

    def get_referral_count(self, instance):
        return RegisteredUser.objects.filter(referred_by=instance).count()

    def get_total_registered(self, instance):
        return RegisteredUser.objects.all().count()

    def get_wait_list_position(self, instance):
        return RegisteredUser.objects.filter(registration_datetime__lt=instance.registration_datetime).count() + 1
