call ./_/vars.bat
Rem ----------------------------------------------------------------------------------------
call ./_/setup_git_local.bat
Rem ----------------------------------------------------------------------------------------
if exist %review_folder_name% (
  rd /S /Q %review_folder_name%
)
mkdir %review_folder_name%
Rem ----------------------------------------------------------------------------------------
set full_review_revisions_file_name=%review_folder_name%/%review_revisions_file_name%
set full_review_commits_file_name=%review_folder_name%/%review_commits_file_name%
Rem ----------------------------------------------------------------------------------------
git -C ./%data_base_folder_name% fetch --all
if exist %data_base_folder_name% (
  git -C ./%data_base_folder_name% rev-list master..origin/master > %full_review_revisions_file_name%
  for /F "tokens=*" %%A in (%full_review_revisions_file_name%) do (
    git -C ./%data_base_folder_name% show %%A >> %full_review_commits_file_name%
	echo ====================================================================== >> %full_review_commits_file_name%
  )
) else (
  echo "You should load repository first"
)
Rem ----------------------------------------------------------------------------------------
set /p DUMMY=Press ENTER to close...
Rem ----------------------------------------------------------------------------------------
Rem -- Iteration over lines of file [https://stackoverflow.com/a/8976789/3621739]
