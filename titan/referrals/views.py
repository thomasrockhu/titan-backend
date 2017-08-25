import random, string, calendar, datetime
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from referrals.models import RegisteredUser
from referrals.serializers import UserReferralSerializer, RegistrationSerializer


import csv


class ChartViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60))
    def retrieve(self, request):
        period = request.query_params.get('period', 'ALL')
        period = period.upper()
        if period in ['1Y', '3Y', '5Y', '10Y', 'YTD', 'ALL']:
            return Response(self.get_chart_from_file(period))
        else:
            raise ValidationError('Invalid period specified')

    def get_chart_from_file(self, period):
        files_map = {
            'YTD': settings.PATH_TO_CSV_CHART_YTD,
            '1Y': settings.PATH_TO_CSV_CHART_1Y,
            '3Y': settings.PATH_TO_CSV_CHART_3Y,
            '5Y': settings.PATH_TO_CSV_CHART_5Y,
            '10Y': settings.PATH_TO_CSV_CHART_10Y,
            'ALL': settings.PATH_TO_CSV_CHART_ALL,
        }

        reader = csv.reader(open(files_map[period]))
        labels = next(reader)[1:]
        titan_data = next(reader)[1:]
        sp500_data = next(reader)[1:]
        return {
            'labels': [calendar.timegm(datetime.datetime.strptime(l, '%m/%d/%Y').timetuple()) for l in labels],
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

    def retrieve_detail(self, request, *args, **kwargs):
        email = request.query_params.get('email', None)
        code = request.query_params.get('code', None)
        if email:
            user = get_object_or_404(RegisteredUser, email=email)
            return Response(UserReferralSerializer(user).data)
        if code:
            user = get_object_or_404(RegisteredUser, referral_code=code)
            return Response(UserReferralSerializer(user).data)

        raise ValidationError('Either email or code must be specified')

    def login(self, request, code, *args, **kwargs):
        user = get_object_or_404(RegisteredUser, referral_code=code)
        request.session['email'] = user.email
        return Response(UserReferralSerializer(user).data)


    @transaction.atomic
    def register_new(self, request):
        registration_data = RegistrationSerializer(data=request.data)
        registration_data.is_valid(raise_exception=True)
        user, created = RegisteredUser.objects.get_or_create(email=registration_data.validated_data['email'])
        if created:
            user.referral_code = self.generate_referral_code()
            user.save()
            self.notify_user_with_email(request.build_absolute_uri('/'), user.referral_code, user.email)
        request.session['email'] = user.email
        return Response(UserReferralSerializer(user).data)

    @transaction.atomic
    def register_from_referral(self, request, code):
        referred_by = get_object_or_404(RegisteredUser, referral_code=code)
        registration_data = RegistrationSerializer(data=request.data)
        registration_data.is_valid(raise_exception=True)
        user, created = RegisteredUser.objects.get_or_create(email=registration_data.validated_data['email'])
        if created:
            user.referred_by = referred_by
            user.referral_code = self.generate_referral_code()
            user.save()
            self.notify_user_with_email(request.build_absolute_uri('/'), user.referral_code, user.email)
            self.notify_referrer_with_email(request.build_absolute_uri('/'), user.referral_code, referred_by.email)
        request.session['email'] = user.email
        return Response(UserReferralSerializer(user).data)

    @staticmethod
    def generate_referral_code(code_length=8):
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(code_length))
        while RegisteredUser.objects.filter(referral_code=code).exists():
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(code_length))
        return code


    @staticmethod
    def notify_user_with_email(base_url, referral_code, email):
        template_html = 'email-titan-template.html'
        template_text = 'email-titan-template.txt'

        context = {'url': '{}#!/{}'.format(base_url, referral_code)}
        plain_msg = render_to_string(template_text, context)
        html_msg = render_to_string(template_html, context)
        send_mail(subject='Welcome to Titan!',
                  message=plain_msg,
                  html_message=html_msg,
                  from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=[email],
                  fail_silently=False)


    @staticmethod
    def notify_referrer_with_email(base_url, referral_code, email):
        template_html = 'email-titan-template-after-signup.html'
        template_text = 'email-titan-template-after-signup.txt'

        context = {'url': '{}#!/{}'.format(base_url, referral_code)}
        plain_msg = render_to_string(template_text, context)
        html_msg = render_to_string(template_html, context)
        send_mail(subject='Thank you!',
                  message=plain_msg,
                  html_message=html_msg,
                  from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=[email],
                  fail_silently=False)
