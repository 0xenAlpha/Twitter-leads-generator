import traceback
import mysql.connector
from pymysql.converters import escape_string 

def connect_db_dict(config:dict):
	"""
	Connect to DB

	params:

	config: db configuration (dict) | example:

	{
		"user": "db_username",
		"password": "db_password",
		"host": "db_host",
		"database": "db_name",
		"raise_on_warnings": true,
		"auth_plugin":"mysql_native_password"
	}
	"""	
	cnx = mysql.connector.connect(**config)
	return cnx,cnx.cursor(dictionary=True)
	
def query_response(cursor,query:str):
	"""
	Fetch Db query response 

	params:

	cursor: db cursor

	query: query to send (str)
	"""
	cursor.execute(query)
	return cursor.fetchall()	


def update_query(cnx,cursor,query:str):
	"""
	Update query with commit 

	params:

	cnx: Mysql connection

	cursor: Mysql cursor

	query: query to send (str)
	"""
	try:
		cursor.execute(query)
		cnx.commit()
	except:				
		print("Query Error :\n\n\n",query,"\n\n\n",traceback.format_exc())
		raise(Exception(traceback.format_exc()))

def update_query_by_template(cnx,cursor,table_name:str,data:dict,conditions:str):	
	"""
	Update table using data dict keys/values as columns names/values

	params:

	cnx: Mysql connection
	
	cursor: Mysql cursor
	
	table name: table to update (str)
	
	data: dictionary where keys, value pairs will be used as columns names, values to update (dict)	
	
	conditions: filters (str) | example: "column1 > 10 AND column2 < 50"
	"""
	try:		
		cursor.execute(_update_query_template(table_name,data,conditions), data)
		cnx.commit()
	except:				
		print("Query Error :\n\n\n", _update_query_template(table_name,data,conditions)%data ,"\n\n\n",traceback.format_exc())
		raise(Exception(traceback.format_exc()))


def add_to_table(cnx,cursor,table_name:str,data:dict):
	"""
	Add new row to table using data dict keys/values as columns names/values
	"""
	try:
		cursor.execute(_create_add_template(table_name,[column for column in data]), data)
		cnx.commit()		
		return cursor.lastrowid
	except:
		print("Query error:\n%s\n%s"%(_create_add_template(table_name,[column for column in data])%data,traceback.format_exc()))
		raise(Exception("Query Error"))
			  	
def record_exists(cursor,table:str,column:str,value): 
	"""
	Check if record exist in DB 

	params:

	cursor: Mysql cursor
	table: table to lookup (str)
	column: column to lookup (str)
	value: value to lookup 
	"""     	
	try:
		cursor.execute("SELECT * FROM %(table)s WHERE %(column)s = '%(value)s'"%{'table':table,'column':column,'value':escape_string(str(value))})
		r=cursor.fetchall()	
		return len(r)>0
	except:		
		raise(Exception(traceback.format_exc()))

			  	
def record_exists_return_primary_key_name(cursor,table_name:str,column:str,value,primary_key_name:str):  
	"""
	Check if record exist in DB and return his primary key value if record found

	params:

	cursor: Mysql cursor
	table name: table to lookup from (str)
	column: column to lookup (str)
	value: value to lookup 
	primary_key_name: primary key name of table
	"""      	
	try:
		cursor.execute("SELECT {primary_key_name} FROM %(table)s WHERE %(column)s = '%(value)s'"%{"primary_key_name":primary_key_name,'table':table_name,'column':column,'value':escape_string(str(value))})
		r=cursor.fetchall()	
		try:
			return r[0][primary_key_name]
		except:
			return False
	except:		
		raise(Exception(traceback.format_exc()))		


def select_from_db(cursor,table_name:str,columns:list,conditions:str,sort:str,limit:int):
	"""
	Select from Db

	params:

	cursor: Mysql cursor
	table name: table to select from (str)
	columns: columns to select (list)
	conditions: filters (str) | example: "column1 > 10 AND column2 < 50"
	sort: which column to order by and if DESC or ASC (str) | example: "column1 DESC"
	limit: how many records to get (int) 
	"""
	try:
		# print(select_query_template(table_name,columns,conditions,sort,limit))
		cursor.execute(_select_query_template(table_name,columns,conditions,sort,limit))
		return cursor.fetchall()	
	except:
		print("Query:\n%s\n%s"%(_select_query_template(table_name,columns,conditions,sort,limit),traceback.format_exc()))
		raise(Exception(traceback.format_exc()))


def _update_query_template(table_name:str,data:str,conditions:str):	
	"""
	templating for update_query_by_template
	"""
	columns_mapping_substrings=[]
	for column in [column for column in data]:
		columns_mapping_substrings.append("%s = %%(%s)s"%(column,column))
	columns_mapping = " %s"%", ".join(columns_mapping_substrings)	
	values_updates = []
	for key in data:
		values_updates.append('%s = "%s"'%(key,data[key]))
	values_updates = ", ".join(values_updates)	
	return "UPDATE `%s` set %s WHERE %s;"%(table_name,columns_mapping,conditions)


def _select_query_template(table_name:str,columns,conditions:str,sort:str,limit:int):	
	"""
	templating for select query
	"""
	query="SELECT %s FROM %s"%(", ".join(columns),table_name)
	if type(columns) is not list:
		if columns=="*":
			query = "SELECT * FROM %s"%(table_name)
		else:
			query="SELECT %s FROM %s"%(columns,table_name)
	else:
		query="SELECT %s FROM %s"%(", ".join(columns),table_name)
	if conditions is not None:
		if type(conditions) is not list:
			query="%s WHERE %s"%(query,conditions)
		else:
			query="%s WHERE %s"%(query," AND ".join(conditions))		
	if sort is not None:
		if type(sort) is not list:
			query="%s ORDER by %s"%(query,sort)
		else:
			query="%s ORDER by %s"%(query,", ".join(sort))	
	if limit is not None:		
			query="%s LIMIT %s"%(query,limit)
	# print(query)
	return query	


def _create_add_template(table_name:str,columns_list:list):
	"""
	templating for add_to_table
	"""
	columns="(%s)"%", ".join(columns_list)
	columns_mapping_substrings=[]
	for column in columns_list:
		columns_mapping_substrings.append("%%(%s)s"%column)
	columns_mapping = "VALUES (%s)"%", ".join(columns_mapping_substrings)
	return "INSERT INTO %s %s %s"%(table_name,columns,columns_mapping)	