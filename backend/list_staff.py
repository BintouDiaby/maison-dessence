import sqlite3

DB = 'db.sqlite3'

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT id, username, email, is_staff, is_superuser FROM auth_user WHERE is_staff=1")
    rows = cur.fetchall()
    print('STAFF USERS:')
    if not rows:
        print('(aucun utilisateur avec is_staff=True)')
    for r in rows:
        print(r)
    con.close()

if __name__ == '__main__':
    main()
