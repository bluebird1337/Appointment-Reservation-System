from ConnectionManager import ConnectionManager
import pymssql

# instantiating a connection manager class and cursor
cm = ConnectionManager()
conn = cm.create_connection()
cursor = conn.cursor()

print("Connect!")

username = 'vincent'
cm = ConnectionManager()
conn = cm.create_connection()

select_username = "SELECT * FROM Caregivers WHERE Username = %s"

cursor = conn.cursor(as_dict=True)
cursor.execute(select_username, username)
#  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
for row in cursor:
    print(row)



# # example 1: getting all names and available doses in the vaccine table
# get_all_vaccines = "SELECT Name, Doses FROM vaccines"
# try:
#     cursor.execute(get_all_vaccines)
#     for row in cursor:
#         print("name:" + str(row['Name']) + ", available_doses: " + str(row['Doses']))
# except pymssql.Error:     
#     print("Error occurred when getting details from Vaccines")

# # example 2: getting all records where the name matches “Pfizer”
# get_pfizer = "SELECT * FROM vaccine WHERE name = %s"
# try:
#     cursor.execute(get_pfizer, 'fizer')
#     for row in cursor:
#         print("name:" + str(row['Name']) + ", available_doses: " + str(row['Doses']))
# except pymssql.Error:     
#     print('Error occurred when getting pfizer from Vaccines')
