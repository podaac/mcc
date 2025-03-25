from behave import given, when, then
from behave.runner import Context
from os.path import realpath, basename
from time import sleep

from UI.pages.mainpage import MainPage
from utils.enums import ReportFormat
from utils.filehandler import FileHandler
from config.globalvariables import GlobalVariables
from config.config import Config


# File wide variables
globalvars = GlobalVariables
conf = Config

@given('go to the MCC page')
def openMCC(context:Context):
    print(f'\r\n===== go to the MCC page =====')

    if globalvars.Driver != None:
        globalvars.Driver.get(conf.MCC_BASEURL)
        print(f"Opening webpage:\n{conf.MCC_BASEURL}")
    else:
        raise Exception("No driver selected for UI execution!!")


@given('a local file "{fileLocation}" is uploaded')
def uploadLocalFile(context:Context, fileLocation:str):
    print(f'\r\n===== a local file "{fileLocation}" is uploaded =====')

    globalvars.TempDictStorage['filename'] = basename(fileLocation)
    absLocation = realpath(fileLocation)
    mainPage = MainPage()
    mainPage.AddFileOrUrl(isLocalFile=True, fileLocationOrURL = absLocation)


@given('an url "{urlLocation}" added for upload')
def uploadUrlFile(context:Context, urlLocation:str):
    print(f'\r\n===== an url "{urlLocation}" added for upload =====')

    mainPage = MainPage()
    mainPage.AddFileOrUrl(isLocalFile=False, fileLocationOrURL = urlLocation)


@given('select "{checkerName}" checker with version "{versionString}"')
def selectChecker(context:Context, checkerName:str, versionString:str):
    print(f'\r\n===== select "{checkerName}" checker with version "{versionString}" =====')

    mainPage = MainPage()
    if checkerName.lower() in ['acdd']:
        mainPage.Add_ACDD_Checker(versionString)
    elif checkerName.lower() in ['cf']:
        mainPage.Add_CF_Checker(versionString)
    elif checkerName.lower() in ['gds2']:
        mainPage.Add_GDS2_Checker(versionString)
    else:
        NotImplemented(f'Checker "{checkerName}" is not implemented!')


@given('select "{outputFormatString}" as an output format')
def selectOutputFormat(context:Context, outputFormatString:str):
    print(f'\r\n===== select "{outputFormatString}" as an output format =====')

    reportFormat:ReportFormat = ReportFormat.from_str(outputFormatString)
    mainPage = MainPage()
    mainPage.SelectReportFormat(format = reportFormat)


@when('press the upload button')
def clickOnUploadButton(context:Context):
    print(f'\r\n===== press the upload button =====')

    mainPage = MainPage()
    mainPage.ClickOnButtonByLocator('uploadButton')


@then('a PDF file is generated')
def verifyReport(context:Context):
    print(f'\r\n===== a PDF file is generated =====')

    timeout = 120
    baseName = globalvars.TempDictStorage['filename']
    fileName = f'{baseName}_metadata_compliance_report.pdf'
    fileExists = FileHandler.WaitForFileToAppear(fileName, timeout = timeout)
    assert fileExists, f'File "{fileName}" failed to appear after {timeout} seconds!'

    fileLocation = f'./{globalvars.Default_Download_Dir}/{fileName}'
    fileSize = int(FileHandler.GetFileSize(fileLocation))
    assert fileSize > 1, f'File size is 0!'


@given('get the MCC limit from the MCC page and save it to "{parameterName}" parameter')
def getMccLimitAndSaveIntoParameter(context:Context, parameterName:str):
    print(f'\r\n===== get the MCC limit from the MCC page and save it to "{parameterName}" parameter =====')
    
    mainPage = MainPage()
    mccLimit = mainPage.GetMccFileLimit()
    globalvars.TempDictStorage['mcc_limit'] = mccLimit


@then('the large file warning shows up on the webpage')
def IsLargeFileWarningPresent(context:Context):
    print(f'\r\n===== the large file warning shows up on the webpage =====')

    mainPage = MainPage()
    is_displayed = mainPage.IsLargeFileWarningDisplayed()
    assert is_displayed, 'The large file warning is not present!'


@then('the progress bar stops')
def IsLargeFileWarningPresent(context:Context):
    print(f'\r\n===== the progress bar stops =====')

    mainPage = MainPage()
    is_displayed = mainPage.ProgressBarIsVisible()
    text = mainPage.GetProgressBarText()
    print(f'Progress bar text: {text}')
    # Check if text is not Uploading or if progressbar is not visible
    assert is_displayed, 'The progress bar is not present!'
    assert 'upload' not in text.lower(), f'The progress bar is still uploading! Text: "{text}"'


@then('the main page is still shown after "{timeout_str}" seconds')
def IsLargeFileWarningPresent(context:Context, timeout_str:str):
    print(f'\r\n===== the main page is still shown after "{timeout_str}" seconds =====')

    mainPage = MainPage()
    sleep(int(timeout_str))
    isLoaded = mainPage.IsPageLoaded()
    assert isLoaded, 'The main page is still loaded!'
