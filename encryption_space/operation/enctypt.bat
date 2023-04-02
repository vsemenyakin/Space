set openssl_path="C:\Program Files\Git\usr\bin\openssl.exe"
set input_folder_name=in
set output_folder_name=out
Rem ----------------------------------------------------------------------------------------
setlocal
set "filter=*.*"
pushd %input_folder_name%
Rem --- Looping is based on [https://stackoverflow.com/questions/41934215/batch-file-get-filename-from-directory-and-save-as-variable]
for %%a in (%filter%) do (
   %openssl_path% rsautl -encrypt -inkey ..\..\keys\public.pem -pubin -in ..\%input_folder_name%\%%a -out ..\%output_folder_name%\%%a.enc
)
popd
endlocal
Rem ----------------------------------------------------------------------------------------
set /p DUMMY=Press ENTER to close...