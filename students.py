# importing module
import pysftp  # used to connect to the Clever sftp site and upload the file
import sys  # needed for  non-scrolling display
import os  # needed to get system variables which have the PS IP and password in them
import oracledb # needed to connect to the PowerSchool database (oracle database)
from datetime import datetime

un = 'PSNavigator'  # PSNavigator is read only, PS is read/write
pw = os.environ.get('POWERSCHOOL_DB_PASSWORD') # the password for the PSNavigator account
cs = os.environ.get('POWERSCHOOL_PROD_DB') # the IP address, port, and database name to connect to

#set up sftp login info, stored as environment variables on system
sftpUN = os.environ.get('CLEVER_SFTP_USERNAME')
sftpPW = os.environ.get('CLEVER_SFTP_PASSWORD')
sftpHOST = os.environ.get('CLEVER_SFTP_ADDRESS')
cnopts = pysftp.CnOpts(knownhosts='known_hosts') #connection options to use the known_hosts file for key validation

print("Username: " + str(un) + " |Password: " + str(pw) + " |Server: " + str(cs))
print("SFTP Username: " + str(sftpUN) + " |SFTP Password: " + str(sftpPW) + " |SFTP Server: " + str(sftpHOST)) #debug so we can see what sftp info is being used
badnames = ['USE', 'TESTSTUDENT', 'TEST STUDENT', 'TESTTT', 'TESTTEST']

# create the connecton to the database
with oracledb.connect(user=un, password=pw, dsn=cs) as con:
    with con.cursor() as cur:  # start an entry cursor
        with open('student_log.txt', 'w') as log:
            with open('Students.csv', 'w') as output:  # open the output file
                print("Connection established: " + con.version)
                print('"Student_id","State_id","Student_number","School_id","Student_city","Dob","Active","First_name","Middle_name","Last_name","Gender","Grade","Student_state","Student_Street","Student_Zip","Student_email","Hispanic_Latino","Race","Ell_Status"',file=output)  # print out header row
                cur.execute('SELECT students.id, students.state_studentNumber, students.student_number, students.schoolid, students.city, students.dob, students.enroll_status, students.first_name, students.middle_name, students.last_name, students.gender, students.grade_level, students.state, students.street, students.zip, students.student_number, u_def_ext_students0.custom_ethnicity, u_def_ext_students0.custom_race, u_def_ext_students0.custom_lep FROM students LEFT JOIN u_def_ext_students0 ON students.dcid = u_def_ext_students0.studentsdcid WHERE students.enroll_status = 0 ORDER BY students.id')
                studentRows = cur.fetchall()  # store the data from the query into the rows variable

                # go through each entry (which is a tuple) in rows. Each entrytuple is a single students's data
                for count, student in enumerate(studentRows):
                    student = list(student) # convert from tuple to list so we can edit the values in the list without having to store each value as a variable
                    try:
                        sys.stdout.write('\rProccessing student entry %i' % count) # sort of fancy text to display progress of how many students are being processed without making newlines
                        sys.stdout.flush()
                        print(student, file=log)
                        student[2] = int(student[2]) # take the student number as an int to get rid of the trailing 0
                        student[5] = student[5].strftime('%Y-%m-%d') # convert the full datetime value to just yyyy-mm-dd
                        student[15] = str(student[2]) + '@d118.org' # take the student number and append the d118.org email on it
                        for fieldnum, field in enumerate(student): # go through each part of the results of fields for students one at a time
                            field = '' if field == None else field # strip out the literal None values and set them to blanks if there is no value
                            print('"' + str(field) + '"', end = '', file=output) # print the value of the field surrounded by quotes, but without a newline after each field so it all stays on one line
                            if fieldnum+1 < len(student): # for every field except the last one
                                print(',', end='', file=output) # print the dividing comma for a csv file
                            else: # for the final field we dont want a trailing comma and instead just want a newline
                                if count+1 < len(studentRows): # if we are not at the last student entry, add a newline after the last field
                                    print('', file=output)
                    except Exception as er:
                        print("Error on " + str(student[3]) + ": " + str(er))