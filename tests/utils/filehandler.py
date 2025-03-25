from time import sleep
from os import mkdir, remove, listdir, path, popen

import json
import psutil
from config.globalvariables import GlobalVariables


# File wide variables
globalvars = GlobalVariables
tempDirName = "tempdata"
tempDirLocation = f"./{tempDirName}"
testdataDirName = "data"

class FileHandler():

    def CreateDirectory(directoryName:str, logging:bool=True):
        if path.isdir(directoryName) == False:
            if logging:
                print(f'\r\nCreating directory {directoryName}...')
            mkdir(directoryName)

    def CreateFile(fileLocation:str, content:str, logging:bool=True):
        string_list = list(content)
        for i in range(0, string_list.__len__(), 1):
            if string_list[i] == '"' and i > 0 and string_list[i-1] != '\\':
                string_list[i] = '\\"'
        replacedContent = "".join(string_list)
        # replacedContent = content.replace('"', '\\"')
        if logging:
            print(f'Creating file: {fileLocation}')
        popen(f'touch {fileLocation}')
        popen(f'echo "{replacedContent}" > {fileLocation}')
        sleep(1)
    
    def DeleteFile(fileLocation:str):
        print(f'Removing file: {fileLocation}')
        command = f"rm {fileLocation}"
        process = popen(command)
        process.close()

    def CheckIfFileExists(fileLocation:str, logging:bool=True):
        if logging:
            print(f"\r\nChecking for file '{fileLocation}' if it exists...")
        fileLocation_rel = path.realpath(fileLocation)
        doExists = path.exists(fileLocation_rel)
        if doExists and logging:
            print("File exists!")
        elif not doExists and logging:
            print("File does not exists!")
        return doExists
    
    def GetFileSize(fileLocation:str, logging:bool=True) -> str:
        if logging:
            print(f'Get file\'s size: {fileLocation}')
        command = "wc -c " + fileLocation + " | awk '{print $1}' "
        process = popen(command)
        content = process.read()
        process.close()
        return content
    
    def WaitForFileToAppear(fileLocation:str, timeout:int=10, logging:bool=True, realPath:bool=True):
        if logging:
            print(f"\r\nWaiting for file '{fileLocation}' to appear...")
        retries = 0
        waitTime = 1
        fileLocation_rel = path.realpath(fileLocation) if realPath else fileLocation
        while retries < timeout/waitTime:
            if path.exists(fileLocation_rel):
                if logging:
                    print(f"File exists!")
                return
            elif path.islink(fileLocation_rel):
                if logging:
                    print(f"Link exists!")
                return
            else:
                sleep(waitTime)
                retries +=1
        if logging:
            print(f"File failed to appear!")

    def DeleteTempData():
        files = listdir(tempDirLocation)
        print(f"\r\nTemp files to remove:\r\n{files}\r\n")
        for file in files:
            if file in globalvars.FilesToIgnoreOnCleanUp:
                print(f'File: "{file}" ignored.')
                pass
            else:
                pidBlocking = None
                timeout = 0
                waitTime = 5
                timeoutLimit = 120
                while (pidBlocking != [] or pidBlocking == None ) and timeout < timeoutLimit:
                    try:
                        if pidBlocking == None:
                            pidBlocking = []
                        print(f'File "{file}" is in used by PIDs: {pidBlocking}...')
                        if pidBlocking == []:
                            remove(tempDirLocation + "/" + file)
                            print(f"File removed: {file}\r\n")
                        else:
                            pidBlocking = CheckIfFileStillBlockedByPids(pidBlocking, file)
                            sleep(waitTime)
                            timeout += waitTime
                    except PermissionError:
                        print(f'Permission error on removing file: "{file}"...')
                        pidBlocking = GetPidsUsingFile(file)
                                      

    def GetJsonFileContent(fileName:str, location:str=tempDirLocation, logging:bool=True, realPath:bool=True):
        if not fileName.endswith('.json'):
            fileName += ".json"
        if not location.endswith('/') and location != "":
            location += '/'

        fileLocation = f"{location}{fileName}"
        FileHandler.WaitForFileToAppear(fileLocation, logging = logging, realPath = realPath)
        fileContent = FileHandler.GetFileContent(fileLocation, realPath = realPath, logging = logging)
        startOfJsonIndex = fileContent.index('{')
        endOfJsonIndex = fileContent.rindex('}')
        cutContent = fileContent[startOfJsonIndex: endOfJsonIndex+1]
        data = json.loads(cutContent)
        return data
    
    def WriteJsonFile(fileName:str, location:str=tempDirLocation, content:dict={}):
        if not fileName.endswith('.json'):
            fileName += ".json"
        if not location.endswith('/') and location != "":
            location += '/'

        fileLocation = f"{location}{fileName}"
        with open(fileLocation, 'r+') as file:
            file.seek(0)
            json.dump(content, file, indent=4)
            file.truncate()

    def GetFileContent(fileLocation:str, realPath:bool=True, logging:bool=True):
        fileLocation_Real = path.realpath(fileLocation) if realPath else fileLocation
        if path.exists(fileLocation_Real):
            if logging:
                print(f'Reading file: {fileLocation_Real}')
            result = open(fileLocation_Real).read()
            return result
        elif path.islink(fileLocation_Real):
            if logging:
                print(f'Reading file: {path.realpath(fileLocation)}')
            result = open(path.realpath(fileLocation)).read()
            return result
        else:
            raise FileExistsError(f"{fileLocation_Real} does not exists!")

def GetPidsUsingFile(file:str) -> list:
    pidBlocking = []
    for proc in psutil.process_iter():
        try:
            # this returns the list of opened files by the current process
            flist = proc.open_files()
            if flist:
                for nt in flist:
                    if file in nt.path:
                        print(f'Process PID: {proc.pid}')
                        print(f'Process Name: {proc.name()}')
                        print(f'\ttFile: {nt.path}')
                        pidBlocking.append(proc.pid)
        except psutil.NoSuchProcess as err:
            print("****",err)
        except psutil.AccessDenied:
            pass
    return pidBlocking


def CheckIfFileStillBlockedByPids(pidBlocking:list[int], file:str) -> list:
    print('Checking if file is freed up...')
    pidToRemoveFromList = []
    for pid in pidBlocking:
        inUse = False
        process = psutil.Process(pid = pid)
        print(f'Process PID: {process.pid}')
        print(f'Process Name: {process.name()}')
        for nt in process.open_files():
            if file in nt.path:
                print(f'\tFile: {nt.path}')
                inUse = True
        if not inUse:
            pidToRemoveFromList.append(pid)
        for pid in pidToRemoveFromList:
            pidBlocking.remove(pid)