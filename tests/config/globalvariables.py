from datetime import datetime, timedelta
from requests import Response


class GlobalVariables():

    # Testrun / Behave related variables
    SkipAll:bool = False
    SkipReason:str = ""
    UtcOffset:timedelta = timedelta(hours=0)
    FilesToIgnoreOnCleanUp:list = []
    ExecutionLength:float = 0

    # Selenium
    Driver = None
    Temp_Dir:str = "tempdata"
    Default_Download_Dir:str = "downloads"

    # TestRail related variables
    TR_ConfigFile_Name = "TR_report_config.json"
    TR_ConfigFile_Location = "./config"
    TR_MilestoneId:int = 0
    TR_RunId:int = 0
    TR_Statuses:dict = {}
    TR_TestResults:list = []
    TR_TestCaseIds:list = []
    TR_CustomComments:dict = {}
    TR_Attachments:dict = {}

    # API
    ResponseToCheck:Response = None

    # Temporary storage variables
    # Feature wide variable, gets cleaned at the end of feature
    TempDictStorage:dict = {}
    TempStorageInt:int = 0
    TempStorageStr:str = ""