from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from UI.pages.pageBase import PageBase
from utils.seleniumutils import SeleniumUtils


# Locators
GranuleName_Locator = '//h1[contains(text(),"Result")]' # XPath
CheckerList_Locator = '//h1[contains(text(),"Check")]' # XPath
ChecekrSubList_Locator = '//div[@id="{0}"]//h2' # XPATH

class ReportPage(PageBase):

    def __init__(self) -> None:
        super().__init__(
            name = "Main page",
            locator = GranuleName_Locator,
            by = By.XPATH)


    def GetGranuleName(self) -> str:
        element:WebElement = SeleniumUtils.FindElement(
            by = By.XPATH,
            locator = GranuleName_Locator)
        return element.text


    def GetCheckerList(self) -> List[str]:
        elements:List[WebElement] = SeleniumUtils.FindElements(
            by = By.XPATH,
            locator = CheckerList_Locator)
        result = []
        for element in elements:
            result.append(element.text)
        return result
    

    def GetCheckerSubList(self, checkerName:str) -> List[str]:
        locator = ChecekrSubList_Locator.format(checkerName.upper())
        elements:List[WebElement] = SeleniumUtils.FindElements(
            by = By.XPATH,
            locator = locator)
        result = []
        for element in elements:
            result.append(element.text)
        return result