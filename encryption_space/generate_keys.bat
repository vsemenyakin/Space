set openssl_path="C:\Program Files\Git\usr\bin\openssl.exe"
set keys_folder_name=keys
Rem ----------------------------------------------------------------------------------------
if exist %keys_folder_name% (
  msg "%username%" Keys folder is exists!
) else (
  mkdir %keys_folder_name%
  %openssl_path% genrsa -aes128 -out %keys_folder_name%\private.pem 1024
  %openssl_path% rsa -in %keys_folder_name%\private.pem -pubout > %keys_folder_name%\public.pem
)
Rem ----------------------------------------------------------------------------------------
set /p DUMMY=Press ENTER to close...