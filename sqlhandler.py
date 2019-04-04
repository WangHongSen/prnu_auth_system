import pickle

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  String,Column,Integer
from sqlalchemy.dialects.sqlite import BLOB

engine = create_engine("sqlite:///PRNU.db")
Session = sessionmaker(bind=engine)
Base = declarative_base() 
  
class User(Base):    
    __tablename__ = "user_table"    
    username = Column(String(50),primary_key=True,nullable=False)    
    password = Column(String(50),nullable=False)   
    fingerprint = Column(BLOB)
class QRcode(Base):    
    __tablename__ = "QRcode_table"    
    encode_data = Column(String(500),primary_key=True,nullable=False)    
    data = Column(String(500),nullable=False)   

def add_new_user(username,password):        
    from handler import encrypt_data
    encode_password = encrypt_data(password)

    session = Session()
    new_user = User(username=username,password=encode_password,fingerprint=None)
    session.add(new_user)
    try:
        session.commit()
        return True
    except:
        #username exists
        return None
    finally:
        session.close()

def get_password_by_username(username):

    session = Session()   
    try:
        user = session.query(User).filter_by(username=username).first()
        encoded_password_in_database = user.password
        return encoded_password_in_database
    except:
        #username does not exist
        return None
    finally:
        session.close() 
    
def get_decode_data(encode_data):

    session = Session()   
    try:
        qrcode = session.query(QRcode).filter_by(encode_data=encode_data).first()
        data = qrcode.data
        return data
    except:
        #encode_data does not exist
        return None
    finally:
        session.close() 
        
def get_fingerprint_from_db(username):

    session = Session()  
    try:
        user = session.query(User).filter_by(username=username).first()
        fingerprint = pickle.loads(user.fingerprint)
        return fingerprint
    except:
        #username does not exist
        return None
    finally:
        session.close()
  
def save_fingerprint_into_db(fingerprint,username):

    fingerprint = pickle.dumps(fingerprint)
    
    session = Session()
    session.query(User).filter(User.username == username).update({'fingerprint' : fingerprint})  
    try:
        session.commit()
        return True
    except:
        #username does not exist
        return None
    finally:
        session.close()
        
def save_encode_data_into_db(encode_data,data):
    session = Session()
    new_QRcode = QRcode(encode_data=encode_data,data=data)
    session.add(new_QRcode)
    try:
        session.commit()
        return True
    except:
        #encode_data exists
        return None
    finally:
        session.close()
        
def init_db():
    session = Session()
    Base.metadata.create_all(engine)
    session.query(User).delete()
    session.query(QRcode).delete()
    session.commit()
    session.close()
    
