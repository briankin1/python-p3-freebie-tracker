#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Company, Dev, Freebie  

# Create an engine
engine = create_engine('sqlite:///freebies.db') 


Session = sessionmaker(bind=engine)

# Create a session instance
session = Session()

# Create the database and tables
Base.metadata.create_all(engine)

# Create some sample data
company1 = Company(name="Tech Corp", founding_year=2000)
dev1 = Dev(name="Alice")
dev2 = Dev(name="Bob")

# Add companies and devs to session and commit
session.add(company1)
session.add(dev1)
session.add(dev2)
session.commit()


freebie1 = company1.give_freebie(dev1, "T-shirt", 10, session)  
freebie2 = company1.give_freebie(dev1, "Mug", 5, session)       
freebie3 = company1.give_freebie(dev2, "Sticker", 1, session)   

# Print details of freebies
print(freebie1.print_details())  # Should print: Alice owns a T-shirt from Tech Corp.
print(freebie2.print_details())  # Should print: Alice owns a Mug from Tech Corp.
print(freebie3.print_details())  # Should print: Bob owns a Sticker from Tech Corp.

# Test the received_one method
print(dev1.received_one("T-shirt"))  # Should return True
print(dev2.received_one("Mug"))       # Should return False

# Test the oldest_company method
oldest_company = Company.oldest_company(session)
print(f"The oldest company is {oldest_company.name} founded in {oldest_company.founding_year}.")


session.close()