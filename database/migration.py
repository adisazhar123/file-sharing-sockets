import sqlite3
conn = sqlite3.connect('file_sharing_sockets.db')

c = conn.cursor()
print 'migrating tables'
c.execute('''CREATE TABLE user(id int AUTOINCREMENT, user_name text, password text, core_dir text)''')
print 'tables migrated'
conn.commit()

conn.close()