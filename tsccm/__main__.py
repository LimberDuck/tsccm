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
import datetime

os_user = getpass.getuser().lower()

if platform.system() == 'Windows':
    keyring.set_keyring(Windows.WinVaultKeyring())
elif platform.system() == 'Darwin':
    keyring.set_keyring(macOS.Keyring())


_login_options = [
    click.option('--address', '-a', default=["127.0.0.1"], multiple=True, prompt='address',
                 help='address to which you want to login',
                 show_default="127.0.0.1"),
    click.option('--port', default="443",
                 help='port to which you want to login',
                 show_default="443"),
    click.option('--username', '-u', default=os_user, prompt='username',
                 help='username which you want to use to login',
                 show_default="current user"),
    click.option('--password', '-p',
                 help='password which you want to use to login'),
    click.option('--insecure', '-k', is_flag=True,
                 help="perform insecure SSL connections and transfers"),
    click.option('--format', '-f', default='table',
                 help='data format to display [table,json,csv]',
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
@click.option('--status', is_flag=True,
              help="Get server status")
@click.option('--ips', is_flag=True,
              help="Use to see number of licensed IPs, active IPs and left IPs")
@click.option('--version', is_flag=True,
              help="Get server version")
def server(address, port, username, password, insecure, format, status, ips, version, verbose):
    """get Tenable.SC server info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, port, insecure)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {} "
                  "Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. "
                      "Please make sure they are correct.")
            sys.exit(1)

        status_info = sccon.status_get()['response']
        system_info = sccon.system_get()['response']

        licensed_ips = status_info['licensedIPs']
        active_ips = status_info['activeIPs']
        left_ips = int(licensed_ips) - int(active_ips)
        left_ips_percentage = str(int(100 - 100 * int(active_ips) / int(licensed_ips)))

        if ips:
            print(one_address + ' ' + '{0:}'.format(int(licensed_ips)) + ' - ' + '{0:}'.format(int(active_ips))
                  + ' = ' + '{0:}'.format(left_ips) + ' (' + left_ips_percentage + '%) remaining IPs')
        elif version:
            system_info_version = system_info['version']
            print(one_address, system_info_version)
        elif status:
            status_info_jobd = status_info['jobd']
            print(one_address, status_info_jobd)
        else:
            print("No option given!")

        sccon.logout()


@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get users list")
def user(address, port, username, password, insecure, format, list, verbose):
    """get Tenable.SC user info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, port, insecure)
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
            users_on_tenablesc = [{
                'id': k['id'],
                'username': k['username'],
                'firstname': k['firstname'],
                'lastname': k['lastname'],
                'roleName': k['role']['name'],
                'createdTime': datetime.datetime.fromtimestamp(int(k['createdTime'])),
                'modifiedTime': datetime.datetime.fromtimestamp(int(k['modifiedTime'])),
                'lastLogin': datetime.datetime.fromtimestamp(int(k['lastLogin'])),
                'locked': k['locked'],
                'failedLogins': k['failedLogins'],
            } for k in users_on_tenablesc]
            if format == 'table':
                print(dataframe_table(users_on_tenablesc),'\n')
            elif format == 'csv':
                print(dataframe_table(users_on_tenablesc).to_csv(), '\n')
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
def group(address, port, username, password, insecure, format, list, verbose):
    """get Tenable.SC group info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, port, insecure)
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
            groups_on_tenablesc = [{
                'id': k['id'],
                'name': k['name'],
                'createdTime': datetime.datetime.fromtimestamp(int(k['createdTime'])),
                'modifiedTime': datetime.datetime.fromtimestamp(int(k['modifiedTime'])),
                'userCount': k['userCount'],
            } for k in groups_on_tenablesc]
            if format == 'table':
                print(dataframe_table(groups_on_tenablesc), '\n')
            elif format == 'csv':
                print(dataframe_table(groups_on_tenablesc).to_csv(), '\n')
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
def scan(address, port, username, password, insecure, format, list, verbose):
    """get Tenable.SC active scan info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, port, insecure)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            scans_on_tenablesc = sccon.scan_get()['response']['manageable']
            scans_on_tenablesc = [{
                'id': k['id'],
                'name': k['name'],
                'ownerUsername': k['owner']['username'],
                'createdTime': datetime.datetime.fromtimestamp(int(k['createdTime'])),
                'modifiedTime': datetime.datetime.fromtimestamp(int(k['modifiedTime'])),
                'scheduleType': k['schedule']['type'],
                'scheduleEnabled': k['schedule']['enabled'],
                'scheduleRepeatRule': k['schedule']['repeatRule'],
                'scheduleStart': k['schedule']['start'],
                'scheduleNextRun': datetime.datetime.fromtimestamp(int(k['schedule']['nextRun'])),
            } for k in scans_on_tenablesc]
            if format == 'table':
                print(dataframe_table(scans_on_tenablesc), '\n')
            elif format == 'csv':
                print(dataframe_table(scans_on_tenablesc).to_csv(), '\n')
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
def scan_result(address, port, username, password, insecure, format, list, verbose):
    """get Tenable.SC scan result info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, port, insecure)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            scan_results_on_tenablesc = sccon.scan_results_get()['response']['manageable']
            scan_results_on_tenablesc = [{
                'id': k['id'],
                'name': k['name'],
                'ownerUsername': k['owner']['username'],
                'createdTime': datetime.datetime.fromtimestamp(int(k['createdTime'])),
                'status': k['status'],
                'importStatus': k['importStatus'],
                'totalIPs': k['totalIPs'],
                'scannedIPs': k['scannedIPs'],
                'startTime': datetime.datetime.fromtimestamp(int(k['startTime'])),
                'finishTime': datetime.datetime.fromtimestamp(int(k['finishTime'])),
                'scanDuration': str(datetime.timedelta(seconds=int(0 if int(k['scanDuration']) == -1 else k['scanDuration']))),
            } for k in scan_results_on_tenablesc]
            if format == 'table':
                print(dataframe_table(scan_results_on_tenablesc), '\n')
            elif format == 'csv':
                print(dataframe_table(scan_results_on_tenablesc).to_csv(), '\n')
            else:
                print(scan_results_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()


@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get scan policies list")
def policy(address, port, username, password, insecure, format, list, verbose):
    """get Tenable.SC policy info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, port, insecure)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            scan_policies_on_tenablesc = sccon.policy_get()['response']['manageable']
            scan_policies_on_tenablesc = [{
                'id': k['id'],
                'name': k['name'],
                'ownerUsername': k['owner']['username'],
                'createdTime': datetime.datetime.fromtimestamp(int(k['createdTime'])),
                'modifiedTime': datetime.datetime.fromtimestamp(int(k['modifiedTime'])),
                'policyTemplateName': k['policyTemplate']['name'],
            } for k in scan_policies_on_tenablesc]
            if format == 'table':
                print(dataframe_table(scan_policies_on_tenablesc), '\n')
            elif format == 'csv':
                print(dataframe_table(scan_policies_on_tenablesc).to_csv(), '\n')
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
def credential(address, port, username, password, insecure, format, list, verbose):
    """get Tenable.SC credential info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, port, insecure)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            credentials_on_tenablesc = sccon.credential_get()['response']['manageable']
            credentials_on_tenablesc = [{
                'id': k['id'],
                'name': k['name'],
                'type': k['type'],
                'authType': k['typeFields']['authType'],
                'ownerUsername': k['owner']['username'],
                'createdTime': datetime.datetime.fromtimestamp(int(k['createdTime'])),
                'modifiedTime': datetime.datetime.fromtimestamp(int(k['modifiedTime'])),
            } for k in credentials_on_tenablesc]
            if format == 'table':
                print(dataframe_table(credentials_on_tenablesc), '\n')
            elif format == 'csv':
                print(dataframe_table(credentials_on_tenablesc).to_csv(), '\n')
            else:
                print(credentials_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()


@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get roles list")
def role(address, port, username, password, insecure, format, list, verbose):
    """get Tenable.SC role info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, port, insecure)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            roles_on_tenablesc = sccon.role_get()['response']
            roles_on_tenablesc = [{
                'id': k['id'],
                'name': k['name'],
                'createdTime': datetime.datetime.fromtimestamp(int(k['createdTime'])),
                'modifiedTime': datetime.datetime.fromtimestamp(int(k['modifiedTime'])),
                'organizationCounts': k['organizationCounts'],
            } for k in roles_on_tenablesc]
            if format == 'table':
                print(dataframe_table(roles_on_tenablesc), '\n')
            elif format == 'csv':
                print(dataframe_table(roles_on_tenablesc).to_csv(), '\n')
            else:
                print(roles_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()

@cli.command()
@add_options(_login_options)
@add_options(_general_options)
@click.option('--list', is_flag=True,
              help="Get audit files list")
def audit_file(address, port, username, password, insecure, format, list, verbose):
    """get Tenable.SC audit file info"""

    for one_address in address:
        one_password = password_check(one_address, username, password, verbose)

        try:
            sccon = TscApi(one_address, port, insecure)
            sccon.login(username, one_password)
        except ConnectionError as e:
            print("Can't reach Tenable.sc API via {}. Please check your connection.".format(one_address))
            sys.exit(1)

        except CustomOAuth2Error as e:
            print("Can't login to Tenable.sc API with supplied credentials. Please make sure they are correct.")
            sys.exit(1)

        if list:
            print(one_address)
            audit_files_on_tenablesc = sccon.audit_file_get()['response']['manageable']
            audit_files_on_tenablesc = [{
                'id': k['id'],
                'name': k['name'],
                'createdTime': datetime.datetime.fromtimestamp(int(k['createdTime'])),
                'modifiedTime': datetime.datetime.fromtimestamp(int(k['modifiedTime'])),
                'filename': k['filename'],
                'originalFilename': k['originalFilename'],
            } for k in audit_files_on_tenablesc]
            if format == 'table':
                print(dataframe_table(audit_files_on_tenablesc), '\n')
            elif format == 'csv':
                print(dataframe_table(audit_files_on_tenablesc).to_csv(), '\n')
            else:
                print(audit_files_on_tenablesc)

        else:
            print("No option given!")

        sccon.logout()


def main():

    print('tsccm v.{}'.format( __version__))
    cli()


if __name__ == '__main__':
    main()
