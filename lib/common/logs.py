import traceback

from lib.common.utils import load_config
from .db import connect_db_dict,add_to_table, query_response, select_from_db
from .settings import DATABASE_CONFIG_FILEPATH, Db

class Log:
	
	def __init__(self,level:str=None) -> None:	
		self.cnx,self.cursor = connect_db_dict(load_config(DATABASE_CONFIG_FILEPATH))		
		self.level=level

	def log_to_db(self,module_name:str,log_body:str) -> None:
		"""
		Log to database

		:param module_name: required - Which module you want to log for
		:type module_name: str	
        
		:param log_body: required - Log body
		:type log_body: str	
        
		""" 
		try:
				return add_to_table(self.cnx,self.cursor,Db.logs_table,
				{
					"module_name":module_name,
					"log":log_body,
					"level":self.level,
				})
		except:
			print(traceback.format_exc())		