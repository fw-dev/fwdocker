@echo off
set datetime=%DATE% %TIME%
set DATAFOLDER="C:\ProgramData\FileWave\FWServer\Data Folder"
set IPA="C:\ProgramData\FileWave\FWServer\ipa"
set logFile=C:\ProgramData\FileWave\FWServer\fwxserver_backup.log

set zdate=%date:~4,2%-%date:~7,2%-%date:~-2%
set zdate=%zdate: =0%
set ztime=%time:~0,2%-%time:~3,2%
set ztime=%ztime: =0%
              
set timestamp=%zdate%--%ztime%

echo "----------------------------"

if [%1]==[] (
        call:syntaxError
	exit /b
)

if [%2]==[] (
	call:syntaxError
	exit /b
)

set script=%0
set backupPath=%1

echo Script is %script%
echo Destination is %backupPath%

set nscript=%script:"=\"%
set nbackupPath=%backupPath:"=\"%

echo Script parameters  "%nscript%  %nbackupPath% now"


if "%2"=="daily" (
      echo Scheduling the backup script to run daily at midnight

      SchTasks /Create /SC DAILY /TN "FileWave Backup" /TR "%nscript%  %nbackupPath% now  >> %logFile%"  /ST 00:01 
      exit /b
)
if "%2" == "weekly" (
      echo Scheduling the backup script to run weekly on Friday midnight

      SchTasks /Create /SC WEEKLY /TN "FileWave Backup" /TR "%nScript%  %nBackupPath% now >> %logFile%"  /ST 00:01   
      exit /b
)

if "%2" == "now" (
      echo Running the back script right now
      goto Backup
)


call:syntaxError
exit /b

:Backup
set DEST=%1
set DEST=%DEST:"=%
set TEMP="%DEST%\temp"
set DB_CONF_FOLDER="%DEST%\fwxserver-Config-DB-%timestamp%"

if not exist "%DEST%" (
 	mkdir "%DEST%"
	echo %datetime% created path  "%DEST%"
)
if not exist "%DEST%" (
	echo Could not create path "%DEST%"
	exit /b
)


if not exist %TEMP% (
	mkdir %TEMP%
	echo %datetime% created path  %TEMP%
)
if not exist %TEMP% (
	echo Could not create path %TEMP%
	exit /b
)

if not exist %DB_CONF_FOLDER% (
	mkdir %DB_CONF_FOLDER%
	echo %datetime% created path  %DB_CONF_FOLDER%
)
if not exist %DB_CONF_FOLDER% (
	echo Could not create path %DB_CONF_FOLDER%
	exit /b
)

set BACKUP_DB="%DB_CONF_FOLDER:"=%\DB"
if not exist %BACKUP_DB% mkdir %BACKUP_DB%

set BACKUP_CERTS="%DB_CONF_FOLDER:"=%\certs"
if not exist %BACKUP_CERTS% mkdir %BACKUP_CERTS%

set DATA_FOLDER="%DEST%\Data Folder"
if not exist %DATA_FOLDER% mkdir %DATA_FOLDER%

set IPA="%DEST%\ipa"
if not exist %IPA%  mkdir %IPA%

set MEDIA="%DEST%\media"
if not exist %MEDIA%  mkdir %MEDIA%


echo Dumping the mdm database to "%BACKUP_DB:"=%\mdm-dump.sql"
"C:\Program Files (x86)\FileWave\postgresql\bin\pg_dump" -U django -Fp -f "%BACKUP_DB:"=%\mdm-dump.sql" mdm

if exist "C:\ProgramData\FileWave\FWServer\DB\admin.sqlite" (
net stop "FileWave Admin Service"
net stop "FileWave Server Service"
net stop "FileWave LDAP"
)

echo Copying the certs folder to %DB_CONF_FOLDER%
xcopy "C:\ProgramData\FileWave\FWServer\certs"  %BACKUP_CERTS%  /e /q


if exist "C:\ProgramData\FileWave\FWServer\DB\admin.sqlite" (
echo Copying the DB folder to %DB_CONF_FOLDER%
xcopy "C:\ProgramData\FileWave\FWServer\DB\*sqlite*" %BACKUP_DB%  /q
)

echo Copying httpd.conf to %DB_CONF_FOLDER%
copy "C:\Program Files (x86)\FileWave\apache\conf\httpd.conf" %DB_CONF_FOLDER%

echo Copying httpd_custom.conf to %DB_CONF_FOLDER%
copy "C:\Program Files (x86)\FileWave\apache\conf\httpd_custom.conf" %DB_CONF_FOLDER%

echo Copying mdm_auth.conf to %DB_CONF_FOLDER%
copy "C:\Program Files (x86)\FileWave\apache\conf\mdm_auth.conf" %DB_CONF_FOLDER%
 
echo Copying apache passwords to %DB_CONF_FOLDER%
copy "C:\Program Files (x86)\FileWave\apache\passwd\passwords" %DB_CONF_FOLDER%


echo Set objArgs = WScript.Arguments > %TEMP%\_zipIt.vbs
echo InputFolder = objArgs(0) >> %TEMP%\_zipIt.vbs
echo ZipFile = objArgs(1) >> %TEMP%\_zipIt.vbs
echo CreateObject("Scripting.FileSystemObject").CreateTextFile(ZipFile, True).Write "PK" ^& Chr(5) ^& Chr(6) ^& String(18, vbNullChar) >> %TEMP%\_zipIt.vbs
echo Set objShell = CreateObject("Shell.Application") >> %TEMP%\_zipIt.vbs
echo Set source = objShell.NameSpace(InputFolder).Items >> %TEMP%\_zipIt.vbs
echo objShell.NameSpace(ZipFile).CopyHere(source) >> %TEMP%\_zipIt.vbs
echo wScript.Sleep 2000 >> %TEMP%\_zipIt.vbs
echo Creating zip archive
cscript.exe //NOLOGO %TEMP%\_zipIt.vbs %DB_CONF_FOLDER% %TEMP%\fwxserver-Config-DB-%timestamp%.zip
DEL /q %TEMP%\_zipIt.vbs

for %%A in (%TEMP%\fwxserver-Config-DB-%timestamp%.zip) do set fileSize=%%~zA
if %filesize% GTR 1000 (
echo Moving archive
move %TEMP%\"fwxserver-Config-DB-%timestamp%.zip" %DEST%
del /q /f %DB_CONF_FOLDER%
rd /q /s %DB_CONF_FOLDER%
) else (
del /q /f %TEMP%\fwxserver-Config-DB-%timestamp%.zip
)

echo Syncing Data Folder to %DATA_FOLDER%
xcopy "C:\ProgramData\FileWave\FWServer\Data Folder"  %DATA_FOLDER% /e /q /d /y

echo Syncing ipa to %IPA%
xcopy "C:\ProgramData\FileWave\FWServer\ipa"  %IPA% /e /q /d /y

echo Syncing media to %MEDIA%
xcopy "C:\ProgramData\FileWave\FWServer\media"  %MEDIA% /e /q /d /y

if exist "C:\ProgramData\FileWave\FWServer\DB\admin.sqlite" (
net start "FileWave Admin Service"
net start "FileWave Server Service"
net start "FileWave LDAP"
)

echo Backup finished.


exit /b

:syntaxError
echo ---------------------------------------------------------------------------
echo  There is a syntax error
echo  HELP:
echo  Automatic Backup example (available frequencies: daily or weekly )         
echo       C:\path\backupFWServer.bat  "F:\backupFolder"  weekly
echo  Manual Backup example:                                                    
echo       "C:\path\backupFWServer.bat "F:\backupFolder"  now
echo So, First parameter is the backup path between quotes and the second is one of the following [now, daily,weekly]                  
echo --------------------------------------------------------------------------
goto:eof
