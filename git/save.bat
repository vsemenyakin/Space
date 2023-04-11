set /p message=Enter commit message: 
Rem ----------------------------------------------------------------------------------------
call ../_/vars.bat
Rem ----------------------------------------------------------------------------------------
call ../_/setup_git_local.bat
Rem ----------------------------------------------------------------------------------------
if exist ./%data_base_folder_name% (
  if NOT exist ./%data_base_folder_name%/.git (
    git -C ./%data_base_folder_name% init
    git -C ./%data_base_folder_name% remote add origin %repository_path%
  )
  git -C ./%data_base_folder_name% add -A
  git -C ./%data_base_folder_name% commit -m "%message%"
  git -C ./%data_base_folder_name% push origin master
) else (
   msg %username% "No base folder exist!"
)
Rem ----------------------------------------------------------------------------------------
set /p DUMMY=Press ENTER to close...
Rem
Rem |--| 1. Exporting variables ("call vars.bat") [https://stackoverflow.com/questions/2763875/batch-file-include-external-file-for-variables]
Rem |--| 2. Input variables for batch files ("/p") [https://stackoverflow.com/questions/1515965/how-to-input-a-string-from-user-into-environment-variable-from-batch-file]
Rem |--| 3. Call git from another folder ("git -C") [https://medium.com/@heba.waly/run-git-from-any-directory-git-c-vs-git-dir-2b6a3936582b]