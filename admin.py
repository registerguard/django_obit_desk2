from django.contrib import admin
from django.contrib.auth.models import User
from django_obit_desk2.forms import ObituaryAdminForm
from django_obit_desk2.models import Death_notice, Obituary, FuneralHomeProfile, \
    Service, DeathNoticeOtherServices, ClassifiedRep

class FuneralHomeProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'city', 'state', 'phone', 'rg_rep',)
    list_editable = ('rg_rep',)
    list_filter = ('user__is_active',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "rg_rep":
            kwargs["queryset"] = ClassifiedRep.objects.filter(user__groups='2').order_by('user__username')
        return super(FuneralHomeProfileAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(FuneralHomeProfile, FuneralHomeProfileAdmin)

class ServiceInline(admin.TabularInline):
    model = Service

class DeathNoticeOtherServicesInline(admin.TabularInline):
    model = DeathNoticeOtherServices

class Death_noticeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'death_notice_in_system', 'ready_for_print', 'funeral_home', 'service_date', 'death_notice_created',)
    list_editable = ('death_notice_in_system',)
    list_filter = ('death_notice_in_system',)
    search_fields = ['last_name', 'first_name',]
    
    # To filter out everything but funeral homes in inline dropdown.
    #
    # For alternative approach to Admin inline model filtering/ordering,
    # see class ObituaryAdminForm in forms.py of this app.
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'funeral_home':
            # Group '1' is 'funeral homes'; TODO: decouple from group id ... 
            kwargs['queryset'] = User.objects.filter(groups='1').order_by('username')
        return super(Death_noticeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    inlines = [
        ServiceInline,
        DeathNoticeOtherServicesInline,
    ]
admin.site.register(Death_notice, Death_noticeAdmin)

class ObituaryAdmin(admin.ModelAdmin):
    list_display = ('death_notice', 'fh', 'user', 'ready_for_print', 'obituary_in_system', 'obituary_publish_date', 'service_date', 'admin_thumbnail', 'admin_thumbnail_two', 'obituary_created', 'status', 'date_of_birth', )
    list_editable = ('obituary_in_system', 'obituary_publish_date')
    search_fields = ['death_notice__last_name', 'death_notice__first_name',]
    date_hierarchy = 'obituary_created'
    ordering = ('-obituary_created',)
    save_on_top = True
    
    class Media:
        js = (
        'http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.min.js',
        'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.14/jquery-ui.min.js',
        'http://www3.registerguard.com/hosted/jquery/js/jquery.cookie.js',
        'http://go.registerguard.com/static/obituary2/lengthEstimator.js',
        )
        # /rgcalendar/www/static/obituary2/lengthEstimator.js
    
    form = ObituaryAdminForm
    
    exclude = ('user',)
    
    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None and not obj.obituary_created:
            obj.user = request.user
        obj.save()
    
    def fh(self, obj):
        return obj.death_notice.funeral_home.username
    fh.short_description = u'Funeral home'

admin.site.register(Obituary, ObituaryAdmin)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service', 'service_date_time',)

admin.site.register(Service, ServiceAdmin)

class ClassifiedRepAdmin(admin.ModelAdmin):
    list_display = ('user', 'rg_rep_phone', 'email', )
    list_editable = ('rg_rep_phone', 'email',)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(groups='2').order_by('username')
        return super(ClassifiedRepAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(ClassifiedRep, ClassifiedRepAdmin)
