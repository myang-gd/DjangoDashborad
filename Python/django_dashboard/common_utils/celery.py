from djcelery.models import IntervalSchedule, CrontabSchedule
from django.forms.models import model_to_dict

def get_interval_cron(context_dict):
    if type(context_dict) != type({}):
        return
    intervalList = []
    for interval in IntervalSchedule.objects.all():
        interval_fields = model_to_dict(interval, fields=[field.name for field in interval._meta.fields])
        interval_fields["display_name"] = 'every %d  %s' % (interval.every, interval.period) 
        intervalList.append(interval_fields)
    context_dict['interval_list'] = intervalList
    cronList = []
    for cron in CrontabSchedule.objects.all():
        cron_fields = model_to_dict(cron, fields=[field.name for field in cron._meta.fields])
        cron_fields["display_name"] = '%s %s %s %s %s (m/h/d/dM/MY)' % (cron.minute, cron.hour, cron.day_of_week, cron.day_of_month, cron.month_of_year) 
        cronList.append(cron_fields)
    context_dict['cron_list'] = cronList