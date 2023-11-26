from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointment import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import re
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None

def is_strong_password(password):
    # Password strength criteria
    length_check = len(password) >= 8
    uppercase_check = any(c.isupper() for c in password)
    lowercase_check = any(c.islower() for c in password)
    digit_check = any(c.isdigit() for c in password)
    special_char_check = any(c in "!@#?" for c in password)

    # Check if all criteria are met
    if (
        length_check
        and uppercase_check
        and lowercase_check
        and digit_check
        and special_char_check
    ):
        print("Password meets all criteria")
        return True, ""  # Password meets all criteria
    else:
        print("Password is not strong enough.")
        message = "Password must have:\n"
        if not length_check:
            message += "- at least 8 characters\n"
        if not uppercase_check:
            message += "- at least one uppercase letter\n"
        if not lowercase_check:
            message += "- at least one lowercase letter\n"
        if not digit_check:
            message += "- at least one digit\n"
        if not special_char_check:
            message += "- at least one special character from '!', '@', '#', '?'\n"
        print (message)
        return False


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Invalid input. Correct format: create_patient <username> <password>")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try different username!")
        return
    
    # check 3: Password strength check
    if not is_strong_password(password):
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("User Created: ", username)
    print(f"{'-'*20}")


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Invalid input. Correct format: create_caregiver <username> <password>")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return
    
    # check 3: Password strength check
    if not is_strong_password(password):
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("User Created: ", username)
    print(f"{'-'*20}")

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patient WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient, current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, please logout first.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed due to invalid input, correct format: [operation_name] [username] [password].")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver, current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, please logout first.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed due to invalid input, correct format: [operation_name] [username] [password].")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    # search_caregiver_schedule <date>
    # check 1: if someone's already logged-in
    global current_caregiver, current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    
    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Invalid input, correct format: upload_availability <mm-dd-yyyy>")
        return

    date = tokens[1]

    # Check for the correct date format (mm-dd-yyyy)
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', date):
        print("Invalid date format. Please use mm-dd-yyyy format.")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    
    # Query to fetch available caregivers for the given date
    sql_query_caregivers = """
        SELECT Username 
        FROM Availabilities 
        WHERE CONVERT(VARCHAR(10), Time, 110) = %s 
        ORDER BY Username
    """

    # Query to fetch available doses for each vaccine
    sql_query_vaccines = """
        SELECT Name, Doses 
        FROM Vaccines
    """

    try:
        cursor = conn.cursor(as_dict=True)

        # Execute query to get available caregivers
        cursor.execute(sql_query_caregivers, date)
        caregiver_rows = cursor.fetchall()

        # Execute query to get available doses for each vaccine
        cursor.execute(sql_query_vaccines)
        vaccine_rows = cursor.fetchall()

        if len(caregiver_rows) == 0:
            print(f"No available caregiver on selected date: {date}")
            print("Please choose another day.")
            return

        # Create a dictionary to store available doses for each vaccine
        vaccine_doses = {row['Name']: row['Doses'] for row in vaccine_rows}

        for caregiver in caregiver_rows:
            username = caregiver['Username']
            available_vaccines_info = [
                f"{vaccine['Name']}: {vaccine_doses.get(vaccine['Name'], 0)}"
                for vaccine in vaccine_rows
            ]
            print(f"Caregiver: {username} | {' '.join(available_vaccines_info)}")

    except pymssql.Error as e:
        print("Database error:", e)
        print("Please try again!")
        return
    except Exception as e:
        print("Error occurred:", e)
        print("Please try again!")
        return
    finally:
        cm.close_connection()
        return 


    
def reserve(tokens):
    # reserve <date> <vaccine>
    #  check 1: check if the current logged-in user is a patient
    global current_patient, current_caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    elif current_patient is None:
        print("Please login as a patient first!")
        return
    
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Invalid input, correct format: reserve <date> <vaccine>")
        return

    date = tokens[1]
    vaccine = tokens[2]

    # check 3: correct date format (mm-dd-yyyy)
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', date):
        print("Invalid date format. Please use mm-dd-yyyy format.")
        return
    
    # Query to fetch first available caregiver for the given date by alphabetical order 
    sql_query_caregivers = """
        SELECT TOP 1 Username 
        FROM Availabilities 
        WHERE CONVERT(VARCHAR(10), Time, 110) = %s 
        ORDER BY Username
    """

    # Query to fetch available doses for specified vaccine
    sql_query_vaccines = """
        SELECT * 
        FROM Vaccines
        WHERE Name = %s
    """

    try: 
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        # Execute query to get available caregiver
        cursor.execute(sql_query_caregivers, str(date))
        caregiver_info = cursor.fetchall()

        # Execute query to get available doses for each vaccine
        cursor.execute(sql_query_vaccines, vaccine)
        vaccine_info = cursor.fetchall()

        # Check if the required vaccine is available
        if len(vaccine_info) == 0:
            print("Not enough available doses!")
            return
        
        # Check if there is available caregiver on selected date
        if len(caregiver_info) == 0:
            print(f"No Caregiver is available on selected date: {date}")
            print("Please choose another day.")
            return
        
        # Create a dictionary to store available doses for vaccine
        vaccine_name = vaccine_info[0]['Name']
        vaccine_doses = vaccine_info[0]['Doses']

        # Select the caregiver in alphabatical order
        selected_caregiver = caregiver_info[0]['Username']
        
        # Perform reserveation
        date_tokens = date.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
        d = datetime.datetime(year, month, day)
        appointment = Appointment(current_patient.username, selected_caregiver, vaccine_name, d)
        appointment._save_to_db()

        # Remove Availability
        delete_availability = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"
        cursor.execute(delete_availability, (d, selected_caregiver))
        conn.commit()

        # Reduce doses
        vaccine_obj = Vaccine(vaccine_name, vaccine_doses).get()
        vaccine_obj.decrease_available_doses(1)

        # Print the reservation details if successful
        print(f"Success! Appointment ID: {appointment.appointment_id}, Caregiver username: {selected_caregiver}")
    except pymssql.Error as e:
        print("Database error:", e)
    except Exception as e:
        print("Error occurred:", e)
    finally:
        cm.close_connection()
        return 


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Invalid input, correct format: upload_availability <mm-dd-yyyy>")
        return

    date = tokens[1]

    # Check for the correct date format (mm-dd-yyyy)
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', date):
        print("Invalid date format. Please use mm-dd-yyyy format.")
        return

    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date! (mm-dd-yyyy)")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    # show_appointments
    #  check 1: check if the current logged-in user is a patient
    global current_patient, current_caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        # Define SQL query for patients
        if current_patient is not None:
            appointment_query = """
                SELECT *
                FROM Appointment
                WHERE PatientName = %s
                ORDER BY Appointment_id;
            """
            cursor.execute(appointment_query, current_patient.username)
        # Define SQL query for caregivers
        else:
            appointment_query = """
                SELECT *
                FROM Appointment
                WHERE CareName = %s
                ORDER BY Appointment_id
            """
            cursor.execute(appointment_query, current_caregiver.username)
        appointments = cursor.fetchall()

        # Check if the there's appointment for this user
        if len(appointments) == 0: 
            print("No appointments found.")
            return 

        for appointment in appointments:
            appointment_id = appointment['Appointment_id']
            vaccine_name = appointment['VaccineName']
            appointment_date = appointment['Time']

            if current_patient is None: # Login user is caregiver
                patient_name = appointment['PatientName']
                print(f"- Appointment ID: {appointment_id}, Vaccine Name: {vaccine_name}, Date: {appointment_date}, Patient Name: {patient_name}")
            else: 
                caregiver_name = appointment['CareName']
                print(f"- Appointment ID: {appointment_id}, Vaccine Name: {vaccine_name}, Date: {appointment_date}, Caregiver Name: {caregiver_name}")
    except pymssql.Error as e:
        print("Error occurred while fetching appointments:", e)
    except Exception as e:
        print("Error occurred:", e)
    finally:
        cm.close_connection()
        return

def logout(tokens):
    try: 
        global current_caregiver, current_patient
        if current_caregiver is None and current_patient is None:
            print("Please login first.")
            return
        else:
            current_caregiver = None
            current_patient = None
            print("Successfully logged out!")
            return
    except: 
        print( "Please try again!")
        return


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1) -> Done
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1) -> Done
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>  (mm-dd-yyyy)")  # // TODO: implement search_caregiver_schedule (Part 2) -> Done
        print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2) -> Done
        print("> upload_availability <date> (mm-dd-yyyy)")
        print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  # // TODO: implement show_appointments (Part 2) -> Done
        print("> logout")  # // TODO: implement logout (Part 2) -> Done
        print("> Quit")
        print()

        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.strip()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
