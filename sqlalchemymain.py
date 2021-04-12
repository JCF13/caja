from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, aliased, relationship

engine = create_engine('sqlite:///db1.sqlite3', echo=True)

Session = sessionmaker(bind=engine)

session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    nickname = Column(String(50))

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
            self.name, self.fullname, self.nickname
        )


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address

User.addresses = relationship(
    "Address", order_by=Address.id, back_populates="user"
)
        


Base.metadata.create_all(engine)

ed_user = User(name="ed", fullname="Ed Jones", nickname="ednickname")
print(ed_user.name)
print(ed_user.nickname)
print(str(ed_user.id))

session.add(ed_user)

our_user = session.query(User).filter_by(name='ed').first()
print(our_user)

print(ed_user is our_user)

session.add_all([
    User(name="wendy", fullname="Wendy Williams", nickname="windy"),
    User(name="mary", fullname="Mary Contrary", nickname="mary"),
    User(name="fred", fullname="Fred Flintstone", nickname="freddy")
])

ed_user.nickname = 'eddie'

print(session.dirty)
print(session.new)

session.commit()

print(ed_user.id)

ed_user.name = "Edwardo"

fake_user = User(name="fakeuser", fullname="Invalid", nickname="12345")
session.add(fake_user)

session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()

session.rollback()

print(ed_user.name)

print(fake_user in session)

session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all()

for instance in session.query(User).order_by(User.id):
    print(instance.name, instance.fullname)

for name, fullname in session.query(User.name, User.fullname):
    print(name, fullname)

for row in session.query(User, User.name).all():
    print(row.User, row.name)

for row in session.query(User.name.label('name_label')).all():
    print(row.name_label)

user_alias = aliased(User, name='user_alias')

for row in session.query(user_alias, user_alias.name).all():
    print(row.user_alias)

for u in session.query(User).order_by(User.id)[1:3]:
    print(u)

for name, in session.query(User.name).\
        filter_by(fullname='Ed Jones'):
    print(name)

for name, in session.query(User.name).\
        filter(User.fullname=='Ed Jones'):
    print(name)

for user in session.query(User).\
        filter(User.name=='ed').\
        filter(User.fullname=='Ed Jones'):
    print(user)

# EQUALS, NOT EQUALS, LIKE, ILIKE, IN, NOT IN, IS, IS NOT, 
# AND, OR, MATCH

# Query.all() -> list
# Query.first()
# Query.one() -> Error si hay más de uno
# Query.one_or_none() -> Igual a one() pero si no hay devuelve None
# Query.scalar()

# Textual SQL -> filter(text(...))
# filter(text(id<:value)).params(value=1)
# Query.from_statement(text(SELECT...))
# stmt = text(...)      stmt = stmt.columns(...)    Query.from_statement(stmt)