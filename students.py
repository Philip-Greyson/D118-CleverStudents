"""Script to synchronize student data from PowerSchool to Clever via SFTP upload.

https://github.com/Philip-Greyson/D118-CleverStudents

Just does a big SQL query for all students, massages a few fields, and outputs it to the .csv file which is then uploaded to Clever via SFTP.
"""


# Script to take values from PowerSchool and put them into a csv file for upload to Clever
# basically just a big SQL query, the results are massaged a tiny bit to get the email and a few other fields format
# then output one student per line to the Students.csv file which is then uploaded to the Clever SFTP server

# importing module
import datetime  # used to get current date for course info
import os  # needed to get environement variables
from datetime import *

import oracledb  # needed to connect to the PowerSchool database (oracle database)
import pysftp  # used to connect to the Clever sftp site and upload the file

DB_UN = os.environ.get('POWERSCHOOL_READ_USER')  # username for read-only database user
DB_PW = os.environ.get('POWERSCHOOL_DB_PASSWORD')  # the password for the database account
DB_CS = os.environ.get('POWERSCHOOL_PROD_DB')  # the IP address, port, and database name to connect to

#set up sftp login info, stored as environment variables on system
SFTP_UN = os.environ.get('CLEVER_SFTP_USERNAME')
SFTP_PW = os.environ.get('CLEVER_SFTP_PASSWORD')
SFTP_HOST = os.environ.get('CLEVER_SFTP_ADDRESS')
CNOPTS = pysftp.CnOpts(knownhosts='known_hosts')  # connection options to use the known_hosts file for key validation

OUTPUT_FILE_NAME = 'Students.csv'
EMAIL_SUFFIX = '@d118.org'  # domain for emails used to construct the student email addresses

print(f"Database Username: {DB_UN} |Password: {DB_PW} |Server: {DB_CS}")  # debug so we can see where oracle is trying to connect to/with
print(f'SFTP Username: {SFTP_UN} | SFTP Password: {SFTP_PW} | SFTP Server: {SFTP_HOST}')  # debug so we can see what info sftp connection is using


if __name__ == '__main__':  # main file execution
    with open('student_log.txt', 'w') as log:
        startTime = datetime.now()
        startTime = startTime.strftime('%H:%M:%S')
        print(f'INFO: Execution started at {startTime}')
        print(f'INFO: Execution started at {startTime}', file=log)
        with open(OUTPUT_FILE_NAME, 'w') as output:  # open the output file
            print('"Student_id","State_id","Student_number","School_id","Student_city","Dob","First_name","Middle_name","Last_name","Gender","Grade","Student_state","Student_Street","Student_Zip","Student_email","Hispanic_Latino","Race","Ell_Status","Frl_status","IEP_status"',file=output)  # print out header row to output file
            try:
                with oracledb.connect(user=DB_UN, password=DB_PW, dsn=DB_CS) as con:  # create the connecton to the database
                    with con.cursor() as cur:  # start an entry cursor
                        print(f'INFO: Connection established to PS database on version: {con.version}')
                        print(f'INFO: Connection established to PS database on version: {con.version}', file=log)
                        # do the big SQL query for active or pre-enrolled students
                        cur.execute('SELECT students.id, students.state_studentNumber, students.student_number, students.schoolid, students.city, students.dob, students.first_name, students.middle_name, students.last_name, students.gender, students.grade_level, students.state, students.street, students.zip, u_def_ext_students0.custom_ethnicity, u_def_ext_students0.custom_race, u_def_ext_students0.custom_lep, students.lunchstatus, s_il_stu_x.iep FROM students LEFT JOIN u_def_ext_students0 ON students.dcid = u_def_ext_students0.studentsdcid LEFT JOIN s_il_stu_x ON students.dcid = s_il_stu_x.studentsdcid WHERE (students.enroll_status = 0 OR students.enroll_status = -1) ORDER BY students.id')
                        students = cur.fetchall()  # store the data from the query into the students variable
                        for student in students:  # go through each student's data
                            try:
                                print(student, file=log)
                                internalID = int(student[0])
                                stateID = int(student[1]) if student[1] else ''  # set to blank string if there is no value
                                stuNum = int(student[2])
                                school = int(student[3])
                                city = student[4] if student[4] else ''  # set to blank string if there is no value
                                birthdate = student[5].strftime('%Y-%m-%d')  # convert the full datetime value to just yyyy-mm-dd
                                firstName = student[6]
                                middleName = student[7] if student[7] else ''  # set to blank string if there is no value
                                lastName = student[8]
                                gender = student[9]
                                grade = int(student[10])
                                state = student[11]
                                address = student[12] if student[12] else ''  # set to blank string if there is no value
                                zipCode = student[13] if student[13] else ''  # set to blank string if there is no value
                                email = str(stuNum) + EMAIL_SUFFIX
                                ethnicity = student[14] if student[14] else ''  # Y or N for hispanic latino. handled by the clever race ethnicity lep script https://github.com/Philip-Greyson/D118-CleverRaceEthnicityLEP
                                race = student[15] if student[15] else ''  # character race code such as W, B, M, etc. handled by the clever race ethnicity lep script
                                lep = student[16] if student[16] else ''  # low english proficiency, handled by the clever race ethnicity lep script
                                if 'F' in student[17] or student[17] == 'T':  # handles 'F' and 'FDC' cases, 'T' for temporary
                                    freeReduced = 'F'  # freee
                                elif student[17] == 'R':
                                    freeReduced = 'R'  # reduced
                                else:  # handles 'E', blank, or 'P'
                                    freeReduced = 'N'  # no discount
                                iep = 'Y' if student[18] == 1 else 'N'  # iep status handling

                                # print out the student's information to the output file
                                print(f'{internalID},{stateID},{stuNum},{school},"{city}",{birthdate},{firstName},{middleName},{lastName},{gender},{grade},"{state}","{address}",{zipCode},{email},{ethnicity},{race},{lep},{freeReduced},{iep}', file=output)

                            except Exception as er:
                                print(f'ERROR while processing student {student[2]}: {er}')
                                print(f'ERROR while processing student {student[2]}: {er}', file=log)

            except Exception as er:
                print(f'ERROR while connecting to PowerSchool or doing query: {er}')
                print(f'ERROR while connecting to PowerSchool or doing query: {er}', file=log)

        try:
            # connect to the Clever SFTP server using the login details stored as environement variables
            with pysftp.Connection(SFTP_HOST, username=SFTP_UN, password=SFTP_PW, cnopts=CNOPTS) as sftp:
                print(f'INFO: SFTP connection to Clever at {SFTP_HOST} successfully established')
                print(f'INFO: SFTP connection to Clever at {SFTP_HOST} successfully established', file=log)
                # print(sftp.pwd) # debug, show what folder we connected to
                # print(sftp.listdir())  # debug, show what other files/folders are in the current directory
                sftp.put(OUTPUT_FILE_NAME)  # upload the file onto the sftp server
                print("INFO: Student sync file placed on remote server")
                print("INFO: Student sync file placed on remote server", file=log)
        except Exception as er:
            print(f'ERROR while connecting or uploading to Clever SFTP server: {er}')
            print(f'ERROR while connecting or uploading to Clever SFTP server: {er}', file=log)

        endTime = datetime.now()
        endTime = endTime.strftime('%H:%M:%S')
        print(f'INFO: Execution ended at {endTime}')
        print(f'INFO: Execution ended at {endTime}', file=log)
