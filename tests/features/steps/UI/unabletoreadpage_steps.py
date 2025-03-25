from behave import given, when, then
from behave.runner import Context

from UI.pages.mainpage import MainPage
from UI.pages.unabletoreadpage import UnableToReadPage


@then('an unable to read page is shown with title "{errorText}"')
def verifyUnableToReadPageTitle(context:Context, errorText:str):
    print(f'\r\n===== an unable to read page is shown with title "{errorText}" =====')

    mainPage = MainPage()
    isLoaded = mainPage.WaitForPageToDisappear()
    assert not isLoaded, f'{mainPage.pageName} failed to change to the new one! Element "{mainPage.byTypeForLocator}" "{mainPage.pageLocator}" is still visible!'

    errorPage = UnableToReadPage()
    isLoaded = errorPage.WaitForPageToLoad()
    assert isLoaded, f'{errorPage.pageName} failed to load! Element "{errorPage.byTypeForLocator}" "{errorPage.pageLocator}" did not appear!'
    currentErrorText = errorPage.GetErrorTitle()
    assert currentErrorText.__contains__(errorText), f'The expected text "{errorText}" is not present on the page!'


@then('an unable to read page is shown with text "{errorText}"')
def verifyUnableToReadPageContent(context:Context, errorText:str):
    print(f'\r\n===== an unable to read page is shown with text "{errorText}" =====')

    mainPage = MainPage()
    isLoaded = mainPage.WaitForPageToDisappear()
    assert not isLoaded, f'{mainPage.pageName} failed to change to the new one! Element "{mainPage.byTypeForLocator}" "{mainPage.pageLocator}" is still visible!'

    errorPage = UnableToReadPage()
    isLoaded = errorPage.WaitForPageToLoad()
    assert isLoaded, f'{errorPage.pageName} failed to load! Element "{errorPage.byTypeForLocator}" "{errorPage.pageLocator}" did not appear!'
    currentErrorText = errorPage.GetErrorMessage()
    assert currentErrorText.__contains__(errorText), f'The expected text "{errorText}" is not present on the page!'
