import datetime
from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from obituary.widgets import SelectWithPopUp
from obituary.models import Death_notice, Service, Obituary, \
    Other_services, DeathNoticeOtherServices
from obituary_settings import DISPLAY_DAYS_BACK

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
        exclude = ('funeral_home', 'death_notice_in_system', 'death_notice_has_run',)

class ObituaryForm(ModelForm):
    def __init__(self, request, *args, **kwargs):
        days_ago = datetime.timedelta(days=DISPLAY_DAYS_BACK)
        
        super(ObituaryForm, self).__init__(*args, **kwargs)
        self.fields['death_notice'].queryset = Death_notice.objects.filter(death_notice_created__gte=( datetime.datetime.now() - days_ago ),funeral_home=request.user).order_by('last_name',)
    
    error_css_class = 'error'
    required_css_class = 'required'
    
    death_notice = forms.ModelChoiceField(Death_notice.objects, widget = SelectWithPopUp)
    date_of_birth = forms.DateField(widget=CalendarWidget())
    
    class Meta:
        model = Obituary
        exclude = ('funeral_home', 'prepaid_by', 'obituary_in_system', 'obituary_has_run', 'obituary_publish_date',)

class Other_servicesForm(ModelForm):
    
    class Meta:
        model = Other_services
        widgets = {
            'other_services_date_time': ObitsCalendarDateTimeWidget(),
        }

Other_servicesFormSet = inlineformset_factory(Obituary,
    Other_services,
    form = Other_servicesForm,
    can_delete=True,
    extra=1,)

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
