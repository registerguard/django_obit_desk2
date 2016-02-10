import datetime
from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django_obit_desk2.widgets import SelectWithPopUp2
from django_obit_desk2.models import Death_notice, Service, Obituary, \
    DeathNoticeOtherServices
from django_obit_desk2.obituary_settings import DISPLAY_DAYS_BACK, INSIDE_OBIT_USERNAMES

class ObitsCalendarDateTimeWidget(forms.DateTimeInput):
    class Media:
        css = {'screen':('http://ajax.googleapis.com/ajax/libs/jqueryui/1/themes/overcast/jquery-ui.css',)}
        js = (
            'http://static.registerguard.com/timepicker/jquery.timepicker.addon.js',
        )

class ServiceForm(ModelForm):
    
    class Meta:
        model = Service
        widgets = {
            'service_date_time': ObitsCalendarDateTimeWidget(),
        }

ServiceFormSet = inlineformset_factory(Death_notice,
    Service,
    form = ServiceForm,
    can_delete=True,
    extra=1,)

class CalendarWidget(forms.DateInput):
    class Media:
        css = {'screen':('http://ajax.googleapis.com/ajax/libs/jqueryui/1/themes/overcast/jquery-ui.css',)}
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1/jquery-ui.min.js',
        )

class DeathNoticeOtherServicesForm(ModelForm):
    
    class Meta:
        model = DeathNoticeOtherServices
        widgets = {
             'other_services_date_time' : ObitsCalendarDateTimeWidget(),
        }

DeathNoticeOtherServicesFormSet = inlineformset_factory(Death_notice,
    DeathNoticeOtherServices,
    form = DeathNoticeOtherServicesForm,
    can_delete = True,
    extra =1,)

class Death_noticeForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    
    death_date = forms.DateField(widget=CalendarWidget())
    
    class Meta:
        model = Death_notice
        exclude = ('funeral_home', 'remembrances', 'death_notice_in_system')

class ObituaryForm(ModelForm):
    def __init__(self, request, *args, **kwargs):
        days_ago = datetime.timedelta(days=DISPLAY_DAYS_BACK)
        
        super(ObituaryForm, self).__init__(*args, **kwargs)
        if request.user.username in INSIDE_OBIT_USERNAMES:
            self.fields['death_notice'].queryset = Death_notice.objects.filter(death_notice_created__gte=( datetime.datetime.now() - days_ago )).order_by('last_name',)
        else:
            self.fields['death_notice'].queryset = Death_notice.objects.filter(death_notice_created__gte=( datetime.datetime.now() - days_ago ),funeral_home=request.user).order_by('last_name',)
    
    error_css_class = 'error'
    required_css_class = 'required'
    
    death_notice = forms.ModelChoiceField(Death_notice.objects, widget = SelectWithPopUp2)
    date_of_birth = forms.DateField(widget=CalendarWidget(), required=False)
    
    class Meta:
        model = Obituary
        exclude = ('funeral_home', 'prepaid_by', 'obituary_in_system', 'obituary_has_run', )
    
    def clean(self):
        DEADLINE_LOOKUP = (
            (0, 82),  # Monday   ->  82 hours (2 p.m. previous Thursday)
            (1, 82),  # Tuesday   -> 82 hours (2 p.m. previous Friday)
            (2, 106), # Wednesday -> 106 hours (2 p.m. previous Friday)
            (3, 58),  # Thursday  -> 58 hours (2 p.m. previous Monday)
            (4, 58),  # Friday    -> 58 hours (2 p.m. previous Tuesday)
            (5, 82),  # Saturday  -> 82 hours (2 p.m. previous Tuesday)
            (6, 82),  # Sunday    -> 82 hours (2 p.m. previous Wednesday)
        )
        
        cleaned_data = self.cleaned_data
        desired_pub_date = cleaned_data.get("obituary_publish_date")
        if desired_pub_date:
            desired_pub_date = datetime.datetime.combine(desired_pub_date, datetime.time(0, 0))
            submission_deadline = desired_pub_date - datetime.timedelta(hours=DEADLINE_LOOKUP[desired_pub_date.weekday()][1])
            # Convert date into datetime so we can compare it to datetime.datetime.now()
            if submission_deadline < datetime.datetime.now():
            
                right_now = datetime.datetime.now()
                
                # BEFORE 2 p.m. on a MONDAY
                if right_now.hour <= 14 and right_now.weekday() == 0:
                    next_pub_date = right_now.date() + datetime.timedelta(days=3)
                # AFTER 2 p.m. on a MONDAY
                elif right_now.hour > 14 and right_now.weekday() == 0:
                    next_pub_date = right_now.date() + datetime.timedelta(days=4)
                # BEFORE 2 p.m. on TUESDAY
                elif right_now.hour <=14 and right_now.weekday() == 1:
                    next_pub_date = right_now.date() + datetime.timedelta(days=3)
                # AFTER 2 p.m. on TUESDAY
                elif right_now.hour > 14 and right_now.weekday() == 1:
                    next_pub_date = right_now.date() + datetime.timedelta(days=5)
                # BEFORE 2 p.m. on WEDNESDAY
                elif right_now.hour <=14 and right_now.weekday() == 2:
                    next_pub_date = right_now.date() + datetime.timedelta(days=4)
                # AFTER 2 p.m. on WEDNESDAY
                elif right_now.hour > 14 and right_now.weekday() == 2:
                    next_pub_date = right_now.date() + datetime.timedelta(days=5)
                # BEFORE 2 p.m. on THURSDAY
                elif right_now.hour <=14 and right_now.weekday() == 3:
                    next_pub_date = right_now.date() + datetime.timedelta(days=4)
                # AFTER 2 p.m. on THURSDAY
                elif right_now.hour > 14 and right_now.weekday() == 3:
                    next_pub_date = right_now.date() + datetime.timedelta(days=5)
                # BEFORE 2 p.m. on FRIDAY
                elif right_now.hour <=14 and right_now.weekday() == 4:
                    next_pub_date = right_now.date() + datetime.timedelta(days=4)
                # AFTER 2 p.m. on FRIDAY
                elif right_now.hour > 14 and right_now.weekday() == 4:
                    next_pub_date = right_now.date() + datetime.timedelta(days=6)
                # It's SATURDAY
                elif  right_now.weekday() == 5:
                    next_pub_date = right_now.date() + datetime.timedelta(days=5)
                # It's SUNDAY
                elif  right_now.weekday() == 6:
                    next_pub_date = right_now.date() + datetime.timedelta(days=4)
                    
                raise forms.ValidationError("The deadline for your requested publication date was %s.  If submit now, the soonest available publication date is %s." % (submission_deadline.strftime('%I:%M %p, %A, %B %d, %Y'), next_pub_date.strftime('%A, %B %d, %Y')) )
        return cleaned_data

class ObituaryAdminForm(forms.ModelForm):
    # See http://stackoverflow.com/questions/1474135/django-admin-ordering-of-foreignkey-and-manytomanyfield-relations-referencing-u
    #
    # For an alternative method for drop-down filtering/ordering of Admin
    # inline fields, see formfield_for_foreignkey override in
    # class Death_noticeAdmin in admin.py of this app.
    death_notice = forms.ModelChoiceField(queryset=Death_notice.objects.order_by('last_name'))
    
    class Meta:
        model = Obituary
    
    def clean(self):
        cleaned_data = self.cleaned_data
        prepaid_by = cleaned_data.get("prepaid_by")
        if not prepaid_by:
            raise forms.ValidationError("You need to enter a name in the 'Prepaid by' field.")
        return cleaned_data
