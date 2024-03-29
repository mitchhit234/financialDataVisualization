#Database creation, requires the use of the export.csv file
#in the format provided by Commerce Bank
import sqlite3
from sqlite3 import Error 
from pathlib import Path
import traceback


#Default filenames, change as needed
#Change db_update as well
ABSOLUTE = str(Path(__file__).parents[1])
RESOURCES = ABSOLUTE + '/resources/'
SQL = ABSOLUTE + '/sql_scripts/'
DB_NAME = RESOURCES + "transaction.db"
TABLE_NAME = "TRANSACTIONS"
TRANSACTION_SCRIPT = SQL + "transaction_creation.sql"
META_SCRIPT = SQL + "meta_creation.sql"
IMPORT_FILE = RESOURCES + "export.csv"


#Will create a database with the desired name
#and return a cursor object to that database
#If the database already exists, it will 
#just return the cursor object
def create_database(desired_name):
  try: 
    conn = sqlite3.connect(desired_name)
    return conn
  except Error as e:
    traceback.print_exc()

#Creates a table as outlined
#in the corresponding sql file
def create_table(cur,filename):
  with open(filename, 'r') as f:
    query = f.read()
  try:
    cur.execute(query)
  except Error as e:
    traceback.print_exc()


#Insert each row from our CSV file into our database
#Will output error messages for duplicate rows
def insert_statement_data(cur,filename,table_name):
  current_num = 1

  #Make sure table is empty. comment out this line if you wish to append data
  #from a statement to another database with data, must not have any overlapping entries
  #or else they will be treated as 2 seperate transactions
  #all transactions must take place after the ones in the database
  cur.execute("DELETE FROM " + table_name)

  #Uncomment these next 3 lines if above line is commented out
  # cur.execute("SELECT MAX(num) FROM " + table_name)
  # current_num = cur.fetchone()
  # current_num = current_num[0]

  with open(filename, 'r') as f:
    rows = f.readlines()
  rows = rows[1:]

  for i in rows:
    col = clean_row(i)   
    deb, cre = net([col[3],col[4]])
    values = [parse_date(col[0]), str(current_num), f'"{col[2]}"', deb, cre]
    statement = generate_insert_sql(table_name,values)
    try:
      cur.execute(statement)
    except Error as e:
      print("Error from sql statement " + statement)
      traceback.print_exc()
    
    current_num += 1


#Take the table name and values to be inserted 
#Values list must be in the same order as 
#defined by the table's column names
def generate_insert_sql(table_name, values):
  statement = "INSERT INTO " + table_name + " VALUES("
  for i in values:
    statement += i + ","
  return statement[:-1] + ')'
    
#Cleaning and parsing the CSV file into columns
def clean_row(st):
  st = st.replace('\n','')
  st = st.replace('"','')
  st = st.split(',')
  return st

#Parse the date format from the CSV statement
#into the format used by sqlite's DATE variable
def parse_date(st):
  p = st.split('/')
  for i in range(len(p)):
    if len(p[i]) == 1:
      p[i] = '0' + p[i]
  ret = p[2] + '-' + p[0] + '-' + p[1]
  return f'"{ret}"'


#Will return the debit or credit value,
#and null for whichever didn't exist
#(Each transaction is either a credit or debit)
def net(debit_credit):
  for i in range(len(debit_credit)):
    if len(debit_credit[i]) == 0:
      debit_credit[i] = 'NULL'
  
  return debit_credit[0], debit_credit[1]



if __name__ == "__main__":
  conn = create_database(DB_NAME)
  cursor = conn.cursor()
  create_table(cursor,TRANSACTION_SCRIPT)
  create_table(cursor,META_SCRIPT)
  insert_statement_data(cursor,IMPORT_FILE,TABLE_NAME) 
  conn.commit()
  conn.close()

