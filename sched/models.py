from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import synonym, relationship
from sqlalchemy.ext.declarative import declarative_base

from werkzeug import check_password_hash, generate_password_hash

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    name = Column('name', String(200))
    email = Column(String(100), unique=True, nullable=False)
    active = Column(Boolean, default=True)

    _password = Column('password', String(100))

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password:
            password = password.strip()
        self._password = generate_password_hash(password)

    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)

    def check_password(self, password):
        if self.password is None:
            return False
        password = password.strip()

        if not password:
            return False

        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, query, email, password):
        email = email.strip().lower()
        user = query(cls).filter(cls.email==email).first()

        if user is None:
            return None, False
        if not user.active:
            return user, False

        return user, user.check_password(password)

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

class Appointment(Base):
    __tablename__ = 'appointment'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now,
        onupdate=datetime.now)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User, lazy='joined', join_depth=1)

    title = Column(String(255))
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    allday = Column(Boolean, default=False)
    location = Column(String(255))
    description = Column(Text)

    @property
    def duration(self):
        delta = self.end - self.start
        return delta.days * 24 * 60 * 60 + delta.seconds

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'
            .format(self=self))

if __name__ == '__main__':
    from datetime import timedelta
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///sched.db', echo=True)
    Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(name='Jeph Do',
                email='jephdo@gmail.com',
                password='secret')
    session.add(user)
    session.commit()

    now = datetime.now()

    session.add(Appointment(
        user_id=user.id,
        title='Important Meeting',
        start=now + timedelta(days=3),
        end=now + timedelta(days=3, seconds=3600),
        allday=False,
        location='The Office'))
    session.commit()

    session.add(Appointment(
        user_id=user.id,
        title='Past Meeting',
        start=now - timedelta(days=3, seconds=3600),
        end=now - timedelta(days=3),
        allday=False,
        location='The Office'))
    session.commit()

    session.add(Appointment(
        user_id=user.id,
        title='Follow Up',
        start=now + timedelta(days=4),
        end=now + timedelta(days=4, seconds=3600),
        allday=False,
        location='The Office'))
    session.commit()

    session.add(Appointment(
        user_id=user.id,
        title='Day Off',
        start=now + timedelta(days=5),
        end=now + timedelta(days=5),
        allday=True))
    session.commit()

    appt = Appointment(
        user_id=user.id,
        title='My Appointment',
        start=now,
        end=now + timedelta(seconds=1800),
        allday=False)

    # Create.
    session.add(appt)
    session.commit()

    # update
    appt.title = 'Your Appointment'
    session.commit()

    # delete
    session.delete(appt)
    session.commit()

    # Demonstration Queries

    # Each `appt` example is a Python object of type Appointment.
    # Each `appts` example is a Python list of Appointment objects.

    # Get an appointment by ID.
    appt = session.query(Appointment).get(1)
    print(appt)

    # Get all appointments.
    appts = session.query(Appointment).all()
    print(appts)

    # Get all appointments before right now, after right now.
    appts = session.query(Appointment).filter(Appointment.start < datetime.now()).all()
    print(appts)
    appts = session.query(Appointment).filter(Appointment.start >= datetime.now()).all()
    print(appts)

    # Get all appointments before a certain date.
    appts = session.query(Appointment).filter(Appointment.start <= datetime(2013, 5, 1)).all()
    print(appts)

    # Get the first appointment matching the filter query.
    appt = session.query(Appointment).filter(Appointment.start <= datetime(2013, 5, 1)).first()
    print(appts)