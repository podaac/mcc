from behave.model import Feature
from behave.runner import Context
from behave.model_core import Status
from datetime import datetime

from utils.seleniumutils import SeleniumUtils
from utils.cleanup import Cleanup
from utils.testrailhandler import TestRailHandler
from utils.behaveutility import BehaveUtility

from config.globalvariables import GlobalVariables
from config.config import Config


conf = Config
globalvars = GlobalVariables
class AfterTestHooks():

    def after_all(context:Context):
        if conf.TestRail_CreateReport:
            TestRailHandler.CloseRun(executionLength = globalvars.ExecutionLength)
            # TestRailHandler.DeleteRun()
        # Cleanup.CustomDataCleanup(context)
        Cleanup.CleanupAfterRun()
        if globalvars.Driver != None:
            globalvars.Driver.quit()

    def after_feature(context, feature: Feature):
        globalvars.ExecutionLength += feature.duration
        globalvars.TempStorageInt = 0
        globalvars.TempStorageStr = ""
        if conf.TestRail_CreateReport:
            TestRailHandler.SendResults()

    def after_scenario(context:Context, scenario):
        if 'tags' in globalvars.TempDictStorage.keys():
            print(f'Old Tags: {context.config.tags}')
            context.config.tags = globalvars.TempDictStorage['tags']
            print(f'New tags: {context.config.tags}')
        if globalvars.Driver != None:
            CreateScreenshot(context)
        if conf.TestRail_CreateReport:
            TestRailHandler.CreateResult(scenario)
        Cleanup.CleanupAfterRun()
        
        if globalvars.Driver != None:
            globalvars.Driver.close()


# ========== Private Methods ==========
def CreateScreenshot(context:Context):
    if context.scenario.status == Status.failed:
        # Creating the screenshot
        scenarioId = BehaveUtility.GetCurrentScenarioID(context)
        time = datetime.now().strftime(conf.TimeFormat)
        screenshotFileName = f"./reports/{scenarioId}_{time}.png"
        SeleniumUtils.MakeScreenshot(screenshotFileName)
            
        # Add screenshot to be attached to run
        if scenarioId not in globalvars.TR_Attachments.keys():
            globalvars.TR_Attachments[scenarioId] = []
        globalvars.TR_Attachments[scenarioId].append(screenshotFileName)
        print(f'Name: {screenshotFileName}')
