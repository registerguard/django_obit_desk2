import datetime
from models import Death_notice

from obituary_settings import DATABASE_DAYS_BACK

def delete_old_items():
    """
    Remove old Death_notices and related Obituaries.
    """
    days_back = datetime.timedelta(days=DATABASE_DAYS_BACK)
    old_items = Death_notice.objects.filter(death_notice_created__lte= (datetime.datetime.now() - days_back))
    old_items.delete()

def output_cleanup_hack(data):
    data = data.replace('..', '.')
    data = data.replace('  ', ' ')
    data = data.replace('; ; ', '; ')
    data = data.replace('> ', '>')
    return data

def adobe_to_web(input_string):
    output_list = [ u'<p>%s</p>' % line for line in input_string.split('\n') ]
    output_list[0] = u'<b>%s</b>' % output_list[0]
    output_string = u'\n'.join(output_list)
    return output_string
