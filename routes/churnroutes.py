from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from database import get_db
from models import db_model
from schemas import Create_customer

router=APIRouter()

@router.post("/create")
def create_customer(data : Create_customer , db : Session = Depends ( get_db ) ):
    new_user=db_model(
        telecom_partner=data.telecom_partner,
        gender=data.gender,
        age=data.age,
        state=data.state,
        city=data.city,
        pincode=data.pincode,
        date_of_registration=data.date_of_registration,
        num_dependents=data.num_dependents,
        estimated_salary=data.estimated_salary,
        calls_made=data.calls_made,
        sms_sent=data.sms_sent,
        data_used=data.data_used,
        churn=data.churn
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return{
        "Status ":"Success",
        "Message":"User Created",
        "new_user": new_user
    }

@router.get("/getbyid/{c_id}")
def read_customer(c_id:int, db: Session = Depends(get_db)):
    #this line is also correct.But it is the long method
    #cdata=db.query(db_model).filter(db_model.customer_id==c_id).first()
    cdata=db.get(db_model,c_id)
    if cdata is None:
        return {"Msg":"Customer not found"}
    return cdata

@router.get("/getallcustomers")
def get_all_customers(db:Session=Depends(get_db)):
    data=db.query(db_model).all()
    if data is None:
        return {"msg":"You have no customers!!!!!!"}
    return data

@router.delete("/deleteuser/{c_id}")
def deleteuser(c_id:int,db:Session=Depends(get_db)):
    data=db.query(db_model,c_id)
    if data is None:
        return {"Msg":"Customer does not exist"}
    db.query(db_model,c_id).delete()
    return {"Msg":"Customer Deleted"}
