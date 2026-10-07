import sqlite3

## connect to sqllite
connection = sqlite3.connect('employee.db')

##create a cursor object to insert record, create table
cursor = connection.cursor()

## create the table
table_info="""
create table EMPLOYEE(
    ID integer primary key,
    NAME varchar(25) not null,
    DEPARTMENT varchar(25) not null,
    SALARY integer not null)
"""

cursor.execute(table_info)

## Insert some more records
cursor.execute('''insert into EMPLOYEE values(1,'John','IT',10000)''')
cursor.execute('''insert into EMPLOYEE values(2,'Alice','HR',12000)''')
cursor.execute('''insert into EMPLOYEE values(3,'Bob','Finance',11000)''')
cursor.execute('''insert into EMPLOYEE values(4,'Eve','IT',13000)''')
cursor.execute('''insert into EMPLOYEE values(5,'Charlie','Audit',9000)''')
cursor.execute('''insert into EMPLOYEE values(6,'David','QA',9500)''')

## display all the records
print("The insert records are")
data=cursor.execute('''select * from EMPLOYEE''')
for row in data:
    print(row)
    
## commit the changes in database
connection.commit()
## close the connection
connection.close()