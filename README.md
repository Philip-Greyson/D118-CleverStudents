# D118-CleverStudents

Script to synchronize student data from PowerSchool into Clever by outputting to a .csv file and uploading via SFTP to their server.

## Overview

This script is a fairly straightforward passing of data from PowerSchool to Clever. For the most part, it just does an SQL query and uses the fields returned directly, but for a few fields there is some massaging of data to get it into a format Clever wants.
The script opens the output file and writes the header row, then does a query for all active or pre-enrolled students in PowerSchool, grabbing all the fields needed. The few fields that need it are changed slightly, and then each student has a row output to the .csv file with all the fields. After all students are processed, the file is uploaded to the Clever SFTP server.

## Requirements

The following Environment Variables must be set on the machine running the script:

- POWERSCHOOL_READ_USER
- POWERSCHOOL_DB_PASSWORD
- POWERSCHOOL_PROD_DB
- CLEVER_SFTP_USERNAME
- CLEVER_SFTP_PASSWORD
- CLEVER_SFTP_ADDRESS

These are fairly self explanatory, and just relate to the usernames, passwords, and host IP/URLs for PowerSchool and the Clever SFTP server (provided by them). If you wish to directly edit the script and include these credentials or to use other environment variable names, you can.

Additionally, the following Python libraries must be installed on the host machine (links to the installation guide):

- [Python-oracledb](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html)
- [pysftp](https://pypi.org/project/pysftp/)

**As part of the pysftp connection to the output SFTP server, you must include the server host key in a file** with no extension named "known_hosts" in the same directory as the Python script. You can see [here](https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-cnopts) for details on how it is used, but the easiest way to include this I have found is to create an SSH connection from a linux machine using the login info and then find the key (the newest entry should be on the bottom) in ~/.ssh/known_hosts and copy and paste that into a new file named "known_hosts" in the script directory.

You will need to change where the IEP information comes from and how it is processed if you are not in IL, as we use the IL demographics table which will not exist on other PowerSchool instances. You could also remove it altogether by removing the entry in the header row, SQL query, and output line.

If you want to include the ethnicity flag, race character, and ELL-status flag how it is set up in the script, you will need to have the data already in PowerSchool in the format Clever expects it. We use a separate script to get the values exported to a local SFTP server and AutoComm them into custom fields for use in this and other scripts. For more info on that, see [here](https://github.com/Philip-Greyson/D118-CleverRaceEthnicityLEP). Otherwise you will need to change how those variables are generated for this script, or just remove them altogether.

## Customization

Besides the processing of the fields mentioned above in the requirements section, the script should just work. Listed below is any other changes you might want to make:

- You will want to edit the `EMAIL_SUFFIX` constant in the student script to match whatever your emails are. Additionally, you may need to change how the email is constructed, as we use their student number. If you need to, you can change the `email =  str(stuNum) + EMAIL_SUFFIX`.
- If you want to add any other optional fields to the output, you will need to add them to the header, change the SQL query to retrieve them, process them, and them add them to the output line in the same field order as the header row.
