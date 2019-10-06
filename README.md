# bitwarden-to-keepass
Export (most of) your Bitwarden items into KeePass database.

## How it works?
It uses official [bitwarden-cli](https://help.bitwarden.com/article/cli/) client to export your items from Bitwarden vault and move them into your KeePass database - that includes logins (with TOTP seeds, URIs, custom fields, attachments, notes) and secure notes.

## Install
- Clone this repository
- Run
```
make build
```

## Run/usage
- First you will need to **create new (empty) KeePass database** (tested with [KeePassXC](https://github.com/keepassxreboot/keepassxc) but it will probably work with others)
- Go into the virtual environment
```
source .venv/bin/activate
```
- [Download](https://help.bitwarden.com/article/cli/#download--install) official bitwarden-cli and do `bw login` (you need `BW_SESSION` for export to work).
- Run
```
python3 bitwarden-to-keepass.py --bw-session BW_SESSION --database-path DATABASE_PATH --database-password DATABASE_PASSWORD [--bw_path BW_PATH]
```
