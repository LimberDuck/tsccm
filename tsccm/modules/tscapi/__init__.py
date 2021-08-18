from tenable.sc import TenableSC
import certstore


class TscApi:
    sc_addr = "127.0.0.1"
    verify = certstore.ca_bundle

    def __init__(self, sc_addr, verify):
        self.sc_addr = sc_addr
        self.verify = verify
        self.sc = TenableSC(sc_addr, ssl_verify=verify)

    def login(self, sc_user, sc_pass):
        self.sc.login(sc_user, sc_pass)

    def status(self):
        response = self.sc.get('status')
        response_json = response.json()
        return response_json

    def system(self):
        response = self.sc.get('system')
        response_json = response.json()
        return response_json

    def logout(self):
        self.sc.logout()

    def user_get(self):
        response = self.sc.get('user?fields=id,username,state')
        response_json = response.json()
        return response_json

    def group_get(self):
        response = self.sc.get('group?fields=id,name')
        response_json = response.json()
        return response_json

    def scan_get(self):
        response = self.sc.get('scan?fields=id,name,createdTime')
        response_json = response.json()
        return response_json

    def scan_results_get(self):
        response = self.sc.get('scanResults?fields=id,name,createdTime')
        response_json = response.json()
        return response_json

    def policy_get(self):
        response = self.sc.get('policy?fields=id,name,createdTime')
        response_json = response.json()
        return response_json

    def credential_get(self):
        response = self.sc.get('credential?fields=id,name,createdTime')
        response_json = response.json()
        return response_json
