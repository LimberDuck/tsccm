from tsccm._version import __version__
from tsccm.modules.tscapi import TscApi
import click
import pandas as pd
from tabulate import tabulate
import getpass
import keyring
from keyring.backends import Windows, macOS
import platform
import sys
from tenable.errors import ConnectionError
from oauthlib.oauth2.rfc6749.errors import CustomOAuth2Error

os_user = getpass.getuser().lower()

if platform.system() == 'Windows':
    keyring.set_keyring(Windows.WinVaultKeyring())
elif platform.system() == 'Darwin':
    keyring.set_keyring(macOS.Keyring())


_login_options = [
    click.option('--address', '-a', default=["127.0.0.1"], multiple=True, prompt='address',
                 help='address to which you want to login',
                 show_default="127.0.0.1"),
    click.option('--username', '-u', default=os_user, prompt='username',
                 help='username which you want to use to login',
                 show_default="current user"),
    click.option('--password', '-p',
                 help='password which you want to use to login'),
    click.option('--verify',
                 help="Set to False if you don't want to verify SSL certificate"),
    click.option('--format', '-f', default='table',
                 help='data format to display [table,json]',
                 show_default="table")
]

_general_options = [
    click.option('-v', '--verbose', count=True)
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def set_vault_password(address, username, password):
    password_from_vault = keyring.get_password(address, username)
    if password_from_vault is None:
        keyring.set_password(address, username, password)
        if platform.system() == 'Windows':
            print("Credentials successfully saved to Windows Credential Manager.")
            print("Windows OS: Your credentials will be stored here "
                  "Control Panel > Credential Manager > Windows Credential > Generic Credentials. "
                  "You can remove or update it anytime.")

        if platform.system() == 'Darwin':
            print("Credentials successfully saved to macOS Credential Manager.")
            print("macOS: Your credentials will be stored here "
                  "Keychain Access > search for \"" + address + "\". "
                                                                "You can remove or update it anytime.")

    elif password_from_vault is not None and password_from_vault != password:
        print('Password for {} @ {} already exist in OS Credential Manager and '
              'is different than provided by you!'.format(username, address))

        vault_update_answer = input('Do you want to update password in '
                                    'OS Credential Manager? (yes): '.format(username,
                                                                            address)) or "yes"

        if vault_update_answer == 'yes':
            keyring.set_password(address, username, password)
            if platform.system() == 'Windows':
                print("Credentials successfully saved to Windows Credential Manager.")
                print("Windows OS: Your credentials will be stored here "
                      "Control Panel > Credential Manager > Windows Credential > Generic Credentials. "
                      "You can remove or update it anytime.")

            if platform.system() == 'Darwin':
                print("Credentials successfully saved to macOS Credential Manager.")
                print("macOS: Your credentials will be stored here "
                      "Keychain Access > search for \"" + address + "\". "
                                                                    "You can remove or update it anytime.")


def get_vault_password(address, username, verbose):
    password = None
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        if verbose:
            print("Looking for password in OS Credential Manager")
        password_from_vault = keyring.get_password(address, username)
        if password_from_vault:
            password = password_from_vault
            if verbose:
                print("Password found.")
        else:
            if verbose:
                print("Password not found.")

    return password


def password_check(address, username, password, verbose):
    if not password:
        password = get_vault_password(address, username, verbose)

    if not password:
        password = click.prompt("password", hide_input=True, confirmation_prompt=True)
        set_vault_password(address, username, password)

    if password:
        set_vault_password(address, username, password)

    return password


def dataframe_table(data, sortby=None, groupby=None, tablefmt=None):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    df = pd.DataFrame(data)
    df.head()
    if sortby:
        df = df.sort_values(by=sortby)
    if groupby:
        df = df.groupby(groupby)[groupby[0]].count().reset_index(name="count")
    s = pd.Series(list(range(1, len(df) + 1)))
    df = df.set_index(s)
    if tablefmt:
        df = str(tabulate(df, headers='keys', tablefmt=tablefmt))
    return df


@click.group()
def cli():
    pass


@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--ips', is_flag=True,
              help="Use to see number of licensed IPs, active IPs and left IPs")
def status(address, username, password, verify, format, ips, verbose):
    """get Tenable.SC status info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, verify)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {} "
                  "Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. "
                      "Please make sure they are correct.")
            sys.exit(1)

        status = sccon.status()['response']

        licensed_ips = status['licensedIPs']
        active_ips = status['activeIPs']
        left_ips = int(licensed_ips) - int(active_ips)
        left_ips_percentage = str(int(100 - 100 * int(active_ips) / int(licensed_ips)))

        if ips:
            print(one_address + ' ' + '{0:}'.format(int(licensed_ips)) + ' - ' + '{0:}'.format(int(active_ips))
                  + ' = ' + '{0:}'.format(left_ips) + ' (' + left_ips_percentage + '%) remaining IPs')
        else:
            jobd_status = status['jobd']
            system_info = sccon.system()
            system_info_version = system_info['response']['version']

            system_info_build_id = system_info['response']['buildID']
            print(one_address, jobd_status, system_info_version, system_info_build_id)

        sccon.logout()


@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get users list")
def user(address, username, password, verify, format, list, verbose):
    """get Tenable.SC user info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, verify)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {} "
                  "Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            users_on_tenablesc = sccon.user_get()['response']
            if format == 'table':
                print(dataframe_table(users_on_tenablesc))
            else:
                print(users_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()


@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get groups list")
def group(address, username, password, verify, format, list, verbose):
    """get Tenable.SC group info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, verify)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            groups_on_tenablesc = sccon.group_get()['response']
            if format == 'table':
                print(dataframe_table(groups_on_tenablesc))
            else:
                print(groups_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()

@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get active scans list")
def scan(address, username, password, verify, format, list, verbose):
    """get Tenable.SC active scan info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, verify)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            scans_on_tenablesc = sccon.scan_get()['response']['usable']

            if format == 'table':
                print(dataframe_table(scans_on_tenablesc))
                pass
            else:
                print(scans_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()


@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get scans results list")
def scan_result(address, username, password, verify, format, list, verbose):
    """get Tenable.SC scan result info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, verify)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            scans_on_tenablesc = sccon.scan_get()['response']['usable']
            if format == 'table':
                print(dataframe_table(scans_on_tenablesc))
            else:
                print(scans_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()


@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get scan policies list")
def policy(address, username, password, verify, format, list, verbose):
    """get Tenable.SC policy info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, verify)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            scan_policies_on_tenablesc = sccon.policy_get()['response']['usable']
            if format == 'table':
                print(dataframe_table(scan_policies_on_tenablesc))
            else:
                print(scan_policies_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()


@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get credentials list")
def credential(address, username, password, verify, format, list, verbose):
    """get Tenable.SC credential info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, verify)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            credentials_on_tenablesc = sccon.credential_get()['response']['usable']
            if format == 'table':
                print(dataframe_table(credentials_on_tenablesc))
            else:
                print(credentials_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()

def main():

    print('tsccm v.{}'.format( __version__))
    cli()


if __name__ == '__main__':
    main()
