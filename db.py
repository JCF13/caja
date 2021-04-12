from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql.schema import ForeignKey

engine = create_engine("sqlite:///db.sqlite3", echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(username: %s, password: %s)>" % (self.username, self.password)


class Article(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    description = Column(String(50))
    price = Column(Integer),

    department_id = Column(Integer, ForeignKey('departments.id'))

    department = relationship("Department", back_populates="content")

    def __repr__(self):
        return "<Article({})>".format(self)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    content = relationship("Content", order_by=Article.id, back_populates="department")

    def __repr__(self):
        return "<Department({})>".format(self)


class IVA(Base):
    __tablename__ = "iva"

    id = Column(Integer, primary_key=True)
    



def create_db():
    Base.metadata.create_all(engine)

    if session.query(User).filter_by(username="1234").one_or_none() is None:
        user = User(username="1234", password="1234")
        session.add(user)
        session.commit()

