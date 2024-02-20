# bitwarden-to-keepass
Export (most of) your Bitwarden items into KeePass database.

## Fork information

This repository is a fork of [davidnemec/bitwarden-to-keepass](https://github.com/davidnemec/bitwarden-to-keepass). 

They did all of the work, I just added the custom URL functionality and created a docker repository. All props to [davidnemec](https://github.com/davidnemec/)!

## How it works?
It uses official [bitwarden-cli](https://bitwarden.com/help/article/cli/) client to export your items from Bitwarden vault and move them into your KeePass database - that includes logins (with TOTP seeds, URIs, custom fields, attachments, notes) and secure notes.

# Usage 

## Environment variables available

- `DATABASE_PASSWORD` (required): The password you want your KeePass file to have.
- `DATABASE_NAME` (optional): The name you want your KeePass file t o have. If not set, it will default to `bitwarden.kdbx`
- `BITWARDEN_URL` (optional): A custom BitWarden/VaultWarden instance. If you are ussing the official https://bitwarden.com, you can leave this blank.

## Backup location

All backups will be written on `/exports`. You need to mount that volume locally in order to retrieve the backup file.

## Docker command

In your terminal, run:

``` sh
$ docker run --rm -it \
     -e DATABASE_PASSWORD=123 \
     -e DATABASE_NAME="my-cool-bitwarden-backup.kdbx" \
     -e BITWARDEN_URL=http://your.bitwarden.instance.com \
     -v ./exports:/exports \
     rogsme/bitwarden-to-keepass
```

**The `--rm --it` is important!** Why?
- `--rm`: The docker container will delete itself after it runs. This ensures no config leaking.
- `-it` The script will ask you your credentials, so docker has to run interactively.

First, the script will ask for your username:

``` sh
$ Email address: your@email.com
```

Then, your master password. The input is hidden, so it won't leak on your terminal:

``` sh
$ Master password: [input is hidden]
```

Finally, if you have 2FA enabled, it will ask for your 2FA code:

``` sh
$ Two-step login code: 123456
```

And I'll start converting your passwords into Keepass! You'll see something simmilar to this:

``` sh
Generating KeePass file /exports/my-cool-bitwarden-backup.kdbx
2024-02-20 15:12:54 :: INFO :: KeePass database does not exist, creating a new one.
2024-02-20 15:13:20 :: INFO :: Folders done (1).
2024-02-20 15:13:36 :: INFO :: Starting to process 999 items.
2024-02-20 15:13:36 :: INFO :: Saving changes to KeePass database.
2024-02-20 15:13:43 :: INFO :: Export completed.
```

In the end, the script will lock and log out from your account:

``` sh
Your vault is locked.
KeePass file /exports/my-cool-bitwarden-backup.kdbx generated successfully
You have logged out.
```

And you can see your file in your mounted directory!

``` sh
$ ls exports
my-cool-bitwarden-backup.kdbx
```


# FAQ

- Why can't I keep my session open?

Basically, security reasons. I preffer the docker container to ask for my credentials each time and not save them.
