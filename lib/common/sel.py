import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import seleniumwire.undetected_chromedriver as webdriver


def create_driver(driver_path:str,headless:bool=False,prefs:dict=None,profile_path:str=None,profile_name:str=None,proxy_data:dict=None):
	"""
	Create a Webdriver instance

	:param driver_path: required - Webdriver binary file path
	
	:param headless: optional - headless mode
	
	:param prefs: optional - Browser options
	
	:param profile_path: optional - Your profile path
	
	:param profile_name: optional - Your profile name
	
	:param proxy_data: optional - Proxy to use
	
	""" 	
	chrome_options = webdriver.ChromeOptions()		
	if headless:
		chrome_options.add_argument('--headless')		
	if profile_name:
		chrome_options.add_argument('--profile-directory={profile_name}'.format(profile_name=profile_name))
	if prefs:
		chrome_options.add_experimental_option("prefs",prefs)
	if profile_path:
		chrome_options.add_argument("--user-data-dir={profile_path}".format(profile_path=profile_path))
	if proxy_data:		
		options = {
		'proxy': {
			'https': 'https://%s:%s@%s:%s'%(proxy_data["username"],proxy_data["password"],proxy_data["ip"],proxy_data["port"]),
				}	
			}	
	return webdriver.Chrome(executable_path=driver_path,options=chrome_options,use_subprocess=True,seleniumwire_options=options)


def scroll_to_bottom(driver):
	"""
	Scroll to bottom of the page

	:param driver: required - Webdriver instance	
	
	""" 
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight-1000)")		
	print("scroll_to_bottom done")    

def scroll_to_bottom_minus(driver):
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight-2000)")		
	print("scroll_to_bottom done")    	
	# print("scroll by","1/%s"%y,"of page")    


def wait_for_element_xpath(driver,xpath:str,set_timeout:int):
	"""
	Wait for element to be present on page

	:param driver: required - Webdriver instance	
	
	:param xpath: required - Xpath query
	
	:param set_timeout: required - How long to wait for the element
	
	""" 	
	timeout=0
	print("Waiting for %s..."%xpath)	
	if not xpath:
		return False
	if not xpath.endswith("]"):
		if xpath.endswith("text()") or "@" in xpath.split("/")[-1]:
			xpath = "/".join(xpath.split("/")[:-1])
			if xpath.endswith("//"):
				xpath = xpath[:-2]
			elif xpath.endswith("/"):
				xpath = xpath[:-1]	
	while timeout!=set_timeout:
		try:			
			return driver.find_element_by_xpath(xpath)
		except:			
			time.sleep(1)
			timeout+=1				
	print("time out for element:",xpath)
	return False    
  

def click_xpath(driver,xpath):
	"""
	Click web element by xpath query

	:param driver: required - Webdriver instance	

	:param xpath: required - Xpath query
	
	""" 
	ele = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,xpath)))
	if ele:
		ele.click()
	

def fill_xpath(driver,xpath:str,text:str,wait_for:int):	
	"""
	Input text to web element

	:param driver: required - Webdriver instance	

	:param xpath: required - Xpath query
	
	:param text: required - Text to input
	
	:param wait_for: required - How many seconds to wait for the element to be present
	
	""" 	
	WebDriverWait(driver, wait_for).until(EC.element_to_be_clickable((By.XPATH,xpath)))
	element = driver.find_element_by_xpath(xpath)
	element.send_keys(text)		

def save_screenshot(driver,filepath:str):
	"""
	Take a screenshot of current tab and save it locally

	:param driver: required - Webdriver instance	

	:param filepath: required - 
	
	""" 	
	driver.save_screenshot("%s.png"%filepath)
	
def scroll_down_and_wait_for_ele(driver,xpath:str,scroll_times:int):
	"""
	Scroll down the page looking for the element to be present

	:param driver: required - Webdriver instance	

	:param xpath: required - Xpath query
	
	:param scroll_times: required - how many times to scroll down
	
	"""	
	if wait_for_element_xpath(driver,xpath,1):return True
	for _ in range(scroll_times):
		scroll_to_bottom(driver)
		if wait_for_element_xpath(driver,xpath,3):return True
	return False