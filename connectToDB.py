import mysql.connector
hostname = 'localhost'
username = 'root'
password = ''
database = 'backend_service_db'

def get_connection_to_DB():
  myConnection = mysql.connector.connect( host=hostname, user=username, passwd=password, db=database )
  return myConnection
