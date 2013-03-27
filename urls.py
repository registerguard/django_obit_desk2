from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm
from django.views.generic import TemplateView
from django_obit_desk2.views import deaths2, fh_index2, logout_view2, \
    manage_death_notice2, manage_obituary2, billing2, print_obituary2, \
    hard_copies_manifest2, billing_excel2, death_notice_count

urlpatterns = list()

'''
Dirty hack: Uncomment following three lines for maintenance mode.
'''
# urlpatterns = patterns('',
#     url(r'^.*$', TemplateView.as_view(template_name="maintenance.html"), name='maintenance'),
# )

urlpatterns += patterns('',
    url(r'^deaths/(?P<death_notice_id>\d+)/$', manage_death_notice2, name='manage_death_notice2'),
    url(r'^deaths/$', manage_death_notice2, name='add_death_notice2'),
    url(r'^obituaries/(?P<obituary_id>\d+)/$', manage_obituary2, name='manage_obituary2'),
    url(r'^obituaries/(?P<obituary_id>\d+)/print/$', print_obituary2, name='print_obituary2'),
    url(r'^obituaries/$', manage_obituary2, name='add_obituary2'),
    url(r'^funeral-home/$', fh_index2, name='death_notice_index2'),
    url(r'^logout/$', logout_view2, name='logout2'),
    (r'^deaths/print/$', deaths2, {'model': 'Death_notice'}),
    (r'^obits/print/$', deaths2, {'model': 'Obituary'}),
    url(r'^password_reset/$', password_reset, name='password_reset2'),
    url(r'^password_reset_done/$', password_reset_done, name='password_reset_done2'),
    url(r'^password_reset/(?P<uidb36>[0-9A-Za-z]+)/(?P<token>[\d\w-]+)/$', password_reset_confirm, name='password_reset_confirm2'),
    url(r'^billing/(?P<billing_month>[a-z]{3})/$', billing2, name='billing2'),
    url(r'^billing/$', billing2, name='billing2'),
    url(r'^billing/excel/$', billing2, {'excel_response': True}, name='billing_excel2'),
    url(r'^hard-copies/$', hard_copies_manifest2, name='hard-copies2'),
    url(r'^death-notices/$', death_notice_count, name='death-notice-count'),
)