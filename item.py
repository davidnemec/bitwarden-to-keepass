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
        if 'login' not in self.item:
            return ''

        return self.item['login']['password'] if self.item['login']['password'] else ''

    def get_notes(self):
        return self.item['notes']

    def get_uris(self):
        if 'login' not in self.item or 'uris' not in self.item['login']:
            return []

        for uri in self.item['login']['uris']:
            uri['uri'] = uri['uri'] if uri['uri'] is not None else ''

        return self.item['login']['uris']

    def get_card_fields(self):
        if 'card' not in self.item:
            return []

        old_items = self.item["card"]
        items = dict()

        if old_items["cardholderName"] is not None:
            items["Cardholder Name"] = old_items["cardholderName"]
        if old_items["brand"] is not None:
            items["Brand Name"] = old_items["brand"]
        if old_items["number"] is not None:
            items["Number"] = old_items["number"]
        if old_items["expMonth"] is not None:
            items["Expiration Month"] = old_items["expMonth"]
        if old_items["expYear"] is not None:
            items["Expiration Year"] = old_items["expYear"]
        if old_items["code"] is not None:
            items["Code"] = old_items["code"]

        return items

    def get_identity_fields(self):
        if 'identity' not in self.item:
            return []

        old_items = self.item["identity"]
        items = dict()

        temp = ""
        found = False

        # format Identity name as firstName middleName lastName
        for i in ["title", "firstName", "middleName", "lastName"]:
            if old_items[i] is not None:
                if found:
                    temp = " ".join([temp, old_items[i]])
                else:
                    found = True
                    temp = "".join([temp, old_items[i]])
        if temp != "":
            items["Identity name"] = temp

        if old_items["username"] is not None:
            items["Identity username"] = old_items["username"]

        if old_items["company"] is not None:
            items["Company"] = old_items["company"]

        if old_items["ssn"] is not None:
            items["National Insurance number"] = old_items["ssn"]

        if old_items["passportNumber"] is not None:
            items["Passport number"] = old_items["passportNumber"]

        if old_items["licenseNumber"] is not None:
            items["License number"] = old_items["licenseNumber"]

        if old_items["email"] is not None:
            items["Email"] = old_items["email"]

        if old_items["phone"] is not None:
            items["Phone"] = old_items["phone"]

        # form address string in below format
        # address1
        # address2
        # address3
        # city, state, postalCode
        # country
        temp, found = "", False
        for i in ["address1", "address2", "address3"]:
            if found:
                temp = "\n".join([temp, old_items[i]])
            else:
                found = True
                temp = "".join([temp, old_items[i]])

        found = False
        for i in ["city", "state", "postalCode"]:
            if found:
                temp = ", ".join([temp, old_items[i]])
            else:
                found = True
                temp = "\n".join([temp, old_items[i]])

        if old_items["country"] is not None:
            temp = "\n".join([temp, old_items["country"]])
        if temp != "":
            items["Address"] = temp

        return items
    def get_custom_fields(self):
        if 'fields' not in self.item:
            return []

        for field in self.item['fields']:
            field['name'] = field['name'] if field['name'] is not None else ''
            field['value'] = field['value'] if field['value'] is not None else ''

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
