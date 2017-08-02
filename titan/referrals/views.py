import random, string, calendar, datetime
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from referrals.models import RegisteredUser
from referrals.serializers import UserReferralSerializer, RegistrationSerializer


import csv

class ChartViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60))
    def retrieve(self, request):
        return Response(self.get_chart_from_file())

    def get_chart_from_file(self):
        reader = csv.reader(open(settings.PATH_TO_CSV_CHART))
        labels = next(reader)[1:]
        titan_data = next(reader)[1:]
        sp500_data = next(reader)[1:]
        return {
            'labels': [calendar.timegm(datetime.datetime.strptime(l, '%m/%d/%y').timetuple()) for l in labels],
            'titan': list(map(float, titan_data)),
            'sp500': list(map(float, sp500_data)),
        }

class StatsViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60))
    def retrieve(self, request):
        return Response(self.get_stats_from_file())

    def get_stats_from_file(self):
        reader = csv.reader(open(settings.PATH_TO_CSV_STATS))
        labels = next(reader)[1:]
        titan_data = next(reader)[1:]
        sp500_data = next(reader)[1:]
        return [{
                'label': labels[i],
                'titan': float(titan_data[i]),
                'sp500': float(sp500_data[i]),
            } for i in range(len(labels))]


class UserViewSet(viewsets.ViewSet):
    queryset = RegisteredUser.objects.all()
    serializer_class = UserReferralSerializer

    def logged_in_details(self, request, *args, **kwargs):
        email = request.session.get('email')
        if email:
            user = get_object_or_404(RegisteredUser, email=email)
            return Response(UserReferralSerializer(user).data)
        raise PermissionDenied

    def retrieve(self, request, code, *args, **kwargs):
        user = get_object_or_404(RegisteredUser, referral_code=code)
        return Response(UserReferralSerializer(user).data)

    def login(self, request, code, *args, **kwargs):
        user = get_object_or_404(RegisteredUser, referral_code=code)
        request.session['email'] = user.email
        return Response(UserReferralSerializer(user).data)

    def register_new(self, request):
        registration_data = RegistrationSerializer(data=request.data)
        registration_data.is_valid(raise_exception=True)
        user, created = RegisteredUser.objects.get_or_create(email=registration_data.validated_data['email'])
        if created:
            user.referral_code = self.generate_referral_code()
            user.save()
            # self.notify_with_email(user)
        request.session['email'] = user.email
        return Response(UserReferralSerializer(user).data)

    def register_from_referral(self, request, code):
        referred_by = get_object_or_404(RegisteredUser, referral_code=code)
        registration_data = RegistrationSerializer(data=request.data)
        registration_data.is_valid(raise_exception=True)
        user, created = RegisteredUser.objects.get_or_create(email=registration_data.validated_data['email'])
        if created:
            user.referred_by = referred_by
            user.referral_code = self.generate_referral_code()
            user.save()
            # self.notify_with_email(user)
        request.session['email'] = user.email
        return Response(UserReferralSerializer(user).data)


    def notify_with_email(self, user):
        send_mail(
            'Welocme to TITAN!',
            "Here's your referal link",
            'noreply@titan.com',
            [user.email],
            fail_silently=True,
        )

    def generate_referral_code(self, code_length=8):
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(code_length))
        while RegisteredUser.objects.filter(referral_code=code).exists():
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(code_length))
        return code
