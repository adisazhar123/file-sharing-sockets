import sqlite3
import os
conn = sqlite3.connect('file_sharing_sockets.db')

c = conn.cursor()
print 'seeding users'

users = [(1, 'adis', 'password123', 'adis'),
        (2, 'bani', 'password123', 'bani'),
        (3, 'rifqi', 'password123', 'rifqi'),
        (4, 'bayu', 'password123', 'bayu'),
        (5, 'fahrizal', 'password123', 'fahrizal'),
        ]

c.executemany('INSERT INTO user VALUES (?,?,?,?)', users)

print 'seeded users'
conn.commit()

conn.close()

core_dir = os.getcwd() + '/../core'
# init user dirs
for user in users:
        if not os.path.exists(core_dir + '/' + user[3]):
                print 'making directory ' +user[3]
                os.makedirs(core_dir + '/' + user[3])
