import os 
from selenium import webdriver

class Request:

    def __init__(self, base_url):
        # path = os.getcwd().split('/')[:-1]
        # _path = '/'.join(path)
        self._phantomjs_path_local = '/usr/bin/phantomjs'
        self._base_url = base_url
        # self._driver = webdriver.Chrome() # Chromium-driver
        self._driver = webdriver.PhantomJS(excutable_path=self._phantomjs_path_local)
       
        # self._driver.add_argument("--remote-debugging-port=9222")
        
        # self._driver = webdriver.PhantomJS(self._phantomjs_path)
    
    def fetch_data(self, forecast, area):
        url = self._base_url.format (forecast=forecast, area=area)
        self._driver.get(url)

        if self._driver.title == '404 Not Found':
            error_message = ('Could not din the area that you search for') 
            raise Exception(error_message)
        
        return self._driver.page_source
    
    