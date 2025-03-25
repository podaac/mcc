from os import path
from time import sleep
from behave.model import Scenario, Step
from behave.model_core import Status as BehaveStatus

from API.testrail import Attachments, Milestones, TestSuites, TestRuns, TestResults, Statuses
from utils.testrailhelpers import Result, StepResult
from utils.filehandler import FileHandler

import json

from config.config import Config
from config.globalvariables import GlobalVariables


# File wide variables
conf = Config
globalvars = GlobalVariables

class TestRailHandler():

    def CreateRun():
        print(f'TestRail ProjectId: {conf.TestRail_projectId}')
        print(f'TestRail SuiteId: {conf.TestRail_suiteId}')

        response_Milestone = Milestones.GetActiveMilestone(conf.TestRail_projectId)
        milestoneId = json.loads(response_Milestone.text)[0]['id']
        print(f'Mileston Id: {milestoneId}')
        
        # Get the test suite name from testrail
        response_Testsuite = TestSuites.GetTestSuiteInfo(conf.TestRail_suiteId)
        testSuiteName = json.loads(response_Testsuite.text)['name']
        print(f'Test Suite Name: {testSuiteName}')

        GetStatuses()

        # Use the test suite name for the result name with some extra info fro the TR_Config file
        configData = FileHandler.GetJsonFileContent(globalvars.TR_ConfigFile_Name, globalvars.TR_ConfigFile_Location)
        suiteNameFormat = configData['SuiteName'][conf.TestRail_suiteId]
        print(f'suiteNameFormat: {suiteNameFormat}')
        resultName = suiteNameFormat.format(
            TestSuiteName = testSuiteName,
            Version = conf.Version_for_TestCase_Report,
            Custom_Text = conf.Versions['Custom_Text'])

        print(f'resultName: {resultName}')
        response_Run = TestRuns.NewTestRun(
            projectId = conf.TestRail_projectId,
            suiteId = conf.TestRail_suiteId,
            milestoneId = milestoneId,
            name = resultName)

        testRunId = json.loads(response_Run.text)['id']
        print(f'Starting a new run with Id: {testRunId}')
        globalvars.TR_MilestoneId = milestoneId
        globalvars.TR_RunId = testRunId

    def CloseRun(executionLength:float=0):
        if executionLength != 0:
            print('Adding total execution time to run description...')
            elapsedMinutes:int = executionLength // 60
            elapsedSeconds = (executionLength % 60) // 1
            if elapsedMinutes > 60:
                elapsedHours = elapsedMinutes // 60
                elapsedMinutes = (elapsedMinutes % 60) // 1
                extraDescription = f'Total Execution Time: {elapsedHours:.0f}h {elapsedMinutes:.0f}m {elapsedSeconds:.2f}s'
            else:
                extraDescription = f'Total Execution Time: {elapsedMinutes:.0f}m {elapsedSeconds:.2f}s'
            baseDescription = TestRailHandler.GenerateDescription()
            newDescription = f'{baseDescription}\r\n\r\n{extraDescription}'

            print('Update test run name in case of component version update...')
            response_Testsuite = TestSuites.GetTestSuiteInfo(conf.TestRail_suiteId)
            testSuiteName = json.loads(response_Testsuite.text)['name']
            configData = FileHandler.GetJsonFileContent(globalvars.TR_ConfigFile_Name, globalvars.TR_ConfigFile_Location)
            suiteNameFormat = configData['SuiteName'][conf.TestRail_suiteId]
            resultName = suiteNameFormat.format(
                TestSuiteName = testSuiteName,
                Version = conf.Version_for_TestCase_Report,
                Custom_Text = conf.Versions['Custom_Text'])


            TestRuns.UpdateTestRun(
                runId = globalvars.TR_RunId,
                name = resultName,
                description = newDescription)

        print(f'\r\nClosing testrail run: {globalvars.TR_RunId}')
        TestRuns.CloseTestRun(globalvars.TR_RunId)
        tries = 0
        while TestRailHandler.GetRunDetails()['is_completed'] == False and tries < 2:
            sleep(1)
            TestRuns.CloseTestRun(globalvars.TR_RunId)
            tries += 1
        print(f'\r\n***********************TESTRAIL RESULT LINK:**************************')
        print(f'{conf.TestRail_baseurl}/index.php?/runs/view/{globalvars.TR_RunId}')
        print(f'**********************************************************************\r\n')
    
    def DeleteRun():
        print(f'Deleting testrail run: {globalvars.TR_RunId}')
        TestRuns.DeleteTestRun(globalvars.TR_RunId)

    def GetRunDetails():
        response = TestRuns.GetTestRunDetails(globalvars.TR_RunId)
        result = json.loads(response.text)
        return result

    def SendResults():
        testCaseIds = globalvars.TR_TestCaseIds
        for result in globalvars.TR_TestResults:
            testCaseIds.append(result.case_id)
            # Debug
            # if result.comment != '':
            #     print(f'{result.case_id}: {result.comment}')
        
        print(f'Adding results for the following test cases to the run: {testCaseIds}')
        TestRuns.UpdateTestRun(
            runId = globalvars.TR_RunId,
            testCaseIds = testCaseIds)
        TestResults.AddResultsToCases(
            runId = globalvars.TR_RunId,
            results = globalvars.TR_TestResults)
        UpdateResultForTestCase() 
        TestRailHandler.AddAttachmentsToRun()

        print('Emptying stored results...')
        globalvars.TR_Attachments.clear()
        globalvars.TR_TestResults.clear()

    def CreateResult(scenario: Scenario):
        result = Result()
        result.status_id = convertScenarioStatusToTestRailStatus(scenario.status)
        result.custom_step_results = extractStepDetailsFromScenario(scenario)
        elapsedMinutes = scenario.duration // 60
        elapsedSeconds = (scenario.duration % 60) // 1
        if (elapsedMinutes < 1 and elapsedSeconds < 0.5):
            result.elapsed = ''
        elif (elapsedMinutes < 1 and elapsedSeconds > 0.5):
            result.elapsed = f'{elapsedSeconds:.2f}s'
        else:
            result.elapsed = f'{elapsedMinutes:.0f}m {elapsedSeconds:.2f}s'
        ver = conf.Version_for_TestCase_Report if conf.Version_for_TestCase_Report != '' else 'Unknown'
        result.version = f'{ver}'
        
        scenarioId = ''
        for tag in scenario.tags:
            if tag.startswith('TRID_'):
                scenarioId = RemovePrefix(tag, 'TRID_')
                if scenarioId.startswith('C'):
                    scenarioId = RemovePrefix(scenarioId, 'C')
        result.case_id = scenarioId
        if scenarioId in globalvars.TR_CustomComments.keys():
            result.comment = globalvars.TR_CustomComments[scenarioId]
        globalvars.TR_TestResults.append(result)

    def GenerateDescription() -> str:
        description = 'Version information:'
        for key in conf.Versions.keys():
            description += f'\r\n  {key}:  {conf.Versions[key]}'
        return description

    def AddAttachmentsToRun():
        for scenarioId in globalvars.TR_Attachments.keys():
            for attachmentLocation in globalvars.TR_Attachments[scenarioId]:
                attachmentLocation_rel = path.realpath(attachmentLocation)
                Attachments.Add_Attachemnt_To_Run(globalvars.TR_RunId, attachmentLocation_rel)
                FileHandler.DeleteFile(attachmentLocation_rel)


def extractStepDetailsFromScenario(scenario: Scenario):
    stepDetails = []
    for step in scenario.all_steps:
        scenario.all_steps
        step:Step
        stepDetail = StepResult()
        stepDetail.content = f'{step.step_type} {step.name}'
        stepDetail.status_id = convertScenarioStatusToTestRailStatus(step.status)
        if stepDetail.status_id == globalvars.TR_Statuses['failed']:
            errortext = f'\r\n\r\nError Message:\r\n{step.error_message}\r\n\r\n'
            errortext += f'\r\n\r\n====================================================================='
            errortext += f'\r\nFeature file location: {step.filename}'
            errortext += f'\r\nError in line: {step.line}'
            stepDetail.actual = errortext
        elif stepDetail.status_id == globalvars.TR_Statuses['blocked']:
            errortext = f'\r\nStep execution was blocked! Reason:\r\n"{scenario.skip_reason}"'
            stepDetail.actual = errortext
        stepDetails.append(stepDetail.__dict__)

    return stepDetails

def convertScenarioStatusToTestRailStatus(status:Scenario.status):
    if status == BehaveStatus.passed:
        return globalvars.TR_Statuses['passed']
    elif status == BehaveStatus.failed:
        return globalvars.TR_Statuses['failed']
    elif status == BehaveStatus.skipped:
        return globalvars.TR_Statuses['blocked']
    elif status == BehaveStatus.untested:
        return globalvars.TR_Statuses['untested']
    elif status == BehaveStatus.undefined:
        return globalvars.TR_Statuses['untested']
    elif status == BehaveStatus.executing:
        return globalvars.TR_Statuses['partial_pass']
    else:
        raise NotImplementedError(f'Step to handle "{status}" status is not implemented!')

def GetStatuses():
    response_statuses = Statuses.GetStatuses()
    statuses = json.loads(response_statuses.text)

    results = {}
    for status in statuses:
        name = status['name']
        value = status['id']
        results[name] = value
    print(f'Test Statuses:\r\n{results}')
    globalvars.TR_Statuses = results

def GetStatusNameFromID(statusId:int) -> str:
    for statusName in globalvars.TR_Statuses.keys():
        if globalvars.TR_Statuses[statusName] == statusId:
            return statusName

def RemovePrefix(text:str, prefix:str):
    if text.startswith(prefix):
        result = text[len(prefix):]
        return result
    return text

def UpdateResultForTestCase():

    testResultCounter = {}
    failedResultCounter = {}

    # Getting test results number for test case Id
    for result in globalvars.TR_TestResults:
        statusName = GetStatusNameFromID(result.status_id)
        if result.case_id in testResultCounter:
            testResultCounter[result.case_id] = testResultCounter[result.case_id] + 1
        else:
            testResultCounter[result.case_id] = 1
            failedResultCounter[result.case_id] = 0

        # Count the number of results that did not pass for the test case Id
        if statusName != 'passed':
            failedResultCounter[result.case_id] = failedResultCounter[result.case_id] + 1

    # Checking test execution status for testcases with more then 1 run
    # And saving non passed status as worst status to update test case with
    updateTC = {}
    for result in globalvars.TR_TestResults:
        if testResultCounter[result.case_id] > 1 and failedResultCounter[result.case_id] > 0:
            statusName = GetStatusNameFromID(result.status_id)
            if statusName != 'passed':
                updateTC[result.case_id] = result.status_id
    
    # Generate the info for adding an extra test result at the end to update test case status in TR
    #   In testrail the last result is shown, so when there are 2 test execution and 1 failed, but the last passed,
    #   then passed will show as overall result. We want to see the worst result as overall result
    if updateTC != {}:
        results = []
        for testCaseId in updateTC.keys():
            emptyResult = Result()
            emptyResult.case_id = testCaseId
            emptyResult.status_id = updateTC[testCaseId]
            emptyResult.comment = 'There were failed iterations of the test case, marking overall result as failed'
            emptyResult.comment += f'\r\nTotal number of variations: {testResultCounter[testCaseId]}'
            emptyResult.comment += f'\r\nFailed number of variations: {failedResultCounter[testCaseId]}'
            results.append(emptyResult)

        print(f'Adding empty result to update testcase status!')
        TestResults.AddResultsToCases(
            runId = globalvars.TR_RunId,
            results = results)
