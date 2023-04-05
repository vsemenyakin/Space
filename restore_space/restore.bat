Rem ---| Variables |---
set restore_folder_name=.
set local_restore_repo_folder_name=__restore_repo__
set restore_repository_path=https://github.com/vsemenyakin/SilenceWarlord_Resotre.git
Rem ----------------------------------------------------------------------------------------
call ./_/setup_git_local.bat
Rem ----------------------------------------------------------------------------------------
setlocal
Rem ----------------------------------------------------------------------------------------
pushd %restore_folder_name%
for /D %%A in (*) do (
  git -C %%A remote add restore-remote %restore_repository_path%
  git -C %%A push restore-remote master:restore/%%A
  git -C %%A remote remove restore-remote
)
popd
Rem ----------------------------------------------------------------------------------------
if exist %local_restore_repo_folder_name% (
  rd /S /Q %local_restore_repo_folder_name%
)
mkdir %local_restore_repo_folder_name%
git -C ./%local_restore_repo_folder_name% clone %restore_repository_path% .
Rem ----------------------------------------------------------------------------------------
endlocal
Rem ----------------------------------------------------------------------------------------
set /p DUMMY=Press ENTER to close...