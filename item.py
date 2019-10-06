from enum import IntEnum
from urllib.parse import urlsplit, parse_qsl


class Types(IntEnum):
    LOGIN = 1
    SECURE_NOTE = 2
    CARD = 3
    IDENTITY = 4


class Item:
    def __init__(self, item):
        self.item = item

    def get_id(self) -> str:
        return self.item['id']

    def get_name(self) -> str:
        return self.item['name']

    def get_folder_id(self) -> str:
        return self.item['folderId']

    def get_username(self) -> str:
        if 'login' not in self.item:
            return ''

        return self.item['login']['username'] if self.item['login']['username'] else ''

    def get_password(self) -> str:
        if 'password' not in self.item:
            return ''

        return self.item['login']['password'] if self.item['login']['password'] else ''

    def get_notes(self):
        return self.item['notes']

    def get_uris(self):
        if 'login' not in self.item or 'uris' not in self.item['login']:
            return []

        return self.item['login']['uris']

    def get_custom_fields(self):
        if 'fields' not in self.item:
            return []

        return self.item['fields']

    def get_attachments(self):
        if 'attachments' not in self.item:
            return []

        return self.item['attachments']

    def get_totp(self):
        if 'login' not in self.item:
            return None, None

        if not self.item['login']['totp']:
            return None, None

        params = urlsplit(self.item['login']['totp']).query
        params = dict(parse_qsl(params))
        period = params.get('period', 30)
        digits = params.get('digits', 6)
        secret = params.get('secret', self.item['login']['totp'])

        return secret, f'{period};{digits}'
