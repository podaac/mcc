from selenium import webdriver

from config.globalvariables import GlobalVariables
from config.config import Config
from utils.enums import BrowserTypes

import os


# File wide variables
conf = Config
globalvars = GlobalVariables

class SeleniumSetup():
    
    def ConfigureSelenium(browser:BrowserTypes):
        print(f'\r\nSelenium version: {conf.Selenium_Version}')
        print(f'Browser Type: {browser.name}')
        if browser == BrowserTypes.CHROME:
            driver = ConfigureChromeDriver()
        elif browser == BrowserTypes.FIREFOX:
            driver = ConfigureFirefoxDriver()
        elif browser == BrowserTypes.IE:
            driver = ConfigureInternetExplorerDriver()
        elif browser == BrowserTypes.EDGE:
            driver = ConfigureEdgeDriver()
        elif browser == BrowserTypes.SAFARI:
            driver = ConfigureSafariDriver()
        elif browser == BrowserTypes.NOT_DEFINED:
            driver = None
        elif browser == None:
            driver = None
        else:
            raise NotImplementedError(f'Configuration for "{browser}" is not implemented!')
        if driver != None:
            # Global settings
            driver.set_window_size(1920,1080)
            driver.maximize_window()
            print(f'Set window size: 1920x1080')
            print(f'Set maximize window')
        return driver


def ConfigureChromeDriver():
    print(f'Configure Chromedriver...')
    options = webdriver.ChromeOptions()
    downloadDir_Real = os.path.realpath(globalvars.Default_Download_Dir)
    chromePrefs = {}
    chromePrefs["profile.default_content_settings.popups"] = 0
    print(f'Adding preference: default content settings / popups: {0}')
    
    # Set up download
    chromePrefs["download.default_directory"] = downloadDir_Real
    chromePrefs["download.prompt_for_download"] = False
    chromePrefs["download.directory_upgrade"] = True
    chromePrefs["safebrowsing_for_trusted_sources_enabled"] = False
    chromePrefs["safebrowsing.enabled"] = False
    print(f'Adding preference: default download directory: {downloadDir_Real}')
    print(f'Adding preference: prompt for download: {False}')
    print(f'Adding preference: download directory upgrade: {True}')
    print(f'Adding preference: safebrowsing enabled: {True}')
    print(f'Adding preference: safebrowsing for trusted sources enabled: {False}')
    print(f'Adding preferences to the option...')
    options.add_experimental_option("prefs", chromePrefs)

    options.add_argument("--headless=new")
    print(f'Set options: headless mode')
    options.add_argument("--no-sandbox")
    print(f'Set options: no-sandbox mode')
    options.add_argument('--disable-dev-shm-usage')
    print(f'Set options: disable dev-shm-usage')
    
    print(f'Adding options to the driver...')
    if conf.Selenium_Version >= '4.10.0':
        driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Chrome(chrome_options=options)
    return driver


def ConfigureFirefoxDriver():
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox('geckodriver', firefox_options=options)
    return driver


def ConfigureEdgeDriver():
    driver = webdriver.Edge('msedgedriver')
    return driver


def ConfigureInternetExplorerDriver():
    options = webdriver.IeOptions()
    driver = webdriver.Ie('IEDriverServer', ie_options=options)
    return driver


def ConfigureSafariDriver():
    driver = webdriver.Safari('safaridriver')
    return driver


def AddToPath(location:str):
    absPath = os.path.abspath(location)
    print(f'AbsPath: {absPath}')
    newPath = absPath
    if 'PATH' in os.environ:
        currentPath = os.environ.get('PATH')
        newPath = f'{currentPath}:{absPath}'
    os.environ['PATH'] = newPath
