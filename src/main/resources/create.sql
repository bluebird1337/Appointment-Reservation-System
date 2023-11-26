CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Patient (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointment(
    Appointment_id varchar(255),
    CareName varchar(255) REFERENCES Caregivers(Username),
    PatientName varchar(255) REFERENCES Patient(Username),
    VaccineName varchar(255) REFERENCES Vaccines(Name),
    Time date,
    PRIMARY KEY(Appointment_id)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);