from sqlalchemy import Column,Integer,String,Date,Boolean
from database import Base
class db_model(Base):
    __tablename__="customerdata"

    customer_id = Column(Integer,primary_key=True,autoincrement=True)

    telecom_partner = Column(String(10),nullable=False)
    gender          = Column(String(10),nullable=False)
    age             = Column(Integer,nullable=False)

    state   = Column(String(50),nullable=False)
    city    = Column(String(50),nullable=False)
    pincode = Column(Integer,nullable=False)

    date_of_registration = Column(Date,nullable=False)

    num_dependents   = Column(Integer,default=0)
    estimated_salary = Column(Integer)

    calls_made = Column(Integer,default=0)
    sms_sent   = Column(Integer,default=0)
    data_used  = Column(Integer,default=0)

    churn=Column(Boolean,default=False)
