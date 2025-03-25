from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from UI.pages.pageBase import PageBase
from utils.seleniumutils import SeleniumUtils


# Locators
Title_Locator = '//body/h1[contains(text(),"ERROR")]' # XPath
ErrorCode_Locator = '//body/h1' # XPath
ErrorText_Locator = '//body' # XPath

class ErrorPage(PageBase):

    def __init__(self) -> None:
        super().__init__(
            name = "Error page",
            locator = Title_Locator,
            by = By.XPATH)


    def GetErrorCode(self) -> str:
        element:WebElement = SeleniumUtils.FindElement(
            by = By.XPATH,
            locator = ErrorCode_Locator)
        return element.text

 
    def GetErrorMessage(self) -> str:
        element:WebElement = SeleniumUtils.FindElement(
            by = By.XPATH,
            locator = ErrorText_Locator)
        return element.text
