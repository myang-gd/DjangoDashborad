if %computername% neq GDCQATOOLS01 exit
python-celery manage.py celery -A django_dashboard worker -l info