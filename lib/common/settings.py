DATABASE_CONFIG_FILEPATH = "/etc/twitter_bot/db_config.json"
PROXY_CONFIG_FILEPATH = "/etc/twitter_bot/proxy_config.json"


class Output_strings:
	twitter_cookies_file = "output/twitter_cookies.txt"
	fetching_followers_error_file = "output/fetching_followers_data_error.txt"
	wasnt_added_follwers_file = "output/wasnt_added_followers.txt"
	skipped_followers_file = "output/skipped_followers.txt"


class Api_consts:
	fetching_followers_url = "https://twitter.com/i/api/graphql/{token}/Followers"


class Twitter:
	username = ""
	password = ""
	messaging_link = "https://twitter.com/messages/{follower_id}-{account_id}"	


class Db:	
	proxies_table = "proxies"
	accounts_table = "accounts"
	followers_table="followers"	
	logs_table = "logs"



class Selenium:	
	driver_binary_file = "/root/chromedriver"
	profile_path = "/root/.config/chromium/"    
	default_profile_name = "Default"
	plugins_profile = "/root/.config/chromium/Profile 1"