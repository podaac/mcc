from behave import given, when, then
from behave.runner import Context

from UI.pages.mainpage import MainPage
from UI.pages.reportpage import ReportPage



@then('the report is generated for "{granuleName}" granule')
def verifyReportGeneration(context:Context, granuleName:str):
    print(f'\r\n===== the report is generated for "{granuleName}" granule =====')

    mainPage = MainPage()
    isLoaded = mainPage.WaitForPageToDisappear()
    assert not isLoaded, f'{mainPage.pageName} failed to change to the new one! Element "{mainPage.byTypeForLocator}" "{mainPage.pageLocator}" is still visible!'

    reportPage = ReportPage()
    isLoaded = reportPage.WaitForPageToLoad()
    assert isLoaded, f'{reportPage.pageName} failed to load! Element "{reportPage.byTypeForLocator}" "{reportPage.pageLocator}" did not appear!'
    granuleInReport = reportPage.GetGranuleName()
    assert granuleInReport.__contains__(granuleName), f'Granule "{granuleName}" is not present in the report "{granuleInReport}"!'


@then('the "{checkerName}" checker is used')
def verifyChecker(context:Context, checkerName:str, logging:bool=True):
    if logging:
        print(f'\r\n===== the "{checkerName}" checker is used =====')

    reportPage = ReportPage()
    checkerList = reportPage.GetCheckerList()
    found = False
    for checkerString in checkerList:
        if checkerString.upper().__contains__(checkerName.upper()):
            found = True
            break
    assert found, f'Checker "{checkerName}" in not amongst the executed checkers: "{checkerList}"'



@then('the "{checkerName}" checker version "{versionString}" is used')
def verifyCheckerAndVersion(context:Context, checkerName:str, versionString:str):
    print(f'\r\n===== the "{checkerName}" checker version "{versionString}" is used =====')

    reportPage = ReportPage()
    found = False
    checkerList = reportPage.GetCheckerList()
    for checkerString in checkerList:
        if checkerString.upper().__contains__(f'{checkerName.upper()}-{versionString.upper()}'):
            print(f'\r\nFound in checker: {checkerName.upper()}-{versionString.upper()}')
            found = True
            break
    if not found:
        subList = reportPage.GetCheckerSubList(checkerName)
        for subtext in subList:
            if subtext.upper().__contains__(versionString.upper()):
                print(f'\r\nFound in sublist: {versionString.upper()}')
                found = True
                break
    assert found, f'Version "{versionString}" is not listed under the checker "{checkerName}": "{subList}"'
