# Fixed tools.py file with correct Pydantic constraints

from google.adk.tools.base_tool import BaseTool
from ..models import Customer
from ..db import SessionLocal
from typing import Optional

from typing import Annotated
from pydantic import BaseModel, StringConstraints

NameType = Annotated[str, StringConstraints(min_length=2, max_length=50)]
PhoneType = Annotated[str, StringConstraints(pattern=r'^\+?[0-9]{10,15}$')]
AddressType = Annotated[str, StringConstraints(min_length=3, max_length=100)]


# ✅ Create Customer
class CreateCustomerInput(BaseModel):
    name: NameType
    phone: PhoneType
    address: AddressType

class CreateCustomerTool(BaseTool):
    def get_input_schema(self):
        return CreateCustomerInput

    def run(self, input: CreateCustomerInput) -> str:
        db = SessionLocal()
        customer = Customer(name=input.name, phone=input.phone, address=input.address)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        db.close()
        return f"✅ Created customer {customer.name} with ID {customer.id}"

create_customer_tool = CreateCustomerTool(
    name="create_customer_tool",
    description="Create a new customer by providing name, phone, and address"
)

# ✅ Read Customers
class ReadCustomerInput(BaseModel):
    id: Optional[int] = None

class ReadCustomerTool(BaseTool):
    def get_input_schema(self):
        return ReadCustomerInput

    def run(self, input: ReadCustomerInput) -> str:
        db = SessionLocal()
        if input.id:
            customer = db.query(Customer).filter(Customer.id == input.id).first()
            db.close()
            if customer:
                return f"📋 Customer ID {customer.id}: {customer.name}, {customer.phone}, {customer.address}"
            else:
                return "❌ Customer not found."
        else:
            customers = db.query(Customer).all()
            db.close()
            return "\n".join([f"{c.id}: {c.name}, {c.phone}, {c.address}" for c in customers]) or "No customers found."

read_customers_tool = ReadCustomerTool(
    name="read_customers_tool",
    description="Read one or all customers. Provide ID to fetch one, or leave blank to list all."
)

# ✅ Update Customer
class UpdateCustomerInput(BaseModel):
    id: int
    name: NameType | None = None
    phone: PhoneType | None = None
    address: AddressType | None = None


class UpdateCustomerTool(BaseTool):
    def get_input_schema(self):
        return UpdateCustomerInput

    def run(self, input: UpdateCustomerInput) -> str:
        db = SessionLocal()
        customer = db.query(Customer).filter(Customer.id == input.id).first()
        if not customer:
            db.close()
            return "❌ Customer not found."
        if input.name: customer.name = input.name
        if input.phone: customer.phone = input.phone
        if input.address: customer.address = input.address
        db.commit()
        db.refresh(customer)
        db.close()
        return f"✅ Updated customer {customer.id}: {customer.name}, {customer.phone}, {customer.address}"

update_customer_tool = UpdateCustomerTool(
    name="update_customer_tool",
    description="Update an existing customer by ID. Optional: name, phone, or address."
)

# ✅ Delete Customer
class DeleteCustomerInput(BaseModel):
    id: int

class DeleteCustomerTool(BaseTool):
    def get_input_schema(self):
        return DeleteCustomerInput

    def run(self, input: DeleteCustomerInput) -> str:
        db = SessionLocal()
        customer = db.query(Customer).filter(Customer.id == input.id).first()
        if not customer:
            db.close()
            return "❌ Customer not found."
        db.delete(customer)
        db.commit()
        db.close()
        return f"🗑️ Deleted customer with ID {input.id}"

delete_customer_tool = DeleteCustomerTool(
    name="delete_customer_tool",
    description="Delete a customer by ID."
)
