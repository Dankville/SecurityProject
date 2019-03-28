from sqlalchemy import Table,Column,Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import mapper, relationship
from database import metadata, DB_Session

class User(object):
    def __init__(self, username=None, email=None, password=None, twoFactorAuthEnabled = False, twoFactorAuthKey = None, role_id = 1):
        self.username = username
        self.email = email
        self.password = password
        self.twoFactorAuthEnabled = twoFactorAuthEnabled
        self.twoFactorAuthKey = twoFactorAuthKey
        self.role_id = role_id

    def __repr__(self):
        return "<User %r with role ID: %s >" % (self.username, self.role_id)

    def __setattr__(self, name, value):
        super(User, self).__setattr__(name, value)


class Role(object):
    def __init__(self, role):
        self.role = role

    def __repr__(self):
        return "<Role: %s>" % self.role

class ResetPwdCode(object):
    def __init__(self, owner, code):
        self.owner = owner
        self.code = code
        

roles = Table('roles', metadata,
    Column('ID', Integer, primary_key=True),
    Column('role', String(8))
)        
mapper(Role, roles)

users = Table('users', metadata,
    Column('ID', Integer, primary_key=True),
    Column('username', String(50), unique = True),
    Column('email', String(100)),
    Column('password', String(100)),
    Column('twoFactorAuthEnabled', Boolean),
    Column('twoFactorAuthKey', String(32)),
    Column('role_id', Integer, ForeignKey('roles.ID'))
)
mapper(User, users)

resetPwdCodes = Table('pwdcodes', metadata,
    Column('ID', Integer, primary_key = True),
    Column('owner', String(50)),
    Column('code', String(8))
)
mapper(ResetPwdCode, resetPwdCodes)