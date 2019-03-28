from models import Role, User
from database import DB_Session
from passlib.hash import pbkdf2_sha256

class RoleInitializer():
    def __init__(self):
        sess = DB_Session()
        roles = sess.query(Role).all()
        if (len(roles) == 0):
            normal = Role("normal")
            admin = Role("admin")
            helpdesk = Role("helpdesk")

            sess.add(normal)
            sess.add(admin)
            sess.add(helpdesk)
            
            sess.commit()
        sess.close()

class UserInitializer():
    def __init__(self):
        sess = DB_Session()
        users = sess.query(User).all()
        if len(users) == 0:
            
            sess.add(User('Piet', 'mposttroep@gmail.com', pbkdf2_sha256.hash('Asdf1234'),  True, 'averylonglonglongkey', 1))
            sess.add(User('Klaas', 'mposttroep@gmail.com', pbkdf2_sha256.hash('Asdf1234'),  True, 'averytalltalltallkey', 2))
            sess.add(User('Freek', 'mposttroep@gmail.com', pbkdf2_sha256.hash('Asdf1234'), True, 'averyhandsomelongkey', 3))

            sess.commit()
        sess.close()
