from behave import given, when, then
from behave.runner import Context

from utils.filehandler import FileHandler
from config.globalvariables import GlobalVariables


# File wide variables
globalvars = GlobalVariables

@given('create file "{fileLocation}" with content "{fileContent}"')
def responseStatusCodeVerification(context:Context, fileLocation:str, fileContent:str):
    print(f'\r\n===== create file "{fileLocation}" with content "{fileContent}" =====')

    FileHandler.CreateFile(fileLocation, fileContent)
    doExists = FileHandler.CheckIfFileExists(fileLocation)
    assert doExists, f'File "{fileLocation}" is not created!'


@given('create file "{fileLocation}" that is equal to "{fileSize}"')
def responseStatusCodeVerification(context:Context, fileLocation:str, fileSize:str):
    print(f'\r\n===== create file "{fileLocation}" that is equal to "{fileSize}" =====')

    if fileSize.lower() in ['mcc limit', 'mcc']:
        fileSize = globalvars.TempDictStorage['mcc_limit']
    print(f'file size: {fileSize}')
    if 'mb' in fileSize.lower():
        size:int = float(fileSize[:-2].strip(' '))
        maxFileSize = int(size*1024*1024)
    elif 'gb' in fileSize.lower():
        size:int = float(fileSize[:-2].strip(' '))
        maxFileSize = int(size*1024*1024*1024)
    else:
        maxFileSize = 1
    print(f'Max file Size: {maxFileSize}')
    try:
        f = open(fileLocation, 'wb')
        f.seek(maxFileSize-1)
        f.write(b'\0')
    except Exception as err:
        print(f'\r\n\r\n**************  EXCEPTION RAISED  ******************')
        print(f'Error message: {err.args}\r\n\r\n')
    f.close()
    
    doExists = FileHandler.CheckIfFileExists(fileLocation)
    fileSize = int(FileHandler.GetFileSize(fileLocation))
    assert doExists, f'File "{fileLocation}" is not created!'
    assert fileSize == maxFileSize, f'File "{fileLocation}" size is "{fileSize}" instead of "{maxFileSize}"!'
