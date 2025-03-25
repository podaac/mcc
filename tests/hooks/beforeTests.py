from behave.runner import Context
from behave.model import Feature
from behave.tag_expression import TagExpression

from utils.filehandler import FileHandler
from utils.testrailhandler import TestRailHandler
from utils.seleniumsetup import SeleniumSetup
from utils.setupcalls import SetupCalls

from config.config import Config
from config.configManager import ConfigManager
from config.globalvariables import GlobalVariables


conf = Config
configManager = ConfigManager
globalvars = GlobalVariables
ignoreTagList = ['skip', 'ignore']

class BeforeTestHooks():

    def before_all(context:Context):
        userdata = context.config.userdata
        configManager.InitializeConfig(userdata)
        print(f'Name of the OS system:', conf.OS)
        print(f'Version of the operating system:', conf.OSVersion)
        SetupCalls.SetUpLogging()
        FileHandler.CreateDirectory(globalvars.Temp_Dir)
        FileHandler.CreateDirectory(globalvars.Default_Download_Dir)

        updatedTags = str(context.config.tags).split(' ')
        print(f'\r\nOriginal tags: {updatedTags}')
        updatedTags.append(f'{conf.Environment},ANY_ENV')
        print(f'Added Environment tag: {updatedTags}\r\n')
        formattedTags = TagExpression(updatedTags)
        context.config.tags = formattedTags

        # TestRail setup
        if conf.TestRail_CreateReport:
            print('Setting up testrail...')
            SetupCalls.UpdatedTrReportVersionList()
            SetupCalls.UpdateComponentVersionData()
            # RunExcelReportGenerator.SetUpWorkbook()
            TestRailHandler.CreateRun()


    def before_feature(context:Context, feature:Feature):
        if globalvars.SkipAll == True:
            feature.skip(reason=globalvars.SkipReason)


    def before_scenario(context, scenario):
        # Reinitialize selenium driver if there was a browser attribute
        for ignoreTag in ignoreTagList:
            for tag in scenario.effective_tags:
                if tag.lower() == ignoreTag.lower():
                    scenario.skip(f'********** Marked with "@{ignoreTag}" **********')
                    globalvars.Driver = None
                    return
        globalvars.Driver = SeleniumSetup.ConfigureSelenium(conf.Browser)
