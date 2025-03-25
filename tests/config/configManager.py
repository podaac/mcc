from os import getenv, popen

import platform

from utils.enums import BrowserTypes

from config.config import Config


# File wide variables
conf = Config

truevalues = ['true', 'yes', 'y', 'enable', 'enabled']
class ConfigManager():

    def InitializeConfig(userdata):
        print(f"\r\nSetting config file variables...")

        # OS
        conf.OS = platform.system().lower()
        conf.OSVersion = platform.release().lower()
        conf.Selenium_Version = ConfigManager.GetSeleniumVersion()
        
        # Global
        conf.Environment = getenv('ENV_TARGET')
        conf.Browser = BrowserTypes.from_str(userdata.get('browser'))

        # Earthdata Login
        conf.MCC_BASEURL = getenv('MCC_BASEURL')
       
        # Testrail
        conf.TestRail_baseurl = getenv('TESTRAIL_API_BASEURL')
        conf.TestRail_username = getenv('TESTRAIL_USER')
        conf.TestRail_apikey = getenv('TESTRAIL_APIKEY')
        conf.TestRail_projectId = userdata.get('projectId')
        conf.TestRail_suiteId = userdata.get('suiteId')
        conf.TestRail_CreateReport = userdata.get('createReport').lower() in truevalues
        print(f"Creating report: {conf.TestRail_CreateReport}")

    def GetSeleniumVersion() -> str:
        command = "pip3 list | grep -i selenium | awk '{print $2}'"
        # command = "pip3 list | grep -i 'selenium '"
        process = popen(command)
        versions = process.readlines()
        process.close()
        return versions[0]