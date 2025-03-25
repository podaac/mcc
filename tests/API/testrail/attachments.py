from requests.models import HTTPBasicAuth

import requests

from config.config import Config


# File wide variables
base_endpoint = '/index.php?/api/v2'
conf = Config

class Attachments():

    def Add_Attachemnt_To_Run(
        runId:int,
        fileLocation:str):
        print(f'Adding attachment to run: {runId} / {fileLocation}')

        endpoint = f'/add_attachment_to_run/{runId}'
        url = conf.TestRail_baseurl + base_endpoint + endpoint

        fileName = fileLocation.split('/')[-1]
        xlsMIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        files = { 'attachment': (fileName, open(fileLocation, 'rb'), { 'Content-Type': xlsMIME })}
        response = requests.post(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            files = files)

        print(f'Response: {response.status_code}')
        if (response.status_code != 200):
            print(f'Response text:\r\n{response.text.encode("utf-8")}\r\n')
            print(f'Request url:\r\n{response.request.url}\r\n')
        
        return response

    def Add_Attachemnt_To_Result(
        resultId:int,
        fileLocation:str):
        print(f'Adding attachment to result: {resultId} / {fileLocation}')

        endpoint = f'/add_attachment_to_result/{resultId}'
        url = conf.TestRail_baseurl + base_endpoint + endpoint

        fileName = fileLocation.split('/')[-1]
        xlsMIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        files = { 'attachment': (fileName, open(fileLocation, 'rb'), { 'Content-Type': xlsMIME })}
        response = requests.post(
            url = url,
            auth = HTTPBasicAuth(conf.TestRail_username, conf.TestRail_apikey),
            files = files)

        print(f'Response: {response.status_code}')
        if (response.status_code != 200):
            print(f'Response text:\r\n{response.text.encode("utf-8")}\r\n')
            print(f'Request url:\r\n{response.request.url}\r\n')
        
        return response