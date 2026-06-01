import bcrypt

pwd_bytes = input("type yоur password: ", ).encode('utf-8')
hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())

def get_pwd_str(password:str):
 decode_pwd = pwd_bytes.decode('utf-8')
 return decode_pwd # - returns the decoded password


def check_pwd ():
 if bcrypt.checkpw(pwd_bytes, hashed):
  print("It Matches!")
 else:
  print("It Does not Match :(")


