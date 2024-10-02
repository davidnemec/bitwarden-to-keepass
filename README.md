# bitwarden-to-keepass
Export (most of) your Bitwarden items into KeePass database.

## How it works?
It uses official [bitwarden-cli](https://bitwarden.com/help/article/cli/) client to export your items from Bitwarden vault and move them into your KeePass database - that includes logins (with TOTP seeds, URIs, custom fields, attachments, notes) and secure notes.

# Usage with docker (docker-compose) - recommended
- Clone this repository
- Run
```
docker-compose run bitwarden-to-keepass
```
- You will be interactively asked to:
  - login to your vault with [bitwarden-cli](https://bitwarden.com/help/article/cli/)
  - and choose KeePass database password

## Optional
- You can edit `.env` and pre-set some options
  - `DATABASE_PASSWORD` - string, used as password for KeePass database
  - `DATABASE_KEYFILE` - path, used as keyfile password for KeePass database
  - `BITWARDEN_URL` - URL, used in case of self-hosted instances or bitwarden.eu
- After the process is finished your database export is in `exports` directory

## Usage without docker (venv)
- Clone this repository
- Run
```
make build
```
- You can either **create new (empty) KeePass database** (tested with [KeePassXC](https://github.com/keepassxreboot/keepassxc) but it will probably work with others) right now, otherwise one will be created when the script is executed
- Go into the virtual environment
```
source .venv/bin/activate
```
- [Download](https://bitwarden.com/help/article/cli/#download-and-install) official bitwarden-cli and do `bw login` (you need `BW_SESSION` for export to work).
- Run
```
python3 bitwarden-to-keepass.py --bw-session BW_SESSION --database-path DATABASE_PATH [--database-password DATABASE_PASSWORD] [--database-keyfile DATABASE_KEYFILE] [--bw-path BW_PATH]
```
