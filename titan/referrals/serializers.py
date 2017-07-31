from django.db.models import Count
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from referrals.models import RegisteredUser


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=RegisteredUser.objects.all())])


class UserReferralSerializer(serializers.Serializer):
    referral_count = serializers.SerializerMethodField()
    referral_code = serializers.CharField()
    wait_list_position = serializers.SerializerMethodField()

    def get_referral_count(self, instance):
        return RegisteredUser.objects.filter(referred_by=instance).count()

    def get_wait_list_position(self, instance):
        referral_count = RegisteredUser.objects.filter(referred_by=instance).count()
        return RegisteredUser.objects.annotate(referral_count=Count('registered_users')).filter(referral_count__gt=referral_count).count() + 1
