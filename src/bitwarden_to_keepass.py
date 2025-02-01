import json
import logging
import subprocess
from argparse import Namespace

from pykeepass import PyKeePass, create_database
from pykeepass.exceptions import CredentialsError

from src.folder import load_folders
from src.item import CustomFieldType, Item, ItemType
from src.set_kp_entry_urls import set_kp_entry_urls

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def bitwarden_to_keepass(args: Namespace) -> None:
    try:
        kp = PyKeePass(
            args.database_path,
            password=args.database_password,
            keyfile=args.database_keyfile,
        )
    except FileNotFoundError:
        logging.info("KeePass database does not exist, creating a new one.")
        kp = create_database(
            args.database_path,
            password=args.database_password,
            keyfile=args.database_keyfile,
        )
    except CredentialsError:
        logging.exception("Wrong password for KeePass database")
        return

    folders = subprocess.check_output(
        [args.bw_path, "list", "folders", "--session", args.bw_session],
        encoding="utf8",
    )
    folders = json.loads(folders)
    groups_by_id = load_folders(kp, folders)
    logging.info("Folders done (%d).", len(groups_by_id))

    items = subprocess.check_output(
        [args.bw_path, "list", "items", "--session", args.bw_session],
        encoding="utf8",
    )
    items = json.loads(items)
    logging.info("Starting to process %d items.", len(items))
    for item in items:
        if item["type"] in [ItemType.CARD, ItemType.IDENTITY]:
            logging.warning("Skipping credit card or identity item %s.", item["name"])
            continue

        bw_item = Item(item)

        is_duplicate_title = False
        try:
            while True:
                entry_title = (
                    bw_item.get_name()
                    if not is_duplicate_title
                    else f"{bw_item.get_name()} - ({bw_item.get_id()}"
                )
                try:
                    entry = kp.add_entry(
                        destination_group=groups_by_id[bw_item.get_folder_id()],
                        title=entry_title,
                        username=bw_item.get_username(),
                        password=bw_item.get_password(),
                        notes=bw_item.get_notes(),
                    )
                    break
                except Exception as e:
                    if "already exists" in str(e):
                        is_duplicate_title = True
                        continue
                    raise

            totp_secret, totp_settings = bw_item.get_totp()
            if totp_secret and totp_settings:
                entry.set_custom_property("TOTP Seed", totp_secret, protect=True)
                entry.set_custom_property("TOTP Settings", totp_settings)

            uris = [uri["uri"] for uri in bw_item.get_uris()]
            set_kp_entry_urls(entry, uris)

            for field in bw_item.get_custom_fields():
                entry.set_custom_property(
                    field["name"],
                    field["value"],
                    protect=field["type"] == CustomFieldType.HIDDEN,
                )

            for attachment in bw_item.get_attachments():
                attachment_raw = subprocess.check_output(
                    [
                        args.bw_path,
                        "get",
                        "attachment",
                        attachment["id"],
                        "--raw",
                        "--itemid",
                        bw_item.get_id(),
                        "--session",
                        args.bw_session,
                    ],
                )
                attachment_id = kp.add_binary(attachment_raw)
                entry.add_attachment(attachment_id, attachment["fileName"])

        except Exception as e:
            logging.warning(
                "Skipping item named %s because of this error: %s",
                item["name"],
                e,
            )
            continue

    logging.info("Saving changes to KeePass database.")
    kp.save()
    logging.info("Export completed.")
