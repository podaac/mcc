from os.path import realpath

from config.config import Config

import requests


# File wide variables
base_endpoint = '/check'
conf = Config

class Check():

    def GetCheck(
            logging:bool=True):
        
        if logging:
            print(f'\r\nGET MCC check...')

        url = conf.MCC_BASEURL + base_endpoint
        custom_header = {
            'Content-Type': 'application/json' }
            
        response = requests.get(
            url = url,
            headers = custom_header)

        if logging:
            print(f'Response: {response.status_code}')
            print(f'Request url:\r\n{response.request.url}\r\n')
            if response.status_code != 200:   
                print(f'Response text:\r\n{response.text.encode("utf-8")}\r\n')
        return response
    
    
    def PostCheck(
            fileLocation:str,
            responseType:str='json',
            useChecker_ACDD:bool=True,
            useChecker_CF:bool=True,
            useChecker_GDS2:bool=True,
            acdd_Version:str='1.1',
            cf_Version:str='1.6',
            gds2_Version:str='L2P',
            logging:bool=True):
        
        if logging:
            print(f'\r\nPosting granule for MCC check...')

        url = conf.MCC_BASEURL + base_endpoint
        
        custom_header = {}
        
        payload = {}
        if responseType == None:
            pass
        else:
            payload['response'] = (None, responseType)
            if logging:
                print(f'Setting response type to "{responseType}"...')

        if fileLocation in ['']:
            payload['file-upload'] = (None, '')
            fileInUse = None
        elif fileLocation == None:
            fileInUse = None
        else:
            realFileLocation = realpath(fileLocation)
            fileInUse = open(realFileLocation, 'rb')
            payload['file-upload'] = fileInUse
            if logging:
                print(f'Adding file to upload...')

        if useChecker_ACDD or useChecker_ACDD == None:
            if useChecker_ACDD == None:
                pass
            else:
                payload['ACDD'] = (None, 'on')
            if acdd_Version != None:
                payload['ACDD-version'] = (None, acdd_Version)
            if logging:
                print(f'Adding ACDD checker version "{acdd_Version}" to check list...')

        if useChecker_CF or useChecker_CF == None:
            if useChecker_CF == None:
                pass
            else:
                payload['CF'] = (None, 'on')
            if cf_Version != None:
                payload['CF-version'] = (None, cf_Version)
            if logging:
                print(f'Adding CF checker version "{cf_Version}" to check list...')

        if useChecker_GDS2 or useChecker_GDS2 == None:
            if useChecker_GDS2 == None:
                pass
            else:
                payload['GDS2'] = (None, 'on')
            if gds2_Version != None:
                payload['GDS2-parameter'] = (None, gds2_Version)
            if logging:
                print(f'Adding GDS2 checker version "{gds2_Version}" to check list...')
        try:
            response = requests.post(
            url = url,
            headers = custom_header,
            files = payload,
            verify = False,
            timeout = 60)
        except Exception as err:
            print(f'\r\n\r\n**************  EXCEPTION RAISED  ******************')
            print(f'Error message: {err.args}\r\n\r\n')
            if fileInUse != None:
                print('Closing file')
                fileInUse.close()
            raise err
        if fileInUse != None:
            print('Closing file')
            fileInUse.close()
            
        tempText = response.text.encode('utf-8')
        if logging:
            print(f'\r\nPayload:\r\n{payload}')
            print(f'\r\nResponse: {response.status_code}')
            print(f'Request url:\r\n{response.request.url}\r\n')
            if response.status_code != 200:   
                print(f'Response text:\r\n{tempText}\r\n')

        return response