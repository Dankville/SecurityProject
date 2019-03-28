import pyotp

class TwoFactorAuth():
    def __init__(self):
        self.authenticator = None

    def GetAuthenticator(self):
        if self.authenticator is not None:
            return self.authenticator

    def SetAuthenticator(self, key):
        self.authenticator = pyotp.TOTP(key)

    def Verify(self, nr):
        if self.authenticator is not None:
            return self.authenticator.verify(nr)