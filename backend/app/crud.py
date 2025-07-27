from sqlalchemy.orm import Session
from .models import Customer

def create_customer(db: Session, name: str, phone: str, address: str):
    c = Customer(name=name, phone=phone, address=address)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

def read_customers(db: Session):
    return db.query(Customer).all()

def read_customer(db: Session, cid: int):
    return db.query(Customer).filter(Customer.id == cid).first()

def update_customer(db: Session, cid: int, name=None, phone=None, address=None):
    c = read_customer(db, cid)
    if not c:
        return None
    if name is not None:
        c.name = name
    if phone is not None:
        c.phone = phone
    if address is not None:
        c.address = address
    db.commit()
    db.refresh(c)
    return c

def delete_customer(db: Session, cid: int):
    c = read_customer(db, cid)
    if not c:
        return False
    db.delete(c)
    db.commit()
    return True
