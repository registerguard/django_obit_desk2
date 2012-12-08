# -*- coding: utf-8 -*-

from django.core.mail import send_mail, send_mass_mail, EmailMessage
from django.db import models
from django.contrib.humanize.templatetags.humanize import apnumber
from django.contrib.auth.models import User
from django.template.defaultfilters import date
from sorl.thumbnail import get_thumbnail, ImageField
from cuddlybuddly.thumbnail.main import Thumbnail
from os import path
import datetime
from dateutil.parser import parse

from obituary_settings import DN_OBIT_EMAIL_RECIPIENTS, BO_OBIT_EMAIL_RECIPIENTS, \
    IMAGING_OBIT_EMAIL_RECIPIENTS, DISPLAY_DAYS_BACK

# Create your models here.

STATUS = (
    ('live','Submitted to R-G',),
    ('drft','Draft',),
)

class baseOtherServices(models.Model):
    '''
    Abstract base class for both Death Notice and Obituary.
    '''
    description = models.CharField(u'Description of other service', max_length=256)
    other_services_date_time = models.DateTimeField(blank=True, null=True)
    other_services_end_date_time = models.DateTimeField(blank=True, null=True, help_text=u'(Optional.)')
    other_services_location = models.CharField(max_length=126)
    
    class Meta:
        abstract = True
        verbose_name = 'Other services'
        verbose_name_plural = 'Other services'
        managed = True
    
    def __unicode__(self):
        return self.description

class FuneralHomeProfile(models.Model):
    STATES = (
        ('Alaska', 'Alaska',),
        ('Ariz.', 'Ariz.',),
        ('Calif.', 'Calif.',),
        ('Colo.', 'Colo.',),
        ('Conn.', 'Conn.',),
        ('Del.', 'Del.',),
        ('Fla.', 'Fla.',),
        ('Ga.', 'Ga.',),
        ('Hawaii', 'Hawaii',),
        ('Idaho', 'Idaho',),
        ('Ill.', 'Ill.',),
        ('Ind.', 'Ind.',),
        ('Iowa', 'Iowa',),
        ('Kan.', 'Kan.',),
        ('Ky.', 'Ky.',),
        ('La.', 'La. ',),
        ('Mass.', 'Mass.',),
        ('Md.', 'Md.',),
        ('Mich.', 'Mich.',),
        ('Minn.', 'Minn.',),
        ('Miss.', 'Miss.',),
        ('Mo.', 'Mo.',),
        ('Mont.', 'Mont.',),
        ('Neb.', 'Neb.',),
        ('Nev.', 'Nev.',),
        ('N.C.', 'N.C.',),
        ('N.D.', 'N.D.',),
        ('N.H.', 'N.H.',),
        ('N.M.', 'N.M.',),
        ('N.J.', 'N.J.',),
        ('N.Y.', 'N.Y.',),
        ('Ohio', 'Ohio',),
        ('Okla.', 'Okla.',),
        ('Pa.', 'Pa.',),
        ('R.I.', 'R.I.',),
        ('S.C.', 'S.C.',),
        ('S.D.', 'S.D.',),
        ('Texas', 'Texas',),
        ('Tenn.', 'Tenn.',),
        ('Utah', 'Utah',),
        ('Va.', 'Va.',),
        ('Vt.', 'Vt.',),
        ('Wash.', 'Wash.',),
        ('W.Va.', 'W.Va.',),
        ('Wis.', 'Wis.',),
        ('Wyo.', 'Wyo.',),
    )
    user = models.OneToOneField(User, related_name='fh_user2')
    full_name = models.CharField(max_length=80)
    address = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=80, blank=True, help_text=u'Leave blank when city name is part of funeral home name, i.e., \'Oakridge Funeral Home Chapel of the Woods\'')
    state = models.CharField(max_length=6, choices=STATES, blank=True, help_text=u'Leave blank if located in Oregon')
    zip_code = models.CharField(max_length=32, blank=True)
    phone = models.CharField(max_length=14, blank=True)
    rg_rep = models.ForeignKey(User, related_name='rg_rep', blank=True, null=True)
    
    class Meta:
        ordering = ('full_name',)
    
    def __unicode__(self):
        if self.city:
            return '%s in %s' % (self.full_name, self.city)
        else:
            return '%s' % self.full_name

class Death_notice(models.Model):
    AGE_UNIT_CHOICES = (
        (1, 'years',),
        (2, 'months',),
        (3, 'days',),
        (4, 'hours',),
    )
    funeral_home = models.ForeignKey(User, related_name='dn_user2')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(u'Middle name or initial', max_length=95, blank=True)
    nickname = models.CharField(max_length=90, blank=True, help_text='Just enter name, without double-quotes, i.e. Jack, not "Jack"')
    last_name = models.CharField(max_length=105)
    age = models.IntegerField()
    age_unit = models.IntegerField(default=1, choices=AGE_UNIT_CHOICES)
    city_of_residence = models.CharField(max_length=110)
    formerly_of = models.CharField(max_length=126, blank=True)
    death_date = models.DateField()
    no_service_planned = models.BooleanField(u'No service planned?', blank=True, help_text=u'Check if NO SERVICE IS PLANNED.')
    remembrances = models.CharField(u'Remembrances to ... ', max_length=255, blank=True, help_text=u'(This item typically used when there won\'t be an obituary, but the deceased has selected an organization.)')
    death_notice_in_system = models.BooleanField()
    death_notice_has_run = models.BooleanField()
    death_notice_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=4, choices=STATUS, default='drft', help_text=u'Only items with a status of \'Submitted to R-G\' will be picked up for publication in the newspaper. (If the Death Notice is a work-in-progress, use the default \'Draft\' status.)</p><p><span style="color: black; font-weight: bold;">NOTE:</span> If you make a change <i style="font-weight: bold;">after</i> a Death Notice has been submitted, you <i style="font-weight: bold;">MUST</i> contact The Register-Guard newsroom.</p>')
    
    class Meta:
        verbose_name = 'Death notice'
        unique_together = ('first_name', 'last_name', 'age', 'death_date',)
        ordering = ('-death_notice_created',)
    
    def __unicode__(self):
        return u'%s %s %s' % (self.first_name, self.middle_name, self.last_name)
    
    def save(self):
        from_email = 'rgnews.registerguard.@gmail.com'
        to_email = DN_OBIT_EMAIL_RECIPIENTS
        message_email = 'Go to the death notice admin page for further information.'
        datatuple = None
        
        if(self.pk and self.status == 'live'):
#             datatuple = None
            datatuple = (
                ('Change made to *PREVIOUSLY-SUBMITTED* Death Notice by %s to %s %s death notice' % (self.funeral_home.funeralhomeprofile.full_name, self.first_name, self.last_name), message_email, from_email, to_email),
            )
        elif not self.pk:
            # a new Death_notice
            message_subj = 'Death notice created by %s for %s %s' % (self.funeral_home.funeralhomeprofile.full_name, self.first_name, self.last_name)
            datatuple = (message_subj, message_email, from_email, to_email,), # <- This trailing comma's vital!
        
        if datatuple:
            send_mass_mail(datatuple)
        super(Death_notice, self).save()
    
    def last_name_no_suffix(self):
        suffixes = (' jr', ' sr', ' ii', ' iii')
        shortened_name = self.last_name
        for suffix in suffixes:
            if self.last_name.lower().count(suffix):
                offset = self.last_name.lower().find(suffix)
                shortened_name = self.last_name[:offset]
                break
        return shortened_name
    
    def ready_for_print(self):
        if self.status == 'live':
            return True
        else:
            return False
    ready_for_print.boolean = True
    ready_for_print.short_description = 'Print ready'
    
    def service_date(self):
        try:
            self.service
            if self.service.service_date_time:
                return u'%s' % date(self.service.service_date_time, "P l, N j")
        except Service.DoesNotExist:
            return u'No service scheduled.'
    
    def age_unit_combo(self):
        if not self.age_unit == 1: # 1 = 'years'
            return u'%s %s' % (self.age, self.get_age_unit_display())
        else:
            return u'%s' % (self.age)

class Service(models.Model):
    SERVICES = (
        ('A celebration of life', 'celebration of life',),
        ('The funeral', 'funeral',),
        ('The funeral Mass', 'funeral Mass',),
        ('The funeral service followed by the burial', 'funeral service followed by the burial',),
        ('A graveside service', 'graveside service',),
        ('A musical celebration of life', 'musical celebration of life',),
        ('A memorial service', 'memorial service',),
        ('A memorial service and reception', 'memorial service and reception',),
        ('A memorial service is planned', 'memorial service is planned',),
        ('A military graveside funeral', 'military graveside funeral',),
        ('A private service', 'private service',),
        ('A service followed by the burial', 'service followed by the burial',),
        ('A visitation', 'visitation',),
        ('A visitation followed by a funeral', 'visitation followed by the funeral',),
    )
    
    death_notice = models.OneToOneField(Death_notice, blank=True, null=True)
    service = models.CharField(choices=SERVICES, max_length=65)
    service_date_time = models.DateTimeField(blank=True, null=True)
    service_end_date_time = models.DateTimeField(blank=True, null=True, help_text=u'(Optional.)')
    service_location = models.CharField(max_length=75, blank=True)
    service_city = models.CharField(max_length=80, blank=True)
    
    class Meta:
        ordering = ('-service_date_time',)
    
    def __unicode__(self):
        return self.service
    
    def full_description(self):
        if self.service_extra_info:
            return u'%s %s' % (self.service, self.service_extra_info)
        else:
            return u'%s' % (self.service)

class DeathNoticeOtherServices(baseOtherServices):
    death_notice = models.OneToOneField(Death_notice)

'''
11/28/12:
Dropped these fields:
place_of_birth
gender
cause_of_death
no_service_planned
service_plans_indefinite
'''
class Obituary(models.Model):
    COPIES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
    )
    
    COST = {
        'FH':    '$25',
        'STAFF': '$50',
    }
    
    def obit_file_name(instance, filename):
        (orig_name, orig_ext) = path.splitext(filename)
#         return 'obit_images/ob.%s.%s%s' % (instance.death_notice.last_name.lower(), instance.death_notice.first_name.lower(), orig_ext)
        return 'obits/%s/%s/ob.%s.%s%s' % (datetime.date.today().year, datetime.date.today().month, instance.death_notice.last_name.lower(), instance.death_notice.first_name.lower(), orig_ext)
    
    user = models.ForeignKey(User, null=True, blank=True, related_name='obit_user2')
    death_notice = models.OneToOneField(Death_notice, primary_key=True, limit_choices_to ={'death_notice_created__gte': datetime.datetime.now() - datetime.timedelta(days=DISPLAY_DAYS_BACK) })
    prepaid_by = models.CharField(max_length=325, blank=True)
    date_of_birth = models.DateField(blank=True, null=True, help_text=u'YYYY-MM-DD format')
    family_contact = models.CharField(max_length=126)
    family_contact_phone = models.CharField(max_length=12)
    obituary_body = models.TextField(help_text=u'Information you may want to include: education, military,  career/work experience,  hobbies, volunteerism, awards, clubs, marriage and divorce, survivors, predeceased by, cause of death, date of birth, service information, remembrances.')
    mailing_address = models.TextField(blank=True, help_text=u'Please include a mailing address in the space above if you would like to receive up to 10 copies of this obituary.')
    number_of_copies = models.IntegerField(choices=COPIES, blank=True, null=True, help_text=u'Number of copies you would like.', default=10)
    photo = ImageField(upload_to=obit_file_name, blank=True)
    photo_two = ImageField(upload_to=obit_file_name, blank=True)
    # Survivors
    status = models.CharField(max_length=4, choices=STATUS, default='drft', help_text=u'Only items with a status of \'Submitted to R-G\' will be picked up for publication in the newspaper. (If the Obituary is a work-in-progress, use the default \'Draft\' status.)</p><p><span style="color: black; font-weight: bold;">NOTE:</span> If you make a change <i style="font-weight: bold;">after</i> an Obituary has been submitted, you <i style="font-weight: bold;">MUST</i> contact your Register-Guard classified representative.</p>')
    
    obituary_in_system = models.BooleanField(u'Obit in DT?')
#     obituary_has_run = models.BooleanField(u'Obit has run?')
    obituary_publish_date = models.DateField(blank=True, null=True, help_text=u"The date to be published, subject to print deadlines. If left empty, the next available date will be used.")
    obituary_created = models.DateTimeField(auto_now_add=True)
    
    flag = models.BooleanField(blank=True)
    service_insignia = models.CharField(max_length=300, blank=True, help_text=u"Enter the relevant branch or branches of service.")
    
    class Meta:
        verbose_name = 'Obituary'
        verbose_name_plural = 'obituaries'
        ordering = ('-obituary_created',)
    
    def __unicode__(self):
        return u'Obituary for %s %s' % (self.death_notice.first_name, self.death_notice.last_name)
    
    def save(self):
        from_email = 'rgnews.registerguard.@gmail.com'
        to_email = DN_OBIT_EMAIL_RECIPIENTS
        message_email = 'Go to the obituary admin page for further information.'
        datatuple = ()
        
        '''
        Change/new e-mails for changed, saved obituaries
        '''
        if not self.obituary_created:
            # a new Obituary
            message_subj = 'Obituary created for %s %s' % (self.death_notice.first_name, self.death_notice.last_name)
            datatuple = (message_subj,  message_email, from_email, to_email,), # <- This trailing comma's vital!
        '''
        Check for photo with an about-to-be-created Obituary.
        '''
        if self.photo and not self.obituary_created:
            to_email = IMAGING_OBIT_EMAIL_RECIPIENTS
            message_subj = 'Photo has been attached to %s %s obituary' % (self.death_notice.first_name, self.death_notice.last_name)
            message_email = 'Photo file %s is attached.' % path.split(self.photo.name)[1]
            imaging_email = EmailMessage()
            imaging_email.subject = message_subj
            imaging_email.body = message_email
            imaging_email.to = to_email
            imaging_email.attach(path.split(self.photo.name)[1], self.photo.read(), 'image/jpg')
            imaging_email.send(fail_silently=False)
        
        '''
        Check if obituary has 'publish_date'
        '''
        if self.obituary_created and self.obituary_publish_date:
            to_email = BO_OBIT_EMAIL_RECIPIENTS
            # Compare what's in database vs. what's on current Web form.
            copy_existing = Obituary.objects.get(pk=self.pk)
            if not copy_existing.obituary_publish_date and self.obituary_publish_date:
                if self.prepaid_by:
                    cost = self.COST['STAFF']
                else:
                    cost = self.COST['FH']
                
                if self.user and (self.user.username in ('lcrossley', 'weeditor',)):
                    message_subj = '[Accounting] Obituary printed for %s %s' % (self.death_notice.first_name, self.death_notice.last_name)
                    message_email = 'Add %s to the invoice of %s.' % (cost, self.death_notice.funeral_home.funeralhomeprofile.full_name)
                elif self.user and (self.user.username in ('wcarole', 'bholmes', 'bnelson', 'jhamilton', 'nkeller', 'phowells',)):
                    message_subj = '[Accounting] PRE-PAID obituary printed for %s %s' % (self.death_notice.first_name, self.death_notice.last_name)
                    message_email = '%s for the %s obituary was prepaid: %s.' % (cost, self.death_notice.funeral_home.funeralhomeprofile.full_name, self.prepaid_by)
                else:
                    message_subj = '[Accounting] Obituary printed for %s %s' % (self.death_notice.first_name, self.death_notice.last_name)
                    message_email = 'Add %s to the invoice of %s. (You can also check http://www.registerguard.com/web/news/obituaries/)' % (cost, self.death_notice.funeral_home.funeralhomeprofile.full_name)
                datatuple = (message_subj,  message_email, from_email, to_email,), # <- This trailing comma's vital!
        
        '''
        Check for attachment of photo to an existing Obituary.
        '''
          # I think maybe we don't care if it's live, if a photo's been attached?
#         if self.obituary_created and self.photo and self.status == 'live':
        if self.obituary_created and self.photo:
            to_email = IMAGING_OBIT_EMAIL_RECIPIENTS
            copy_existing = Obituary.objects.get(pk=self.pk)
            if not copy_existing.photo and self.photo:
                '''
                TODO: Factor this e-mailer out; rename image to that of decedent; take out mime-type;
                '''
                message_subj = 'Photo has been attached to %s %s obituary' % (self.death_notice.first_name, self.death_notice.last_name)
                message_email = 'Photo file %s is attached.' % path.split(self.photo.name)[1]
                imaging_email = EmailMessage()
                imaging_email.subject = message_subj
                imaging_email.body = message_email
                imaging_email.to = to_email
                imaging_email.attach(path.split(self.photo.name)[1], self.photo.read(), 'image/jpg')
                imaging_email.send(fail_silently=False)
        
        if datatuple:
            send_mass_mail(datatuple)
        super(Obituary, self).save()
    
    def admin_thumbnail(self):
        if self.photo:
            cbim = Thumbnail(self.photo.name, 180, 180)
            return u'<a href="%s" target="_blank"><img src="%s%s"></a>' % (self.photo.url, self.photo.storage.base_url, cbim)
        else:
            return u'(No photo)'
    admin_thumbnail.short_description = u'Thumbnail'
    admin_thumbnail.allow_tags = True
    
    ##
    ## MODEL ATTRIBUTES FOR THE OBITUARY ADMIN
    ##
    def display_photo_file_name(self):
        if self.photo:
            return self.photo.name
        else:
            return u'(No photo)'
    display_photo_file_name.short_description = u'File path'
    
    def service_date(self):
        try:
            self.death_notice.service
            if self.death_notice.service.service_date_time:
                return u'%s' % date(self.death_notice.service.service_date_time, "P l, N j,")
        except Service.DoesNotExist:
            return u'No service scheduled.'
    
    def ready_for_print(self):
        if self.status == 'live':
            return True
        else:
            return False
    ready_for_print.boolean = True
    ready_for_print.short_description = 'Print ready'
