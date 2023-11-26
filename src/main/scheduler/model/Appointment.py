import hashlib  # For generating a hash-based ID
import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql

class Appointment:
    def __init__(self, patient, caregiver, vaccine, time):
        self.caregiver = caregiver
        self.patient = patient
        self.vaccine = vaccine
        self.time = time
        self.appointment_id = self._generate_appointment_id()

    def _generate_appointment_id(self):
        # Combine patient, caregiver, and vaccine information
        combined_info = f"{self.patient}-{self.caregiver}-{self.vaccine}"
        # Create a unique hash using hashlib
        appointment_id = hashlib.sha256(combined_info.encode()).hexdigest()[:6]  # Using SHA256 hash and taking the first 6 characters
        return appointment_id

    def _save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_appointment = "INSERT INTO Appointment VALUES (%s, %s, %s, %s, %s)"
        try:
            cursor.execute(add_appointment, (self.appointment_id, self.caregiver, self.patient, self.vaccine, self.time))
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    def __str__(self):
        return f"Appintment ID: {self.appointment_id}, Caregiver: {self.caregiver}, Patient: {self.patient}, Vaccine Name: {self.vaccine}, Time: {self.time}"
