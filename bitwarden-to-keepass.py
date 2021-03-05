import json
import logging
import os
import subprocess

from argparse import ArgumentParser
from shlex import quote

from pykeepass import PyKeePass, create_database
from pykeepass.exceptions import CredentialsError

from item import Item, Types as ItemTypes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s :: %(levelname)s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


def bitwarden_to_keepass(args):
    try:
        kp = PyKeePass(args.database_path, password=args.database_password, keyfile=args.database_keyfile)
    except FileNotFoundError:
        logging.info('KeePass database does not exist, creating a new one.')
        kp = create_database(args.database_path, password=args.database_password, keyfile=args.database_keyfile)
    except CredentialsError as e:
        logging.error(f'Wrong password for KeePass database: {e}')
        return

    folders = subprocess.check_output(f'{quote(args.bw_path)} list folders --session {quote(args.bw_session)}', shell=True, encoding='utf8')
    folders = json.loads(folders)
    groups = {}
    for folder in folders:
        groups[folder['id']] = kp.add_group(kp.root_group, folder['name'])
    logging.info(f'Folders done ({len(groups)}).')

    items = subprocess.check_output(f'{quote(args.bw_path)} list items --session {quote(args.bw_session)}', shell=True, encoding='utf8')
    items = json.loads(items)
    logging.info(f'Starting to process {len(items)} items.')
    for item in items:
        if item['type'] in [ItemTypes.CARD, ItemTypes.IDENTITY]:
            logging.warning(f'Skipping credit card or identity item "{item["name"]}".')
            continue

        bw_item = Item(item)

        is_duplicate_title = False
        while True:
            entry_title = bw_item.get_name() if not is_duplicate_title else '{name} - ({item_id}'.format(name=bw_item.get_name(), item_id=bw_item.get_id())
            try:
                entry = kp.add_entry(
                    destination_group=groups[bw_item.get_folder_id()],
                    title=entry_title,
                    username=bw_item.get_username(),
                    password=bw_item.get_password(),
                    notes=bw_item.get_notes()
                )
                break
            except Exception as e:
                if 'already exists' in str(e):
                    is_duplicate_title = True
                    continue

                logging.warning(f'Skipping item named "{item["name"]}" because of this error: {repr(e)}')
                break

        totp_secret, totp_settings = bw_item.get_totp()
        if totp_secret and totp_settings:
            entry.set_custom_property('TOTP Seed', totp_secret)
            entry.set_custom_property('TOTP Settings', totp_settings)

        for uri in bw_item.get_uris():
            entry.url = uri['uri']
            break # todo append additional uris to notes?

        for field in bw_item.get_custom_fields():
            entry.set_custom_property(field['name'], field['value'])

        for attachment in bw_item.get_attachments():
            attachment_tmp_path = f'/tmp/attachment/{attachment["fileName"]}'
            attachment_path = subprocess.check_output(f'{quote(args.bw_path)} get attachment'
                                                      f' --raw {quote(attachment["id"])} '
                                                      f'--itemid {quote(bw_item.get_id())} '
                                                      f'--output {quote(attachment_tmp_path)} --session {quote(args.bw_session)}', shell=True, encoding='utf8').rstrip()
            attachment_id = kp.add_binary(open(attachment_path, 'rb').read())
            entry.add_attachment(attachment_id, attachment['fileName'])
            os.remove(attachment_path)

    logging.info('Saving changes to KeePass database.')
    kp.save()
    logging.info('Export completed.')


def check_args(args):
    if args.database_keyfile:
        if not os.path.isfile(args.database_keyfile) or not os.access(args.database_keyfile, os.R_OK):
            logging.error('Key File for KeePass database is not readable.')
            return False

    if not os.path.isfile(args.bw_path) or not os.access(args.bw_path, os.X_OK):
        logging.error('bitwarden-cli was not found or not executable. Did you set correct \'--bw-path\'?')
        return False

    return True


def environ_or_required(key):
    return (
        {'default': os.environ.get(key)} if os.environ.get(key)
        else {'required': True}
    )


parser = ArgumentParser()
parser.add_argument(
    '--bw-session',
    help='Session generated from bitwarden-cli (bw login)',
    **environ_or_required('BW_SESSION'),
)
parser.add_argument(
    '--database-path',
    help='Path to KeePass database. If database does not exists it will be created.',
    **environ_or_required('DATABASE_PATH'),
)
parser.add_argument(
    '--database-password',
    help='Password for KeePass database',
    **environ_or_required('DATABASE_PASSWORD'),
)
parser.add_argument(
    '--database-keyfile',
    help='Path to Key File for KeePass database',
    default=os.environ.get('DATABASE_KEYFILE', None),
)
parser.add_argument(
    '--bw-path',
    help='Path for bw binary',
    default=os.environ.get('BW_PATH', 'bw'),
)
args = parser.parse_args()

check_args(args) and bitwarden_to_keepass(args)
