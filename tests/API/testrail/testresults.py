from requests.models import HTTPBasicAuth

import requests
import json

from config.config import Config


# File wide variables
base_endpoint = '/index.php?/api/v2'
conf = Config

class TestResults():

    def AddResultsToCases(runId, results:list):
        endpoint = f'/add_results_for_cases/{runId}'
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = {
            'Content-Type': 'application/json' }

        jsonContent = json.dumps(results, default=lambda o: o.__dict__, indent=2)
        if jsonContent.startswith('['):
            newContent = '{ "results": '
            newContent += jsonContent
            newContent += ' }'

        print('Adding Test Results...')
        response = requests.post(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header,
            data = newContent)
        
        print(f'Response: {response.status_code}')
        if (response.status_code != 200):
            print(f'Response text:\r\n{response.text.encode("utf-8")}\r\n')
            print(f'Request url:\r\n{response.request.url}\r\n')
        
        return response

    def GetResultsForCase(runId, testCaseId):
        endpoint = f'/get_results_for_case/{runId}/{testCaseId}'
        url = conf.TestRail_baseurl + base_endpoint + endpoint
        custom_header = {
            'Content-Type': 'application/json' }

        print(f'Getting Test Results for run: {runId} , testcase: {testCaseId}...')
        response = requests.get(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            headers = custom_header)
        
        print(f'Response: {response.status_code}')
        if (response.status_code != 200):
            print(f'Response text:\r\n{response.text.encode("utf-8")}\r\n')
            print(f'Request url:\r\n{response.request.url}\r\n')
        
        return response