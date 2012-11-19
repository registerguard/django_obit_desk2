from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm
from django.views.generic.simple import direct_to_template
from django_obit_desk2.views import deaths, fh_index, logout_view, manage_death_notice, \
    manage_obituary, billing, print_obituary, hard_copies_manifest, billing_excel

urlpatterns = list()

'''
Dirty hack: Uncomment following three lines for maintenance mode.
'''
# urlpatterns = patterns('',
#     url(r'^.*$', direct_to_template, {'template': 'maintenance.html'})
# )

urlpatterns += patterns('',
    url(r'^deaths/(?P<death_notice_id>\d+)/$', manage_death_notice, name='manage_death_notice'),
    url(r'^deaths/$', manage_death_notice, name='add_death_notice'),
    url(r'^obituaries/(?P<obituary_id>\d+)/$', manage_obituary, name='manage_obituary'),
    url(r'^obituaries/(?P<obituary_id>\d+)/print/$', print_obituary, name='print_obituary'),
    url(r'^obituaries/$', manage_obituary, name='add_obituary'),
    url(r'^funeral-home/$', fh_index, name='death_notice_index'),
    url(r'^logout/$', logout_view, name='logout'),
    (r'^deaths/print/$', deaths, {'model': 'Death_notice'}),
    (r'^obits/print/$', deaths, {'model': 'Obituary'}),
    url(r'^password_reset/$', password_reset, name='password_reset'),
    url(r'^password_reset_done/$', password_reset_done, name='password_reset_done'),
    url(r'^password_reset/(?P<uidb36>[0-9A-Za-z]+)/(?P<token>[\d\w-]+)/$', password_reset_confirm, name='password_reset_confirm'),
    url(r'^billing/(?P<billing_month>[a-z]{3})/$', billing, name='billing'),
    url(r'^billing/$', billing, name='billing'),
    url(r'^billing/excel/$', billing, {'excel_response': True}, name='billing_excel'),
    url(r'^hard-copies/$', hard_copies_manifest, name='hard-copies'),
)