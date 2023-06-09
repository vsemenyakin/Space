set openssl_path="C:\Program Files\Git\usr\bin\openssl.exe"
set input_folder_name=in
set output_folder_name=out
set keys_folder=in\keys\private.pem
Rem ----------------------------------------------------------------------------------------
setlocal
set "filter=*.*"
pushd %input_folder_name%
Rem --- Looping is based on [https://stackoverflow.com/questions/41934215/batch-file-get-filename-from-directory-and-save-as-variable]
Rem --- Getting file name is based on [https://stackoverflow.com/questions/3215501/batch-remove-file-extension]
for %%a in (%filter%) do (
   %openssl_path% rsautl -decrypt -inkey ..\%keys_folder% -in %%a > ..\out\%%~na
)
popd
endlocal
Rem ----------------------------------------------------------------------------------------
set /p DUMMY=Press ENTER to close...