# Discord File Hosting

Discord_file_hosting is a project that enables file hosting from a Discord server. For the hosting to function properly, you'll need an SFTP server. Please note that Discord might potentially suspend your account/server for this reason, so I recommend doing this on an alternate account. 

The program operates by using Upload.py to split a file into parts and then sends them to a Discord channel and stores them in the files.json on the SFTP server. Additionally, Download.py retrieves these files from the Discord channel and assembles them into one. Optionally, you can use the website located in the 'website' folder. The site requires Web.py to function correctly; otherwise, it won't work.

### Configuration:

- **Download.py**: 
  - Change the IP, password, and username to your actual SFTP credentials in lines 18.
  - Replace the channel_id with the correct Discord channel ID in line 33.
  - Update discord_bot_token in line 71 with the actual token.

- **Upload.py**:
  - Modify IP, username, and password with your SFTP server details in lines 100, 101, and 102.
  - Replace token and channel_id with the correct values in lines 131 and 132.

- **Website Configuration in Web.py**:
  - Change IP, username, and password to your actual SFTP server details in lines 14, 16, and 17.

Please ensure you make these configurations accurately for the project to work seamlessly.
