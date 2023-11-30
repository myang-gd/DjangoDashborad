prunsrv.exe //IS//LogOutputer-WindowService --DisplayName="LogOutputer-WindowService" --Description="LogOutputer-WindowService" ^
							--Startup=auto --Install=%CD%\prunsrv.exe --Jvm="C:\Program Files\Java\jdk1.8.0_92_green\jre\bin\server\jvm.dll" --Classpath=%CD%\..\target\LogOutputer-0.0.1-SNAPSHOT.jar ^
                            --StartMode=jvm --StartClass=com.greendotcorp.log.LogOutputer.Bootstrap --StartMethod=start --StartParams=start ^
							--StopMode=jvm --StopClass=com.greendotcorp.log.LogOutputer.Bootstrap --StopMethod=stop --StopParams=stop ^
							--StdOutput=auto --StdError=auto --LogPath="%cd%\logs" --LogLevel=Debug ^ ++JvmOptions=-DQA_LOG=F:\QA_Log ^