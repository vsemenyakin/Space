call vars.bat
Rem ----------------------------------------------------------------------------------------
call setup_git_local.bat
Rem ----------------------------------------------------------------------------------------
if exist %data_base_folder_name% (
  git -C ./%data_base_folder_name% pull origin master
) else (
  git clone %repository_path% ./%data_base_folder_name%
)
Rem ----------------------------------------------------------------------------------------
set /p DUMMY=Press ENTER to close...