from pykeepass.entry import Entry


def set_kp_entry_urls(entry: Entry, urls: list[str]) -> None:
    """Store a list of URLs coming from a Bitwarden entry in different
    attributes and custom properties of a KeePass entry, depending on whether
    it's an identifier for an Android or iOS app or it's a generic URL"""
    android_apps = ios_apps = extra_urls = 0

    for url in urls:
        match url.partition("://"):
            case ("androidapp", "://", app_id):
                # It's an Android app registered by Bitwarden's mobile app
                # Store multiple apps in AndroidApp, AndroidApp_1, etc.
                #  so that KeePassDX's autofill picks it up
                prop_name = (
                    "AndroidApp" if android_apps == 0 else f"AndroidApp_{android_apps}"
                )
                android_apps += 1
                entry.set_custom_property(prop_name, app_id)
            case ("iosapp", "://", app_id):
                # It's an iOS app registered by Bitwarden's mobile app
                # Maybe properly set up autofill for a macOS/iPhone/iPad
                #  KeePass-compatible app like StrongBox or Keepassium
                ios_apps += 1
                entry.set_custom_property(f"iOS app #{ios_apps}", app_id)
            case _:
                # Assume it's a generic URL.
                # First one goes to the standard URL attribute
                #  and the remaining ones go to URL_1, URL_2 and so on
                if entry.url is None:
                    entry.url = url
                else:
                    extra_urls += 1
                    entry.set_custom_property(f"KP2A_URL_{extra_urls}", url)
