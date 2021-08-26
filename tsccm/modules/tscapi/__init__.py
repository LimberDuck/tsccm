from tenable.sc import TenableSC
import certstore
import urllib3


class TscApi:

    def __init__(self, host='127.0.0.1', port=443, insecure=None):
        self.host = host
        self.port = port
        if not insecure:
            self.verify = certstore.ca_bundle
        else:
            self.verify = False
            urllib3.disable_warnings()

        self.sc = TenableSC(self.host, self.port, ssl_verify=self.verify)

    def login(self, sc_user, sc_pass):
        self.sc.login(sc_user, sc_pass)

    def logout(self):
        self.sc.logout()

    def status_get(self):
        response = self.sc.get('status')
        response_json = response.json()
        return response_json

    def system_get(self):
        response = self.sc.get('system')
        response_json = response.json()
        return response_json

    def user_get(self):
        response = self.sc.get('user?fields=id,username,firstname,lastname,role,createdTime,modifiedTime,lastLogin,locked,failedLogins')
        response_json = response.json()
        return response_json

    def group_get(self):
        response = self.sc.get('group?fields=id,name,createdTime,modifiedTime,userCount')
        response_json = response.json()
        return response_json

    def scan_get(self):
        response = self.sc.get('scan?fields=id,name,owner,createdTime,modifiedTime,schedule')
        response_json = response.json()
        return response_json

    def scan_results_get(self):
        response = self.sc.get('scanResult?fields=id,name,owner,createdTime,status,importStatus,totalIPs,scannedIPs,startTime,finishTime,scanDuration')
        response_json = response.json()
        return response_json

    def policy_get(self):
        response = self.sc.get('policy?fields=id,name,owner,createdTime,modifiedTime,policyTemplate')
        response_json = response.json()
        return response_json

    def credential_get(self):
        response = self.sc.get('credential?fields=id,name,type,typeFields,owner,createdTime,modifiedTime')
        response_json = response.json()
        return response_json

    def role_get(self):
        response = self.sc.get('role?fields=id,name,createdTime,modifiedTime,organizationCounts')
        response_json = response.json()
        return response_json

    def audit_file_get(self):
        response = self.sc.get('auditFile?fields=id,name,createdTime,modifiedTime,filename,originalFilename')
        response_json = response.json()
        return response_json
