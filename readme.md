# File Storage using Python socket
This is a python project which functions as a file storage, similar to FTP but this project is using ```socket``` instead of FTP. This program consists of two part; _server_ and _client_. Server serves the client by spawning dedicated thread and let the client connects to that thread. Client uses ```Tkinter``` library as its GUI. Tested on **Python 2.7**. Will be updated later.

## Functions
##### Login
Method      : ```AUTHENTICATE```
How-to      : Select **Account** > **Login** > login by entering username and password on the popup menu.
##### Download
Method      : ```DOWNLOAD```
How-to      : Select the file you want to download > **Right-Click** > **Download**. A prompt will ask you where to put the downloaded file (on your personal computer), the file will be on the directory you choose from the prompt.
##### Upload
Method      : ```UPLOAD```
How-to      : Select **Action** > **Upload**. A prompt will ask you what file to upload to your own file storage. The file will be uploaded on the current working directory of the user.
##### Delete
Method      : ```DELETE```
How-to      : Select the file or directory you want to delete > **Right-Click** > **Delete**. The file will be deleted.
##### Share File
Method      : ```SHARE```
How-to      : Select the file you want to share > **Right-Click** > **Share**. A prompt will ask you which user you want to share the file with. Press **OK** and then a new directory will be created on your (as a user) root directory named "[Shared To] - ```user```". The user which file you shared to will have a new directory created on his/her root named "[Shared From] - ```the user that shared the file```". The shared file will be copied inside both folders, and act **AS A SAME FILE**.

##### Register New User (Soon!)
## Steps
1. Run `python setup.py` to create db tables and seed users, using Sqlite.

**Sample user credentials (from setup.py):**
- user: adis | pwd: password123
- user: bani | pwd: password123
- user: rifqi | pwd: password123
- user: bayu | pwd: password123
- user: fahrizal | pwd: password123

2. Run ```python server.py``` 
3. Run ```python client.py``` 
4. Used ports:
    - Command port: 1337
    - Data port: 1338
5. Click Account -> Login -> fill in credentials
6. You will have your file storage ready!


### Info
- Folder _core_ holds User's files and folders.
- Files can be shared between users and will be stored on "[Shared To] - (_user_)" directory.
