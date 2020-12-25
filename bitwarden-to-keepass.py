import json
import logging
import os
import subprocess

from argparse import ArgumentParser
from shlex import quote

from pykeepass import PyKeePass, create_database
from pykeepass.exceptions import CredentialsError

from item import Item, Types as ItemTypes

logging.getLogger().setLevel(logging.INFO)


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
        if item['type'] == ItemTypes.CARD:
            logging.warning(f'Skipping credit card item "{item["name"]}".')
            continue

        bw_item = Item(item)

        e = kp.add_entry(
            groups[bw_item.get_folder_id()],
            title=bw_item.get_name(),
            username=bw_item.get_username(),
            password=bw_item.get_password(),
            notes=bw_item.get_notes()
        )

        totp_secret, totp_settings = bw_item.get_totp()
        if totp_secret and totp_settings:
            e.set_custom_property('TOTP Seed', totp_secret)
            e.set_custom_property('TOTP Settings', totp_settings)

        for uri in bw_item.get_uris():
            e.url = uri['uri']
            break # todo append additional uris to notes?

        for field in bw_item.get_custom_fields():
            e.set_custom_property(str(field['name']), field['value'])

        for attachment in bw_item.get_attachments():
            attachment_tmp_path = f'./attachment_tmp/{attachment["fileName"]}'
            attachment_path = subprocess.check_output(f'{quote(args.bw_path)} get attachment'
                                                      f' --raw {quote(attachment["id"])} '
                                                      f'--itemid {quote(bw_item.get_id())} '
                                                      f'--output {quote(attachment_tmp_path)} --session {quote(args.bw_session)}', shell=True, encoding='utf8').rstrip()
            attachment_id = kp.add_binary(open(attachment_path, 'rb').read())
            e.add_attachment(attachment_id, attachment['fileName'])
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


parser = ArgumentParser()
parser.add_argument('--bw-session', help='Session generated from bitwarden-cli (bw login)', required=True)
parser.add_argument('--database-path', help='Path to KeePass database. If database does not exists it will be created.', required=True)
parser.add_argument('--database-password', help='Password for KeePass database', required=True)
parser.add_argument('--database-keyfile', help='Path to Key File for KeePass database', default=None)
parser.add_argument('--bw-path', help='Path for bw binary', default='bw')
args = parser.parse_args()

check_args(args) and bitwarden_to_keepass(args)
