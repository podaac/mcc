from time import sleep
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.timeouts import Timeouts
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, TimeoutException

from config.globalvariables import GlobalVariables


# File wide variables
globalvars = GlobalVariables

class SeleniumUtils():

    def FindElement(by:By, locator:str, timeout:int=30, logging:bool=True) -> WebElement:
        current_timeouts:Timeouts = globalvars.Driver.timeouts
        globalvars.Driver.set_page_load_timeout(timeout)
        # print(f'page_load FE: {current_timeouts.page_load}')
        i = 0
        retry = 3
        while i < retry:
            try:
                element:WebElement = globalvars.Driver.find_element(
                    by = by,
                    value = locator)
                if logging:
                    print(f"Element found: {locator}")
                globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)
                return element
            except NoSuchElementException as e1:
                i += 1
                if logging:
                    print(f"Element not found: {locator}")
                if i == retry:
                    globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)
                    raise e1
            except StaleElementReferenceException as e2:
                i += 1
                if logging:
                    print(f"StaleElement found: {locator}")
                if i == retry:
                    globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)
                    raise e2
            sleep(1)
        globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)


    def FindElements(by:By, locator:str, timeout:int=30, logging:bool=True) -> List[WebElement]:
        current_timeouts:Timeouts = globalvars.Driver.timeouts
        globalvars.Driver.set_page_load_timeout(timeout)
        # print(f'page_load FEs: {current_timeouts.page_load}')
        i = 0
        retry = 3
        while i < retry:
            try:
                elements:List[WebElement] = globalvars.Driver.find_elements(
                    by = by,
                    value = locator)
                if logging:
                    print(f"Elements found: {locator}")
                    print(f'Count: {len(elements)}')
                globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)
                return elements
            except NoSuchElementException as e1:
                i += 1
                if logging:
                    print(f"Element not found: {locator}")
                if i == retry:
                    globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)
                    raise e1
            except StaleElementReferenceException as e2:
                i += 1
                if logging:
                    print(f"StaleElement found: {locator}")
                if i == retry:
                    globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)
                    raise e2
            sleep(1)
        globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)

    
    def ClickOnElement(by:By, locator:str, timeout:int=30, logging:bool=True) -> None:
        current_timeouts:Timeouts = globalvars.Driver.timeouts
        globalvars.Driver.set_page_load_timeout(timeout)
        # print(f'page_load CE: {current_timeouts.page_load}')
        i = 0
        retry = 3
        while i < retry:
            try:
                SeleniumUtils.FindElement(
                    by = by,
                    locator = locator,
                    timeout = timeout).click()
                globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)
                if logging:
                    print(f'Clicked on element: {locator}')
                return
            except StaleElementReferenceException as e:
                i += 1
                if logging:
                    print(f"StaleElement found: {locator}")
                if i == retry:
                    globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)
                    raise e
                sleep(1)
            except ElementClickInterceptedException as clickIntercepted:
                i += 1
                if logging:
                    print(f'Element was blocked by something!')
                    print(f'{clickIntercepted.msg}')
                globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)
                raise clickIntercepted
            except TimeoutException as t:
                i += 1
                if logging:
                    print(f'Click action was timed out!')
                    print(f'{t.msg}')
        globalvars.Driver.set_page_load_timeout(current_timeouts.page_load)

    
    def SendKeysToElement(by:By, locator:str, text:str, timeout:int=30, logging:bool=True) -> None:
        element:WebElement = SeleniumUtils.FindElement(
            by = by,
            locator = locator,
            timeout = timeout,
            logging = logging)
        element.clear()
        element.send_keys(text)

    def MakeScreenshot(filename:str):
        print(f'Creating screenshot: {filename}')
        doSaved = globalvars.Driver.get_screenshot_as_file(filename)
        if not doSaved:
            print(f'There was an error during making the screenshot, it was saved: "{doSaved}"!')

    def SelectElementInDropdown(by:By, locator:str, value:str, timeout:int=30, logging:bool=True) -> None:
        SeleniumUtils.ClickOnElement(
            by = by,
            locator = locator,
            timeout = timeout,
            logging = logging)
        subLocator = locator + f'/option[.="{value}"]'
        SeleniumUtils.ClickOnElement(
            by = by,
            locator = subLocator,
            timeout = timeout,
            logging = logging)