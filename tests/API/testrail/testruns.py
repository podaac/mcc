from requests.models import HTTPBasicAuth

import requests
import json

from config.config import Config


# File wide variables
base_endpoint = '/index.php?/api/v2'
conf = Config

class TestRuns():

    def NewTestRun(
        projectId:int,
        name:str,
        milestoneId:int,
        suiteId:int,
        includeAll:bool = False,
        testCaseIds:list = []
        ):

        endpoint = f'/add_run/{projectId}'
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = {
            'Content-Type': 'application/json' }

        description = 'Version information:'
        for key in conf.Versions.keys():
            description += f'\r\n  {key}:  {conf.Versions[key]}'

        content = dict()
        content['name'] = name
        content['description'] = description
        content['suite_id'] = int(suiteId)
        content['milestone_id'] = int(milestoneId)
        content['include_all'] = bool(includeAll)
        content['refs'] = ''
        content['case_ids'] = testCaseIds
        jsonContent = json.dumps(content)

        response = requests.post(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header,
            data = jsonContent)
        return response

    def UpdateTestRun(runId:int, testCaseIds:list=[], name:str='', description:str=''):
        endpoint = f'/update_run/{runId}'
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = { 
            'Content-Type': 'application/json' }

        content = {}
        if testCaseIds != []:
            content['case_ids'] = testCaseIds
        if description != '':
            content['description'] = description
        if name != '':
            content['name'] = name
        if content != {}:
            response = requests.post(
                url = url,
                auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
                headers = custom_header,
                json = content)
            return response
        return None

    def CloseTestRun(runId:int):
        endpoint = f'/close_run/{runId}'
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = { 
            'Content-Type': 'application/json' }

        print('Closing Test Run...')
        response = requests.post(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header)
        
        if response.status_code != 200:
            print(f'Response: {response.status_code}')
            print(f'Response text:\r\n{response.text.encode("utf-8")}\r\n')
            print(f'Request url:\r\n{response.request.url}\r\n')
        return response

    def DeleteTestRun(runId:int):
        endpoint = f'/delete_run/{runId}'
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = { 
            'Content-Type': 'application/json' }

        print('Deleting Test Run...')
        response = requests.post(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header)
        return response
    
    def GetTestRunDetails(runId:int):
        endpoint = f'/get_run/{runId}'
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = { 
            'Content-Type': 'application/json' }

        print('Getting Test Run details...')
        response = requests.get(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header)
        return response

    def GetOpenRuns(projectId:int):
        endpoint = f'/get_runs/{projectId}'
        print(f'conf.TestRail_baseurl: {conf.TestRail_baseurl}')
        print(f'base_endpoint: {base_endpoint}')
        print(f'endpoint: {endpoint}')
        url = conf.TestRail_baseurl + base_endpoint + endpoint + '&is_completed=0' 
        custom_header = { 
            'Content-Type': 'application/json' }

        print('Getting Test Runs...')
        response = requests.get(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header)
        return response
