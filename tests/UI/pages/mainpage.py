from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import re

from UI.pages.pageBase import PageBase
from utils.seleniumutils import SeleniumUtils
from utils.enums import ReportFormat


# Locators
UploadButton_Locator = 'uploadButton' # ID
TabSelector_Locator = '//ul[@role="tablist"]/li/a[.="{0}"]' # XPath
ProgressBar_Locator = 'progressBar' # ID
Warning_Locator = 'warningDiv' # ID
CheckerCheckbox_Locator = '//input[@type="checkbox" and @name="{0}"]' # XPATH
ACDDVersionDropdown_Locator = '//select[@name="ACDD-version"]' # XPATH
CFVersionDropdown_Locator = '//select[@name="CF-version"]' # XPATH
GDS2VersionDropdown_Locator = '//select[@name="GDS2-parameter"]' # XPATH
ReportFormatRadioButton_Locator = '//input[@class="responseRadioBox" and @value="{0}"]' # XPath
ChooseFileButton_Locator = 'fileInput' # ID
UrlField_Locator = 'urlInput' # ID
MccFileSize_Locator = '//label[@for="fileInput"]//small' #XPATH

class MainPage(PageBase):

    def __init__(self) -> None:
        super().__init__(
            name = 'Main page',
            locator = UploadButton_Locator,
            by = By.ID)

    def SelectReportFormat(self, format:ReportFormat):
        locator = ReportFormatRadioButton_Locator.format(format.name.lower())
        SeleniumUtils.ClickOnElement(
            by = By.XPATH,
            locator = locator)

    def Add_ACDD_Checker(self, version:str):
        locator = CheckerCheckbox_Locator.format('ACDD')
        SeleniumUtils.ClickOnElement(
            by = By.XPATH,
            locator = locator)
        SeleniumUtils.SelectElementInDropdown(
            by = By.XPATH,
            locator = ACDDVersionDropdown_Locator,
            value = version)


    def Add_CF_Checker(self, version:str):
        locator = CheckerCheckbox_Locator.format('CF')
        SeleniumUtils.ClickOnElement(
            by = By.XPATH,
            locator = locator)
        SeleniumUtils.SelectElementInDropdown(
            by = By.XPATH,
            locator = CFVersionDropdown_Locator,
            value = version)


    def Add_GDS2_Checker(self, version:str):
        locator = CheckerCheckbox_Locator.format('GDS2')
        SeleniumUtils.ClickOnElement(
            by = By.XPATH,
            locator = locator)
        SeleniumUtils.SelectElementInDropdown(
            by = By.XPATH,
            locator = GDS2VersionDropdown_Locator,
            value = version)

    def SelectTab(self, tabName:str):
        locator = TabSelector_Locator.format(tabName)
        SeleniumUtils.ClickOnElement(
            by = By.XPATH,
            locator = locator)

    def AddFileOrUrl(self, isLocalFile:bool, fileLocationOrURL:str):
        if isLocalFile:
            # self.SelectTab('Local File')
            chooseFileButton:WebElement = SeleniumUtils.FindElement(
                by = By.ID,
                locator = ChooseFileButton_Locator)
            chooseFileButton.send_keys(fileLocationOrURL)
        # else:
        #     self.SelectTab('Remote File/OPeNDAP')
        #     SeleniumUtils.SendKeysToElement(
        #         by = By.ID,
        #         locator = UrlField_Locator,
        #         text = fileLocationOrURL)

    def GetMccFileLimit(self) -> str:
        element = SeleniumUtils.FindElement(
            by = By.XPATH,
            locator = MccFileSize_Locator)
        text = element.text
        pattern = 'maximum size ([0-9.,]+.[GMT]B)'
        mo = re.search(pattern = pattern, string = text)
        return mo[1]


    def IsLargeFileWarningDisplayed(self) -> bool:
        element:WebElement = SeleniumUtils.FindElement(
            by = By.ID,
            locator = Warning_Locator)
        text = element.text
        return element.is_displayed() and 'selected file is large' in text.lower()


    def ProgressBarIsVisible(self) -> bool:
        element = SeleniumUtils.FindElement(
            by = By.ID,
            locator = ProgressBar_Locator)
        return element.is_displayed()


    def GetProgressBarText(self) -> str:
        element = SeleniumUtils.FindElement(
            by = By.ID,
            locator = ProgressBar_Locator)
        return element.text
