# sqlalchemy for our db stuff
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# Base class that the other models will inherit from
Base = declarative_base()


engine = create_engine('sqlite:///freebies.db')

# Setting up session stuff 
Session = sessionmaker(bind=engine)
session = Session()

# This handles the many-to-many relationship between devs and companies
# Had to look this up to get the syntax right 
dev_freebies = Table(
    'dev_freebies', 
    Base.metadata,
    Column('dev_id', Integer, ForeignKey('devs.id'), primary_key=True),
    Column('company_id', Integer, ForeignKey('companies.id'), primary_key=True)
)

class Company(Base):
    __tablename__ = 'companies'
    
    # Basic company info
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # company names can't be null
    founding_year = Column(Integer, nullable=False)

    # Relations...this took me a while to get right
    freebies = relationship('Freebie', back_populates='company')
    devs = relationship('Dev', secondary=dev_freebies, back_populates='companies')

    @classmethod
    def oldest_company(cls, session):
        
        return session.query(cls).order_by(cls.founding_year).first()
    
    def give_freebie(self, dev, item_name, value, session):
        """Give a freebie to a dev - returns None if something goes wrong"""
        # Create new freebie
        new_freebie = Freebie(
            dev_id=dev.id, 
            company_id=self.id, 
            item_name=item_name, 
            value=value
        )
        
        session.add(new_freebie)
        
        # Had to Wrap this in try/except cause db operations can be specific sometimes
        try:
            session.commit()
        except Exception as e:
            session.rollback()  # always rollback on error
            print(f"Ugh, something went wrong: {e}")  
            return None
            
        return new_freebie

class Dev(Base):
    __tablename__ = 'devs'

    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # Relationship stuff
    freebies = relationship('Freebie', back_populates='dev')
    companies = relationship('Company', secondary=dev_freebies, back_populates='devs')

    def received_one(self, item_name):
        # Check if dev got specific freebie 
        
        for freebie in self.freebies:
            if freebie.item_name == item_name:
                return True
        return False

    def give_away(self, dev, freebie):
        # Let devs give away their freebies
        
        if freebie.dev == self:  
            freebie.dev = dev

class Freebie(Base):
    __tablename__ = 'freebies'

    # Columns for tracking 
    id = Column(Integer, primary_key=True)
    item_name = Column(String, nullable=False)
    value = Column(Integer, nullable=False)  
    
    # Foreign keys
    dev_id = Column(Integer, ForeignKey('devs.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)

    # Relations
    dev = relationship('Dev', back_populates='freebies')
    company = relationship('Company', back_populates='freebies')

    def print_details(self):
        # Quick way to see who owns what
        return f"{self.dev.name} owns a {self.item_name} from {self.company.name}."

# DB setup stuff

engine = create_engine('sqlite:///freebie_app.db')
Session = sessionmaker(bind=engine)

def initialize_database():
    # Creates all the tables - you can run this when setting up the app
    Base.metadata.create_all(engine)

# Only run init if we're running this file directly
if __name__ == "__main__":
    initialize_database()  # sets up the db
    
# 