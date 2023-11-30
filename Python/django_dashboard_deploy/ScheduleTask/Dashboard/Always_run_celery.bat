@echo off
set count=0
set execution_name=python-celery.exe
set worker_task_name=Celery-worker
set beat_task_name=Celery-beat
set mem_execution_name=memcached.exe
set mem_task_name=Memcache

if %computername% neq GDCQATOOLS01 exit

for /f "tokens=1,*" %%a in ('tasklist ^|find /I /C "%execution_name%"') do set count=%%a

if not %count% == 6 ( 
	if not %count% == 0 (
	    taskkill /f /im "%execution_name%"
	)
        schtasks /End /TN "%worker_task_name%" && schtasks /End /TN "%beat_task_name%" && schtasks /Run /TN "%worker_task_name%" && schtasks /Run /TN  "%beat_task_name%"
)

tasklist /fi "Imagename eq %mem_execution_name%" | find "No tasks" && schtasks /End /TN "%mem_task_name%" && schtasks /Run /TN "%mem_task_name%"

