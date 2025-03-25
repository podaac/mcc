from behave import when, then
from behave.runner import Context

from config.globalvariables import GlobalVariables


# File wide variables
globalvars = GlobalVariables

@then('the response status code is "{responseCodeString}"')
def responseStatusCodeVerification(context:Context, responseCodeString:str):
    print(f'\r\n===== the response status code is "{responseCodeString} =====')

    expectedStatusCode = int(responseCodeString)
    actualStatusCode = globalvars.ResponseToCheck.status_code
    errorMessage = f'Expected status code: "{expectedStatusCode}", actual status code: "{actualStatusCode}"'
    if not actualStatusCode == expectedStatusCode:
        print(f'responseText:\r\n\r\n{globalvars.ResponseToCheck.text.encode("utf-8")}\r\n\r\n')
        print(errorMessage)
    assert actualStatusCode == expectedStatusCode, errorMessage


@then('the response contains "{expectedText}"')
def responseTextContentVerification(context:Context, expectedText:str):
    print(f'\r\n===== the response contains "{expectedText}" =====')

    responseText = globalvars.ResponseToCheck.text    
    doContains = responseText.strip(' ').__contains__(expectedText)
    errorMessage = f'The response text does not contains the following text: "{expectedText}"'
    if not doContains:
        print(f'responseText:\r\n\r\n{responseText.encode("utf-8")}\r\n\r\n')
        print(errorMessage)
    assert doContains, errorMessage
