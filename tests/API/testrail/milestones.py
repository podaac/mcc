from requests.models import HTTPBasicAuth

import requests

from config.config import Config


# File wide variables
base_endpoint = "/index.php?/api/v2"
conf = Config

class Milestones():

    def GetMilestones(projectId):
        endpoint = "/get_milestones/{0}".format(projectId)
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = {
            "Content-Type": "application/json" }
        response = requests.get(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header)
        return response

    def GetActiveMilestone(projectId):
        endpoint = "/get_milestones/{0}&is_completed=0&is_started=1".format(projectId)
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = {
            "Content-Type": "application/json" }

        response = requests.get(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header)
        return response