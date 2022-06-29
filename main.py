from lib.common.utils import get_args
from lib.twitter_scraper.sync_tw import Sync

"""
Get running params

account_to_scrape: the targetd account username

task: ("message" | "comment" ) either you want to message the followers or comment on their tweets (leave it empty if just you want to scrape followers)
""" 
args = get_args()

"""
Initiate the scraper
""" 
scraper = Sync()

"""
Run the script
""" 
if args["account_to_scrape"]:
	scraper.scrape_followers(args["account_to_scrape"])    
else:
	if args["task"]=="message":		
		scraper.send_messages()
	elif args["task"]=="comment":
		scraper.comment_on_profiles()
 
