import codecs, datetime
from dateutil import relativedelta
from django import forms
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models.loading import get_models, get_app, get_apps
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.utils.html import escape
from django.utils.translation import ugettext
from django.views.generic.list_detail import object_list
from django_obit_desk2.models import Death_notice, Obituary
from django_obit_desk2.forms import Death_noticeForm, ServiceFormSet, \
    ObituaryForm, DeathNoticeOtherServicesFormSet
from django_obit_desk2.utils import output_cleanup_hack, adobe_to_web

from obituary_settings import DISPLAY_DAYS_BACK

# Create your views here.

def deaths2(request, model=None, file=None):
    # Set the right template
    if request.META['HTTP_USER_AGENT'].count('Macintosh') and model == 'Death_notice':
        template_name = 'death_list_unix_line_endings2.html'
    elif request.META['HTTP_USER_AGENT'].count('Macintosh') and model == 'Obituary':
        template_name = 'obituary_list_unix_line_endings2.html'
    elif model == 'Death_notice':
        template_name = 'death_list_windows_line_endings2.html'
    else:
        template_name = 'obituary_list_windows_line_endings2.html'
        
    model = eval(model)
    if model == Death_notice:
        queryset = model.objects.filter(death_notice_in_system=False, status='live').order_by('last_name')
        '''
        Possible change: Allow for Death Notice while Obituary gets to Live status
        queryset = model.objects.filter(death_notice_in_system=False, status='live', obituary__status='drft').order_by('last_name')
        '''
    else:
        queryset = model.objects.filter(obituary_in_system=False, status='live').order_by('death_notice__last_name')
    
    t = loader.get_template(template_name)
    c = RequestContext(request, {'object_list': queryset })
    data = t.render(c).replace('  ', ' ')
    data = data.replace('..', '.')
    data = data.replace('; ; ', '; ')
    data = data.replace('> ', '>')
    r = HttpResponse(data, mimetype='text/plain;charset=utf-8')
    r['Content-Disposition'] = 'attachment; filename=%s-[%s].txt;' % (model._meta.verbose_name_plural.lower().replace(' ', '-'), datetime.datetime.now().strftime('%Y-%m-%d-%I-%M-%S-%p'))
    return r

@login_required
def fh_index2(request):
    
    days_ago = datetime.timedelta(days=DISPLAY_DAYS_BACK)
    
    death_notices = Death_notice.objects.filter(death_notice_created__gte=( datetime.datetime.now() - days_ago ), funeral_home__username=request.user.username)
    obituaries = Obituary.objects.filter(obituary_created__gte=( datetime.datetime.now() - days_ago ), death_notice__funeral_home__username=request.user.username)
    ObituaryFactoryFormSet = modelform_factory(Obituary)
    
    return render_to_response('fh_index2.html', {
        'death_notices': death_notices,
        'obituaries': obituaries,
        'user': request.user,
    }, context_instance=RequestContext(request))

@login_required
def manage_death_notice2(request, death_notice_id=None):
    if request.method == 'POST':
        if request.POST.has_key('delete_death_notice'):
            Death_notice.objects.filter(funeral_home__username=request.user.username).get(pk=death_notice_id).delete()
            msg = ugettext('The %(verbose_name)s was deleted.') %\
                { 'verbose_name': Death_notice._meta.verbose_name }
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(reverse('death_notice_index2'))
        
        if death_notice_id:
            death_notice = Death_notice.objects.get(pk=death_notice_id)
            form = Death_noticeForm(request.POST, request.FILES, instance=death_notice)
            formset = ServiceFormSet(request.POST, instance=death_notice)
            dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST, instance=death_notice)
        else:
            form = Death_noticeForm(request.POST, request.FILES)
            formset = ServiceFormSet(request.POST)
            dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid() and dn_os_formset.is_valid():
            death_notice = form.save(commit=False)
            death_notice.funeral_home = request.user
            death_notice.save()
            formset = ServiceFormSet(request.POST, instance=death_notice)
            formset.save()
            dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST, instance=death_notice)
            msg = ugettext('Death notice for %s %s saved.' % (death_notice.first_name, death_notice.last_name))
            messages.success(request, msg, fail_silently=True)
            dn_os_formset.save()
            if request.POST.has_key('add_another'):
                return HttpResponseRedirect(reverse('add_death_notice2'))
            else:
                return HttpResponseRedirect(reverse('death_notice_index2'))
    else:
        if death_notice_id:
            death_notice = Death_notice.objects.get(pk=death_notice_id)
            form = Death_noticeForm(instance=death_notice)
            formset = ServiceFormSet(instance=death_notice)
            dn_os_formset = DeathNoticeOtherServicesFormSet(instance=death_notice)
        else:
            form = Death_noticeForm()
            formset = ServiceFormSet(instance=Death_notice())
            dn_os_formset = DeathNoticeOtherServicesFormSet(instance=Death_notice())
    
    response_dict = {
        'form': form,
        'formset': formset,
        'other_services_formset': dn_os_formset,
        'death_notice_id': death_notice_id,
    }
    
    # To be used for Preview
    if death_notice_id:
        response_dict['object_list'] = [death_notice]
    
    t = loader.get_template('manage_death_notice2.html')
    c = RequestContext(request, response_dict)
    data = t.render(c)
    r = HttpResponse(data)
    return r
    return render_to_response('manage_death_notice2.html', response_dict, context_instance=RequestContext(request))

# http://docs.djangoproject.com/en/1.3/topics/forms/modelforms/
@login_required
def manage_obituary2(request, obituary_id=None):
    if obituary_id:
        # Editing existing record ... 
        obituary = get_object_or_404(Obituary, pk=obituary_id)
    else:
        # Creating new record ... 
        obituary = Obituary()
    
    if request.method == 'POST':
        if request.POST.has_key('delete') and obituary_id:
            current_obit = Obituary.objects.filter(death_notice__funeral_home__username=request.user.username).get(pk=obituary_id)
            current_obit.delete()
            msg = ugettext('The %(verbose_name)s for %(first)s %(last)s was deleted.') % \
                {
                    'verbose_name': Obituary._meta.verbose_name,
                    'first': current_obit.death_notice,
                    'last': current_obit.death_notice.last_name,
                }
            messages.success(request, msg, fail_silently=False)
            return HttpResponseRedirect(reverse('death_notice_index2'))
        
        if obituary_id:
            current_obit = Obituary.objects.filter(death_notice__funeral_home__username=request.user.username).get(pk=obituary_id)
        
        form = ObituaryForm(request, request.POST, request.FILES, instance=obituary)
        
        if form.is_valid():
            msg = ugettext('The %(verbose_name)s for %(first)s %(last)s was updated.') % \
                {
                    'verbose_name': Obituary._meta.verbose_name,
                    'first': obituary.death_notice.first_name,
                    'last': obituary.death_notice.last_name,
                }
            messages.success(request, msg, fail_silently=False)
            
            obituary = form.save()
            if request.POST.has_key('submit'):
                return HttpResponseRedirect(reverse('death_notice_index2'))
            elif request.POST.has_key('submit_add'):
                return HttpResponseRedirect(reverse('add_obituary2'))
            else:
                return HttpResponseRedirect(reverse('django_obit_desk2.views.manage_obituary2', args=(obituary.pk,)))
    else:
        if obituary_id:
            current_obit = Obituary.objects.get(pk=obituary_id)
            form = ObituaryForm(request, instance=obituary)
        else:
            form = ObituaryForm(request)
    
    ob_response_dict = {
        'form': form,
        'obituary_id': obituary_id,
    }
    
    # To be used for Preview
    if obituary_id:
        tm = loader.get_template('obituary_list_unix_include2.txt')
        ct = RequestContext(request, {'object_list': [current_obit]})
#         ct = RequestContext(request)
#         ct['object_list'] = [current_obit]
        dt = tm.render(ct)
        dt = output_cleanup_hack(dt)
        dt = adobe_to_web(dt)
        ob_response_dict['obit_preview'] = dt
        ob_response_dict['current_obit'] = current_obit
    
    return render_to_response('manage_obituary2.html', ob_response_dict, context_instance=RequestContext(request))

def logout_view2(request):
    logout(request)
    return HttpResponseRedirect(reverse('death_notice_index2'))

@login_required
def add_new_model2(request, model_name):
    if (model_name.lower() == model_name):
        normal_model_name = model_name.capitalize()
    else:
        normal_model_name = model_name
    
#     app_list = get_apps()
#     for app in app_list:
    app = get_app('django_obit_desk2')
    for model in get_models(app):
        if model.__name__ == normal_model_name:
            form = modelform_factory(model)
            
            if normal_model_name == 'Death_notice':
                dn_name = model._meta.verbose_name
                form = Death_noticeForm
                service_form = ServiceFormSet
                dn_os_formset = DeathNoticeOtherServicesFormSet
            
            if request.method == 'POST':
                form = form(request.POST)
                service_form = service_form(request.POST)
                dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST)
                if form.is_valid() and service_form.is_valid() and dn_os_formset.is_valid():
                    try:
                        if normal_model_name == 'Death_notice':
                            new_obj = form.save(commit=False)
                            new_obj.funeral_home = request.user
                            new_obj.save()
                            service_form = ServiceFormSet(request.POST, instance=new_obj)
                            service_form.save()
                            dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST, instance=new_obj)
                            dn_os_formset.save()
                        else:
                            new_obj = form.save()
                    except forms.ValidationError, error:
                        new_obj = None
                    
                    if new_obj:
                         return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                                (escape(new_obj._get_pk_val()), escape(new_obj)))
            else:
               form = form()
            
            page_context = {
                'form': form, 
                'service_form': service_form, 
                'other_services_formset': dn_os_formset, 
                'field': normal_model_name, 
                'dn_verbose_name': dn_name, 
                'dn_app_name': app, 
            }
            return render_to_response('dn_popup2.html', page_context, context_instance=RequestContext(request))

@login_required
def billing2(request, billing_month=None, excel_response=False):
    now = datetime.datetime.now()
    this_month = now.month
    one_month_back = now + relativedelta.relativedelta(months=-1)
    if billing_month:
        run_obits = Obituary.objects.filter(obituary_publish_date__isnull=False, obituary_publish_date__gte='2012-2-1').order_by('-obituary_publish_date')
    else:
        # If no date requested, get current month
        run_obits = Obituary.objects.filter(obituary_publish_date__isnull=False, obituary_publish_date__gte='2012-2-1').order_by('-obituary_publish_date')
    response_dict = {
        'ad_reps': ('wcarole', 'bholmes', 'bnelson', 'jhamilton', 'nkeller', 'phowells',),
        'newsroom': ('lcrossley', 'weeditor',),
        'run_obits': run_obits,
        'month': billing_month,
    }
    if excel_response:
        t = loader.get_template('manage_billing.html')
        c = RequestContext(request, response_dict)
        xls = t.render(c)
        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s' % 'excel.xls'
        return response
    else:
        return render_to_response('manage_billing.html', response_dict, context_instance=RequestContext(request))

@login_required
def billing_excel2(xls, fname="foo.xls"):
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % fname
    xls.save(response)
    return response

@login_required
def print_obituary2(request, obituary_id=None):
    '''
    Coding Horror: Pretty much copied line-for-line 
    from manage_obituary(request, obituary_id=None), ~ Line 241, above. 
    '''
    if obituary_id:
        obit = Obituary.objects.get(pk=obituary_id)
        tm = loader.get_template('obituary_list_unix_include2.txt')
        ct = RequestContext(request, {'object_list': [obit]})
        dt = tm.render(ct)
        dt = output_cleanup_hack(dt)
        dt = adobe_to_web(dt)
    response_dict = {
        'obit_string': dt,
        'obit': obit,
    }
    return render_to_response('print_obituary2.html', response_dict, context_instance=RequestContext(request))

@login_required
def hard_copies_manifest2(request):
    have_run_list = Obituary.objects.filter(obituary_publish_date__isnull=False).order_by('-obituary_publish_date')
    response_dict = {
        'list': have_run_list,
    }
    return render_to_response('hard_copies_manifest.html', response_dict, context_instance=RequestContext(request))