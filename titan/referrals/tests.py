from django.contrib.sessions.models import Session
from rest_framework.test import APITestCase

from referrals.models import RegisteredUser


class NewUserJoinTestCase(APITestCase):
    def test_email_is_required_for_registration(self):
        assert RegisteredUser.objects.count() == 0
        response = self.client.post('/api/join/', {'email': 'invalid-email.com'})
        assert response.status_code == 400
        assert RegisteredUser.objects.count() == 0

    def test_user_can_join_providing_valid_email(self):
        assert RegisteredUser.objects.count() == 0
        self.client.post('/api/join/', {'email': 'valid@email.com'})
        assert RegisteredUser.objects.count() == 1

    def test_email_must_be_unique(self):
        assert RegisteredUser.objects.count() == 0
        self.client.post('/api/join/', {'email': 'valid@email.com'})
        assert RegisteredUser.objects.count() == 1
        response = self.client.post('/api/join/', {'email': 'valid@email.com'})
        assert response.status_code == 400
        assert RegisteredUser.objects.count() == 1


    def test_after_registration_user_gets_referral_code(self):
        self.client.post('/api/join/', {'email': 'valid@email.com'})
        user = RegisteredUser.objects.first()
        assert user.referral_code is not None
        assert user.referred_by is None


    def test_after_registration_user_is_logged_in(self):
        self.client.post('/api/join/', {'email': 'valid@email.com'})
        assert Session.objects.first().get_decoded().get('email') == 'valid@email.com'


    def test_registration_returns_user_data(self):
        response = self.client.post('/api/join/', {'email': 'valid@email.com'})
        data = response.data
        user = RegisteredUser.objects.first()

        assert data['referral_count'] == 0
        assert data['referral_code'] == user.referral_code
        assert data['wait_list_position'] == 1


class ReferralUserJoinTestCase(APITestCase):
    def setUp(self):
        self.user = RegisteredUser.objects.create(email='test@email.com', referral_code='TEST123')
        self.url = '/api/join/{}/'.format(self.user.referral_code)


    def test_invalid_referral_code_returns_404(self):
        response = self.client.post('/api/join/INVALID/', {'email': 'valid@email.com'})
        assert response.status_code == 404

    def test_email_is_required_for_registration(self):
        assert RegisteredUser.objects.count() == 1
        response = self.client.post(self.url, {'email': 'invalid-email.com'})
        assert response.status_code == 400
        assert RegisteredUser.objects.count() == 1

    def test_user_can_join_providing_valid_email(self):
        assert RegisteredUser.objects.count() == 1
        self.client.post(self.url, {'email': 'valid@email.com'})
        assert RegisteredUser.objects.count() == 2

    def test_email_must_be_unique(self):
        assert RegisteredUser.objects.count() == 1
        response = self.client.post(self.url, {'email': 'test@email.com'})
        assert response.status_code == 400
        assert RegisteredUser.objects.count() == 1


    def test_after_registration_user_gets_referral_code(self):
        self.client.post(self.url, {'email': 'valid@email.com'})
        user = RegisteredUser.objects.last()
        assert user.referral_code is not None

    def test_after_registration_update_referral_count(self):
        self.client.post(self.url, {'email': 'valid@email.com'})
        user = RegisteredUser.objects.last()
        assert user.referred_by == self.user
        self.user.refresh_from_db()
        assert self.user.registered_users.count() == 1


    def test_after_registration_user_is_logged_in(self):
        self.client.post(self.url, {'email': 'valid@email.com'})
        assert Session.objects.first().get_decoded().get('email') == 'valid@email.com'


    def test_registration_returns_user_data(self):
        response = self.client.post(self.url, {'email': 'valid@email.com'})
        data = response.data
        user = RegisteredUser.objects.last()

        assert data['referral_count'] == 0
        assert data['referral_code'] == user.referral_code
        assert data['wait_list_position'] == 2


class GetUserDataTestCase(APITestCase):
    def setUp(self):
        self.user = RegisteredUser.objects.create(email='test@email.com', referral_code='TEST123')
        self.url = '/api/user/{}/'.format(self.user.referral_code)

    def test_if_user_does_not_exist_return_404(self):
        response = self.client.get('/api/user/INVALID/')
        assert response.status_code == 404

    def test_user_can_view_other_users_data(self):
        data = self.client.get(self.url).data
        assert data['referral_count'] == 0
        assert data['referral_code'] == self.user.referral_code
        assert data['wait_list_position'] == 1

    def test_user_viewing_other_users_data_does_not_login(self):
        assert Session.objects.count() == 0
        self.client.get(self.url)
        assert Session.objects.count() == 0


class LoginUserDataTestCase(APITestCase):
    def setUp(self):
        self.user = RegisteredUser.objects.create(email='test@email.com', referral_code='TEST123')
        self.url = '/api/user/{}/'.format(self.user.referral_code)

    def test_if_user_does_not_exist_return_404(self):
        response = self.client.post('/api/user/INVALID/')
        assert response.status_code == 404

    def test_user_can_log_in(self):
        data = self.client.post(self.url).data
        assert data['referral_count'] == 0
        assert data['referral_code'] == self.user.referral_code
        assert data['wait_list_position'] == 1

    def test_login_sets_session(self):
        self.client.post(self.url)
        assert Session.objects.first().get_decoded().get('email') == self.user.email
