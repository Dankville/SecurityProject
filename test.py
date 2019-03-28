from passlib.hash import pbkdf2_sha256

hash1 = pbkdf2_sha256.hash("password1")
print(hash1)

hash2 = pbkdf2_sha256.hash("password1")
print(hash2)

print(len(hash1))

print(pbkdf2_sha256.verify("password1", hash1))
