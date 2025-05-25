import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

Base = declarative_base()

# Teams Table
class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="team")

# Company Locations Table (independent)
class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False, default='Poland')
    office_name = Column(String, nullable=False)

# Users Table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    team_id = Column(Integer, ForeignKey('teams.id'))
    team = relationship("Team", back_populates="users")

    # One-to-one relationship with PaidLeave
    paid_leave = relationship("PaidLeave", uselist=False, back_populates="user")

# Paid Leave Summary Table
class PaidLeave(Base):
    __tablename__ = 'paid_leaves'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)

    total_allocated = Column(Integer, nullable=False, default=0)
    utilized = Column(Integer, nullable=False, default=0)

    user = relationship("User", back_populates="paid_leave")

    @property
    def remaining(self):
        return self.total_allocated - self.utilized


DATABASE_URL = "sqlite:///example.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    teams = [
        Team(name="IT"),
        Team(name="HR"),
        Team(name="Finance"),
        Team(name="DevOps")
    ]
    session.add_all(teams)
    session.commit()

    users = [
        User(name="Alice", email="alice@example.com", team=teams[0]),  # IT
        User(name="Alan", email="alan@example.com", team=teams[0]),  # IT
        User(name="Aldrin", email="aldrin@example.com", team=teams[0]),  # IT

        User(name="Bob", email="bob@example.com", team=teams[1]),      # HR
        User(name="Benjamin", email="benjamin@example.com", team=teams[1]),      # HR
        User(name="Beatrice", email="beatrice@example.com", team=teams[1]),      # HR
        User(name="Bianca", email="bianca@example.com", team=teams[1]),      # HR
        User(name="Betty", email="betty@example.com", team=teams[1]),      # HR

        User(name="Charlie", email="charlie@example.com", team=teams[2]),  # Finance
        User(name="Chang", email="chang@example.com", team=teams[2]),  # Finance

        User(name="Diana", email="diana@example.com", team=teams[3]),   # DevOps
        User(name="David", email="david@example.com", team=teams[3]),  # DevOps
        User(name="Denise", email="denise@example.com", team=teams[3]),   # DevOps

    ]
    session.add_all(users)
    session.commit()

    paid_leaves = [
        PaidLeave(user=users[0], total_allocated=24, utilized=4),   # Alice
        PaidLeave(user=users[1], total_allocated=24, utilized=3),   # Alan
        PaidLeave(user=users[2], total_allocated=24, utilized=6),   # Aldrin

        PaidLeave(user=users[3], total_allocated=24, utilized=5),   # Bob
        PaidLeave(user=users[4], total_allocated=24, utilized=7),   # Benjamin
        PaidLeave(user=users[5], total_allocated=24, utilized=2),   # Beatrice
        PaidLeave(user=users[6], total_allocated=24, utilized=8),   # Bianca
        PaidLeave(user=users[7], total_allocated=24, utilized=1),   # Betty

        PaidLeave(user=users[8], total_allocated=24, utilized=3),   # Charlie
        PaidLeave(user=users[9], total_allocated=24, utilized=4),   # Chang

        PaidLeave(user=users[10], total_allocated=24, utilized=6),  # Diana
        PaidLeave(user=users[11], total_allocated=24, utilized=7),  # David
        PaidLeave(user=users[12], total_allocated=24, utilized=5),  # Denise
    ]

    session.add_all(paid_leaves)
    session.commit()

    locations = [
        Location(city="Warsaw", country="Poland", office_name="Warsaw HQ"),
        Location(city="Krakow", country="Poland", office_name="Krakow Tech Center"),
        Location(city="Wroclaw", country="Poland", office_name="Wroclaw Finance Hub"),
        Location(city="Gdansk", country="Poland", office_name="Gdansk Innovation Lab"),
        Location(city="Poznan", country="Poland", office_name="Poznan Support Office"),
    ]

    session.add_all(locations)
    session.commit()

    session.close()
    print("Database populated.")


if __name__ == "__main__":
    if not os.path.exists("example.db"):
        init_db()
    else:
        print("The database 'example.db' already exists.")