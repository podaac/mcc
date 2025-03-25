from requests.models import HTTPBasicAuth

import requests

from config.config import Config


# File wide variables
base_endpoint = "/index.php?/api/v2"
conf = Config

class TestSuites():

    def GetTestSuiteInfo(suiteId):
        endpoint = "/get_suite/{0}".format(suiteId)
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = {
            "Content-Type": "application/json" }

        response = requests.get(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header)
        return response
