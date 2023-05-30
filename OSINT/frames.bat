@echo off
Rem ---------------------------
set start_time=2
set end_time=7
set interval=1
Rem ---------------------------
set input_folder_name=in
set output_folder_name=out
Rem ---------------------------
rd /s /q %output_folder_name%
Rem ---------------------------
setlocal
set "filter=*.*"
pushd %input_folder_name%
for %%a in (%filter%) do (
	if NOT [%%~na]==[] (
		echo Input [%%a] is on work...
		mkdir ..\%output_folder_name%\%%~na
		for /L %%i in (%start_time%,%interval%,%end_time%) do (
			echo Processing frame at [%%i]
			ffmpeg -i %%a -ss %%i -frames:v 1 ..\%output_folder_name%\%%~na\%%~na_%%i.png >> ..\%output_folder_name%\%%~na\log.txt 2>&1
			echo ======================================================================= >> ..\%output_folder_name%\%%~na\log.txt
			echo ======================================================================= >> ..\%output_folder_name%\%%~na\log.txt
			echo ======================================================================= >> ..\%output_folder_name%\%%~na\log.txt
		)
		echo Intput [%%a] processed	
	)	
)
popd
endlocal