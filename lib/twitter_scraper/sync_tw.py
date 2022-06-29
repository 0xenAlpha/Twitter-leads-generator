import random,traceback
import requests,json
import time
from datetime import datetime
from django.conf import settings
from lib.common.logs import Log
from lib.common.sel import click_xpath, create_driver, fill_xpath, save_screenshot, scroll_down_and_wait_for_ele, wait_for_element_xpath
from lib.common import settings
from lib.common.db import add_to_table, connect_db_dict, record_exists, select_from_db, update_query_by_template
from lib.common.utils import load_config, log_a, log_w, workspace_path_join,fetch_json
from lib.common import xpath

random.randint(5, 10)
class Sync:

	def __init__(self) -> None:        
		self.cnx,self.cursor = connect_db_dict(load_config(settings.DATABASE_CONFIG_FILEPATH))        
		self.skipped_followers_file = workspace_path_join(settings.Output_strings.skipped_followers_file)        
		self.fetching_followers_data_error_file = workspace_path_join(settings.Output_strings.fetching_followers_error_file)        
		self.wasnt_added_followers_file = workspace_path_join(settings.Output_strings.wasnt_added_follwers_file)    


	def scrape_followers(self,account_to_scrape:str):      
		"""
		Scrape username followers

		:param account_to_scrape: required - username of the target account		

		"""                        
		self.account_to_scrape = account_to_scrape
		self.get_account("scrape")        
		self.login()        
		self.get_headers()        
		self.get_followers_from_twitter()

	def send_messages(self):
		"""
		Send Message to follower		
		""" 
		print("Sending messages")
		while True:
			try:
				self.get_account("message")    
				self.get_follower("message") 
				self.get_message("message")       
				self.message_follower()                
				self.delay()
			except:
				self.kill_driver()
				print("Can't send the message Error was %s"%traceback.format_exc())
			input("Next?")
			
	def kill_driver(self):
		"""
		Kill webdriver instance	
		"""
		try:
			self.driver.close()
			self.driver.quit()
		except:pass 
	
	def comment_on_profiles(self):
		"""
		Comment on last or pinned tweets
		"""		
		while True:
			try:
				self.get_account("comment")    
				self.get_follower("comment") 
				self.get_message("comment")       
				self.comment_on_profile()                
				self.delay()
			except:
				self.kill_driver()
				print("Can't comment Error was %s"%traceback.format_exc())
			input("Next?")
			

	def comment_on_profile(self):
		"""
		Comment on last or pinned tweets		
		"""
		update_query_by_template(self.cnx,self.cursor,settings.Db.followers_table,{"last_try_to_comment_timestamp":datetime.now()},"id=%s"%self.follower_data["id"])
		self.login()
		self.driver.get("https://twitter.com/i/user/%s/"%self.follower_user_id)
		if scroll_down_and_wait_for_ele(self.driver,xpath.Twitter.reply_btn,3):
			click_xpath(self.driver,xpath.Twitter.reply_btn)
			fill_xpath(self.driver,xpath.Twitter.reply_input,self.message,3)
			click_xpath(self.driver,xpath.Twitter.reply_btn_final)
			time.sleep(3)
			update_query_by_template(self.cnx,self.cursor,settings.Db.followers_table,{"last_try_to_comment_timestamp":datetime.now(),"commented":True},"id=%s"%self.follower_data["id"])
		else:
			update_query_by_template(self.cnx,self.cursor,settings.Db.followers_table,{"last_try_to_comment_timestamp":datetime.now(),"commented":False,"log":"No tweets to comment to"},"id=%s"%self.follower_data["id"])        

	def delay(self):
		"""
		Kill last driver and wait for a random amount of time
		"""
		self.kill_driver()       
		nbr_seconds = random.randint(5, 10)
		print("Sleeping for %s seconds"%nbr_seconds)
		time.sleep(nbr_seconds)

	def get_message(self,interaction):
		"""
		Fetch messages from conversation (static for MVP)
		"""
		if interaction=="message":
			self.message= "Hey there"
		elif interaction == "comment":
			self.message= "Nice!"
		else:
			Log().log_to_db(module_name="get_message",log_body="{interaction} isn't handled".format(interaction=interaction))

	def message_follower(self):
		"""
		Send Message to followers		
		"""
		self.login()
		update_query_by_template(self.cnx,self.cursor,settings.Db.followers_table,{"last_try_to_message_timestamp":datetime.now()},"id=%s"%self.follower_data["id"])
		self.driver.get("https://twitter.com/i/user/%s/"%self.follower_user_id)
		if wait_for_element_xpath(self.driver,xpath.Twitter.message_btn_profile,3):
			click_xpath(self.driver,xpath.Twitter.message_btn_profile)
			fill_xpath(self.driver,xpath.Twitter.message_input,self.message,8)
			click_xpath(self.driver,xpath.Twitter.message_btn)   
			time.sleep(3)  
			update_query_by_template(self.cnx,self.cursor,settings.Db.followers_table,{"last_try_to_message_timestamp":datetime.now(),"messaged":True},"id=%s"%self.follower_data["id"])
		else:
			update_query_by_template(self.cnx,self.cursor,settings.Db.followers_table,{"last_try_to_message_timestamp":datetime.now(),"messaged":False,"log":"messaging deactivated"},"id=%s"%self.follower_data["id"])         

	def get_account(self,interaction):
		"""
		Retrieve the least used account for sending requests, messages and comments
		"""
		if interaction=="scrape":
			order_column = "last_time_used_to_scrape"
		elif interaction=="message":
			order_column = "last_time_used_to_message"
		elif interaction=="comment":
			order_column = "last_time_used_to_comment"
		else:            
			Log().log_to_db(module_name="get_account",log_body="{interaction} isn't handled".format(interaction=interaction))
			exit("{interaction} isn't handled".format(interaction=interaction))
		self.account_data = select_from_db(self.cursor,settings.Db.accounts_table,["username","password","proxy_used"],None,"%s ASC"%order_column,1)[0]
		self.account_username = self.account_data["username"]
		update_query_by_template(self.cnx,self.cursor,settings.Db.accounts_table,{order_column:datetime.now()},"username='%s'"%self.account_data["username"])
		print("Account Selected :",self.account_username)

	def get_follower(self,interaction):    
		"""
		Get the tageted account followers
		"""    
		if interaction=="message":
			order_column = "last_try_to_message_timestamp"
			check_if_done_column = "messaged"
		elif interaction=="comment":
			order_column = "last_try_to_comment_timestamp"
			check_if_done_column = "commented"
		else:            
			Log().log_to_db(module_name="get_account",log_body="{interaction} isn't handled".format(interaction=interaction))
			exit("{interaction} isn't handled".format(interaction=interaction))
		self.follower_data = select_from_db(self.cursor,settings.Db.followers_table,["id","name","user_id"],"{check_if_done_column} IS NULL".format(check_if_done_column=check_if_done_column),"%s ASC"%order_column,1)[0]
		self.follower_user_id = self.follower_data["user_id"]

		 
	def get_proxy(self):
		"""
		Select the least used proxy from database
		"""
		return select_from_db(self.cursor,settings.Db.proxies_table,"*","ip='%s'"%self.account_data["proxy_used"],None,1)[0]

	# Implement login here.
	def login(self):
		"""
		Login to twitter
		"""
		# Create driver
		proxy_data = self.get_proxy()
		self.driver = create_driver(settings.Selenium.driver_binary_file,profile_name=self.account_username,profile_path=settings.Selenium.profile_path,proxy_data=proxy_data) 
		input()
		# self.driver.get("https://ifconfig.co/") 
		# input()
		# Check if already logged in
		self.driver.get("https://twitter.com")  
		if not self.check_if_logged_in():

			# Login
			self.driver.get("https://twitter.com/i/flow/login")
			fill_xpath(self.driver,xpath.Twitter.username_input,self.account_username,5)
			click_xpath(self.driver,xpath.Twitter.next_btn)
			fill_xpath(self.driver,xpath.Twitter.password_input,self.account_data["password"],10)
			click_xpath(self.driver,xpath.Twitter.login_btn)

			# Log error and screenshot if login was unsuccessful
			if not self.check_if_logged_in():
				screenshot_path = "output/screenshots/cant_login_{epoch}".format(epoch=time.time())
				save_screenshot(self.driver,workspace_path_join(screenshot_path))
				Log().log_to_db("Login","{username} Can't Login, Screenshot saved at {screenshot_path}".format(username=self.account_username,screenshot_path=screenshot_path))


	def get_headers(self):
		"""
		Generate the inital headers using webdriver, then use it on the requests library
		"""
		# Access Profile Followers
		self.driver.get("https://twitter.com/{account_to_scrape}/followers".format(account_to_scrape=self.account_to_scrape))

		# Wait for followers to load
		wait_for_element_xpath(self.driver,xpath.Twitter.followers_flow,20)
		
		# Extract followers headers and token
		self.followers_request_headers= None
		for request in self.driver.requests:
			if "Followers" in request.url:                
				self.followers_request=request
				self.followers_request_headers= dict(request.headers)
				self.followeres_request_token= request.url.split("/")[6]                
		
		# Kill driver
		self.driver.quit()

		# Log errors 
		if not self.followers_request_headers:
			Log().log_to_db(module_name="get_headers",log_body="{username} Can't get followers_request_headers for profile {account_to_scrape}".format(username=self.account_username,account_to_scrape=self.account_to_scrape))
	
	# Implement check If logged in here
	def check_if_logged_in(self):
		"""
		Check if login was successful 
		"""
		return wait_for_element_xpath(self.driver,xpath.Twitter.profile_span,8)
	 
	def get_followers_from_twitter(self):
		"""
		Fetch the targeted account followers
		"""
		self.twitter_scraper_session = requests.Session()
		self.twitter_scraper_session.headers.update(self.followers_request_headers)
		self.firstPage = True
		self.lastPage = False
		self.lastCursorValue = ""
		self.followers = []

		# get followers by cursor pagination.
		while(not self.lastPage):
			try:                
				self.payload = {
					"variables":'{"userId":"1443283482655039497","count":20,"includePromotedContent":false,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"__fs_dont_mention_me_view_api_enabled":true,"__fs_interactive_text_enabled":true,"__fs_responsive_web_uc_gql_enabled":false}'
				}                
				self.update_payload()
				json_data = fetch_json(self.twitter_scraper_session,settings.Api_consts.fetching_followers_url.format(token=self.followeres_request_token),self.payload,headers = None, proxy = None)
				log_w("json_data",str(json_data))
				instructions = json_data["data"]["user"]["result"]["timeline"]["timeline"]["instructions"]
				entries = None
				for ins in instructions:
					if(ins["type"] == "TimelineAddEntries"):
						entries = ins["entries"]

				for entry in entries:
					entryContent = entry["content"]
					if(entryContent["entryType"] == "TimelineTimelineItem"):
						result = entryContent["itemContent"]["user_results"]["result"]
						user_id = result["rest_id"]        
						name = result["legacy"]["name"]
						follower = {
							"user_id":user_id,
							"name":name.encode('ascii', 'ignore'),
						}
						self.followers.append(follower)
						print(follower)                        
						self.lastPage = True

						# save follower to db.            
						self.save_follower_to_db(follower)

					elif(entryContent["entryType"] == "TimelineTimelineCursor" and entryContent["cursorType"] == "Bottom"):
						cursor_value = entryContent["value"]
						self.lastCursorValue = cursor_value
						self.lastPage = False

				self.firstPage = False



			except:
				print(traceback.format_exc())

		

	
	
	def save_follower_to_db(self,follower):
		"""
		Save the targeted account followers to database
		"""
		try:
			if record_exists(self.cursor,settings.Db.followers_table,"user_id",follower["user_id"]):
			   log_a(self.skipped_followers_file,str(follower)+"\n") 
			else:
				add_to_table(self.cnx,self.cursor,settings.Db.followers_table,follower)
				return True
		except:
			log_a(self.wasnt_added_followers_file,str(follower)+"\n")
			return False


	def update_payload(self):
		"""
		Update cursor variable to retrieve json response from API
		"""
		if not self.firstPage:                    
			payload_variable_json = self.payload["variables"]
			payload_variable_dict = json.loads(payload_variable_json)
			payload_variable_dict.update({"cursor":self.lastCursorValue})
			self.payload["variables"]=json.dumps(payload_variable_dict)            
			
