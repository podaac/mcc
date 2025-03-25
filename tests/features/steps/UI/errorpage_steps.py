from behave import given, when, then
from behave.runner import Context

from UI.pages.mainpage import MainPage
from UI.pages.errorpage import ErrorPage



@then('an error page is shown with text "{errorText}"')
def verifyErrorPageContent(context:Context, errorText:str):
    print(f'\r\n===== an error page is shown with "{errorText}" =====')

    mainPage = MainPage()
    isLoaded = mainPage.WaitForPageToDisappear()
    assert not isLoaded, f'{mainPage.pageName} failed to change to the new one! Element "{mainPage.byTypeForLocator}" "{mainPage.pageLocator}" is still visible!'

    errorPage = ErrorPage()
    isLoaded = errorPage.WaitForPageToLoad()
    assert isLoaded, f'{errorPage.pageName} failed to load! Element "{errorPage.byTypeForLocator}" "{errorPage.pageLocator}" did not appear!'
    currentErrorText = errorPage.GetErrorMessage()
    assert currentErrorText.__contains__(errorText), f'The expected text "{errorText}" is not present on the page!'
    

@then('the error code on the error page is "{errorCode}"')
def verifyErrorPageContent(context:Context, errorCode:str):
    print(f'\r\n===== an error page is shown with "{errorCode}" =====')

    mainPage = MainPage()
    isLoaded = mainPage.WaitForPageToDisappear()
    assert not isLoaded, f'{mainPage.pageName} failed to change to the new one! Element "{mainPage.byTypeForLocator}" "{mainPage.pageLocator}" is still visible!'

    errorPage = ErrorPage()
    isLoaded = errorPage.WaitForPageToLoad()
    assert isLoaded, f'{errorPage.pageName} failed to load! Element "{errorPage.byTypeForLocator}" "{errorPage.pageLocator}" did not appear!'
    currentErrorCode = errorPage.GetErrorCode()
    assert currentErrorCode.__contains__(errorCode), f'The shown error code "{currentErrorCode}" does not contain the expected one "{errorCode}"!'
