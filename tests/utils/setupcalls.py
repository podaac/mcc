from behave.model import ScenarioOutline

from utils.filehandler import FileHandler

import subprocess, os, sys, copy

from config.config import Config
from config.configManager import ConfigManager
from config.globalvariables import GlobalVariables


# File wide variables
conf = Config
configManager  = ConfigManager
globalvars = GlobalVariables

class SetupCalls():

    def SetUpLogging():
        print(f'\r\nSetting up file logging...')
        tee = subprocess.Popen(['tee', 'log_LatestRun.txt'], stdin=subprocess.PIPE)
        # Cause tee's stdin to get a copy of our stdin/stdout (as well as that
        # of any child processes we spawn)
        os.dup2(tee.stdin.fileno(), sys.stderr.fileno())
        if conf.OS != 'windows':
            os.dup2(tee.stdin.fileno(), sys.stdout.fileno())

    def UpdatedTrReportVersionList():
        print(f'\r\nUpdating Testrail report component list information...')

        data = FileHandler.GetJsonFileContent(globalvars.TR_ConfigFile_Name, globalvars.TR_ConfigFile_Location)
        # Added Custom_Text variable. It is used to add custom text to the title of the test result in Testrail reporting.
        # It is only used when the component_version.json has a Custom_Text input else it's empty.
        conf.Versions['Custom_Text'] = ''
        for component in data['ComponentVersionsToShowInReport'][conf.TestRail_suiteId]:
            conf.Versions[component] = 'Unknown'


    def UpdateComponentVersionData():
        print(f'\r\nUpdating component version information...')
        
        # Update Environment information
        if 'Environment' in conf.Versions.keys():
            conf.Versions['Environment'] = conf.Environment

        # Update Test Framework version from file
        if 'Test_Framework' in conf.Versions.keys():
            versionFileLocation = './VERSION'
            conf.Versions['Test_Framework'] = FileHandler.GetFileContent(versionFileLocation)
        
        # Update MCC API version
        if 'MCC_API' in conf.Versions.keys():
            conf.Versions['MCC_API'] = 'No version data'

        # Update Browser
        if 'Browser' in conf.Versions.keys():
            conf.Versions['Browser'] = conf.Browser.name

        # Update component versions from dedicated json file
        filename = 'component_version_info.json'
        location = './config'
        fileLocation = f'{location}/{filename}'
        
        fileExists = FileHandler.CheckIfFileExists(fileLocation)
        if fileExists:
            componentVersionData = FileHandler.GetJsonFileContent(filename, location)
            for component in componentVersionData.keys():
                if component in conf.Versions.keys():
                    conf.Versions[component] = componentVersionData[component]

        # Update version for testcase report
        configData = FileHandler.GetJsonFileContent(globalvars.TR_ConfigFile_Name, globalvars.TR_ConfigFile_Location)
        componentName = configData['VersionToUseInTestSuiteName'][conf.TestRail_suiteId]
        if componentName not in ['', 'None']:
            if componentName in conf.Versions.keys():
                conf.Version_for_TestCase_Report = conf.Versions[componentName]
            else:
                conf.Version_for_TestCase_Report = f' {componentName} not present'

        # Print versions
        for component in conf.Versions.keys():
            print(f'{component}: {conf.Versions[component]}')
        print(f'\r\nVersion for testcase: {conf.Version_for_TestCase_Report}\r\n\r\n')


    def UpdateScenarioWithCustomData(context):
        # Update scenario with custom test data if it was supplied
        ignoreList = ['', None, 'None']
        filename = 'custom_testdata.json'
        location = './config'
        fileLocation = f'{location}/{filename}'

        # Extract the scenarioIds for Custom test data
        fileExists = FileHandler.CheckIfFileExists(fileLocation)
        updatedScenarios = []
        if fileExists:
            customTestData = FileHandler.GetJsonFileContent(filename, location, logging=False)
            scenarioIds = customTestData.keys()
            for scenarioId in scenarioIds:
                if customTestData[scenarioId] != []:
                    tr_testId = 'TRID_C' + scenarioId

                    # Get the scenario that matches the scenarioId
                    scen = ''
                    for scenario in context.feature.scenarios:
                        if type(scenario) == ScenarioOutline and tr_testId in scenario.tags:
                            scen = scenario
                            break
                        
                    # Check if the current scenario has a custom test data or not with scenario ID
                    if type(scen) == ScenarioOutline:
                        for example in scen.examples:
                            # Copy the original row of the examples table
                            origRow = copy.deepcopy(example.table.rows[0])

                            # Get the column index of the current variable
                            headers = example.table.headings
                            example.table.rows = []
                            rowIndex = 0
                            for testDataRow in customTestData[scenarioId]:
                                newRow = copy.deepcopy(origRow)
                                variableNames = testDataRow.keys()
                                for variableName in variableNames:
                                    newValue = customTestData[scenarioId][rowIndex][variableName]
                                    if newValue not in ignoreList:
                                        # Get the column index of the current variable
                                        headerIndex = headers.index(variableName)

                                        # Update the column of the new row with the test data
                                        newRow.cells[headerIndex] = newValue

                                # Add the edited row to the empty table
                                example.table.rows.append(newRow)
                                rowIndex += 1
                        updatedScenarios.append(scen)
        return updatedScenarios