set md5sum_path="C:\Program Files\Git\usr\bin\md5sum.exe"
set input_folder_name=in
set output_folder_name=out
Rem ----------------------------------------------------------------------------------------
setlocal
set "filter=*.*"
pushd %input_folder_name%
Rem --- Looping is based on [https://stackoverflow.com/questions/41934215/batch-file-get-filename-from-directory-and-save-as-variable]
for %%a in (%filter%) do (
   %md5sum_path% %%a > ..\%output_folder_name%\%%~na.hash.txt
)
popd
endlocal