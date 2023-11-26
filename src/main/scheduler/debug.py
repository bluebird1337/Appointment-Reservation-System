from model.Appointment import Appointment
import datetime


dete = "05-28-2000"

date_tokens = dete.split("-")
month = int(date_tokens[0])
day = int(date_tokens[1])
year = int(date_tokens[2])
d = datetime.datetime(year, month, day)

username = "aa"
caregiver = "test1"
vaccine_name = "AZ"

appointment = Appointment(username, caregiver, vaccine_name, d)
appointment._save_to_db()
print(appointment)
