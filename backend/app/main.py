from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .db import Base, engine
from .deps import get_db
from .models import Customer
from .schemas import (
    CustomerCreate, CustomerUpdate, CustomerOut, ChatbotIn
)
from .crud import (
    create_customer, read_customers, read_customer,
    update_customer, delete_customer
)
from .agents.adk_agent import run_agent

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gemini CRUD with ADK Tools (No ADK Web Framework)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ---------- REST CRUD (for Form & Table) ----------

@app.post("/customers", response_model=CustomerOut)
def api_create_customer(payload: CustomerCreate, db=Depends(get_db)):
    return create_customer(db, **payload.dict())

@app.get("/customers", response_model=List[CustomerOut])
def api_list_customers(db=Depends(get_db)):
    return read_customers(db)

@app.get("/customers/{cid}", response_model=CustomerOut)
def api_get_customer(cid: int, db=Depends(get_db)):
    c = read_customer(db, cid)
    if not c:
        raise HTTPException(404, "Customer not found")
    return c

@app.put("/customers/{cid}", response_model=CustomerOut)
def api_update_customer(cid: int, payload: CustomerUpdate, db=Depends(get_db)):
    c = update_customer(db, cid, **payload.dict(exclude_unset=True))
    if not c:
        raise HTTPException(404, "Customer not found")
    return c

@app.delete("/customers/{cid}")
def api_delete_customer(cid: int, db=Depends(get_db)):
    ok = delete_customer(db, cid)
    if not ok:
        raise HTTPException(404, "Customer not found")
    return {"deleted": True}

# ---------- Chatbot endpoint (NL → ADK Agent → CRUD tool) ----------

@app.post("/chatbot")
def chatbot(body: ChatbotIn):
    result = run_agent(body.message)
    return {"result": result}
