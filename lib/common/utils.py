import os,json
from pathlib import Path
import os,argparse


def workspace_path_join(local_path:str) -> str:  
	"""
	Join project root folder path with local path

	:param local_path: required
	:type local_path: str	
		
	"""  
	return os.path.join(Path(__file__).parents[2],local_path)        

def log_a(log_file:str,data:str) -> None:
	"""
	Log a new line to a log file

	:param log_file: required - 
	:type log_file: str

	:param data: required	
	:type data: str
		
	""" 	
	with open(log_file,"a",encoding="utf8") as f:
		f.write(data)

def log_w(log_file:str,data:str) -> None:
	"""
	Empty log file and write new log

	:param log_file: required - 
	:type log_file: str

	:param data: required	
	:type data: str
		
	""" 	
	with open(log_file,"w",encoding="utf8") as f:
		f.write(data)

def save_page(filepath:str,source:str) -> None:
	"""
	Save page source into local file

	:param filepath: required - 
	:type filepath: str

	:param source: required	
	:type source: str
		
	""" 	
	while True:		
		if filepath[-1] in ["*","?","/","\\","|",":","<",">"," "]:
			filename=filepath[:-1]			
		else:
			break
	with open("%s.htm"%filepath,"w",encoding="utf-8") as f:
		f.write(str(source))		 

	
def list_from_file(filepath:str) -> list:
	"""
	Generate a list out of file lines

	:param filepath: required - 
	:type filename: str

	:param source: required	
	:type source: str
		
	""" 	
	try:
		with open(filepath) as f:    	
			return [x.strip() for x in f.readlines()]			
	except:
		print("file not found : %s"%filepath)
		return []	

def load_config(config_file_path):
	"""
	Load config file

	:param config_file_path: required - 
	:type filename: str

	"""		
	with open(config_file_path) as config_file:
		return json.load(config_file)

def fetch_json(session,url:str,request_body:dict,headers:dict,proxy:dict):	
	"""
	Fetch API json responses 

	:param session: required - Requests session to use
	:type session: requests.Session

	:param url: required - API endpoit
	:type url: str

	:param request_body: required - Request payload
	:type request_body: dict

	:param headers: required - Request headers
	:type headers: dict

	:param proxy: required - Proxy to use
	:type proxy: dict
			
	"""		
	r = session.get(url,params=request_body,headers= headers,proxies=proxy,verify=False)						
	try:
		json_data= json.loads(r.text)
	except:
		save_page(workspace_path_join("output/invalid_json"),r.text)
		raise( Exception("Can't Format JSON check logs.."))
	return json_data		


def get_args() -> dict:
	"""
	Get running params
	"""

	parser = argparse.ArgumentParser(description='Crypto Lead Generator')
	parser.add_argument('-t','--task', help='',required=True)
	parser.add_argument('-a','--account_to_scrape', help='',required=False)
	args = parser.parse_args()
	print("\n## Run  params ## ","\n\n")	
	params={}
	for arg in vars(args):
		print(arg, " = ", getattr(args, arg),"\n")
		params[arg]=getattr(args, arg)
	return params	