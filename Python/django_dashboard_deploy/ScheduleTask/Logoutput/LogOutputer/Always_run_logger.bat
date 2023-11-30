@echo off
set count=0
set execution_name=prunsrv.exe
set service_name=LogOutputer-WindowService

if %computername% neq GDCQATOOLS01 exit

for /f "tokens=1,*" %%a in ('tasklist ^|find /I /C "%execution_name%"') do set count=%%a

if %count% == 0 ( 
	sc start "%service_name%"
)
