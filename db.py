from sqlalchemy import create_engine, Column, String, Integer, Float
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
        return "<User({})>".format(self)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    description = Column(String(50))
    price = Column(Float)

    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship("Department", back_populates="articles")

    iva_type = Column(Integer, ForeignKey('iva.id'))
    iva = relationship("Iva", back_populates="articles")

    def __repr__(self):
        return "<Article({})>".format(self)


class Iva(Base):
    __tablename__ = "iva"

    id = Column(Integer, primary_key=True)
    type = Column(Integer)

    articles = relationship("Article", order_by=Article.id, back_populates="iva")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    description = Column(String(50))

    family_id = Column(Integer, ForeignKey('families.id'))
    family = relationship("Family", back_populates="departments")

    articles = relationship("Article", order_by=Article.id, back_populates="department")

    def __repr__(self):
        return "<Department({})>".format(self)


class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    description = Column(String(50))

    departments = relationship("Department", order_by=Department.id, back_populates="family")

    def __repr__(self):
        return "<Family(name: %s)>" % self.name
        

def create_db():
    Base.metadata.create_all(engine)

    if session.query(User).filter_by(username="1234").one_or_none() is None:
        user = User(username="1234", password="1234")
        session.add(user)

        session.add_all([
            Iva(type=21),
            Iva(type=10),
            Iva(type=4),
        ])

        session.commit()

