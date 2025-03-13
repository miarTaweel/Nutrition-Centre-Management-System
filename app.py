from datetime import datetime, timedelta

import MySQLdb
from flask import Flask, render_template, request, flash, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from decimal import Decimal, ROUND_HALF_UP

import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Add a secret key for session management
# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Miar1210447'
app.config['MYSQL_DB'] = 'nutritionCentre'
mysql = MySQL(app)



@app.route('/')
def index():
    return render_template('indexOut.html')  # The HTML file created above
@app.route('/home')
def home():
    return render_template('index.html')  # The HTML file created above

@app.route('/loginn')
def loginn():
    return render_template('login.html')  # The HTML file created above


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (email, password,))
        account = cur.fetchone()

        if account:
            flash(f'Logged in as: {email}', 'success')
            return render_template('index.html')
        else:
            flash('Incorrect email or password', 'danger')

        cur.close()

    return render_template('login.html')

@app.route('/diets')
def diets():
    diets=fetchall_diets()
    return render_template('diets.html',diets=diets)

@app.route('/patients')
def patients():
    patients = fetchall_patients()
    return render_template('Patients.html', patients=patients, error_message=None)

@app.route('/pastPatients')
def pastPatients():
    patients = fetchall_pastPatients()
    return render_template('pastPatients.html', patients=patients, error_message=None)

@app.route('/past')
def past():
    return render_template('Past.html',  error_message=None)

@app.route('/inbody-scans')
def inBody():
    inBodys = fetchall_inBodys()
    return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)

@app.route('/membership')
def memberships():
    memberships = fetchall_memberships()
    return render_template('membership.html', memberships=memberships)

@app.route('/laboratory')
def laboratory():
    return render_template('laboratory.html')



def fetchall_Tests():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""select PatientID, date_taken, next_date_to_take, p.test_id, testType  
from patienttakemedicaltest p, medicaltest t
where p.test_id =t.test_id""")
        tests = cur.fetchall()
        test_list = []
        for row in tests:
            test_dict = {
                'PatientID': row['PatientID'],
                'date_taken': row['date_taken'],
                'next_date_to_take': row['next_date_to_take'],
                'test_id': row['test_id'],
                'testType': row['testType'],
            }
            test_list.append(test_dict)
        cur.close()
        return test_list

    except Exception as e:
        print("Error:", e)
        return []

def fetchall_pastPatients():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM Patients where status='dismissed'")
        patients = cur.fetchall()
        patient_list = []

        for row in patients:
            patient_dict = {
                'PatientID': row['PatientID'],
                'FirstName': row['FirstName'],
                'LastName': row['LastName'],
                'Email': row['Email'],
                'PhoneNumber': row['PhoneNumber'],
                'Age': row['Age'],
                'DietID': row['DietID'],
                }
            patient_list.append(patient_dict)
        cur.close()
        return patient_list

    except Exception as e:
        print("Error:", e)
        return []


@app.route('/search_pastPatients', methods=['GET', 'POST'])
def search_pastPatients():
    global cur, conn
    try:
        search_value=""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['searchOption']
        if search_criteria == "PatientID":
            search_value = request.form['searchInput']
            search_criteria = "PatientID"
        elif search_criteria == "FirstName":
            search_value = request.form['searchInput']
            search_criteria = "FirstName"
        elif search_criteria == "LastName":
            search_value = request.form['searchInput']
            search_criteria = "LastName"
            # Perform search by ID
        elif search_criteria == "PhoneNumber":
            search_value = request.form['searchInput']
            search_criteria="PhoneNumber"
        elif search_criteria == "Age":
            search_value = request.form['searchInput']
            search_criteria = "Age"
            # Perform search by Phone Number
        elif search_criteria == "Email":
            search_value = request.form['searchInput']
            # Perform search by Email
        elif search_criteria == ".":
            patients = fetchall_pastPatients()
            return render_template('pastPatients.html', search_criteria='',patients=patients, error_message=None)
            # Perform search by Email
        print(search_criteria,"=",search_value)
        search_query = f"SELECT * FROM Patients WHERE {search_criteria} LIKE %s and status='dismissed'"
        term_with_percent = f"{search_value}"
        cur.execute(search_query, (term_with_percent,))
        patients= cur.fetchall()
        print(patients)

        cur.close()
        # Fetch all matching rows
        patient_list = []
        for row in patients:
            patient_dict = {
                'PatientID': row[0],
                'FirstName': row[1],
                'LastName': row[2],
                'Email': row[3],
                'PhoneNumber': row[4],
                'Age': row[5],
                'DietID': row[6],
            }
            patient_list.append(patient_dict)
        print(patient_list)

        if patient_list:
          return render_template('pastPatients.html',search_criteria='', patients=patient_list)
    except Exception as e:
        print(f"Error searching : {e}")
        return render_template('pastPatients.html')

    flash("An error occurred while searching data: Could not find searched Data", "error")
    conn.rollback()
    return render_template('pastPatients.html')


@app.route('/pastPatient_Details', methods=['POST'])
def showpastInbody():
    try:
        PatientID = request.form['patientDetailsID']
        if PatientID == "":
            inBodys = fetchall_inBodys()
            patients = fetchall_pastPatients()
            diets = fetchall_diets()
            memberships = fetchall_memberships()
            tests=fetchall_Tests()
            print(tests)
            return render_template('pastPatients.html', patients=patients,tests=tests, diets=diets, memberships=memberships,
                                   inbodyscans=inBodys, search_criteria='.', error_message=None)

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM patients WHERE PatientID = %s and status='dismissed'", (PatientID,))
        patients = cur.fetchall()

        if not patients:  # If no patient found with the given ID
            flash("Patient not found with the given ID.", "error")
            return render_template('pastPatients.html', patients=None, diets=None, memberships=None,
                                   inbodyscans=None, search_criteria='.', error_message=None)
              # Redirect to home or appropriate page

        patient_list = []
        for row in patients:
            patient_dict = {
                'PatientID': row[0],
                'FirstName': row[1],
                'LastName': row[2],
                'Email': row[3],
                'PhoneNumber': row[4],
                'Age': row[5],
                'DietID': row[6],
            }
            patient_list.append(patient_dict)
        print(patient_list)
        cur.close()

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM inbodyscan WHERE PatientID = %s", (PatientID,))
        inBody = cur.fetchall()

        inBody_list = []

        for row in inBody:
            inBody_dict = {
                'InBodyID': row[0],
                'ScanDate': row[1],
                'TotalSkeletalMuscleMass': row[2],
                'TotalBodyFat': row[3],
                'TotalBodyWater': row[4],
                'WaistHipRatio': row[5],
                'ObesityDegree': row[6],
                'PatientID': row[7]
            }
            inBody_list.append(inBody_dict)
        cur.close()
        print("here")
        cur = mysql.connection.cursor()
        cur.execute("""select PatientID, date_taken, next_date_to_take, p.test_id, testType  
from patienttakemedicaltest p, medicaltest t
where p.test_id =t.test_id and PatientID=%s """, (PatientID,))

        tests = cur.fetchall()
        print(tests)

        test_list = []
        for row in tests:
            test_dict = {
                'PatientID': row[0],
                'date_taken': row[1],
                'next_date_to_take': row[2],
                'test_id': row[3],
                'testType': row[4],
            }
            test_list.append(test_dict)
        cur.close()

        print(test_list)

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM membership WHERE PatientId = %s", (PatientID,))
        memberships = cur.fetchall()

        membership_list = []

        for row in memberships:
            membership_dict = {
                'membership_id': row[0],
                'registration_date': row[1],
                'membership_fees': row[2],
                'payment_type': row[3],
                'insurance_type': row[4],
                'visits_per_month': row[5],
                'membership_duration': row[6],
            }
            membership_list.append(membership_dict)
        cur.close()

        cur = mysql.connection.cursor()
        cur.execute("SELECT DietID FROM patients WHERE PatientID = %s", (PatientID,))
        dietID = cur.fetchone()

        cur.execute("SELECT * FROM diet WHERE DietID = %s", (dietID,))
        diets = cur.fetchall()

        diet_list = []

        # Iterating over fetched rows
        for row in diets:
            diet_dict = {
                'DietID': row[0],
                'DietType': row[1],
                'CarbIntake': row[2],
                'ProteinIntake': row[3],
                'LiquidIntake': row[4],
                'CaloriesPerMeal': row[5],
            }
            diet_list.append(diet_dict)

        cur.close()
        print(diet_list)

        return render_template('pastPatients.html', patients=patient_list,tests=test_list, diets=diet_list, memberships=membership_list,
                               inbodyscans=inBody_list, search_criteria='.', error_message=None)
    except Exception as e:
        flash("An error occurred while processing the request.", "error")
        print(e)  # Print the error for debugging
        return render_template('pastPatients.html', patients=None,tests=None ,diets=None, memberships=None,
                               inbodyscans=None, search_criteria='.', error_message=None) # Redirect to home or appropriate page

def fetchall_patients():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM Patients where status='active'")
        patients = cur.fetchall()
        patient_list = []

        for row in patients:
            patient_dict = {
                'PatientID': row['PatientID'],
                'FirstName': row['FirstName'],
                'LastName': row['LastName'],
                'Email': row['Email'],
                'PhoneNumber': row['PhoneNumber'],
                'Age': row['Age'],
                'DietID': row['DietID'],
                }
            patient_list.append(patient_dict)
        cur.close()
        return patient_list

    except Exception as e:
        print("Error:", e)
        return []

@app.route('/add_Patient', methods=['POST'])
def insert_Patient():
    if request.method == 'POST':
        try:
            # Get data from the form
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            Email = request.form['email']
            phoneNumber = request.form['phoneNumber']
            age = request.form['age']

            # Insert data into the "patients" table
            insert_query = "INSERT INTO patients (FirstName, LastName, Email, PhoneNumber, Age) VALUES (%s, %s, %s, %s, %s)"
            patient_data = (firstName, lastName, Email, phoneNumber, age)
            cur = mysql.connection.cursor()
            cur.execute(insert_query, patient_data)
            # Commit changes and close the connection
            mysql.connection.commit()
            cur.close()
            flash("Patient inserted successfully!", "success")
            # Redirect back to the home page after adding a new patient
            patients = fetchall_patients()
            return render_template('Patients.html', patients=patients,search_criteria='', error_message=None)
        except MySQLdb.IntegrityError as e:
            # Check if the error is due to duplicate entry
            if "Duplicate entry" in str(e):
                flash("This email or phone number has already been inserted. Please try again.", "error")
            else:
                flash("An error occurred while inserting the patient. Please try again.", "error")
            patients = fetchall_patients()
            return render_template('Patients.html', patients=patients,search_criteria='', error_message=None)
        except Exception as e:
            print(f"Error inserting: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            patients = fetchall_patients()
            return render_template('Patients.html', patients=patients, search_criteria='',error_message=None)

@app.route('/Clear', methods=['POST'])
def clear_patients():
    insert_query = "UPDATE Patients SET status = 'dismissed';"

    cur = mysql.connection.cursor()
    cur.execute(insert_query)
    mysql.connection.commit()
    cur.close()
    flash("Patients have been Cleared successfully!", "success")
    patients = fetchall_patients()
    return render_template('Patients.html', patients=patients,search_criteria='', error_message=None)




@app.route('/delete_Patient', methods=['POST'])
def Delete_Patient():
    if request.method == 'POST':
        try:
            print("Start Deleting ")
            # Get data from the form
            patient_id = request.form['patientID']

            # Check if the patient ID exists in the database
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM patients WHERE PatientID = %s and status = 'active'", (patient_id,))
            patient = cur.fetchone()
            cur.close()

            if patient:
                # If the patient exists, proceed with deletion
                delete_query = "UPDATE Patients SET status = 'dismissed' WHERE PatientID = %s"
                cur = mysql.connection.cursor()
                cur.execute(delete_query, (patient_id,))
                mysql.connection.commit()
                cur.close()

                flash("Patient Deleted successfully!", "success")
            else:
                # If the patient doesn't exist, return an error message
                flash("Patient with ID {} does not exist".format(patient_id), "error")

            # Redirect back to the home page after deletion attempt
            patients = fetchall_patients()
            return render_template('Patients.html', search_criteria='',patients=patients, error_message=None)

        except Exception as e:
            print(f"Error deleting patient: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            patients = fetchall_patients()
            return render_template('Patients.html', search_criteria='',patients=patients, error_message=None)

@app.route('/search_Patients', methods=['GET', 'POST'])
def search_Patients():
    global cur, conn
    try:
        search_value=""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['searchOption']
        if search_criteria == "PatientID":
            search_value = request.form['searchInput']
            search_criteria = "PatientID"
        elif search_criteria == "FirstName":
            search_value = request.form['searchInput']
            search_criteria = "FirstName"
        elif search_criteria == "LastName":
            search_value = request.form['searchInput']
            search_criteria = "LastName"
            # Perform search by ID
        elif search_criteria == "PhoneNumber":
            search_value = request.form['searchInput']
            search_criteria="PhoneNumber"
        elif search_criteria == "Age":
            search_value = request.form['searchInput']
            search_criteria = "Age"
            # Perform search by Phone Number
        elif search_criteria == "Email":
            search_value = request.form['searchInput']
            # Perform search by Email
        elif search_criteria == ".":
            patients = fetchall_patients()
            return render_template('Patients.html', search_criteria='',patients=patients, error_message=None)
            # Perform search by Email
        print(search_criteria,"=",search_value)
        search_query = f"SELECT * FROM Patients WHERE {search_criteria} LIKE %s and status='active'"
        term_with_percent = f"{search_value}"
        cur.execute(search_query, (term_with_percent,))
        patients= cur.fetchall()
        print(patients)

        cur.close()
        # Fetch all matching rows
        patient_list = []
        for row in patients:
            patient_dict = {
                'PatientID': row[0],
                'FirstName': row[1],
                'LastName': row[2],
                'Email': row[3],
                'PhoneNumber': row[4],
                'Age': row[5],
                'DietID': row[6],
            }
            patient_list.append(patient_dict)
        print(patient_list)

        if patient_list:
          return render_template('Patients.html',search_criteria='', patients=patient_list)
    except Exception as e:
        print(f"Error searching : {e}")
        return render_template('Patients.html')

    flash("An error occurred while searching data: Could not find searched Data", "error")
    conn.rollback()
    return render_template('Patients.html')


@app.route('/del_Patients', methods=['GET', 'POST'])
def del_Patients():
    try:
        search_value = ""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['deleteOption']

        if search_criteria == "PatientID":
            search_value1 = request.form['deleteByPatientID']
            print(search_value1)

            # Check if PatientID exists
            cur.execute("SELECT * FROM patients WHERE PatientID = %s and status='active'", (search_value1,))
            patient = cur.fetchone()
            if not patient:
                flash("PatientID does not exist", "error")
            else:
                search_query = "DELETE FROM patienttakemedicaltest WHERE PatientID = %s"
                cur.execute(search_query, (search_value1,))
                flash("Deleted Successfully")

        elif search_criteria == "TestID":
            search_value1 = request.form['deleteByTestID']
            print(search_value1)

            # Check if TestID exists
            cur.execute("SELECT * FROM test WHERE test_id = %s", (search_value1,))
            test = cur.fetchone()
            if not test:
                flash("TestID does not exist", "error")
            else:
                search_query = "DELETE FROM patienttakemedicaltest WHERE test_id = %s"
                cur.execute(search_query, (search_value1,))
                flash("Deleted Successfully")

        elif search_criteria == "all":
            search_value1 = request.form['deletePatientID']
            search_value2 = request.form['deleteTestID']

            # Check if PatientID and TestID exist
            cur.execute("SELECT * FROM patients WHERE PatientID = %s", (search_value1,))
            patient = cur.fetchone()
            cur.execute("SELECT * FROM medicaltest WHERE test_id = %s", (search_value2,))
            test = cur.fetchone()

            if not patient:
                flash("PatientID does not exist", "error")
            elif not test:
                flash("TestID does not exist", "error")
            else:
                search_query = "DELETE FROM patienttakemedicaltest WHERE PatientID = %s AND test_id = %s"
                cur.execute(search_query, (search_value1, search_value2))
                flash("Deleted Successfully")

        else:
            flash("Invalid search criteria", "error")

        conn.commit()
        cur.close()

    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred. Please try again.", "error")
        conn.rollback()

    patients = fetchall_patients()
    return render_template('Patients.html', search_criteria='', patients=patients, error_message=None)


@app.route('/update', methods=['GET', 'POST'])
def update_patient():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            ID = request.form['updatePatientID']
            fName = request.form['updateFirstName']
            lName = request.form['updateLastName']
            email = request.form['updateEmail']
            Number = request.form['updatePhoneNumber']
            age = request.form['updateAge']

            update_query = "UPDATE Patients SET"
            update_data = []
            if fName:
                update_query += " FirstName=%s,"
                update_data.append(fName)
            if lName:
                update_query += " LastName=%s,"
                update_data.append(lName)
            if email:
                update_query += " Email=%s,"
                update_data.append(email)
            if Number:
                update_query += " PhoneNumber=%s,"
                update_data.append(Number)
            if age:
                update_query += " Age=%s,"
                update_data.append(age)

            # Remove the trailing comma and close the SET clause
            update_query = update_query.rstrip(',')
            update_query += " WHERE PatientID=%s and status='active'"

            # Append the PatientID to the update_values list
            update_data.append(ID)

            # Execute the update query
            cur = conn.cursor()
            rows_affected = cur.execute(update_query, update_data)
            conn.commit()
            cur.close()

            if rows_affected == 0:
                flash(f"No patient found with ID {ID}", "error")
            else:
                flash("Patient updated successfully!", "success")

            patients = fetchall_patients()
            return render_template('Patients.html', patients=patients)
        except Exception as e:
            flash(f"Error updating patient: {e}", "error")
            print(f"Error updating Patients: {e}")
            patients = fetchall_patients()
            return render_template('Patients.html', patients=patients)

    else:
        patients = fetchall_patients()
        return render_template('Patients.html',search_criteria='', patients=patients)
from flask import flash

@app.route('/patient_Details', methods=['POST'])
def showInbody():
    try:
        PatientID = request.form['patientDetailsID']
        if PatientID == "":
            inBodys = fetchall_inBodys()
            patients = fetchall_patients()
            diets = fetchall_diets()
            memberships = fetchall_memberships()
            tests=fetchall_Tests()
            print(tests)
            return render_template('Patients.html', patients=patients,tests=tests, diets=diets, memberships=memberships,
                                   inbodyscans=inBodys, search_criteria='.', error_message=None)

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM patients WHERE PatientID = %s and status='active'", (PatientID,))
        patients = cur.fetchall()

        if not patients:  # If no patient found with the given ID
            flash("Patient not found with the given ID.", "error")
            return render_template('Patients.html', patients=None, diets=None, memberships=None,
                                   inbodyscans=None, search_criteria='.', error_message=None)
              # Redirect to home or appropriate page

        patient_list = []
        for row in patients:
            patient_dict = {
                'PatientID': row[0],
                'FirstName': row[1],
                'LastName': row[2],
                'Email': row[3],
                'PhoneNumber': row[4],
                'Age': row[5],
                'DietID': row[6],
            }
            patient_list.append(patient_dict)
        print(patient_list)
        cur.close()

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM inbodyscan WHERE PatientID = %s", (PatientID,))
        inBody = cur.fetchall()

        inBody_list = []

        for row in inBody:
            inBody_dict = {
                'InBodyID': row[0],
                'ScanDate': row[1],
                'TotalSkeletalMuscleMass': row[2],
                'TotalBodyFat': row[3],
                'TotalBodyWater': row[4],
                'WaistHipRatio': row[5],
                'ObesityDegree': row[6],
                'PatientID': row[7]
            }
            inBody_list.append(inBody_dict)
        cur.close()
        print("here")
        cur = mysql.connection.cursor()
        cur.execute("""select PatientID, date_taken, next_date_to_take, p.test_id, testType  
from patienttakemedicaltest p, medicaltest t
where p.test_id =t.test_id and PatientID=%s """, (PatientID,))

        tests = cur.fetchall()
        print(tests)

        test_list = []
        for row in tests:
            test_dict = {
                'PatientID': row[0],
                'date_taken': row[1],
                'next_date_to_take': row[2],
                'test_id': row[3],
                'testType': row[4],
            }
            test_list.append(test_dict)
        cur.close()

        print(test_list)

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM membership WHERE PatientId = %s", (PatientID,))
        memberships = cur.fetchall()

        membership_list = []

        for row in memberships:
            membership_dict = {
                'membership_id': row[0],
                'registration_date': row[1],
                'membership_fees': row[2],
                'payment_type': row[3],
                'insurance_type': row[4],
                'visits_per_month': row[5],
                'membership_duration': row[6],
            }
            membership_list.append(membership_dict)
        cur.close()

        cur = mysql.connection.cursor()
        cur.execute("SELECT DietID FROM patients WHERE PatientID = %s", (PatientID,))
        dietID = cur.fetchone()

        cur.execute("SELECT * FROM diet WHERE DietID = %s", (dietID,))
        diets = cur.fetchall()

        diet_list = []

        # Iterating over fetched rows
        for row in diets:
            diet_dict = {
                'DietID': row[0],
                'DietType': row[1],
                'CarbIntake': row[2],
                'ProteinIntake': row[3],
                'LiquidIntake': row[4],
                'CaloriesPerMeal': row[5],
            }
            diet_list.append(diet_dict)

        cur.close()
        print(diet_list)

        return render_template('Patients.html', patients=patient_list,tests=test_list, diets=diet_list, memberships=membership_list,
                               inbodyscans=inBody_list, search_criteria='.', error_message=None)
    except Exception as e:
        flash("An error occurred while processing the request.", "error")
        print(e)  # Print the error for debugging
        return render_template('Patients.html', patients=None,tests=None ,diets=None, memberships=None,
                               inbodyscans=None, search_criteria='.', error_message=None) # Redirect to home or appropriate page

def fetchall_diets():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM diet")
        diets = cur.fetchall()
        diet_list = []

        for row in diets:

            diet_dict = {
                'DietID': row['DietID'],
                'DietType': row['DietType'],
                'CarbIntake': row['CarbIntake'],
                'ProteinIntake': row['ProteinIntake'],
                'LiquidIntake': row['LiquidIntake'],
                'CaloriesPerMeal': row['CaloriesPerMeal'],

            }
            diet_list.append(diet_dict)
        cur.close()
        return diet_list

    except Exception as e:
        print("Error:", e)
        return []


@app.route('/add_diet', methods=['POST'])
def insert_diet():
    if request.method == 'POST':
        try:

            # Get data from the form
            DietType = request.form['dietType']
            CarbIntake = request.form['carbIntake']
            ProteinIntake = request.form['proteinIntake']
            LiquidIntake = request.form['liquidIntake']
            CaloriesPerMeal = request.form['caloriesPerMeal']

            # Insert data into the "patients" table
            insert_query = "INSERT INTO diet (DietType, CarbIntake, ProteinIntake, LiquidIntake, CaloriesPerMeal) VALUES (%s, %s, %s, %s, %s)"
            diet_data = (DietType, CarbIntake, ProteinIntake, LiquidIntake, CaloriesPerMeal)
            cur = mysql.connection.cursor()
            cur.execute(insert_query, diet_data)
            # Commit changes and close the connection
            mysql.connection.commit()
            cur.close()
            flash("diet inserted successfully!", "success")
            # Redirect back to the home page after adding a new patient
            diets = fetchall_diets()
            return render_template('diets.html', diets=diets,error_message=None)
        except MySQLdb.IntegrityError as e:
            # Check if the error is due to duplicate entry
            flash("An error occurred while inserting the diet. Please try again.", "error")
            diets = fetchall_diets()
            return render_template('diets.html', diets=diets, error_message=None)
        except Exception as e:
            print(f"Error inserting: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            diets = fetchall_diets()
            return render_template('diets.html', diets=diets, error_message=None)




@app.route('/delete_diet', methods=['POST'])
def Delete_diet():
    if request.method == 'POST':
        try:
            print("Start Deleting ")
            # Get data from the form
            diet_id = request.form['dietID']

            # Check if the patient ID exists in the database
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM diet WHERE DietID = %s", (diet_id,))
            diet = cur.fetchone()
            cur.close()

            if diet:
                # If the patient exists, proceed with deletion
                delete_query = "DELETE FROM diet WHERE DietID = %s"
                cur = mysql.connection.cursor()
                cur.execute(delete_query, (diet_id,))
                mysql.connection.commit()
                cur.close()

                flash("Diet Deleted successfully!", "success")
            else:
                # If the patient doesn't exist, return an error message
                flash("Diet with ID {} does not exist".format(diet_id), "error")

            diets = fetchall_diets()
            return render_template('diets.html', diets=diets)

        except Exception as e:
            print(f"Error deleting diet: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            diets = fetchall_diets()
            return render_template('diets.html', diets=diets)


@app.route('/search_diets', methods=['GET', 'POST'])
def search_diet():
    global cur, conn
    try:

        search_value=""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['searchOption']
        if search_criteria == "DietID":
            search_value = request.form['searchInput']

        elif search_criteria == "DietType":
            search_value = request.form['searchInput']

        elif search_criteria == "CarbIntake":
            search_value = request.form['searchInput']

        elif search_criteria == "ProteinIntake":
            search_value = request.form['searchInput']

        elif search_criteria == "LiquidIntake":
            search_value = request.form['searchInput']

        elif search_criteria == "CaloriesPerMeal":
            search_value = request.form['searchInput']
        elif search_criteria == "Count":
            query = """
                   SELECT d.DietID, d.DietType, COUNT(p.PatientID) AS NumberOfPatients, AVG(p.Age) AS AverageAge
                   FROM diet d
                   LEFT JOIN patients p ON d.DietID = p.DietID
                   GROUP BY d.DietID, d.DietType
                   ORDER BY d.DietID;
                   """

            cur.execute(query)
            results = cur.fetchall()
            diet_list = []

            for row in results:
                diet_dict = {
                    'DietID': row[0],
                    'DietType': row[1],
                    'NumberOfPatients': row[2],
                    'AverageAge': row[3] if row[3] is not None else 0  # Handle None case for diets with no patients
                }
                diet_list.append(diet_dict)

            for diet in diet_list:
                print( f"DietID: {diet['DietID']}, DietType: {diet['DietType']}, NumberOfPatients: {diet['NumberOfPatients']}, AverageAge: {diet['AverageAge']:.2f}")

            cur.close()
            return render_template('diets.html', diet_stats=diet_list,search_criteria=search_criteria)
        elif search_criteria == ".":
            diets = fetchall_diets()
            return render_template('diets.html', diets=diets)
            # Perform search by Email
        print(search_criteria,"=",search_value)
        search_query = f"SELECT * FROM diet WHERE {search_criteria} LIKE %s"
        term_with_percent = f"{search_value}"
        cur.execute(search_query, (term_with_percent,))
        diets= cur.fetchall()
        print(diets)
        cur.close()
        # Fetch all matching rows
        diet_list = []

        for row in diets:
            diet_dict = {
                'DietID': row[0],
                'DietType': row[1],
                'CarbIntake': row[2],
                'ProteinIntake': row[3],
                'LiquidIntake': row[4],
                'CaloriesPerMeal': row[5],

            }
            diet_list.append(diet_dict)
        cur.close()

        if diet_list:
          return render_template('diets.html', diets=diet_list)
    except Exception as e:
        print(f"Error searching : {e}")
        return render_template('diets.html')
    flash("Could not find searched Data", "error")
    conn.rollback()
    return render_template('diets.html')

@app.route('/update_diets', methods=['GET', 'POST'])
def update_diet():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            ID = request.form['updateDietID']
            DietType = request.form['updateDietType']
            CarbIntake = request.form['updateCarbIntake']
            ProteinIntake = request.form['updateProteinIntake']
            LiquidIntake = request.form['updateLiquidIntake']
            CaloriesPerMeal = request.form['updateCaloriesPerMeal']

            update_query = "UPDATE diet SET"
            update_data = []
            if DietType:
                update_query += " DietType=%s,"
                update_data.append(DietType)
            if CarbIntake:
                update_query += " CarbIntake=%s,"
                update_data.append(CarbIntake)
            if ProteinIntake:
                update_query += " ProteinIntake=%s,"
                update_data.append(ProteinIntake)
            if LiquidIntake:
                update_query += " LiquidIntake=%s,"
                update_data.append(LiquidIntake)
            if CaloriesPerMeal:
                update_query += " CaloriesPerMeal=%s,"
                update_data.append(CaloriesPerMeal)

            # Remove the trailing comma and close the SET clause
            update_query = update_query.rstrip(',')
            update_query += " WHERE DietID=%s"

            # Append the PatientID to the update_values list
            update_data.append(ID)

            # Execute the update query
            cur = conn.cursor()
            rows_affected = cur.execute(update_query, update_data)
            conn.commit()
            cur.close()

            if rows_affected == 0:
                flash(f"No Diet found with ID {ID}", "error")
            else:
                flash("Diet updated successfully!", "success")

            diets = fetchall_diets()
            return render_template('diets.html', diets=diets)
        except Exception as e:
            flash(f"Error updating Diets: {e}", "error")
            print(f"Error updating Diets: {e}")
            diets = fetchall_diets()
            return render_template('diets.html', diets=diets)

    else:
        diets = fetchall_diets()
        return render_template('diets.html', diets=diets)


@app.route('/diet_Details', methods=['POST'])
def showdietPatients():
    try:
        DietID = request.form['patientDetailsID']
        if DietID == "":

            cur = mysql.connection.cursor()
            cur.execute("SELECT PatientID, FirstName, LastName, Email, PhoneNumber, Age,p.DietID FROM patients p,diet d WHERE p.DietID = d.DietID and status='active'")
            patients  = cur.fetchall()

            patient_list = []
            for row in patients:
                patient_dict = {
                    'PatientID': row[0],
                    'FirstName': row[1],
                    'LastName': row[2],
                    'Email': row[3],
                    'PhoneNumber': row[4],
                    'Age': row[5],
                    'DietID': row[6],
                }
                patient_list.append(patient_dict)

            print(patient_list)
            cur.close()
            diets = fetchall_diets()

            return render_template('diets.html', patients=patient_list, diets=diets, search_criteria='.', error_message=None)

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM diet WHERE DietID = %s", (DietID,))
        diets = cur.fetchall()

        if not diets:  # If no patient found with the given ID
            flash("Diet not found with the given ID.", "error")
            return render_template('diet.html', patients=None, diets=None, search_criteria='.', error_message=None)

        diet_list = []
        # Iterating over fetched rows
        for row in diets:
            diet_dict = {
                'DietID': row[0],
                'DietType': row[1],
                'CarbIntake': row[2],
                'ProteinIntake': row[3],
                'LiquidIntake': row[4],
                'CaloriesPerMeal': row[5],
            }
            diet_list.append(diet_dict)

        cur.close()
        print(diet_list)

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM patients WHERE DietID = %s and status='active'", (DietID,))
        patients = cur.fetchall()

        patient_list = []
        for row in patients:
            patient_dict = {
                'PatientID': row[0],
                'FirstName': row[1],
                'LastName': row[2],
                'Email': row[3],
                'PhoneNumber': row[4],
                'Age': row[5],
                'DietID': row[6],
            }
            patient_list.append(patient_dict)
        print(patient_list)
        cur.close()

        return render_template('diets.html', patients=patient_list, diets=diet_list, search_criteria='.', error_message=None)
    except Exception as e:
        flash("An error occurred while processing the request.", "error")
        print(e)  # Print the error for debugging
        return render_template('diets.html', patients=None, diets=None, memberships=None,
                               inbodyscans=None, search_criteria='.', error_message=None) # Redirect to home or appropriate page


@app.route('/Clear_Diets', methods=['POST'])
def clear_diets():
    insert_query = "DELETE FROM diet;"
    insert_query2 = "ALTER TABLE diet AUTO_INCREMENT = 1;"

    cur = mysql.connection.cursor()
    cur.execute(insert_query)
    cur.execute(insert_query2)
    mysql.connection.commit()
    cur.close()
    flash("Diets have been Cleared successfully!", "success")
    diets = fetchall_diets()
    return render_template('diets.html', diets=diets)

def fetchall_inBodys():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""SELECT InBodyID, ScanDate, TotalSkeletalMuscleMass, TotalBodyFat, TotalBodyWater, WaistHipRatio, ObesityDegree, i.PatientID FROM inbodyscan i,patients p where i.PatientID=p.PatientID and status ='active'
                    Union
select  InBodyID, ScanDate, TotalSkeletalMuscleMass, TotalBodyFat, TotalBodyWater, WaistHipRatio, ObesityDegree, 
    PatientID  from inbodyscan where PatientID is NULL""")
        inbodyscans = cur.fetchall()
        inbodyscan_list = []

        for row in inbodyscans:

            inbodyscan_dict = {
                'InBodyID': row['InBodyID'],
                'ScanDate': row['ScanDate'],
                'TotalSkeletalMuscleMass': row['TotalSkeletalMuscleMass'],
                'TotalBodyFat': row['TotalBodyFat'],
                'TotalBodyWater': row['TotalBodyWater'],
                'WaistHipRatio': row['WaistHipRatio'],
                'ObesityDegree': row['ObesityDegree'],
                'PatientID': row['PatientID']

            }
            inbodyscan_list.append(inbodyscan_dict)
        cur.close()
        return inbodyscan_list

    except Exception as e:
        print("Error:", e)
        return []


@app.route('/search_inbodyscan', methods=['GET', 'POST'])
def search_inbody():
    global cur, conn
    try:
        search_value=""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['searchOption']
        if search_criteria == "InBodyID":
            search_value = request.form['searchInput']

        elif search_criteria == "ScanDate":
            search_value = request.form['searchInput']

        elif search_criteria == "TotalSkeletalMuscleMass":
            search_value = request.form['searchInput']

        elif search_criteria == "TotalBodyFat":
            search_value = request.form['searchInput']

        elif search_criteria == "WaistHipRatio":
            search_value = request.form['searchInput']

        elif search_criteria == "ObesityDegree":
            search_value = request.form['searchInput']

        elif search_criteria == ".":
            inBodys = fetchall_inBodys()
            return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)
        # Perform search by Email
        print(search_criteria,"=",search_value)
        search_query = f"""SELECT * FROM inbodyscan WHERE {search_criteria} LIKE %s and InBodyID IN (
    SELECT InBodyID 
    FROM inBodyScan i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT InBodyID 
    FROM inBodyScan 
    WHERE PatientID IS NULL
)"""
        term_with_percent = f"{search_value}"
        cur.execute(search_query, (term_with_percent,))
        inBody= cur.fetchall()
        print(inBody)
        cur.close()
        # Fetch all matching rows
        inBody_list = []

        for row in inBody:
            inBody_dict = {
                'InBodyID': row[0],
                'ScanDate': row[1],
                'TotalSkeletalMuscleMass': row[2],
                'TotalBodyFat': row[3],
                'TotalBodyWater': row[4],
                'WaistHipRatio': row[5],
                'ObesityDegree': row[6],
                'PatientID': row[7]
            }
            inBody_list.append(inBody_dict)
        cur.close()

        if inBody_list:
            return render_template('inBodyTest.html', inbodyscans=inBody_list, error_message=None)
    except Exception as e:
        print(f"Error searching : {e}")
        return render_template('inBodyTest.html')
    flash("Could not find searched Data", "error")
    conn.rollback()
    return render_template('inBodyTest.html')


@app.route('/add_inbodyscan', methods=['POST'])
def insert_inbodyscan():
    if request.method == 'POST':
        try:
            # Get data from the form

            ScanDate = request.form['scanDate']
            TotalSkeletalMuscleMass = request.form['totalSkeletalMuscleMass']
            TotalBodyFat = request.form['totalBodyFat']
            TotalBodyWater = request.form['totalBodyWater']
            WaistHipRatio = request.form['waistHipRatio']
            ObesityDegree = request.form['obesityDegree']

            # Insert data into the "patients" table
            insert_query = "INSERT INTO inbodyscan ( ScanDate, TotalSkeletalMuscleMass, TotalBodyFat, TotalBodyWater, WaistHipRatio, ObesityDegree) VALUES (%s, %s, %s, %s, %s, %s)"
            inBody_data = ( ScanDate, TotalSkeletalMuscleMass, TotalBodyFat, TotalBodyWater, WaistHipRatio, ObesityDegree)
            cur = mysql.connection.cursor()
            cur.execute(insert_query, inBody_data)
            # Commit changes and close the connection
            mysql.connection.commit()
            cur.close()
            flash("Inbody inserted successfully!", "success")
            # Redirect back to the home page after adding a new patient
            inBodys = fetchall_inBodys()
            return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)

        except MySQLdb.IntegrityError as e:
            # Check if the error is due to duplicate entry
            flash("An error occurred while inserting the inbody. Please try again.", "error")
            inBodys = fetchall_inBodys()
            return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)

        except Exception as e:
            print(f"Error inserting: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            inBodys = fetchall_inBodys()
            return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)


@app.route('/delete_inbodyscan', methods=['POST'])
def Delete_Inbody():
    if request.method == 'POST':
        try:
            print("Start Deleting ")
            # Get data from the form
            inbody_id = request.form['inbodyID']

            # Check if the patient ID exists in the database
            cur = mysql.connection.cursor()
            cur.execute("""SELECT * FROM inbodyscan WHERE InBodyID = %s and InBodyID IN (
    SELECT InBodyID 
    FROM inBodyScan i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT InBodyID 
    FROM inBodyScan 
    WHERE PatientID IS NULL
)""", (inbody_id,))
            inbody = cur.fetchone()
            cur.close()

            if inbody:
                # If the patient exists, proceed with deletion
                delete_query = "DELETE FROM inbodyscan WHERE InBodyID = %s"
                cur = mysql.connection.cursor()
                cur.execute(delete_query, (inbody_id,))
                mysql.connection.commit()
                cur.close()

                flash("InBody Scan Deleted successfully!", "success")
            else:
                # If the patient doesn't exist, return an error message
                flash("InBody Scan with ID {} does not exist".format(inbody_id), "error")

            inBodys = fetchall_inBodys()
            return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)

        except Exception as e:
            print(f"Error deleting InBody Scan: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            inBodys = fetchall_inBodys()
            return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)



@app.route('/update_inbodyscan', methods=['GET', 'POST'])
def update_inBody():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()
            ID = request.form['updateInBodyID']

            query = """
                SELECT * FROM inbodyscan
                WHERE InBodyID = %s AND InBodyID IN (
                    SELECT InBodyID 
                    FROM inBodyScan i 
                    JOIN Patients p ON i.PatientID = p.PatientID 
                    WHERE p.status = 'active'
                    UNION
                    SELECT InBodyID 
                    FROM inBodyScan 
                    WHERE PatientID IS NULL
                )
                """
            cur.execute(query, (ID,))
            inbodys = cur.fetchall()

            if not inbodys:
                flash(f"No InBody found with ID {ID}", "error")
                inBodys = fetchall_inBodys()
                return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)


            ScanDate = request.form['updateScanDate']
            TotalSkeletalMuscleMass = request.form['updateTotalSkeletalMuscleMass']
            TotalBodyFat = request.form['updateTotalBodyFat']
            TotalBodyWater = request.form['updateTotalBodyWater']
            WaistHipRatio = request.form['updateWaistHipRatio']
            ObesityDegree = request.form['updateObesityDegree']

            update_query = "UPDATE inbodyscan SET"
            update_data = []
            if ScanDate:
                update_query += " ScanDate=%s,"
                update_data.append(ScanDate)
            if TotalSkeletalMuscleMass:
                update_query += " TotalSkeletalMuscleMass=%s,"
                update_data.append(TotalSkeletalMuscleMass)
            if TotalBodyFat:
                update_query += " TotalBodyFat=%s,"
                update_data.append(TotalBodyFat)
            if TotalBodyWater:
                update_query += " TotalBodyWater=%s,"
                update_data.append(TotalBodyWater)
            if  WaistHipRatio:
                update_query += " WaistHipRatio=%s,"
                update_data.append(WaistHipRatio)
            if  ObesityDegree:
                update_query += " ObesityDegree=%s,"
                update_data.append(ObesityDegree)
            # Remove the trailing comma and close the SET clause
            update_query = update_query.rstrip(',')
            update_query += """ WHERE InBodyID=%s """

            # Append the PatientID to the update_values list
            update_data.append(ID)

            # Execute the update query

            rows_affected = cur.execute(update_query, update_data)
            conn.commit()
            cur.close()

            if rows_affected == 0:
                flash(f"No Inbody found with ID {ID}", "error")
            else:
                flash("Inbody updated successfully!", "success")


            inBodys = fetchall_inBodys()
            return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)



        except Exception as e:
            flash(f"Error updating Inbody: {e}", "error")
            print(f"Error updating Inbody: {e}")

            inBodys = fetchall_inBodys()
            return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)

    else:
        inBodys = fetchall_inBodys()
        return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)


@app.route('/Clear_inbodyscans', methods=['POST'])
def clear_inbodys():
    insert_query = "DELETE FROM inbodyscan;"
    insert_query2 = "ALTER TABLE inbodyscan AUTO_INCREMENT = 1000;"

    cur = mysql.connection.cursor()
    cur.execute(insert_query)
    cur.execute(insert_query2)
    mysql.connection.commit()
    cur.close()
    flash("inBodyTest have been Cleared successfully!", "success")
    inBodys = fetchall_inBodys()
    return render_template('inBodyTest.html', inbodyscans=inBodys, error_message=None)

@app.route('/Assign_Inbody', methods=['GET', 'POST'])
def Assign_Inbody():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            ID = request.form['update_inBody_id']
            PatientId = request.form['update_PatientId']

            # Check if the PatientId exists in the patients table
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM patients WHERE PatientID = %s and status='active'", (PatientId,))
            patient_exists = cur.fetchone()[0]

            if patient_exists == 0:
                flash(f"No patient found with ID {PatientId}", "error")
                return inBody()

            # Check if the membership is already assigned to a patient
            cur.execute("""SELECT PatientID FROM inbodyscan WHERE InBodyID = %s and InBodyID IN (
    SELECT InBodyID 
    FROM inBodyScan i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT InBodyID 
    FROM inBodyScan 
    WHERE PatientID IS NULL
)
""" , (ID,))
            result = cur.fetchone()

            if result is None:
                flash(f"No inbody found with ID {ID}", "error")
                return inBody()


            # Perform the assignment if the membership is not already assigned
            update_query = "UPDATE inbodyscan  SET PatientID = %s WHERE InBodyID= %s"
            update_data = (PatientId, ID)

            # Execute the update query
            rows_affected = cur.execute(update_query, update_data)
            conn.commit()
            cur.close()

            if rows_affected == 0:
                flash(f"No Inbody found with ID {ID}", "error")
            else:
                flash(" assigned to patient successfully!", "success")

            return inBody()
        except Exception as e:
            flash(f"Error", "error")
            print(f"Error Assigning : {e}")

            return inBody()
    else:
        return inBody()


def fetchall_memberships():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""SELECT * FROM membership where membership_id in(
    SELECT membership_id
    FROM membership i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT membership_id
    FROM membership 
    WHERE PatientID IS NULL)""")
        memberships = cur.fetchall()
        membership_list = []

        for row in memberships:
            membership_dict = {
                'membership_id': row['membership_id'],
                'registration_date': row['registration_date'],
                'membership_fees': row['membership_fees'],
                'payment_type': row['payment_type'],
                'insurance_type': row['insurance_type'],
                'visits_per_month': row['visits_per_month'],
                'membership_duration': row['membership_duration'],
                'PatientId': row['PatientId'],

            }
            membership_list.append(membership_dict)
        cur.close()
        print(membership_list)  # This is to debug if data is being fetched correctly
        return membership_list

    except Exception as e:
        print("Error:", e)
        return []


@app.route('/add_membership', methods=['POST'])
def insert_membership():
    if request.method == 'POST':
        try:
            print("here")
            # Get data from the form
            registration_date = request.form['registrationDate']

            membership_fees = request.form['membershipFees']
            payment_type = request.form['paymentType']
            insurance_type = request.form['insuranceType']
            visits_per_month = request.form['visitsPerMonth']
            membership_duration = request.form['membershipDuration']
            print("here2")
            insert_query = "INSERT INTO membership ( registration_date, membership_fees, payment_type, insurance_type, visits_per_month, membership_duration) VALUES ( %s, %s, %s, %s , %s, %s)"
            membership_data =  (registration_date, membership_fees, payment_type, insurance_type, visits_per_month, membership_duration)
            cur = mysql.connection.cursor()
            cur.execute(insert_query, membership_data)
            print(insert_query, membership_data)
            mysql.connection.commit()
            cur.close()
            flash("Membership inserted successfully!", "success")


            memberships = fetchall_memberships()
            return render_template('membership.html', memberships=memberships)

        except MySQLdb.IntegrityError as e:
            # Check if the error is due to duplicate entry
            if "Duplicate entry" in str(e):
                flash("This email or phone number has already been inserted. Please try again.", "error")
            else:
                flash("An error occurred while inserting the Membership. Please try again.", "error")

            memberships = fetchall_memberships()
            return render_template('membership.html', memberships=memberships)

        except Exception as e:
            print(f"Error inserting: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            memberships = fetchall_memberships()
            return render_template('membership.html', memberships=memberships)

@app.route('/clear_memberships', methods=['POST'])
def clear_membership():
    insert_query = """DELETE FROM membership where membership_id in(
    SELECT membership_id
    FROM membership i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT membership_id
    FROM membership 
    WHERE PatientID IS NULL);"""
    insert_query2 = "ALTER TABLE membership AUTO_INCREMENT = 1;"

    cur = mysql.connection.cursor()
    cur.execute(insert_query)
    cur.execute(insert_query2)
    mysql.connection.commit()
    cur.close()
    flash("All Memberships have been Cleared successfully!", "success")
    memberships = fetchall_memberships()
    return render_template('membership.html', memberships=memberships)



@app.route('/delete_membership', methods=['POST'])
def Delete_membership():
    if request.method == 'POST':
        try:
            print("Start Deleting ")
            # Get data from the form
            membership_id = request.form['membership_id']

            # Check if the patient ID exists in the database
            cur = mysql.connection.cursor()
            cur.execute("""SELECT * FROM membership WHERE membership_id = %s and membership_id in(
    SELECT membership_id
    FROM membership i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT membership_id
    FROM membership 
    WHERE PatientID IS NULL)""", (membership_id,))
            membership = cur.fetchone()
            cur.close()

            if membership:
                # If the patient exists, proceed with deletion
                delete_query = "DELETE FROM membership WHERE membership_id = %s"
                cur = mysql.connection.cursor()
                cur.execute(delete_query, (membership_id,))
                mysql.connection.commit()
                cur.close()

                flash("Membership Deleted successfully!", "success")
            else:

                flash("Membership with ID {} does not exist".format(membership_id), "error")


            memberships = fetchall_memberships()
            return render_template('membership.html', memberships=memberships)

        except Exception as e:
            print(f"Error deleting Membership: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            memberships = fetchall_memberships()
            return render_template('membership.html', memberships=memberships)


@app.route('/search_membership', methods=['GET', 'POST'])
def search_membership():
    global cur, conn
    try:
        search_value=""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['searchOption']
        if search_criteria == "membership_id":
            search_value = request.form['searchInput']

        elif search_criteria == "registration_date":
            search_value = request.form['searchInput']

        elif search_criteria == "membership_fees":
            search_value = request.form['searchInput']


        elif search_criteria == "payment_type":
            search_value = request.form['searchInput']

        elif search_criteria == "insurance_type":
            search_value = request.form['searchInput']


        elif search_criteria == "visits_per_month":
            search_value = request.form['searchInput']

        elif search_criteria == "membership_duration":
            search_value = request.form['searchInput']

        elif search_criteria == ".":
            memberships = fetchall_memberships()
            return render_template('membership.html', memberships=memberships)

        print(search_criteria,"=",search_value)
        search_query = f"""SELECT * FROM membership WHERE {search_criteria} LIKE %s and membership_id in(
    SELECT membership_id
    FROM membership i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT membership_id
    FROM membership 
    WHERE PatientID IS NULL);
 """
        term_with_percent = f"{search_value}"
        cur.execute(search_query, (term_with_percent,))
        memberships= cur.fetchall()
        print(memberships)

        cur.close()

        membership_list = []

        for row in memberships:
            membership_dict = {
                'membership_id': row[0],
                'registration_date': row[1],
                'membership_fees': row[2],
                'payment_type': row[3],
                'insurance_type': row[4],
                'visits_per_month': row[5],
                'membership_duration': row[6],
                'PatientId': row[7],
            }
            membership_list.append(membership_dict)
        cur.close()

        if membership_list:
          return render_template('membership.html', memberships=membership_list)
    except Exception as e:
        print(f"Error searching : {e}")
        return render_template('membership.html')

    flash("Membership Doesnt Exist", "error")
    conn.rollback()
    return render_template('membership.html')


#membership_id, registration_date, membership_fees, payment_type, insurance_type, visits_per_month, membership_duration, PatientId
@app.route('/update_membership', methods=['GET', 'POST'])
def update_membership():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            ID = request.form['update_membership_id']

            cur = mysql.connection.cursor()

            cur.execute("""select * from membership where membership_id =%s and membership_id in(
                SELECT membership_id
                FROM membership i 
                JOIN Patients p ON i.PatientID = p.PatientID 
                WHERE p.status = 'active'
                UNION
                SELECT membership_id
                FROM membership 
                WHERE PatientID IS NULL)

            """, (ID,))
            memb = cur.fetchall()

            if not memb:  # If no patient found with the given ID
                flash("membership not found for the given ID.", "error")
                return render_template('membership.html', patients=None, memberships=None, search_criteria='.',
                                       error_message=None)

            registration_date = request.form['update_registration_date']
            membership_fees = request.form['update_membership_fees']
            payment_type= request.form['update_payment_type']
            insurance_type = request.form['update_insurance_type']
            visits_per_month = request.form['update_visits_per_month']
            membership_duration= request.form['update_membership_duration']

            update_query = "UPDATE membership SET"
            update_data = []
            if registration_date:
                update_query += " registration_date=%s,"
                update_data.append(registration_date)
            if membership_fees:
                update_query += " membership_fees=%s,"
                update_data.append(membership_fees)
            if payment_type:
                update_query += " payment_type=%s,"
                update_data.append(payment_type)
            if insurance_type :
                update_query += " insurance_type =%s,"
                update_data.append(insurance_type )
            if visits_per_month:
                update_query += " visits_per_month=%s,"
                update_data.append(visits_per_month)
            if membership_duration:
                update_query += " membership_duration=%s,"
                update_data.append(membership_duration)

            # Remove the trailing comma and close the SET clause
            update_query = update_query.rstrip(',')
            update_query += " WHERE membership_id=%s"

            # Append the PatientID to the update_values list
            update_data.append(ID)

            # Execute the update query
            cur = conn.cursor()
            rows_affected = cur.execute(update_query, update_data)
            conn.commit()
            cur.close()

            if rows_affected == 0:
                flash(f"No membership found with ID {ID}", "error")
            else:
                flash("membership updated successfully!", "success")


            return memberships()
        except Exception as e:
            flash(f"Error updating membership : {e}", "error")
            print(f"Error updating memberships: {e}")

            return memberships()

    else:

        return memberships()

@app.route('/Assign_membership', methods=['GET', 'POST'])
def Assign_membership():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()
            ID = request.form['update_membership_id']
            PatientId = request.form['update_PatientId']

            # Check if the PatientId exists in the patients table
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM patients WHERE PatientID = %s and status='active'", (PatientId,))
            patient_exists = cur.fetchone()[0]

            if patient_exists == 0:
                flash(f"No patient found with ID {PatientId}", "error")
                return memberships()

            # Check if the membership is already assigned to a patient
            cur.execute("""SELECT PatientId FROM membership WHERE membership_id = %s and membership_id in(
    SELECT membership_id
    FROM membership i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT membership_id
    FROM membership 
    WHERE PatientID IS NULL)

""", (ID,))
            result = cur.fetchone()

            if result is None:
                flash(f"No membership found with ID {ID}", "error")
                return memberships()

            current_patient_id = result[0]


            # Perform the assignment if the membership is not already assigned
            update_query = "UPDATE membership SET PatientId = %s WHERE membership_id = %s"
            update_data = (PatientId, ID)

            # Execute the update query
            rows_affected = cur.execute(update_query, update_data)
            conn.commit()
            cur.close()

            if rows_affected == 0:
                flash(f"No membership found with ID {ID}", "error")
            else:
                flash("Membership assigned to patient successfully!", "success")

            return memberships()
        except Exception as e:
            flash(f"This Patient has already been assigned a membership, Enter another patient", "error")
            print(f"Error updating memberships: {e}")

            return memberships()
    else:
        return memberships()



@app.route('/ShowInbodypatients', methods=['POST'])
def ShowInbodypatients():
    try:
        inbodyID = request.form['inbodyID']
        if inbodyID == "":

            patients=fetchall_patients()
            inbodys=fetchall_inBodys()

            return render_template('inBodyTest.html', patients=patients, inbodyscans=inbodys, search_criteria='.', error_message=None)

        cur = mysql.connection.cursor()

        cur.execute("""SELECT * FROM inbodyscan WHERE InBodyID = %s and InBodyID IN (
    SELECT InBodyID 
    FROM inBodyScan i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT InBodyID 
    FROM inBodyScan 
    WHERE PatientID IS NULL
);
 """,(inbodyID,))
        inbodys = cur.fetchall()

        if not inbodys:  # If no patient found with the given ID
            flash("Inbody not found with the given ID.", "error")
            return render_template('inBodyTest.html', patients=None, inbodyscans=None, search_criteria='.', error_message=None)

        inBody_list = []

        for row in inbodys:
            inBody_dict = {
                'InBodyID': row[0],
                'ScanDate': row[1],
                'TotalSkeletalMuscleMass': row[2],
                'TotalBodyFat': row[3],
                'TotalBodyWater': row[4],
                'WaistHipRatio': row[5],
                'ObesityDegree': row[6],
                'PatientID': row[7]
            }
            inBody_list.append(inBody_dict)
        cur.close()

        print(inBody_list)
        cur = mysql.connection.cursor()

        cur.execute("select p.PatientID, FirstName, LastName, Email, PhoneNumber, Age from inbodyscan i, patients p where p.PatientID=i.PatientID and InBodyID=%s", (inbodyID,))
        patients = cur.fetchall()
        print(patients)
        patient_list = []
        for row in patients:
            patient_dict = {
                'PatientID': row[0],
                'FirstName': row[1],
                'LastName': row[2],
                'Email': row[3],
                'PhoneNumber': row[4],
                'Age': row[5],

            }
            patient_list.append(patient_dict)
        print(patient_list)
        cur.close()

        return render_template('inBodyTest.html', patients=patient_list, inbodyscans=inBody_list, search_criteria='.',
                               error_message=None)
    except Exception as e:
        flash("An error occurred while processing the request.", "error")
        print(e)  # Print the error for debugging
        return render_template('inBodyTest.html', patients=None, diets=None, memberships=None,
                               inbodyscans=None, search_criteria='.', error_message=None) # Redirect to home or appropriate page


@app.route('/ShowMembershippatients', methods=['POST'])
def ShowMembershipPatients():
    try:
        membership_id = request.form['membership_id']
        if membership_id == "":

            patients = fetchall_patients()


            memberships=fetchall_memberships()

            return render_template('membership.html', patients= patients, memberships=memberships, search_criteria='.', error_message=None)

        cur = mysql.connection.cursor()

        cur.execute("""select * from membership where membership_id =%s and membership_id in(
    SELECT membership_id
    FROM membership i 
    JOIN Patients p ON i.PatientID = p.PatientID 
    WHERE p.status = 'active'
    UNION
    SELECT membership_id
    FROM membership 
    WHERE PatientID IS NULL)

""",(membership_id,))
        memberships = cur.fetchall()

        if not memberships:  # If no patient found with the given ID
            flash("membership not found for the given ID.", "error")
            return render_template('membership.html', patients=None, memberships=None, search_criteria='.', error_message=None)

        membership_list = []

        for row in memberships:
            membership_dict = {
                'membership_id': row[0],
                'registration_date': row[1],
                'membership_fees': row[2],
                'payment_type': row[3],
                'insurance_type': row[4],
                'visits_per_month': row[5],
                'membership_duration': row[6],
                'PatientId': row[7],
            }
            membership_list.append(membership_dict)
        cur.close()

        print(membership_list)
        cur = mysql.connection.cursor()

        cur.execute("select p.PatientID, FirstName, LastName, Email, PhoneNumber, Age, DietID from membership m , patients p where p.PatientId=m.PatientId and membership_id =%s", (membership_id,))
        patients = cur.fetchall()
        print(patients)
        patient_list = []
        for row in patients:
            patient_dict = {
                'PatientID': row[0],
                'FirstName': row[1],
                'LastName': row[2],
                'Email': row[3],
                'PhoneNumber': row[4],
                'Age': row[5],

            }
            patient_list.append(patient_dict)
        print(patient_list)
        cur.close()

        return render_template('membership.html', patients=patient_list, memberships=membership_list, search_criteria='.',
                               error_message=None)
    except Exception as e:
        flash("An error occurred while processing the request.", "error")
        print(e)  # Print the error for debugging
        return render_template('membership.html', patients=None, diets=None, memberships=None,
                               inbodyscans=None, search_criteria='.', error_message=None) # Redirect to home or appropriate page






@app.route('/AssignMedicalTest', methods=['POST'])
def insert_patient_medicaltest():
    print("here")
    cur = mysql.connection.cursor()
    print("here")
    patient_id = request.form['assignPatientID']
    test_id = request.form['medicalTestID']
    print(patient_id)
    print(test_id)
    print("here")
    try:
        # Check if patient_id exists in the patients table
        query = "SELECT * FROM patients WHERE PatientID = %s and status='active'"
        print("Executing query:", query, "with patient_id:", patient_id)
        cur.execute(query, (patient_id,))
        patient_exists = cur.fetchone()
        print("Patient exists:", patient_exists)

        if not patient_exists:
            flash("This patient doesn't exist.")
            print(f"Error: Patient ID {patient_id} does not exist.")
            return patients()

        # Check if test_id exists in the medicaltest table
        cur.execute("SELECT * FROM medicaltest WHERE test_id = %s", (test_id,))
        test_exists = cur.fetchone()

        if not test_exists:
            print(f"Error: Test ID {test_id} does not exist.")
            flash("This test doesn't exist.")
            return patients()

        # Both IDs exist, proceed to insert into patienttakemedicaltest table
        date_taken = datetime.date.today()
        next_date_to_take = date_taken + timedelta(weeks=1)
        date_taken_str = date_taken.strftime('%Y-%m-%d')
        next_date_to_take_str = next_date_to_take.strftime('%Y-%m-%d')
        print(date_taken_str)
        print(next_date_to_take_str)
        cur.execute(
            "INSERT INTO patienttakemedicaltest (PatientID, test_id, date_taken, next_date_to_take) VALUES (%s, %s, %s, %s)",
            (patient_id, test_id, date_taken, next_date_to_take)
        )

        # Commit the transaction
        mysql.connection.commit()

        # Verify the insertion
        cur.execute(
            "SELECT * FROM patienttakemedicaltest WHERE PatientID = %s AND test_id = %s AND date_taken = %s",
            (patient_id, test_id, date_taken_str)
        )
        inserted_record = cur.fetchone()
        print("Inserted record:", inserted_record)

        if inserted_record:
            # Retrieve patient name and test name for the flash message
            cur.execute("SELECT FirstName FROM patients WHERE PatientID = %s", (patient_id,))
            patient_name = cur.fetchone()[0]

            cur.execute("SELECT testType FROM medicaltest WHERE test_id = %s", (test_id,))
            test_name = cur.fetchone()[0]

            message = f"Patient {patient_name} with ID {patient_id} has been assigned the test: {test_name} today."
            print(message)
            flash(message)
        else:
            print(f"Failed to verify the insertion of test record for patient ID {patient_id} and test ID {test_id}.")
            flash("Test assignment verification failed.")

        return patients()

    except Exception as e:
        print(f"Database error: {str(e)}")
        flash("This Patient Has Already been assigned this test")
        return patients()

    finally:
        # Close the cursor
        cur.close()


@app.route('/assignDietPatient', methods=['GET', 'POST'])
def Assign_dietpatient():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()
            ID = request.form['DietID']
            PatientId = request.form['assignPatientID']

            # Check if the PatientId exists in the patients table
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM patients WHERE PatientID = %s", (PatientId,))
            patient_exists = cur.fetchone()[0]

            if patient_exists == 0:
                flash(f"No patient found with ID {PatientId}", "error")
                return diets()

            # Check if the membership is already assigned to a patient
            cur.execute("SELECT * FROM diet WHERE DietID = %s", (ID,))
            result = cur.fetchone()

            if result is None:
                flash(f"No Diet found with ID {ID}", "error")
                return diets()

            current_patient_id = result[0]


            # Perform the assignment if the membership is not already assigned
            update_query = "UPDATE patients SET DietID = %s WHERE PatientID = %s"
            update_data = (ID ,PatientId)

            # Execute the update query
            rows_affected = cur.execute(update_query, update_data)
            conn.commit()
            cur.close()

            if rows_affected == 0:
                flash(f"No Diet found with ID {ID}", "error")
            else:
                flash("Diet assigned to patient successfully!", "success")

            return diets()
        except Exception as e:
            flash(f"This Patient has already been assigned a Diet, Enter another patient", "error")
            print(f"Error updating memberships: {e}")

            return diets()
    else:
        return diets()






#LEENA **********************************************************


def get_nutritionist_data():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM nutritionist WHERE active like 'active'")
        fetchdata = cur.fetchall()
        cur.close()
        return fetchdata
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/add_nutritionist', methods=['GET', 'POST'])
def insert_nutritionist():
    if request.method == 'POST':
        try:
            global start_id
            # Get data from the form
            conn = mysql.connection
            nutritionistName = request.form['nutritionistName']
            nutritionistPhoneNumber = request.form['nutritionistPhoneNumber']
            salary = request.form['salary']
            VisitsNumber = request.form['VisitsNumber']
            nutritionistEmail = request.form['nutritionistEmail']
            shiftHours = request.form['shiftHours']
            absenceNum = request.form['absenceNum']
            room_duration = request.form['room_duration']
            room_id = request.form['room_id']

            # Insert data into the "nutritionist" table
            insert_query = "INSERT INTO nutritionist (nutritionistName, nutritionistPhoneNumber, salary, VisitsNumber, email, shiftHours, absenceNum,room_duration,room_id) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s)"
            nutritionist_data = (
            nutritionistName, nutritionistPhoneNumber, salary, VisitsNumber, nutritionistEmail, shiftHours, absenceNum,
            room_duration, room_id)
            print(f"data====={nutritionist_data}")
            cur = conn.cursor()
            cur.execute(insert_query, nutritionist_data)
            update_query = "UPDATE CheckupRoom SET availability_status = 'occupied' WHERE room_id = %s"
            cur.execute(update_query, (room_id,))
            # Commit changes and close the connection
            conn.commit()
            cur.close()
            print("Nutritionist inserted successfully!")
            # Redirect back to the home page after adding a new nutritionist
            flash("Nutritionist inserted successfully!", "success")
            # Redirect back to the home page after adding a new nutritionist
            data = get_nutritionist_data()
            return render_template('nutritionist.html', nutritionists=data)
        except Exception as e:
            # Check if the error is due to duplicate entry
            if "1062" in str(e):
                flash("Error: Phone number or email already exists.", "error")
            else:
                flash(f"Error inserting nutritionist: {e}", "error")
            data = get_nutritionist_data()
            return render_template('nutritionist.html', nutritionists=data)

    else:
        data = get_nutritionist_data()
        return render_template('nutritionist.html', nutritionists=data)


@app.route('/update_nutritionist', methods=['GET', 'POST'])
def update_nutritionist():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()
            ID = request.form['nutritionistID']
            nutritionistName = request.form['nutritionistName']
            nutritionistPhoneNumber = request.form['nutritionistPhoneNumber']
            salary = request.form['salary']
            VisitsNumber = request.form['VisitsNumber']
            nutritionistEmail = request.form['nutritionistEmail']
            shiftHours = request.form['shiftHours']
            absenceNum = request.form['absenceNum']
            room_duration = request.form['room_duration']
            room_id = request.form['room_id']

            check_query = "SELECT * FROM nutritionist WHERE nutritionistID = %s and active like 'active' "
            cur.execute(check_query, (ID,))
            existing_nutritionist = cur.fetchone()
            if not existing_nutritionist:
                data = get_nutritionist_data()
                flash("Error: The requested nutritionist doesnt exist. Please choose a different ID.", "error")
                return render_template('nutritionist.html', nutritionists=data)

            update_query = "UPDATE nutritionist SET"
            update_data = []
            if nutritionistName:
                update_query += " nutritionistName=%s,"
                update_data.append(nutritionistName)
            if nutritionistPhoneNumber:
                update_query += " nutritionistPhoneNumber=%s,"
                update_data.append(nutritionistPhoneNumber)
            if salary:
                update_query += " salary=%s,"
                update_data.append(salary)
            if VisitsNumber:
                update_query += " VisitsNumber=%s,"
                update_data.append(VisitsNumber)
            if nutritionistEmail:
                update_query += " email=%s,"
                update_data.append(nutritionistEmail)
            if shiftHours:
                update_query += " shiftHours=%s,"
                update_data.append(shiftHours)
            if absenceNum:
                update_query += " absenceNumber=%s,"
                update_data.append(absenceNum)
            if room_duration:
                update_query += " room_duration=%s,"
                update_data.append(room_duration)
            if room_id:
                update_query += " room_id=%s,"
                room_update_query = "UPDATE CheckupRoom SET availability_status = 'occupied' WHERE room_id = %s"
                cur.execute(room_update_query, (room_id,))
                update_data.append(room_id)

            # Remove the trailing comma and close the SET clause
            update_query = update_query.rstrip(',')
            update_query += " WHERE nutritionistID=%s"

            # Append the nutritionistID to the update_values list
            update_data.append(ID)

            # Execute the update query

            cur.execute(update_query, update_data)
            conn.commit()
            cur.close()
            print("Nutritionist updated successfully!")
            flash("Nutritionist updated successfully!.", "success")

            data = get_nutritionist_data()
            return render_template('nutritionist.html', nutritionists=data)
        except Exception as e:
            print(f"Error updating nutritionist: {e}")
            flash("Error: An error occurred while Updating nutritionist Data.", "error")
            data = get_nutritionist_data()
            return render_template('nutritionist.html',
                                   nutritionists=data)  # Render the home template in case of an error

    else:
        data = get_nutritionist_data()
        return render_template('nutritionist.html',
                               nutritionists=data)  # Render the add nutritionist form for GET requests


def select_by_salary(table, min_salary, max_salary):
    try:
        conn = mysql.connection
        cur = conn.cursor()
        if table == "nutritionist":
            # SQL query to select nutritionists within the salary range
            select_query = "SELECT * FROM nutritionist WHERE salary BETWEEN %s AND %s and WHERE active like 'active'order by salary desc "
            cur.execute(select_query, (min_salary, max_salary))
            nutritionists = cur.fetchall()  # Fetch all matching rows
            cur.close()  # Close the cursor
            print(f"Selecting nutritionists successfully!")
            return nutritionists  # Return the fetched nutritionists as a list of dictionaries

        elif table == "lab_technician":
            # SQL query to select lab technicians within the salary range
            select_query = "SELECT * FROM lab_technician WHERE salary BETWEEN %s AND %s and  active like 'active'"
            cur.execute(select_query, (min_salary, max_salary))
            lab_technicians = cur.fetchall()  # Fetch all matching rows
            cur.close()  # Close the cursor

            print(f"Selecting lab technicians successfully! {lab_technicians}")
            return lab_technicians  # Return the fetched lab technicians as a list of dictionaries

        else:
            print(f"Error: Unknown table '{table}' specified")
            return []  # Return an empty list if an unknown table is specified

    except Exception as e:
        print(f"Error fetching {table} by salary: {e}")
        return []  # Return an empty list if an error occurs


# @app.route('/salary', methods=['GET', 'POST'])
@app.route('/nutritionist', methods=['GET', 'POST'])
def salary():
    if request.method == 'POST':
        try:
            return render_template('nutritionist.html')

        except Exception as e:
            print(f"Error processing request: {e}")
            return "Internal Server Error", 500
    else:
        print(f"inside if{request.method}")
        data = get_nutritionist_data()
        return render_template('nutritionist.html', nutritionists=data)


@app.route('/delete_nutritionist', methods=['GET', 'POST'])
def delete_nutritionist():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()

            ID = request.form.get('nutritionistID')  # Get the nutritionist ID from the form

            # Check if the nutritionist exists
            check_query = "SELECT room_id FROM nutritionist WHERE nutritionistID = %s"
            cur.execute(check_query, (ID,))
            existing_nutritionist = cur.fetchone()

            if not existing_nutritionist:
                flash(f"Error: Nutritionist with ID:{ID} doesn't exist. Please choose a different ID.", "error")
                data = get_nutritionist_data()
                return render_template('nutritionist.html', nutritionists=data)

            # Get the current date
            current_date = datetime.date.today()

            # Update the nutritionist's status to 'dismissed' and set the dismissedDate
            update_nutritionist_query = """
                UPDATE nutritionist 
                SET active = 'dismissed', dismissedDate = %s 
                WHERE nutritionistID = %s
            """
            cur.execute(update_nutritionist_query, (current_date, ID))

            # Update the availability status of the related check-up room
            room_id = existing_nutritionist[0]  # Access the first element of the tuple
            update_room_query = "UPDATE CheckupRoom SET availability_status = 'available' WHERE room_id = %s"
            cur.execute(update_room_query, (room_id,))

            conn.commit()
            cur.close()

            flash(f"Nutritionist with ID:{ID} was dismissed successfully!", "success")
            data = get_nutritionist_data()
            return render_template('nutritionist.html', nutritionists=data)
        except Exception as e:
            print(f"Error in deleting nutritionist: {e}")
            flash(f"Error: There was an error in dismissing the nutritionist.", "error")
            data = get_nutritionist_data()
            return render_template('nutritionist.html', nutritionists=data)
    else:
        data = get_nutritionist_data()
        return render_template('nutritionist.html', nutritionists=data)


@app.route('/clear_all_nutritionists', methods=['GET', 'POST'])
def clear_all_nutritionists():
    global conn

    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()
            cur.execute("UPDATE nutritionist SET active = 'dismissed', dismissedDate = CURDATE()")
            conn.commit()
            flash("All nutritionist data marked as dismissed successfully!", "success")
            print("All nutritionist data marked as dismissed successfully!")
            cur.close()
            data = get_nutritionist_data()
            return render_template('nutritionist.html', nutritionists=data)
        except Exception as e:
            print(f"Error marking nutritionist data as dismissed: {e}")
            flash("An error occurred while marking nutritionist data as dismissed", "error")
            conn.rollback()
            data = get_nutritionist_data()
            return render_template('nutritionist.html', nutritionists=data)
    else:
        return render_template('nutritionist.html')


@app.route('/search_nutritionists', methods=['GET', 'POST'])
def search_nutritionists():
    global cur, conn
    try:
        search_value = ""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['searchCriteria']
        if search_criteria == "id":
            search_value = request.form['idInput']
            search_criteria = "nutritionistID"
        elif search_criteria == "shifthours":
            search_value = request.form['shifthoursInput']
            search_criteria = "shiftHours"
        elif search_criteria == "absence":
            search_value = request.form['absenceInput']
            search_criteria = "absenceNum"
        elif search_criteria == "phoneNumber":
            search_value = request.form['phoneInput']
            search_criteria = "nutritionistPhoneNumber"
        elif search_criteria == "name":
            search_value = request.form['nameInput']
            search_criteria = "nutritionistName"
        elif search_criteria == "email":
            search_value = request.form['emailInput']
            search_criteria = "email"
        elif search_criteria == "salary":
            search_value = request.form['salaryInput']
            search_criteria = "salary"
        elif search_criteria == "room_duration":
            search_value = request.form['roomDurationInput']
            search_criteria = "room_duration"
        elif search_criteria == "room_id":
            search_value = request.form['roomIdInput']
            search_criteria = "room_id"
        elif search_criteria == "salaryRange":
            min_salary = request.form['minSalary']
            max_salary = request.form['maxSalary']
            search_query = """
                SELECT * FROM nutritionist 
                WHERE salary BETWEEN %s AND %s 
                AND active like 'active'
            """
            cur.execute(search_query, (min_salary, max_salary))
            nutritionists = cur.fetchall()
            cur.close()
            if not nutritionists:
                flash("Could not find searched Data!", "fail")
            return render_template('nutritionist.html', nutritionists=nutritionists)
        elif search_criteria == "searchAll":
            search_query = "SELECT * FROM nutritionist WHERE active like 'active'"
            cur.execute(search_query)
            nutritionists = cur.fetchall()
            cur.close()
            if not nutritionists:
                flash("Could not find searched Data!", "fail")
            return render_template('nutritionist.html', nutritionists=nutritionists)
        elif search_criteria == "salaryDeduction":
            nutritionist_id = request.form['nutritionistIdInput']
            if not nutritionist_id:
                search_query = """
                    SELECT
                        nutritionistID,
                        nutritionistName,
                        ROUND((salary / VisitsNumber) / shiftHours, 2) AS paid_per_hour,
                        absenceNum,
                        salary,
                        ROUND(salary - (absenceNum * (salary / VisitsNumber) ), 2) AS salary_after_deduction
                    FROM
                        nutritionist
                    WHERE active like 'active'
                    ORDER BY
                        absenceNum DESC;
                """
                cur.execute(search_query)
            else:
                search_query = """
                    SELECT
                        nutritionistID,
                        nutritionistName,
                        ROUND((salary / VisitsNumber) / shiftHours, 2) AS paid_per_hour,
                        absenceNum,
                        salary,
                        ROUND(salary - (absenceNum * (salary / VisitsNumber) ), 2) AS salary_after_deduction
                    FROM
                        nutritionist
                    WHERE nutritionistID = %s AND active like 'active'
                    ORDER BY
                        absenceNum DESC;
                """
                cur.execute(search_query, (nutritionist_id,))
            nutritionists = cur.fetchall()
            cur.close()
            if nutritionists:
                flash("Nutritionist data retrieved successfully!", "success")
                return render_template('nutritionist.html', display_salary_deduction=nutritionists,
                                       search_criteria=search_criteria)
            else:
                flash("Could not find searched Data!", "error")
                data = get_nutritionist_data()
                return render_template('nutritionist.html', nutritionists=data)
        elif search_criteria == "search_room":
            nutritionist_id = request.form['nutritionistIdInput']
            search_query = """
                SELECT 
                    cr.room_id, 
                    cr.special_requirements, 
                    cr.availability_status 
                FROM 
                    CheckupRoom cr 
                JOIN 
                    nutritionist n ON cr.room_id = n.room_id 
                WHERE 
                    n.nutritionistID = %s AND n.active like 'active';
            """
            cur.execute(search_query, (nutritionist_id,))
            checkup_rooms = cur.fetchall()
            cur.close()
            if checkup_rooms:
                flash("Nutritionist data retrieved successfully!", "success")
            else:
                flash("Could not find searched Data!", "error")
                data = get_nutritionist_data()
                return render_template('nutritionist.html', nutritionists=data)
            return render_template('nutritionist.html', checkup_rooms=checkup_rooms, search_criteria=search_criteria)
        search_query = f"SELECT * FROM nutritionist WHERE {search_criteria} LIKE %s AND active like 'active'"
        term_with_percent = f"{search_value}%"
        cur.execute(search_query, (term_with_percent,))
        nutritionists = cur.fetchall()
        cur.close()
        if nutritionists:
            flash("Nutritionist data retrieved successfully!", "success")
            return render_template('nutritionist.html', nutritionists=nutritionists)
    except Exception as e:
        print(f"Error searching nutritionist: {e}")
        flash("An error occurred while searching nutritionist data: Could not find searched Data", "error")
        return render_template('nutritionist.html')
    flash("An error occurred while searching nutritionist data: Could not find searched Data", "error")
    conn.rollback()
    data = get_nutritionist_data()
    return render_template('nutritionist.html', nutritionists=data)


def get_nutritionist_salaries_stats():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        query = "SELECT SUM(salary), AVG(salary) FROM nutritionist WHERE active like 'active' "
        cur.execute(query)

        result = cur.fetchone()
        salary_sum = result[0] if result[0] is not None else 0
        salary_avg = result[1] if result[1] is not None else 0

        cur.close()

        print(f"Total sum of salaries: {salary_sum}")
        print(f"Average salary: {salary_avg}")

        return salary_sum, salary_avg
    except Exception as e:
        print(f"Error calculating salary statistics: {e}")
        return 0, 0


@app.route('/get_nutritionist_salary_stats', methods=['GET'])
def get_nutritionist_salary_stats():
    salary_sum, salary_avg = get_nutritionist_salaries_stats()
    return jsonify({
        'salary_sum': salary_sum,
        'salary_avg': salary_avg
    })


# ********************************************************************************************

def get_lab_technician_data():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM lab_technician where active like 'active'")
        fetchdata = cur.fetchall()

        cur.close()  # Close the cursor outside the loop
        return fetchdata
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/update_LabTechnicians', methods=['GET', 'POST'])
def update_LabTechnicians():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            technicianID = request.form['technicianID']
            technicianName = request.form.get('technicianName')
            technicianPhoneNumber = request.form.get('technicianPhoneNumber')
            salary = request.form.get('salary')
            visitsPerMonth = request.form.get('visitsPerMonth')
            technicianEmail = request.form.get('technicianEmail')
            tools = request.form.get('tools')
            lab_id = request.form.get('lab_id')
            shiftHours = request.form.get('shiftHours')
            cur = conn.cursor()

            check_query = "SELECT * FROM lab_technician WHERE technicianID = %s and  active like 'active'"
            cur.execute(check_query, (technicianID,))
            existing = cur.fetchone()
            if not existing:
                flash("Error: The requested lab technician doesnt exist. Please choose a different ID.", "error")
                data = get_lab_technician_data()
                return render_template('lab_technician.html', technicians=data)

            update_query = "UPDATE lab_technician SET"
            update_data = []
            if technicianName:
                update_query += " technicianName=%s,"
                update_data.append(technicianName)
            if shiftHours:
                update_query += " shiftHours=%s,"
                update_data.append(shiftHours)

            if technicianPhoneNumber:
                update_query += " technicianPhoneNumber=%s,"
                update_data.append(technicianPhoneNumber)
            if salary:
                update_query += " salary=%s,"
                update_data.append(salary)
            if visitsPerMonth:
                update_query += " VisitsNumber=%s,"
                update_data.append(visitsPerMonth)
            if technicianEmail:
                update_query += " technicianEmail=%s,"
                update_data.append(technicianEmail)
            if tools:
                update_query += " tools=%s,"
                update_data.append(tools)
            if lab_id:
                update_query += " lab_id=%s,"
                update_data.append(lab_id)
                room_update_query = "UPDATE LaboratoryRoom SET availability_status = 'occupied' WHERE lab_id = %s"
                cur.execute(room_update_query, (lab_id,))

            # Remove the trailing comma and close the SET clause
            update_query = update_query.rstrip(',')
            update_query += " WHERE technicianID=%s"

            # Append the technicianID to the update_data list
            update_data.append(technicianID)

            # Execute the update query

            cur.execute(update_query, update_data)
            conn.commit()
            cur.close()

            flash("Lab Technician updated successfully!", "success")
            print("Lab Technician updated successfully!")
            data = get_lab_technician_data()
            return render_template('lab_technician.html', technicians=data)
        except Exception as e:
            print(f"Error updating Lab Technician: {e}")
            flash(f"Error updating Lab Technician: {e}", "error")
            data = get_lab_technician_data()
            return render_template('lab_technician.html', technicians=data)

    else:
        return render_template('lab_technician.html')


@app.route('/add_lab_technician', methods=['GET', 'POST'])
def insert_lab_technician():
    try:
        print("hi")
        # Get data from the form
        conn = mysql.connection
        technicianName = request.form['technicianName']
        technicianPhoneNumber = request.form['technicianPhoneNumber']
        salary = request.form['salary']
        VisitsNumber = request.form['VisitsNumber']
        technicianEmail = request.form['technicianEmail']
        shiftHours = request.form['shiftHours']
        labID = request.form['lab_id']
        tools = request.form['tools']

        # Insert data into the "lab_technician" table
        insert_query = "INSERT INTO lab_technician (technicianName, technicianPhoneNumber, salary, VisitsNumber, technicianEmail, shiftHours,tools,lab_id) VALUES (%s,%s,%s,%s, %s, %s, %s, %s)"
        technician_data = (
        technicianName, technicianPhoneNumber, salary, VisitsNumber, technicianEmail, shiftHours, tools, labID)
        print(f"data====={technician_data}")
        cur = conn.cursor()
        cur.execute(insert_query, technician_data)
        update_query = "UPDATE LaboratoryRoom SET availability_status = 'occupied' WHERE lab_id = %s"
        cur.execute(update_query, (labID,))
        # Commit changes and close the connection
        conn.commit()
        cur.close()
        print("Lab technician inserted successfully!")
        # Redirect back to the home page after adding a new lab technician
        flash("Lab technician inserted successfully!", "success")
        data = get_lab_technician_data()
        return render_template('lab_technician.html', technicians=data)
    except Exception as e:
        # Check if the error is due to duplicate entry
        if "1062" in str(e):
            flash("Error: Phone number or email already exists.", "error")

        else:
            flash(f"Error inserting lab technician: {e}", "error")
        data = get_lab_technician_data()
        return render_template('lab_technician.html', technicians=data)


@app.route('/clear_all_lab_technicians', methods=['GET', 'POST'])
def clear_all_lab_technicians():
    global conn
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()

            # Update the status of all lab technicians to 'dismissed'
            update_technicians_query = "UPDATE lab_technician SET active = 'dismissed'"
            cur.execute(update_technicians_query)

            # Update the lab ID status to 'available'
            update_lab_query = "UPDATE LaboratoryRoom SET availability_status = 'available' WHERE lab_id IN (SELECT lab_id FROM lab_technician)"
            cur.execute(update_lab_query)

            conn.commit()
            cur.close()
            flash("All lab technician data updated successfully!", "success")
            data = get_lab_technician_data()
            return render_template('lab_technician.html', technicians=data)

        except Exception as e:
            print(f"Error updating lab technician data: {e}")
            flash("An error occurred while updating lab technician data", "error")
            conn.rollback()
            data = get_lab_technician_data()
            return render_template('lab_technician.html', technicians=data)

    else:
        data = get_lab_technician_data()
        return render_template('lab_technician.html', technicians=data)


@app.route('/lab_technician', methods=['GET', 'POST'])
def lab_technician():
    if request.method == 'POST':
        try:

            data = get_lab_technician_data()
            return render_template('lab_technician.html', technicians=data)

        except Exception as e:
            print(f"Error processing request: {e}")
            return "Internal Server Error", 500
    else:
        data = get_lab_technician_data()
        return render_template('lab_technician.html', technicians=data)


@app.route('/delete_lab_technician', methods=['GET', 'POST'])
def delete_lab_technician():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()

            ID = request.form.get('deleteTechnicianID')  # Get the technician ID from the form

            check_query = "SELECT lab_id FROM lab_technician WHERE technicianID = %s"
            cur.execute(check_query, (ID,))
            existing_technician = cur.fetchone()
            if not existing_technician:
                flash(f"Error: Lab Technician with ID: {ID} doesn't exist. Please choose a different ID.", "error")
                data = get_lab_technician_data()
                return render_template('lab_technician.html', technicians=data)

            # Get the current date
            current_date = datetime.date.today()

            # Update the technician's status to 'dismissed' and set the dismissedDate
            update_technician_query = """
                UPDATE lab_technician 
                SET active = 'dismissed', dismissedDate = %s 
                WHERE technicianID = %s
            """
            cur.execute(update_technician_query, (current_date, ID))

            # Update the availability status of the related lab room
            lab_id = existing_technician[0]  # Accessing the first element of the tuple
            update_lab_query = "UPDATE LaboratoryRoom SET availability_status = 'available' WHERE lab_id = %s"
            cur.execute(update_lab_query, (lab_id,))

            conn.commit()
            cur.close()

            flash(f"Lab Technician with ID: {ID} has been dismissed successfully.", "success")
            data = get_lab_technician_data()
            return render_template('lab_technician.html', technicians=data)

        except Exception as e:
            print(f"Error in dismissing lab technician: {e}")
            flash(f"Error in dismissing lab technician: {e}", "error")
            data = get_lab_technician_data()
            return render_template('lab_technician.html', technicians=data)

    else:
        data = get_lab_technician_data()
        return render_template('lab_technician.html', technicians=data)


@app.route('/search_lab_technicians', methods=['GET', 'POST'])
def search_lab_technicians():
    global cur, conn
    try:
        search_value = ""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['searchCriteria']
        if search_criteria == "id":
            search_value = request.form['idInput']
            search_criteria = "technicianID"
        elif search_criteria == "shiftHours":
            search_value = request.form['shiftHoursInput']
        elif search_criteria == "tools":
            search_value = request.form['toolsInput']
            search_criteria = "tools"
        elif search_criteria == "phoneNumber":
            search_value = request.form['phoneInput']
            search_criteria = "technicianPhoneNumber"
        elif search_criteria == "name":
            search_value = request.form['nameInput']
            search_criteria = "technicianName"
        elif search_criteria == "email":
            search_criteria = "technicianEmail"
            search_value = request.form['emailInput']
        elif search_criteria == "salary":
            search_value = request.form['salaryInput']
        elif search_criteria == "lab_id":
            search_value = request.form['labIDInput']
        elif search_criteria == "salaryRange":
            min_salary = request.form['minSalary']
            max_salary = request.form['maxSalary']
            lab_technicians = select_by_salary("lab_technician", min_salary, max_salary)
            if not lab_technicians:
                flash("Could not find searched Data!", "fail")
            else:
                flash("Lab technician data retrieved successfully!", "success")
            return render_template('lab_technician.html', technicians=lab_technicians)
        elif search_criteria == "select_all":
            lab_technicians = get_lab_technician_data()
            if not lab_technicians:
                flash("Could not find searched Data!", "fail")
            else:
                flash("Lab technician data retrieved successfully!", "success")
            return render_template('lab_technician.html', technicians=lab_technicians)
        elif search_criteria == "search_lab_room":
            technician_id = request.form['technicianIdInput']
            search_query = """
                SELECT
                    lr.lab_id,
                    lr.test_id,
                    lr.availability_status,
                    lr.special_requirements
                FROM
                    LaboratoryRoom lr
                JOIN
                    lab_technician lt ON lr.lab_id = lt.lab_id
                WHERE
                    lt.technicianID = %s
                    AND lt.active like 'active'
            """
            cur.execute(search_query, (technician_id,))
            lab_rooms = cur.fetchall()
            cur.close()
            if lab_rooms:
                flash("Lab technician data retrieved successfully!", "success")
            else:
                flash("Could not find searched Data!", "fail")

            return render_template('lab_technician.html', lab_rooms=lab_rooms, search_criteria=search_criteria)

        search_query = f"SELECT * FROM lab_technician WHERE {search_criteria} LIKE %s AND active like 'active'"
        term_with_percent = f"{search_value}"
        cur.execute(search_query, (term_with_percent,))
        lab_technicians = cur.fetchall()
        cur.close()

        if lab_technicians:
            return render_template('lab_technician.html', technicians=lab_technicians)
    except Exception as e:
        print(f"Error searching lab technician: {e}")
        flash(f"Error searching lab technician: {e}", "error")
        data = get_lab_technician_data()
        return render_template('lab_technician.html', technicians=data)

    flash("An error occurred while searching lab technician data: Could not find searched data", "error")
    conn.rollback()
    data = get_lab_technician_data()
    return render_template('lab_technician.html', technicians=data)


def get_technician_salaries_stats():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        # SQL query to calculate the sum and average of salaries
        query = "SELECT SUM(salary), AVG(salary) FROM lab_technician where active like 'active'"
        cur.execute(query)

        result = cur.fetchone()
        salary_sum = result[0] if result[0] is not None else 0
        salary_avg = result[1] if result[1] is not None else 0

        cur.close()

        print(f"Total sum of salaries: {salary_sum}")
        print(f"Average salary: {salary_avg}")

        return salary_sum, salary_avg
    except Exception as e:
        print(f"Error calculating salary statistics: {e}")
        return 0, 0


@app.route('/get_salary_stats', methods=['GET'])
def get_salary_stats():
    salary_sum, salary_avg = get_technician_salaries_stats()
    return jsonify({
        'salary_sum': salary_sum,
        'salary_avg': salary_avg
    })


# ****************************************************************************************************
def get_checkuproom_data():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM CheckupRoom")
        fetchdata = cur.fetchall()
        cur.close()
        checkup_rooms_list = [
            {
                'room_id': room[0],
                'special_requirements': room[1],
                'availability_status': room[2]
            } for room in fetchdata
        ]
        return checkup_rooms_list
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/checkuproom', methods=['GET', 'POST'])
def checkuproom():
    if request.method == 'POST':
        try:

            return render_template('checkuproom.html')

        except Exception as e:
            print(f"Error processing request: {e}")
            return "Internal Server Error", 500
    else:
        data = get_checkuproom_data()
        return render_template('checkuproom.html', checkup_rooms=data)


@app.route('/add_checkup_room', methods=['GET', 'POST'])
def insert_checkup_room():
    if request.method == 'POST':
        try:
            # Get data from the form
            conn = mysql.connection
            special_requirements = request.form['special_requirements']
            availability_status = request.form['availability_status']

            # Insert data into the "CheckupRoom" table
            insert_query = "INSERT INTO CheckupRoom ( special_requirements, availability_status) VALUES ( %s, %s)"
            room_data = (special_requirements, availability_status)

            cur = conn.cursor()
            cur.execute(insert_query, room_data)

            # Commit changes and close the connection
            conn.commit()
            cur.close()

            # Redirect back to the home page after adding a new check-up room
            flash("Check-up room inserted successfully!", "success")
            data = get_checkuproom_data()
            return render_template('checkuproom.html', checkup_rooms=data)
        except Exception as e:
            # Check if the error is due to duplicate entry
            if "1062" in str(e):
                flash("Error: Room ID already exists.", "error")
            else:
                flash(f"Error inserting check-up room: {e}", "error")
            data = get_checkuproom_data()
            return render_template('checkuproom.html', checkup_rooms=data)

    else:
        data = get_checkuproom_data()
        return render_template('checkuproom.html', checkup_rooms=data)


@app.route('/delete_checkup_room', methods=['GET', 'POST'])
def delete_checkup_room():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()

            room_id = request.form.get('room_id')  # Get the room ID from the form

            check_query = "SELECT * FROM CheckupRoom WHERE room_id = %s"
            cur.execute(check_query, (room_id,))
            existing_room = cur.fetchone()
            if not existing_room:
                flash(f"Error: Check-up room with ID: {room_id} doesn't exist. Please choose a different ID.", "error")
                return render_template('checkuproom.html')

            delete_query = "DELETE FROM CheckupRoom WHERE room_id = %s"
            cur.execute(delete_query, (room_id,))
            conn.commit()
            cur.close()

            flash(f"Check-up room with ID: {room_id} has been successfully deleted.", "success")
            return render_template('checkuproom.html')
        except Exception as e:
            print(f"Error in deleting check-up room: {e}")
            flash(f"Error in deleting check-up room: {e}", "error")
            return render_template('checkuproom.html')
    else:
        return render_template('checkuproom.html')


@app.route('/update_checkup_room', methods=['POST'])
def update_checkup_room():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        # Extract data from the form
        room_id = request.form['room_id']
        special_requirements = request.form.get('special_requirements')
        availability_status = request.form.get('availability_status')

        # Check if the room with the given ID exists
        check_query = "SELECT * FROM CheckupRoom WHERE room_id = %s"
        cur.execute(check_query, (room_id,))
        existing_room = cur.fetchone()
        if not existing_room:
            flash("Error: Room with the provided ID doesn't exist. Please choose a different ID.", "error")
            data = get_checkuproom_data()
            return render_template('checkuproom.html', checkup_rooms=data)

        # Build the UPDATE query dynamically based on provided fields
        update_query = "UPDATE CheckupRoom SET "
        update_data = []
        if special_requirements:
            update_query += "special_requirements = %s, "
            update_data.append(special_requirements)
        if availability_status:
            update_query += "availability_status = %s, "
            update_data.append(availability_status)

        # Remove the trailing comma and space from the query
        update_query = update_query.rstrip(', ')

        # Append the WHERE clause to the query
        update_query += " WHERE room_id = %s"
        update_data.append(room_id)

        # Execute the UPDATE query
        cur.execute(update_query, update_data)
        conn.commit()
        cur.close()

        flash("Check-up room information updated successfully!", "success")
        data = get_checkuproom_data()
        return render_template('checkuproom.html', checkup_rooms=data)

    except Exception as e:
        print(f"Error updating check-up room: {e}")
        flash(f"Error updating check-up room: {e}", "error")
        data = get_checkuproom_data()
        return render_template('checkuproom.html', checkup_rooms=data)

    data = get_checkuproom_data()
    return render_template('checkuproom.html', checkup_rooms=data)


@app.route('/search_checkup_rooms', methods=['POST'])
def search_checkup_rooms():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        # Get the search criteria from the form
        search_criteria = request.form['searchCriteria']

        # Initialize the SQL query and search value
        search_query = ""
        search_value = ()

        # Modify the SQL query based on the selected search criteria
        if search_criteria == "room_id":
            search_value = (request.form['roomIDInput'],)
            search_query = "SELECT * FROM CheckupRoom WHERE room_id = %s"

        elif search_criteria == "special_requirements":
            search_value = (f"%{request.form['specialRequirementsInput']}%",)
            search_query = "SELECT * FROM CheckupRoom WHERE special_requirements LIKE %s"

        elif search_criteria == "availability_status":
            search_value = (request.form['availabilityStatusInput'],)
            search_query = "SELECT * FROM CheckupRoom WHERE availability_status = %s"

        elif search_criteria == "request_nutritionist":

            search_value = (f"%{request.form['roomIDInput']}%",)
            print(search_value)
            search_query = """
                SELECT 
                    CheckupRoom.room_id, 
                    CheckupRoom.availability_status,
                    nutritionist.nutritionistID, 
                    nutritionist.nutritionistName, 
                    nutritionist.nutritionistPhoneNumber, 
                    nutritionist.VisitsNumber, 
                    nutritionist.email, 
                    nutritionist.shiftHours, 
                    nutritionist.room_duration
                FROM CheckupRoom 
                LEFT JOIN nutritionist 
                ON CheckupRoom.room_id = nutritionist.room_id
                WHERE CheckupRoom.room_id like  %s
            """

        elif search_criteria == "select_all":
            search_query = "SELECT * FROM CheckupRoom"
            search_value = ()

        # Execute the SQL query with the appropriate search value
        cur.execute(search_query, search_value)
        checkup_rooms = cur.fetchall()
        cur.close()

        # Handle the "request_nutritionist" criteria separately
        if search_criteria == "request_nutritionist":
            return render_template('checkuproom.html', rooms=checkup_rooms, search_criteria=search_criteria)

        # Initialize a list to store the retrieved check-up rooms
        checkup_rooms_list = [
            {
                'room_id': room[0],
                'special_requirements': room[1],
                'availability_status': room[2]
            } for room in checkup_rooms
        ]

        # Flash a success message and render the template with the search results
        if checkup_rooms:
            flash("Checkup rooms retrieved successfully!", "success")
            return render_template('checkuproom.html', checkup_rooms=checkup_rooms_list,
                                   search_criteria=search_criteria)
        else:
            flash("No data found for the given criteria.", "failure")
            data = get_checkuproom_data()
            return render_template('checkuproom.html', checkup_rooms=data)

    except Exception as e:
        print(f"Error searching check-up rooms: {e}")
        flash("An error occurred while searching check-up rooms data.", "error")
        data = get_checkuproom_data()
        return render_template('checkuproom.html', checkup_rooms=data)


@app.route('/clear_all_checkuprooms', methods=['GET', 'POST'])
def clear_all_checkuprooms():
    global conn

    if request.method == 'POST':
        try:
            print("hi")
            conn = mysql.connection
            cur = conn.cursor()
            cur.execute("DELETE FROM CheckupRoom")  # Pass the ID as a tuple
            conn.commit()
            flash("All checkup room data cleared successfully!", "success")
            print("checkup room  data cleared successfully!")
            cur.close()
            return render_template('checkuproom.html')

        except Exception as e:
            print(f"Error clearing nutritionist data: {e}")
            flash("An error occurred while clearing nutritionist data", "error")
            conn.rollback()
            return render_template('checkuproom.html')

    else:
        data = get_checkuproom_data()
        return render_template('checkuproom.html', checkup_rooms=data)


# **********************************************************************************************
def get_laboratoryroom_data():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM LaboratoryRoom")
        fetchdata = cur.fetchall()
        cur.close()
        return fetchdata
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/laboratoryroom', methods=['GET', 'POST'])
def laboratoryRoom():
    try:
        data = get_laboratoryroom_data()
        return render_template('laboratoryroom.html', laboratory_rooms=data)

    except Exception as e:
        print(f"Error processing request: {e}")
        return "Internal Server Error", 500


@app.route('/add_laboratory_room', methods=['GET', 'POST'])
def insert_laboratory_room():
    if request.method == 'POST':
        try:
            # Get data from the form
            conn = mysql.connection
            test_id = request.form['test_id']
            availability_status = request.form['availability_status']
            special_requirements = request.form['special_requirements']

            # Insert data into the "LaboratoryRoom" table
            insert_query = "INSERT INTO LaboratoryRoom ( test_id, availability_status, special_requirements) VALUES ( %s, %s, %s)"
            lab_data = (test_id, availability_status, special_requirements)

            cur = conn.cursor()
            cur.execute(insert_query, lab_data)

            # Commit changes and close the connection
            conn.commit()
            cur.close()

            # Redirect back to the home page after adding a new laboratory room
            flash("Laboratory room inserted successfully!", "success")
            data = get_laboratoryroom_data()
            return render_template('laboratoryroom.html', laboratory_rooms=data)

        except Exception as e:
            # Check if the error is due to duplicate entry
            if "1062" in str(e):
                flash("Error: Laboratory ID already exists.", "error")
            else:
                flash(f"Error inserting laboratory room: {e}", "error")
            data = get_laboratoryroom_data()
            return render_template('laboratoryroom.html', laboratory_rooms=data)

    else:
        data = get_laboratoryroom_data()
        return render_template('laboratoryroom.html', laboratory_rooms=data)


@app.route('/delete_laboratory_room', methods=['GET', 'POST'])
def delete_laboratory_room():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()

            lab_id = request.form.get('lab_id')  # Get the lab ID from the form

            check_query = "SELECT * FROM LaboratoryRoom WHERE lab_id = %s"
            cur.execute(check_query, (lab_id,))
            existing_room = cur.fetchone()
            if not existing_room:
                flash(f"Error: Laboratory room with ID: {lab_id} doesn't exist. Please choose a different ID.", "error")
                return render_template('laboratoryroom.html')

            delete_query = "DELETE FROM LaboratoryRoom WHERE lab_id = %s"
            cur.execute(delete_query, (lab_id,))
            conn.commit()
            cur.close()

            flash(f"Laboratory room with ID: {lab_id} has been successfully deleted.", "success")
            return render_template('laboratoryroom.html')
        except Exception as e:
            print(f"Error in deleting laboratory room: {e}")
            flash(f"Error in deleting laboratory room: {e}", "error")
            return render_template('laboratoryroom.html')
    else:
        return render_template('laboratoryroom.html')


@app.route('/update_laboratory_room', methods=['POST'])
def update_laboratory_room():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        # Extract data from the form
        lab_id = request.form['lab_id']
        test_id = request.form.get('test_id')
        availability_status = request.form.get('availability_status')
        special_requirements = request.form.get('special_requirements')

        # Check if the room with the given ID exists
        check_query = "SELECT * FROM LaboratoryRoom WHERE lab_id = %s"
        cur.execute(check_query, (lab_id,))
        existing_room = cur.fetchone()
        if not existing_room:
            flash("Error: Laboratory room with the provided ID doesn't exist. Please choose a different ID.", "error")
            data = get_laboratoryroom_data()
            return render_template('laboratoryroom.html', laboratory_rooms=data)

        # Build the UPDATE query dynamically based on provided fields
        update_query = "UPDATE LaboratoryRoom SET "
        update_data = []
        if test_id:
            update_query += "test_id = %s, "
            update_data.append(test_id)
        if availability_status:
            update_query += "availability_status = %s, "
            update_data.append(availability_status)
        if special_requirements:
            update_query += "special_requirements = %s, "
            update_data.append(special_requirements)

        # Remove the trailing comma and space from the query
        update_query = update_query.rstrip(', ')

        # Append the WHERE clause to the query
        update_query += " WHERE lab_id = %s"
        update_data.append(lab_id)

        # Execute the UPDATE query
        cur.execute(update_query, update_data)
        conn.commit()
        cur.close()

        flash("Laboratory room information updated successfully!", "success")
        data = get_laboratoryroom_data()
        return render_template('laboratoryroom.html', laboratory_rooms=data)

    except Exception as e:
        print(f"Error updating laboratory room: {e}")
        flash(f"Error updating laboratory room: {e}", "error")
        data = get_laboratoryroom_data()
        return render_template('laboratoryroom.html', laboratory_rooms=data)


@app.route('/search_laboratory_rooms', methods=['POST'])
def search_laboratory_rooms():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        search_criteria = request.form['searchCriteria']
        search_query = ""
        search_value = ()

        if search_criteria == "lab_id":
            search_value = (request.form['labIDInput'],)
            search_query = "SELECT * FROM LaboratoryRoom WHERE lab_id = %s"

        elif search_criteria == "test_id":
            search_value = (request.form['testIDInput'],)
            search_query = "SELECT * FROM LaboratoryRoom WHERE test_id = %s"

        elif search_criteria == "special_requirements":
            search_value = (f"%{request.form['specialRequirementsInput']}%",)
            search_query = "SELECT * FROM LaboratoryRoom WHERE special_requirements LIKE %s"

        elif search_criteria == "availability_status":
            search_value = (request.form['availabilityStatusInput'],)
            search_query = "SELECT * FROM LaboratoryRoom WHERE availability_status LIKE %s"

        elif search_criteria == "labTechnician_Uses_Laboratory":
            lab_id_input = request.form['labTechnician_Uses_LaboratoryInput']
            if lab_id_input:
                search_value = (lab_id_input,)
                search_query = """
                    SELECT 
                        LaboratoryRoom.lab_id, 
                        LaboratoryRoom.availability_status, 
                        lab_technician.technicianID, 
                        lab_technician.technicianName, 
                        lab_technician.technicianPhoneNumber,
                        lab_technician.VisitsNumber, 
                        lab_technician.technicianEmail, 
                        lab_technician.shiftHours, 
                        lab_technician.tools
                    FROM 
                        LaboratoryRoom 
                    LEFT JOIN 
                        lab_technician ON LaboratoryRoom.lab_id = lab_technician.lab_id 
                    WHERE 
                        LaboratoryRoom.lab_id like %s
                """
            else:
                search_query = """
                    SELECT 
                        LaboratoryRoom.lab_id, 
                        LaboratoryRoom.availability_status, 
                        lab_technician.technicianID, 
                        lab_technician.technicianName, 
                        lab_technician.technicianPhoneNumber,
                        lab_technician.VisitsNumber, 
                        lab_technician.technicianEmail, 
                        lab_technician.shiftHours, 
                        lab_technician.tools
                    FROM 
                        LaboratoryRoom 
                    LEFT JOIN 
                        lab_technician ON LaboratoryRoom.lab_id = lab_technician.lab_id 
                """
                search_value = ()

        elif search_criteria == "Test_DoneIn_Laboratory":
            lab_id_input = request.form['Test_DoneIn_LaboratoryInput']
            if lab_id_input:
                search_value = (lab_id_input,)
                search_query = """
                    SELECT LaboratoryRoom.lab_id, LaboratoryRoom.availability_status, 
                    MedicalTest.test_id, MedicalTest.testType 
                    FROM LaboratoryRoom 
                    LEFT JOIN MedicalTest ON LaboratoryRoom.test_id = MedicalTest.test_id 
                    WHERE LaboratoryRoom.lab_id = %s
                """
            else:
                search_query = """
                    SELECT LaboratoryRoom.lab_id, LaboratoryRoom.availability_status, 
                    MedicalTest.test_id, MedicalTest.testType 
                    FROM LaboratoryRoom 
                    LEFT JOIN MedicalTest ON LaboratoryRoom.test_id = MedicalTest.test_id
                """
                search_value = ()

        else:
            search_query = "SELECT * FROM LaboratoryRoom"
            search_value = ()

        cur.execute(search_query, search_value)
        laboratory_rooms = cur.fetchall()
        cur.close()
        flash("Laboratory room information retrieved successfully!", "success")

        if search_criteria == "labTechnician_Uses_Laboratory":
            return render_template('laboratoryroom.html', technician_data=laboratory_rooms,
                                   search_criteria=search_criteria)

        if search_criteria == "Test_DoneIn_Laboratory":
            return render_template('laboratoryroom.html', test_data=laboratory_rooms, search_criteria=search_criteria)

        if laboratory_rooms:
            flash("Laboratory rooms retrieved successfully!", "success")
            return render_template('laboratoryroom.html', laboratory_rooms=laboratory_rooms,
                                   search_criteria=search_criteria)
        else:
            flash("No data found for the given criteria.", "failure")
            data = get_laboratoryroom_data()
            return render_template('laboratoryroom.html', laboratory_rooms=data)

    except Exception as e:
        print(f"Error searching laboratory rooms: {e}")
        flash("An error occurred while searching laboratory rooms data.", "error")
        data = get_laboratoryroom_data()
        return render_template('laboratoryroom.html', laboratory_rooms=data)


@app.route('/clear_all_laboratory_rooms', methods=['GET', 'POST'])
def clear_all_laboratory_rooms():
    global conn
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()
            cur.execute("DELETE FROM LaboratoryRoom")  # Clear all records from LaboratoryRoom table
            conn.commit()
            flash("All laboratory room data cleared successfully!", "success")
            cur.close()
            return render_template('laboratoryroom.html')
        except Exception as e:
            print(f"Error clearing laboratory room data: {e}")
            flash("An error occurred while clearing laboratory room data", "error")
            conn.rollback()
            return render_template('laboratoryroom.html')
    else:
        return render_template('laboratoryroom.html')


# *************************************************************************************************

@app.route('/medicalTest', methods=['GET', 'POST'])
def medicalTest():
    try:
        data = get_medicalTest_data()
        return render_template('medicalTest.html', results=data, search_criteria="test_id")

    except Exception as e:
        print(f"Error processing request: {e}")

        return "Internal Server Error", 500


def get_medicalTest_data():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM MedicalTest")
        fetchdata = cur.fetchall()
        cur.close()
        return fetchdata
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/add_medicalTest', methods=['GET', 'POST'])
def add_medicalTest():
    if request.method == 'POST':
        try:
            print("helloooo")
            # Get data from the form
            conn = mysql.connection
            testType = request.form['testType']

            # Insert data into the "LaboratoryRoom" table
            insert_query = "INSERT INTO MedicalTest (testType) VALUES (%s)"
            test_data = (testType,)
            cur = conn.cursor()
            cur.execute(insert_query, test_data)

            # Commit changes and close the connection
            conn.commit()
            cur.close()

            # Redirect back to the home page after adding a new laboratory room
            flash("medical Test data inserted successfully!", "success")
            print("medical Test data inserted successfully!")
            data = get_medicalTest_data()
            return render_template('medicalTest.html', results=data, search_criteria="test_id")
        except Exception as e:
            # Check if the error is due to duplicate entry
            if "1062" in str(e):
                flash("Error: MedicalTest  ID already exists.", "error")
                print("error in inserting medical!")

            else:
                flash(f"Error inserting MedicalTest: {e}", "error")
                print(f"error in inserting medical{e}!")

            data = get_medicalTest_data()
            return render_template('medicalTest.html', results=data, search_criteria="test_id")
    else:
        data = get_medicalTest_data()
        return render_template('medicalTest.html', results=data, search_criteria="test_id")


@app.route('/update_medicalTest', methods=['GET', 'POST'])
def update_medicalTest():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        # Extract data from the form
        test_id = request.form['test_id']
        test_type = request.form['test_type']

        # Check if the test with the given ID exists
        check_query = "SELECT * FROM MedicalTest WHERE test_id = %s"
        cur.execute(check_query, (test_id,))
        existing_test = cur.fetchone()
        if not existing_test:
            flash("Error: Medical test with the provided ID doesn't exist. Please choose a different ID.", "error")
            data = get_medicalTest_data()
            return render_template('medicalTest.html', results=data, search_criteria="test_id")

        # Build the UPDATE query dynamically based on provided fields
        update_query = "UPDATE MedicalTest SET "
        update_data = []
        if test_type:
            update_query += "testType = %s, "
            update_data.append(test_type)

        # Remove the trailing comma and space from the query
        update_query = update_query.rstrip(', ')

        # Append the WHERE clause to the query
        update_query += " WHERE test_id = %s"
        update_data.append(test_id)

        # Execute the UPDATE query
        cur.execute(update_query, update_data)
        conn.commit()
        cur.close()

        flash("Medical test information updated successfully!", "success")
        data = get_medicalTest_data()
        return render_template('medicalTest.html', results=data, search_criteria="test_id")
    except Exception as e:
        print(f"Error updating medical test: {e}")
        flash(f"Error updating medical test: {e}", "error")
        data = get_medicalTest_data()
        return render_template('medicalTest.html', results=data, search_criteria="test_id")


@app.route('/delete_medicalTest', methods=['GET', 'POST'])
def delete_medical_test():
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()

            test_id = request.form.get('test_id')  # Get the test ID from the form

            check_query = "SELECT * FROM MedicalTest WHERE test_id = %s"
            cur.execute(check_query, (test_id,))
            existing_test = cur.fetchone()
            if not existing_test:
                flash(f"Error: Medical test with ID: {test_id} doesn't exist. Please choose a different ID.", "error")
                return render_template('medicalTest.html')

            delete_query = "DELETE FROM MedicalTest WHERE test_id = %s"
            cur.execute(delete_query, (test_id,))
            conn.commit()
            cur.close()

            flash(f"Medical test with ID: {test_id} has been successfully deleted.", "success")
            data = get_medicalTest_data()
            return render_template('medicalTest.html', results=data, search_criteria="test_id")

        except Exception as e:
            print(f"Error in deleting medical test: {e}")
            flash(f"Error in deleting medical test: {e}", "error")
            data = get_medicalTest_data()
            return render_template('medicalTest.html', results=data, search_criteria="test_id")
    else:
        data = get_medicalTest_data()
        return render_template('medicalTest.html', results=data, search_criteria="test_id")


@app.route('/clear_all_medicalTest', methods=['GET', 'POST'])
def clear_all_medicalTest():
    global conn
    if request.method == 'POST':
        try:
            conn = mysql.connection
            cur = conn.cursor()
            cur.execute("DELETE FROM MedicalTest")  # Clear all records from LaboratoryRoom table
            conn.commit()
            flash("All medical Test data cleared successfully!", "success")
            cur.close()
            data = get_medicalTest_data()
            return render_template('medicalTest.html', results=data, search_criteria="test_id")
        except Exception as e:
            print(f"Error clearing medical Test data: {e}")
            flash("An error occurred while clearing medical Test data", "error")
            conn.rollback()
            data = get_medicalTest_data()
            return render_template('medicalTest.html', results=data, search_criteria="test_id")
    else:
        data = get_medicalTest_data()
        return render_template('medicalTest.html', results=data, search_criteria="test_id")


@app.route('/search_medicalTest', methods=['POST'])
def search_medicalTest():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        # Get the search criteria from the form
        search_criteria = request.form['searchCriteria']

        # Initialize the SQL query and search value
        search_query = ""
        search_value = ()

        # Modify the SQL query based on the selected search criteria
        if search_criteria == "test_id":
            search_value = (request.form['testIDInput'],)
            search_query = "SELECT * FROM MedicalTest WHERE test_id = %s"

        elif search_criteria == "testType":
            search_value = (f"%{request.form['testTypeInput']}%",)
            search_query = "SELECT * FROM MedicalTest WHERE testType like  %s"

        elif search_criteria == "date_last_taken":
            search_value = (f"%{request.form['date_last_takenInput']}%",)

            search_query = """
                SELECT MedicalTest.test_id, MedicalTest.testType,Patients.PatientID, Patients.FirstName,Patients.LastName,PatientTakeMedicalTest.date_taken,PatientTakeMedicalTest.next_date_to_take
                FROM PatientTakeMedicalTest
                JOIN Patients ON Patients.PatientID = PatientTakeMedicalTest.PatientID
                JOIN MedicalTest ON MedicalTest.test_id = PatientTakeMedicalTest.test_id
                WHERE PatientTakeMedicalTest.date_taken LIKE %s
            """

        elif search_criteria == "next_date_to_take":
            search_value = (f"%{request.form['next_date_to_takeInput']}%",)
            search_query = """
                SELECT MedicalTest.test_id, MedicalTest.testType,Patients.PatientID, Patients.FirstName,Patients.LastName,PatientTakeMedicalTest.date_taken,PatientTakeMedicalTest.next_date_to_take
                FROM PatientTakeMedicalTest
                JOIN Patients ON Patients.PatientID = PatientTakeMedicalTest.PatientID
                JOIN MedicalTest ON MedicalTest.test_id = PatientTakeMedicalTest.test_id
                WHERE PatientTakeMedicalTest.next_date_to_take like %s
            """

        elif search_criteria == "test_patient_count":
            search_query = """
                SELECT MedicalTest.test_id, MedicalTest.testType, COUNT(PatientTakeMedicalTest.PatientID) AS patient_count, LaboratoryRoom.lab_id
                FROM MedicalTest
                LEFT JOIN PatientTakeMedicalTest ON MedicalTest.test_id = PatientTakeMedicalTest.test_id
                LEFT JOIN LaboratoryRoom ON MedicalTest.test_id = LaboratoryRoom.test_id
                GROUP BY MedicalTest.test_id, MedicalTest.testType, LaboratoryRoom.lab_id
                order by 3 desc
            """
            search_value = ()

        elif search_criteria == "laboratory_rooms_by_test":
            search_value = (request.form['testIDInput'],)
            search_query = """
                        SELECT LaboratoryRoom.lab_id, LaboratoryRoom.availability_status, LaboratoryRoom.special_requirements, MedicalTest.testType
                        FROM LaboratoryRoom
                        JOIN MedicalTest ON LaboratoryRoom.test_id = MedicalTest.test_id
                        WHERE LaboratoryRoom.test_id = %s
                        """
        elif search_criteria == "patients_by_test_id":
            search_value = (request.form['testIDInput'],)
            search_query = """
                            SELECT Patients.PatientID, Patients.FirstName, Patients.LastName, Patients.Email, Patients.PhoneNumber, Patients.Age, Patients.DietID, MedicalTest.testType
                            FROM PatientTakeMedicalTest
                            JOIN Patients ON Patients.PatientID = PatientTakeMedicalTest.PatientID
                            JOIN MedicalTest ON MedicalTest.test_id = PatientTakeMedicalTest.test_id
                            WHERE PatientTakeMedicalTest.test_id = %s
                        """
        elif search_criteria == "one_day_left":
            search_query = """
                       SELECT Patients.PatientID, Patients.FirstName, Patients.LastName, Patients.Email, Patients.PhoneNumber, MedicalTest.testType, PatientTakeMedicalTest.next_date_to_take
                       FROM PatientTakeMedicalTest
                       JOIN Patients ON Patients.PatientID = PatientTakeMedicalTest.PatientID
                       JOIN MedicalTest ON MedicalTest.test_id = PatientTakeMedicalTest.test_id
                       WHERE PatientTakeMedicalTest.next_date_to_take < CURDATE()
                   """
            search_value = ()
        elif search_criteria == "select_all":
            search_query = "SELECT * FROM MedicalTest"
            search_value = ()

        # Execute the SQL query with the appropriate search value
        cur.execute(search_query, search_value)
        results = cur.fetchall()
        print(results)
        cur.close()

        # Flash a success message and render the template with the search results
        if results:
            flash("Data retrieved successfully!", "success")
            return render_template('medicalTest.html', results=results, search_criteria=search_criteria)
        else:
            flash("No data found for the given criteria.", "failure")
            data = get_medicalTest_data()
            return render_template('medicalTest.html', results=data, search_criteria="test_id")

    except Exception as e:
        print(f"Error searching data: {e}")
        flash("An error occurred while searching data.", "error")
        data = get_medicalTest_data()
        return render_template('medicalTest.html', results=data, search_criteria="test_id")


# *****************************************************************************************
@app.route('/top_nutritionists', methods=['GET', 'post'])
def top_nutritionists():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = """
            SELECT  nutritionistID, nutritionistName,salary  
            FROM  nutritionist 
            WHERE active like 'active'
            ORDER BY salary DESC  
            LIMIT 3

        """
        cur.execute(query)
        top_nutritionists = cur.fetchall()
        cur.close()
        flash("Data retrieved successfully!", "success")
        return render_template('statistics.html', top_nutritionists=top_nutritionists)
    except Exception as e:
        print(f"Error fetching top nutritionists: {e}")
        return render_template('statistics.html')


@app.route('/top_lab_technicians', methods=['GET', 'post'])
def top_lab_technicians():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = """
            SELECT  technicianID,  technicianName,  salary 
            FROM lab_technician 
            WHERE active like 'active'
            ORDER BY salary DESC  
            LIMIT 3
        """
        cur.execute(query)
        top_lab_technicians = cur.fetchall()
        cur.close()
        flash("Data retrieved successfully!", "success")
        return render_template('statistics.html', top_lab_technicians=top_lab_technicians)
    except Exception as e:
        print(f"Error fetching top lab technicians: {e}")
        flash("Error fetching top lab technicians.", "error")
        return render_template('statistics.html')


@app.route('/count_nutritionists', methods=['GET'])
def count_nutritionists():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM nutritionist WHERE active like 'active'"
        cur.execute(query)
        count_nutritionists = cur.fetchone()[0]
        cur.close()
        return count_nutritionists
    except Exception as e:
        print(f"Error counting nutritionists: {e}")
        return None


@app.route('/count_lab_technicians', methods=['GET'])
def count_lab_technicians():
    global cur, conn
    try:

        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM lab_technician where active like 'active'"
        cur.execute(query)
        count_lab_technicians = cur.fetchone()[0]
        cur.close()
        return count_lab_technicians
    except Exception as e:
        print(f"Error counting lab technicians: {e}")
        return None


@app.route('/count_laboratory_rooms', methods=['GET'])
def count_laboratory_rooms():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM LaboratoryRoom"
        cur.execute(query)
        count_laboratory_rooms = cur.fetchone()[0]
        cur.close()
        return count_laboratory_rooms
    except Exception as e:
        print(f"Error counting laboratory rooms: {e}")
        return None


@app.route('/count_medical_tests', methods=['GET'])
def count_medical_tests():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM MedicalTest"
        cur.execute(query)
        count_medical_tests = cur.fetchone()[0]
        cur.close()
        return count_medical_tests
    except Exception as e:
        print(f"Error counting medical tests: {e}")
        return None


@app.route('/count_diets', methods=['GET'])
def count_diets():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM diet"
        cur.execute(query)
        count_diets = cur.fetchone()[0]
        cur.close()
        return count_diets
    except Exception as e:
        print(f"Error counting diets: {e}")
        return None


@app.route('/count_patients', methods=['GET'])
def count_patients():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM Patients where status = 'active'"
        cur.execute(query)
        count_patients = cur.fetchone()[0]
        cur.close()
        return count_patients
    except Exception as e:
        print(f"Error counting patients: {e}")
        return None


@app.route('/count_checkup_rooms', methods=['GET'])
def count_checkup_rooms():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM CheckupRoom"
        cur.execute(query)
        count_checkup_rooms = cur.fetchone()[0]
        cur.close()
        return count_checkup_rooms
    except Exception as e:
        print(f"Error counting checkup rooms: {e}")
        return None


@app.route('/count_patient_medical_test', methods=['GET'])
def count_patient_take_medical_tests():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM PatientTakeMedicalTest"
        cur.execute(query)
        count_patient_take_medical_tests = cur.fetchone()[0]
        cur.close()
        return count_patient_take_medical_tests
    except Exception as e:
        print(f"Error counting Patient Take Medical Tests: {e}")
        return None


@app.route('/count_membership', methods=['GET'])
def count_membership():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM membership"
        cur.execute(query)
        count_membership = cur.fetchone()[0]
        cur.close()
        return count_membership
    except Exception as e:
        print(f"Error counting memberships: {e}")
        return None


@app.route('/count_inBodyScan', methods=['GET'])
def count_inBodyScan():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM inBodyScan"
        cur.execute(query)
        count_inBodyScan = cur.fetchone()[0]
        cur.close()
        return count_inBodyScan
    except Exception as e:

        print(f"Error counting inBodyScans: {e}")
        return None


@app.route('/statistics')
def statistics():
    nutritionist_count = count_nutritionists()
    session['count_nutritionists'] = nutritionist_count

    lab_technician_count = count_lab_technicians()
    session['count_lab_technicians'] = lab_technician_count

    checkup_room_count = count_checkup_rooms()
    session['count_checkup_rooms'] = checkup_room_count

    laboratory_room_count = count_laboratory_rooms()
    session['count_laboratory_room'] = laboratory_room_count

    medical_test_count = count_medical_tests()
    session['count_medical_test'] = medical_test_count

    diet_count = count_diets()
    session['count_diet'] = diet_count

    patient_count = count_patients()
    session['count_patient'] = patient_count

    patient_take_medical_test_count = count_patient_take_medical_tests()
    session['count_patient_medical_test'] = patient_take_medical_test_count

    membership_count = count_membership()
    session['count_membership'] = membership_count

    inBodyScan_count = count_inBodyScan()
    session['count_inBodyScan'] = inBodyScan_count

    return render_template('statistics.html',
                           nutritionist_count=nutritionist_count,
                           lab_technician_count=lab_technician_count,
                           checkup_room_count=checkup_room_count,
                           laboratory_room_count=laboratory_room_count,
                           medical_test_count=medical_test_count,
                           diet_count=diet_count,
                           patient_count=patient_count,
                           patient_take_medical_test_count=patient_take_medical_test_count,
                           membership_count=membership_count,
                           inBodyScan_count=inBodyScan_count)


@app.route('/patient_payment_status', methods=['GET', 'POST'])
def patient_payment_status():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        payment_option = request.form.get('paymentOption')
        if payment_option == "show_all_payments":
            query = """
                SELECT 
                    p.FirstName,
                    p.LastName,
                    p.PatientID,
                    m.payment_type,
                    (m.membership_fees * m.membership_duration) AS total_payment,
                    GREATEST(0, (m.membership_fees * m.membership_duration) - 
                    (SELECT TIMESTAMPDIFF(MONTH, m.registration_date, CURDATE()) * m.membership_fees)) AS patient_debt
                FROM 
                    Patients p
                JOIN 
                    membership m ON p.PatientID = m.PatientId;
            """
            cur.execute(query)
        elif payment_option == "search_patient_payment":
            patient_id = request.form['patientIDInput']
            query = """
                SELECT 
                    p.FirstName,
                    p.LastName,
                    p.PatientID,
                    m.payment_type,
                    (m.membership_fees * m.membership_duration) AS total_payment,
                    GREATEST(0, (m.membership_fees * m.membership_duration) - 
                    (SELECT TIMESTAMPDIFF(MONTH, m.registration_date, CURDATE()) * m.membership_fees)) AS patient_debt
                FROM 
                    Patients p
                JOIN 
                    membership m ON p.PatientID = m.PatientId
                WHERE 
                    p.PatientID = %s;
            """
            cur.execute(query, (patient_id,))

        patient_payments = cur.fetchall()
        cur.close()
        if patient_payments:
            flash("Data retrieved successfully!", "success")
        else:
            flash(f"No data was found By inserted patient ID!", "error")
        return render_template('statistics.html', patient_payments=patient_payments)
    except Exception as e:
        flash(f"Error fetching patient payment status: {e}", "error")
        return render_template('statistics.html')


@app.route('/calculate_center_balance', methods=['GET', 'POST'])
def calculate_center_balance():
    try:
        conn = mysql.connection
        cur = conn.cursor()

        # Get nutritionist salary sum
        salary_sum_nutritionist, avg_nutritionist = get_nutritionist_salaries_stats()

        # Convert salary_sum_nutritionist to Decimal
        salary_sum_nutritionist = Decimal(salary_sum_nutritionist)

        # Get lab technician salary sum
        query_lab_technician = "SELECT SUM(salary) FROM lab_technician WHERE active like 'active';"
        cur.execute(query_lab_technician)
        result_lab_technician = cur.fetchone()
        salary_sum_lab_technician = Decimal(result_lab_technician[0]) if result_lab_technician[
                                                                             0] is not None else Decimal(0)

        # Total salary sum
        total_salary_sum = salary_sum_nutritionist + salary_sum_lab_technician

        # Get total payment from memberships
        query = "SELECT SUM(m.membership_fees * m.membership_duration) AS total_payment FROM membership m;"
        cur.execute(query)
        result = cur.fetchone()
        total_payment = Decimal(result[0]) if result[0] is not None else Decimal(0)

        # Calculate center balance
        center_balance = total_payment - total_salary_sum

        # Round the results to three decimal points
        total_salary_sum = total_salary_sum.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        total_payment = total_payment.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        center_balance = center_balance.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

        # Prepare data list
        data_list = [total_salary_sum, total_payment, center_balance]

        cur.close()
        flash("Data retrieved successfully!", "success")
        return render_template('statistics.html', center_balance=data_list)
    except Exception as e:
        flash(f"Error calculating center balance: {e}", "error")
        return render_template('statistics.html')


@app.route('/expired_memberships', methods=['GET', 'POST'])
def expired_memberships():
    global cur, conn
    try:
        conn = mysql.connection
        cur = conn.cursor()
        query = """
            SELECT 
                p.PatientID,
                p.FirstName,
                p.LastName,
                p.Email,
                p.PhoneNumber,
                p.Age,
                p.DietID,
                m.registration_date
            FROM 
                Patients p
            JOIN 
                membership m ON p.PatientID = m.PatientId
            WHERE 
                DATE_ADD(m.registration_date, INTERVAL m.membership_duration MONTH) < CURDATE() and p.status="active";
        """
        cur.execute(query)
        expired_memberships = cur.fetchall()
        cur.close()
        flash("Data retrieved successfully!", "success")
        return render_template('statistics.html', expired_memberships=expired_memberships)
    except Exception as e:
        flash(f"Error fetching expired memberships: {e}", "error")
        return render_template('statistics.html')


# ***************************************************************************************************

def get_dismissed_nutritionist_data():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM nutritionist WHERE active like 'dismissed'")
        fetchdata = cur.fetchall()
        cur.close()
        return fetchdata
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/dismissedNutri', methods=['GET', 'POST'])
def dismissedNutri():
    if request.method == 'POST':
        try:
            return render_template('dismissedNutri.html')

        except Exception as e:
            print(f"Error processing request: {e}")
            return "Internal Server Error", 500
    else:
        print(f"inside if{request.method}")
        data = get_dismissed_nutritionist_data()
        return render_template('dismissedNutri.html', nutritionists=data)


@app.route('/search_dismissedNutritionists', methods=['GET', 'POST'])
def search_dismissedNutritionists():
    global cur, conn
    try:
        print("iam hereeeee")
        search_value = ""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['searchCriteria']

        if search_criteria == "id":
            search_value = request.form['idInput']
            search_criteria = "nutritionistID"
        elif search_criteria == "shifthours":
            search_value = request.form['shifthoursInput']
            search_criteria = "shiftHours"
        elif search_criteria == "absence":
            search_value = request.form['absenceInput']
            search_criteria = "absenceNum"
        elif search_criteria == "phoneNumber":
            search_value = request.form['phoneInput']
            search_criteria = "nutritionistPhoneNumber"
        elif search_criteria == "name":
            search_value = request.form['nameInput']
            search_criteria = "nutritionistName"
        elif search_criteria == "email":
            search_value = request.form['emailInput']
            search_criteria = "email"
        elif search_criteria == "salary":
            search_value = request.form['salaryInput']
            search_criteria = "salary"
        elif search_criteria == "room_duration":
            search_value = request.form['roomDurationInput']
            search_criteria = "room_duration"
        elif search_criteria == "room_id":
            search_value = request.form['roomIdInput']
            search_criteria = "room_id"
        elif search_criteria == "dismissed_date":
            search_value = request.form['dismissedDateInput']
            search_criteria = "dismissedDate"
        elif search_criteria == "searchAll":

            nutritionists = get_dismissed_nutritionist_data()

            if not nutritionists:
                flash("Could not find searched Data!", "fail")
            return render_template('dismissedNutri.html', nutritionists=nutritionists)
        elif search_criteria == "search_room":
            nutritionist_id = request.form['nutritionistIdInput']
            search_query = """
                SELECT 
                    cr.room_id, 
                    cr.special_requirements, 
                    cr.availability_status 
                FROM 
                    CheckupRoom cr 
                JOIN 
                    nutritionist n ON cr.room_id = n.room_id 
                WHERE 
                    n.nutritionistID = %s AND n.active like 'dismissed';
                """
            cur.execute(search_query, (nutritionist_id,))
            checkup_rooms = cur.fetchall()
            cur.close()
            if checkup_rooms:
                flash("Nutritionist data retrieved successfully!", "success")
            else:
                flash("Could not find searched Data!", "error")
                data = get_dismissed_nutritionist_data()
                return render_template('dismissedNutri.html', nutritionists=data)
            return render_template('dismissedNutri.html', checkup_rooms=checkup_rooms, search_criteria=search_criteria)

        search_query = f"SELECT * FROM nutritionist WHERE {search_criteria} LIKE %s AND active like 'dismissed'"
        term_with_percent = f"{search_value}%"
        cur.execute(search_query, (term_with_percent,))
        nutritionists = cur.fetchall()
        cur.close()

        if nutritionists:
            flash("Nutritionist data retrieved successfully!", "success")
            return render_template('dismissedNutri.html', nutritionists=nutritionists)
    except Exception as e:
        print(f"Error searching nutritionist: {e}")
        flash("An error occurred while searching nutritionist data: Could not find searched Data", "error")
        return render_template('dismissedNutri.html')

    flash("An error occurred while searching nutritionist data: Could not find searched Data", "error")
    conn.rollback()
    data = get_dismissed_nutritionist_data()
    return render_template('dismissedNutri.html', nutritionists=data)


# ********************************************************************************************

def get_dismissedlab_technician_data():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM lab_technician WHERE active like 'dismissed'")
        fetchdata = cur.fetchall()
        cur.close()
        return fetchdata
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/dismissedTech', methods=['GET', 'POST'])
def dismissedTech():
    if request.method == 'POST':
        try:
            return render_template('dismissedTech.html')

        except Exception as e:
            print(f"Error processing request: {e}")
            return "Internal Server Error", 500
    else:
        print(f"inside if{request.method}")
        data = get_dismissedlab_technician_data()
        return render_template('dismissedTech.html', technicians=data)


@app.route('/search_dismissedlab_technicians', methods=['GET', 'POST'])
def search_dismissedlab_technicians():
    global cur, conn
    try:
        search_value = ""
        conn = mysql.connection
        cur = conn.cursor()
        search_criteria = request.form['searchCriteria']

        if search_criteria == "id":
            search_value = request.form['idInput']
            search_criteria = "technicianID"
        elif search_criteria == "shiftHours":
            search_value = request.form['shiftHoursInput']
            search_criteria = "shiftHours"
        elif search_criteria == "tools":
            search_value = request.form['toolsInput']
            search_criteria = "tools"
        elif search_criteria == "phoneNumber":
            search_value = request.form['phoneInput']
            search_criteria = "technicianPhoneNumber"
        elif search_criteria == "name":
            search_value = request.form['nameInput']
            search_criteria = "technicianName"
        elif search_criteria == "email":
            search_criteria = "technicianEmail"
            search_value = request.form['emailInput']
        elif search_criteria == "salary":
            search_value = request.form['salaryInput']
            search_criteria = "salary"
        elif search_criteria == "lab_id":
            search_value = request.form['labIDInput']
            search_criteria = "lab_id"
        elif search_criteria == "dismissed_date":
            search_value = request.form['dismissedDateInput']
            search_criteria = "dismissedDate"
        elif search_criteria == "select_all":
            search_query = "SELECT * FROM lab_technician WHERE active like 'dismissed'"
            cur.execute(search_query)
            lab_technicians = cur.fetchall()
            cur.close()
            if not lab_technicians:
                flash("Could not find searched Data!", "fail")
            else:
                flash("Lab technician data retrieved successfully!", "success")
            return render_template('dismissedTech.html', technicians=lab_technicians)
        elif search_criteria == "search_lab_room":
            technician_id = request.form['technicianIdInput']
            search_query = """
                SELECT
                    lr.lab_id,
                    lr.test_id,
                    lr.availability_status,
                    lr.special_requirements
                FROM
                    LaboratoryRoom lr
                JOIN
                    lab_technician lt ON lr.lab_id = lt.lab_id
                WHERE
                    lt.technicianID = %s AND lt.active like 'dismissed'
            """
            cur.execute(search_query, (technician_id,))
            lab_rooms = cur.fetchall()
            cur.close()
            flash("Lab technician data retrieved successfully!", "success")
            return render_template('dismissedTech.html', lab_rooms=lab_rooms, search_criteria=search_criteria)

        search_query = f"SELECT * FROM lab_technician WHERE {search_criteria} LIKE %s AND active like 'dismissed'"
        term_with_percent = f"{search_value}%"
        cur.execute(search_query, (term_with_percent,))
        lab_technicians = cur.fetchall()
        cur.close()

        if lab_technicians:
            flash("Lab technician data retrieved successfully!", "success")
            return render_template('dismissedTech.html', technicians=lab_technicians)
    except Exception as e:
        print(f"Error searching lab technician: {e}")
        flash(f"Error searching lab technician: {e}", "error")
        data = get_dismissedlab_technician_data()
        return render_template('dismissedTech.html', technicians=data)

    flash("An error occurred while searching lab technician data: Could not find searched data", "error")
    conn.rollback()
    data = get_dismissedlab_technician_data()
    return render_template('dismissedTech.html', technicians=data)


if __name__ == '__main__':
    app.run(debug=True)
                    