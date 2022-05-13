import selenium
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
'''
from selenium.webdriver.chrome.options import Options
#from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.chrome.service import Service
'''

class element_has_css_class(object):
  """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """
  def __init__(self, locator, css_class):
    self.locator = locator
    self.css_class = css_class

  def __call__(self, driver):
    element = driver.find_element(*self.locator)   # Finding the referenced element
    if self.css_class in element.get_attribute("class"):
        return element
    else:
        return False


#@st.cache
def scrape_shows():

    print(selenium.__version__)

    #options = Options()
    #options.add_argument("--headless")
    ##options.add_argument("--disable-browser-side-navigation")
    #options.add_argument('--profile-directory=Default')

    #exec_path = 'data/operadriver'
    exec_path = 'data/geckodriver'
    #exec_path = 'data/chromedriver'
    #exec_path = '/home/edoardo/.wdm/drivers/operadriver/linux64/v.99.0.4844.51/operadriver_linux64/operadriver'
    #service = Service(executable_path=GeckoDriverManager().install())
    #service = Service(executable_path=OperaDriverManager().install())
    #driver = webdriver.Opera(executable_path=exec_path) #, options=options)
    #driver = webdriver.Firefox(executable_path=exec_path, firefox_options=options)
    driver = webdriver.Firefox(executable_path=exec_path) 
    #driver = webdriver.Chrome(executable_path=exec_path) #, chrome_options=options)
    #driver = webdriver.Firefox(service=service, options=options)
    #driver = webdriver.PhantomJS() #Firefox(service=service, options=options)
    
    #service = Service(executable_path=ChromeDriverManager().install())
    #driver = webdriver.Opera(service=service, options=options)
    print('Waiting...')
    url = 'https://www.nanowar.it/live/'
    driver.get(url)
    #WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='wt-cli-element medium cli-plugin-button wt-cli-accept-all-btn cookie_action_close_header cli_action_button']"))).click()
    wait = WebDriverWait(driver, 10)
    element = wait.until(element_has_css_class((By.ID, 'city'), "city"))
    print('Done. Beautiful soup.')
    soup = BeautifulSoup(driver.page_source, 'lxml')

    tables = soup.find_all('table')

    dfs = pd.read_html(str(tables))
    print(len(dfs))
    print(dfs[0].head())
    '''
    '''

def main():
    scrape_shows()

if __name__ == '__main__':

    main()

