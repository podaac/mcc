from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import NoSuchElementException

from utils.enums import ElementStates
from utils.seleniumutils import SeleniumUtils


class PageBase():
        
    def __init__(self, name:str, locator:str, by:By=By.ID) -> None:
        self._pageName = name
        self._pageLocator = locator
        self._byType = by

    @property 
    def pageLocator(self):
        return self._pageLocator
    
    @property 
    def byTypeForLocator(self):
        return self._byType
    
    @property 
    def pageName(self):
        return self._pageName

    def IsPageLoaded(self) -> bool:
        try:
            element:WebElement = SeleniumUtils.FindElement(
                by = self.byTypeForLocator,
                locator = self.pageLocator,
                timeout = 5)
            return element.is_displayed()
        except NoSuchElementException:
            return False

    def WaitForPageToLoad(self, timeout:int=30) -> bool:
        print(f'\r\nWaiting for {self.pageName} to load...')
        isLoaded = False
        timer = 0
        while isLoaded == False and timer < timeout:
            isLoaded = self.IsPageLoaded()
            if isLoaded == False:
                sleep(1)
                timer += 1
        return isLoaded

    def WaitForPageToDisappear(self, timeout:int=60) -> bool:
        print(f'\r\nWaiting for {self.pageName} to change...')
        isLoaded = True
        timer = 0
        while isLoaded == True and timer < timeout:
            isLoaded = self.IsPageLoaded()
            if isLoaded == True:
                sleep(1)
                timer += 3
        return isLoaded

    def ClickOnButtonWithText(self, buttonName:str):
        print(f'\r\nClicking on button {buttonName}...')
        button_Locator = f'//*[.="{buttonName}"]'
        self.ClickOnButtonByLocator(by=By.XPATH, locator=button_Locator)

    def ClickOnButtonByLocator(self, locator:str, by:By=By.ID):
        SeleniumUtils.ClickOnElement(by=by, locator=locator)

    def GetStateForButtonWithText(self, buttonName:str) -> ElementStates:
        print(f"\r\nGetting {buttonName} button's state...")
        button_Locator = f'//*[.="{buttonName}"]'
        button:WebElement = SeleniumUtils.FindElement(by=By.XPATH, locator=button_Locator)
        if button.is_displayed and button.is_enabled:
            return ElementStates.CLICKABLE
        elif button.is_displayed and not button.is_enabled:
            return ElementStates.INACTIVE
        elif button.is_displayed:
            return ElementStates.VISIBLE
        elif not button.is_displayed:
            return ElementStates.HIDDEN
