class Config():

    # OS
    OS = ""
    OSVersion = ""
    Selenium_Version = ""

    # Environment Information
    Environment:str = ""
    Browser = ""
    Versions:dict = {}
    Version_for_TestCase_Report:str = ""
    TimeFormat:str = "%Y-%m-%d_-_%H_%M_%S"

    # MCC
    MCC_BASEURL = ""
  
    # TestRail
    TestRail_baseurl = ""
    TestRail_username = ""
    TestRail_apikey = ""
    TestRail_projectId = 0
    TestRail_suiteId = 0
    TestRail_CreateReport = False
    Version_for_TestCase_Report:str = ""
