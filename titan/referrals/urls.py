from django.conf.urls import url

from referrals.views import UserViewSet

urlpatterns = [
    url(r'join/$', UserViewSet.as_view({'post': 'register_new'})),
    url(r'join/(?P<code>[\w]+)/$', UserViewSet.as_view({'post': 'register_from_referral'})),

    url(r'user/$', UserViewSet.as_view({'get': 'logged_in_details'})),
    url(r'user/(?P<code>[\w]+)/$', UserViewSet.as_view({'get': 'retrieve', 'post': 'login'})),
]
