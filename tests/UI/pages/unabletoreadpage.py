from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from UI.pages.pageBase import PageBase
from utils.seleniumutils import SeleniumUtils


# Locators
Title_Locator = '//body//div[@class="row"]//h1[contains(text(), "Unable to read file")]' # XPath
ErrorTitle_Locator = '//body//div[@class="row"]//h1' # XPath
ErrorText_Locator = '//body//div[@class="row"]//p[2]' # XPath

class UnableToReadPage(PageBase):

    def __init__(self) -> None:
        super().__init__(
            name = "Unable to read page",
            locator = Title_Locator,
            by = By.XPATH)


    def GetErrorTitle(self) -> str:
        element:WebElement = SeleniumUtils.FindElement(
            by = By.XPATH,
            locator = ErrorTitle_Locator)
        return element.text


    def GetErrorMessage(self) -> str:
        element:WebElement = SeleniumUtils.FindElement(
            by = By.XPATH,
            locator = ErrorText_Locator)
        return element.text
