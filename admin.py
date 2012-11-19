from django.contrib import admin
from django.contrib.auth.models import User
from obituary.forms import ObituaryAdminForm
from obituary.models import Death_notice, Obituary, FuneralHomeProfile, \
    Service, DeathNoticeOtherServices

class FuneralHomeProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'city', 'state', 'phone',)
    list_filter = ('user__is_active',)

admin.site.register(FuneralHomeProfile, FuneralHomeProfileAdmin)

class ServiceInline(admin.TabularInline):
    model = Service

class DeathNoticeOtherServicesInline(admin.TabularInline):
    model = DeathNoticeOtherServices

class Death_noticeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'funeral_home', 'ready_for_print', 'service_date', 'death_notice_created', 'death_notice_in_system', 'death_notice_has_run',)
    list_editable = ('death_notice_in_system', 'death_notice_has_run',)
    list_filter = ('death_notice_in_system', 'death_notice_has_run',)
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
    list_display = ('death_notice', 'fh', 'user', 'ready_for_print', 'obituary_in_system', 'obituary_publish_date', 'service_date', 'admin_thumbnail', 'obituary_created', 'status', 'date_of_birth', )
    list_editable = ('obituary_in_system', 'obituary_publish_date')
    search_fields = ['death_notice__last_name', 'death_notice__first_name',]
    date_hierarchy = 'obituary_created'
    ordering = ('-obituary_created',)
    save_on_top = True
    
    form = ObituaryAdminForm
    
    exclude = ('user',)
    
    # An artifact of unimplemented http://djangosnippets.org/snippets/2261/
#     death_notice_fk_filter_related_only=True
#     death_notice_fk_filter_name_field='city_of_residence'
    
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
