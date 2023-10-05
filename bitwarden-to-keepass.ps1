# MICROSOFT WINDOWS POWER SHELL SCRIPT

# INSTRUCTIONS
# 1. Install Python for Windows
# 2. Download the latest Bitwarden CLI executable and place in a sub-folder folder named: bitwardencli
# 3. Optional: Edit the configuration below to set different hosts, key files or output folders
# 4. Run this script, no admin rights required

# Setup the virtual environment and install libraries
py -m venv .
Scripts\activate
py -m pip install -r requirements.txt

# Set configuration
$BW_PATH="bitwardencli/bw.exe"
$DATABASE_PATH="exports/"+(get-date -Format "yyyy-MM-dd_HHmmss")+"_bitwarden-export.kdbx"
#$DATABASE_PASSWORD = "secret-password" #If disabled, will prompt for a password at runtime (safer practice)
#$DATABASE_KEYFILE="exports/my_keepass.key" # Optional
#Invoke-Expression "$BW_PATH config server https://your.bw.domain.com" #Self-hosted vault

# Check for the Bitwarden CLI
if ( -Not (Test-Path $BW_PATH))
{
	Write-Host "ERROR! Could not find required Bitwarden CLI executable in $BW_PATH" -ForegroundColor red 
	exit
}

#Unlock and sync the bitwarden vault
Invoke-Expression "$BW_PATH login"
$BW_SESSION= Invoke-Expression "$BW_PATH unlock --raw"
Invoke-Expression "$BW_PATH sync"

# Ask for the new DB password
if (!$DATABASE_PASSWORD) {
$DATABASE_PASSWORD=Read-Host "`nPlease enter the password for KeePass DB: "}

# Perform the backup
py bitwarden-to-keepass.py --bw-session $BW_SESSION --database-path $DATABASE_PATH --database-password $DATABASE_PASSWORD --database-keyfile $DATABASE_KEYFILE --bw-path $BW_PATH

# Lock the vault
Invoke-Expression "$BW_PATH lock"

# Unset sensitive variables
Remove-Variable DATABASE_PASSWORD
Remove-Variable BW_SESSION

pause