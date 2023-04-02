call vars.bat
Rem ----------------------------------------------------------------------------------------
git -C %data_base_folder_name% remote add restore-remote %restore_repository_path%
git -C %data_base_folder_name% checkout -b restore-branch/%user_name%
git -C %data_base_folder_name% push restore-remote restore-branch/%user_name%
Rem ----------------------------------------------------------------------------------------
set /p DUMMY=Press ENTER to close...