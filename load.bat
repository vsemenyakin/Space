call vars.bat
Rem ----------------------------------------------------------------------------------------
if exist data_base_folder_name (
  git -C ./%data_base_folder_name% remote remove restore-remote
  git -C ./%data_base_folder_name% remote set-url origin %repository_path%
  git -C ./%data_base_folder_name% reset --hard origin/main
  git -C ./%data_base_folder_name% pull origin main
) else (
  git clone %repository_path% ./%data_base_folder_name%
)
Rem ----------------------------------------------------------------------------------------
set /p DUMMY=Press ENTER to close...