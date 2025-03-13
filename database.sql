CREATE database nutritioncentre;

use nutritioncentre;

CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255) ,
    fname VARCHAR(255) 
);


INSERT INTO admin (email, password, fname) VALUES
('Miar2004@hotmail.com', '1210447', 'Miar'),
('Leena2003@hotmail.com', '1211460', 'Leena');

CREATE TABLE diet (
    DietID INT AUTO_INCREMENT PRIMARY KEY,
    DietType VARCHAR(50),
    CarbIntake DECIMAL(10, 2),
    ProteinIntake DECIMAL(10, 2),
    LiquidIntake DECIMAL(10, 2),
    CaloriesPerMeal INT
);

CREATE TABLE Patients (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    PhoneNumber VARCHAR(20) UNIQUE,
    Age INT,
    DietID INT,
    FOREIGN KEY (DietID) REFERENCES Diet(DietID)
) AUTO_INCREMENT=100;

CREATE TABLE membership (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    registration_date DATE,
    membership_fees DECIMAL(10, 2),
    payment_type VARCHAR(20),
    insurance_type VARCHAR(50),
    visits_per_month INT,
    membership_duration INT,
    PatientId INT UNIQUE,
    FOREIGN KEY (PatientId) REFERENCES patients(PatientId)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);
CREATE TABLE inBodyScan (
    InBodyID INT AUTO_INCREMENT PRIMARY KEY,
    ScanDate DATE,
    TotalSkeletalMuscleMass DECIMAL(10,2),
    TotalBodyFat DECIMAL(10,2),
    TotalBodyWater DECIMAL(10,2),
    WaistHipRatio DECIMAL(5,2),
    ObesityDegree VARCHAR(50),
    PatientID INT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON UPDATE CASCADE ON DELETE CASCADE
) AUTO_INCREMENT=1000;
-- Check-up Room Table
CREATE TABLE CheckupRoom (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    special_requirements VARCHAR(255),
    availability_status VARCHAR(50)
)AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS nutritionist (
    nutritionistID  INT AUTO_INCREMENT PRIMARY KEY,
    VisitsNumber INT,
    salary REAL,
    nutritionistPhoneNumber INT,
    nutritionistName VARCHAR(32),
    email VARCHAR(100), -- Assuming email addresses can be up to 100 characters
    shiftHours INT,
    absenceNum INT,
    room_duration INT,
	room_id INT  NOT NULL UNIQUE, -- Foreign key referencing the Check-up Room table
    FOREIGN KEY (room_id) REFERENCES CheckupRoom(room_id) ON DELETE CASCADE
)AUTO_INCREMENT=1000000;


CREATE TABLE MedicalTest (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    testType VARCHAR(50)  UNIQUE -- Type of test (CBC, TSH, Lipid Profile, Vitamins, etc.)

)AUTO_INCREMENT=1;


CREATE TABLE LaboratoryRoom (
    lab_id INT AUTO_INCREMENT PRIMARY KEY,
    test_id INT,
    availability_status VARCHAR(50),
	special_requirements VARCHAR(255), -- New attribute for special requirements
    FOREIGN KEY (test_id) REFERENCES MedicalTest(test_id)
)AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS lab_technician (
    technicianID INT AUTO_INCREMENT PRIMARY KEY,
    technicianName VARCHAR(100),
    technicianPhoneNumber VARCHAR(15)  UNIQUE,
    salary REAL,
	VisitsNumber INT,
    technicianEmail VARCHAR(100)  UNIQUE,
    shiftHours INT ,
    tools VARCHAR(255),
    lab_id INT  NOT NULL UNIQUE, -- Foreign key referencing the Check-up Room table
    FOREIGN KEY (lab_id) REFERENCES LaboratoryRoom(lab_id) ON DELETE CASCADE
   
)AUTO_INCREMENT=1000000;


CREATE TABLE PatientTakeMedicalTest (
    PatientID INT,
    test_id INT,
    date_taken DATE,
    next_date_to_take DATE,
    PRIMARY KEY (PatientID, test_id),
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES MedicalTest(test_id)
);


INSERT INTO diet (DietType, CarbIntake, ProteinIntake, LiquidIntake, CaloriesPerMeal) VALUES
('Low Carb', 50.00, 150.00, 2000.00, 600),
('High Protein', 100.00, 200.00, 2500.00, 700),
('Vegan', 300.00, 50.00, 1500.00, 500);

INSERT INTO Patients (FirstName, LastName, Email, PhoneNumber, Age, DietID) VALUES
('Ahmed', 'Halawa', 'ahmed.H@gmail.com', '123-456-7890', 30, 1),
('Fatima', 'Jabari', 'fatima.j@yahoo.com', '234-567-8901', 25, 2),
('Ali', 'AbuAbed', 'ali.alansari@gmail.com', '345-678-9012', 40, 3),
('Noura', 'Alsharif', 'noura.alsharif@hotmail.com', '456-789-0123', 35, 1),
('Mohamed', 'Ladaweh', 'mohamed.a@outlook.com', '567-890-1234', 28, 2);


INSERT INTO CheckupRoom (special_requirements, availability_status) VALUES
('Standard equipment', 'Available'),
('Standard equipment', 'Available'),
('Special needs equipment', 'Occupied'),
('Standard equipment', 'Under maintenance'),
('Special needs equipment', 'Available');

INSERT INTO medicaltest (test_id, testType) VALUES (1, 'Blood Test');
INSERT INTO medicaltest (test_id, testType) VALUES (2, 'X-Ray');
INSERT INTO medicaltest (test_id, testType) VALUES (3, 'MRI');
INSERT INTO medicaltest (test_id, testType) VALUES (4, 'Ultrasound');
INSERT INTO medicaltest (test_id, testType) VALUES (5, 'CT Scan');


INSERT INTO LaboratoryRoom ( test_id, availability_status, special_requirements)
VALUES 
( 1, 'Available', 'Requires specialized centrifuge equipment'),
( 2, 'Occupied', 'Quiet environment needed for thyroid function tests'),
( 3, 'Available', 'Need for advanced lipid testing equipment');

INSERT INTO lab_technician (technicianName, technicianPhoneNumber, salary, VisitsNumber, technicianEmail, shiftHours, tools, lab_id) 
VALUES 
('Ahmed Ali', '123456789', 5000.00, 10, 'ahmed.ali@gmail.com', 8, 'Microscope', 2),
('Fatima Hassan', '987654321', 5500.00, 8, 'fatima.hassan@yahoo.com', 8, 'Spectrophotometer', 3),
('Omar Khaled', '555888999', 6000.00, 12, 'omar.khaled@gmail.com', 8, 'Bunsen burner', 1);



INSERT INTO nutritionist (VisitsNumber, salary, nutritionistPhoneNumber, nutritionistName, email, shiftHours, absenceNum, room_duration, room_id) VALUES
(25, 5000.50, 1234567, 'Ahmad Al-Ali', 'ahmad.alali@yahoo.com', 8, 2, 6, 1),
(30, 6000.75, 2345678, 'Fatima Al-Hasan', 'fatima.alhasan@gmail.com', 7, 1, 4, 2),
(20, 4500.00, 3456789, 'Ali Al-Kurdi', 'ali.alkurdi@hotmail.com', 9, 3, 5, 3),
(15, 5500.25, 4567890, 'Noor Al-Refai', 'noor.alrefai@yahoo.com', 8, 0, 6, 4),
(18, 4800.80, 5678901, 'Mohammed Salama', 'mohammed.salama@gmail.com', 7, 2, 5, 5);

INSERT INTO membership (registration_date, membership_fees, payment_type, insurance_type, visits_per_month, membership_duration, PatientId)
VALUES
( '2023-01-15', 99.99, 'VISA', 'Basic', 10, 12, 100),
( '2023-02-20', 149.99, 'cash', 'Premium', 20, 6, 102),
( '2023-03-05', 199.99, 'VISA', 'Gold', 30, 3, 101),
('2023-04-10', 79.99, 'cash', 'Silver', 15, 12, 104);

INSERT INTO inBodyScan (ScanDate, TotalSkeletalMuscleMass, TotalBodyFat, TotalBodyWater, WaistHipRatio, ObesityDegree, PatientID) 
VALUES 
('2024-06-04', 55.8, 18.5, 57.2, 0.80, 'Overweight', 104),
('2024-06-05', 48.7, 22.1, 49.5, 0.90, 'Obese', 101),
('2024-06-06', 65.3, 12.9, 63.7, 0.70, 'Normal', 102),
('2024-06-07', 40.2, 30.4, 40.8, 1.00, 'Obese', 100),
('2024-06-08', 57.6, 16.3, 58.9, 0.82, 'Overweight', 101),
('2024-06-09', 62.1, 14.2, 60.5, 0.73, 'Normal', 102),
('2024-06-10', 53.4, 20.7, 55.0, 0.88, 'Overweight', 103);
