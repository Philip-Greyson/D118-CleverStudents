# CLEVER STUDENT SYNC  

Script to take values from PowerSchool and put them into a csv file for upload to Clever.  
Basically just a big SQL query, the results are massaged a tiny bit to get the email and a few other fields format correct.  
Then outputs one student per line to the Students.csv file which is then uploaded to the Clever SFTP server.  

In order to use you will need the following  

- Python (created and tested on Python 3.10.6) installed on the host <https://www.python.org/downloads/release/python-3106/>  
- A PowerSchool server that has its database accessible to the server/computer this script is running on
- The connection info of the PowerSchool server and the Clever SFTP server stored as environment variables on the host
- The oracledb driver/library installed on the host <https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html>
- The pysftp library on the host <https://pysftp.readthedocs.io/en/release_0.2.9/>
- The hostkey for the Clever SFTP server saved to a file called known_hosts in the same directory as the python script
    - I do this by manually generating an ssh connection in the linux terminal and then copying from ~/.ssh/known_hosts to the file to transfer to a windows host