import requests
from packaging import version
from tsccm._version import __version__ as current_version
from tsccm import __about__


def check_for_update():

    PACKAGE_NAME = __about__.__package_name__

    try:
        response = requests.get(
            f"https://pypi.org/pypi/{PACKAGE_NAME}/json", timeout=1.5
        )
        response.raise_for_status()
        latest = response.json()["info"]["version"]
        read_more = (
            f"> Read more:\n"
            f"> https://limberduck.org/en/latest/tools/{PACKAGE_NAME}\n"
            f"> https://github.com/LimberDuck/{PACKAGE_NAME}\n"
            f"> https://github.com/LimberDuck/{PACKAGE_NAME}/releases"
        )
        if version.parse(latest) > version.parse(current_version):
            print(
                f"\n> A new version of {PACKAGE_NAME} is available: {latest} (you have {current_version})"
            )
            print(f"> Update with: pip install -U {PACKAGE_NAME}\n")
            print(read_more)
        elif version.parse(latest) == version.parse(current_version):
            print(
                f"\n> You are using the latest version of {PACKAGE_NAME}: {current_version}\n"
            )
            print(read_more)
        else:
            print(
                f"\n> You are using a pre-release version of {PACKAGE_NAME}: {current_version}"
            )
            print(f"> Latest released version of {PACKAGE_NAME}: {latest}\n")
            print(read_more)
    except requests.exceptions.ConnectionError as e:
        print("> Could not check for updates: Connection error.\n")
        print(e)
    except Exception as e:
        print("> Could not check for updates:\n")
        print(e)
