import sqlalchemy
import csv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Time, Date, DateTime
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

engine = create_engine('sqlite:///cinema.db', echo=True)
Session = sessionmaker(bind=engine)

class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(Integer, primary_key=True)
    realname = Column(String(40))
    username = Column(String(40))
    email = Column(String(40))
    password = Column(String(30))
    is_vip = Column(Boolean)
    is_admin = Column(Boolean)
    balance = Column(Float)

    bookings = relationship("Booking", back_populates='customer')
    reviews = relationship("Review", back_populates='customer')

    def __repr__(self):
        return "<Customer(customer_id={0}, realname={1}, username={2}, email={3}, password={4}, is_vip={5}, is_admin={7} balance={6},>".format(
            self.customer_id, self.realname, self.username, self.email, self.password, self.is_vip, self.balance, self.is_admin
        )

class Movie(Base):
    __tablename__ = 'movies'

    movie_id = Column(Integer, primary_key=True)
    movie_title = Column(String(50))
    movie_genre = Column(String(40))
    length = Column(Integer)
    director = Column(String(100))
    cast = Column(String(300))
    viewing_price = Column(Float)
    description = Column(String(1000))

    viewings = relationship("Viewing", back_populates='movie')
    reviews = relationship("Review", back_populates='movie')

    def __repr__(self):
        return "<Movie(movie_id={6}, movie_title={0}, movie_genre={1}, viewing_price={2}, length={3}, director={4}, cast={5}, description={7}>".format(
            self.movie_title, self.movie_genre, self.viewing_price, self.length, self.director, self.cast, self.movie_id, self.description
        )

class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key=True)
    post_time = Column(Time)
    post_date = Column(Date)
    comment = Column(String(500))
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    movie_id = Column(Integer, ForeignKey('movies.movie_id'))

    customer = relationship("Customer", back_populates='reviews')
    movie = relationship("Movie", back_populates='reviews')

    def __repr__(self):
        return "<Review(review_id={0}, post_time={1}, post_date={2}, comment={3}, customer_id={4}, movie_id={5}>".format(
            self.review_id, self.post_time, self.post_date, self.comment, self.customer_id, self.movie_id
        )

class Viewing(Base):
    __tablename__ = 'viewings'

    viewing_id = Column(Integer, primary_key=True)
    start_datetime = Column(DateTime)
    screen_id = Column(Integer, ForeignKey('screens.screen_id'))
    movie_id = Column(Integer, ForeignKey('movies.movie_id'))
    seats_available = Column(Integer)
    vip_seats_available = Column(Integer)

    movie = relationship("Movie", back_populates='viewings')
    screen = relationship("Screen", back_populates='viewings')
    bookings = relationship("Booking", back_populates='viewing')

    def __repr__(self):
        return "<Viewing(start_datetime={0}, screen_id={1}, movie_id={2}, number_booked={3}>".format(
            self.start_datetime, self.screen_id, self.movie_id, self.number_booked
        )

class Booking(Base):
    __tablename__ = 'bookings'

    booking_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    viewing_id = Column(Integer, ForeignKey('viewings.viewing_id'))
    price = Column(Float)
    vip_seat = Column(Boolean)

    customer = relationship("Customer", back_populates='bookings')
    viewing = relationship("Viewing", back_populates='bookings')

    def __repr__(self):
        return "<Screen(booking_id={3}, customer_id={0}, viewing_id={4}, price={1}, vip_seat={2}>".format(
            self.customer_id, self.price, self.vip_seat, self.booking_id, self.viewing_id
        )

class Screen(Base):
    __tablename__ = 'screens'

    screen_id = Column(Integer, primary_key=True)
    total_seats = Column(Integer)
    vip_seats = Column(Integer)

    viewings = relationship("Viewing", back_populates='screen')

    def __repr__(self):
        return "<Screen(screen_id={0}, total_seats={1}, vip_seats={2}>".format(
            self.screen_id, self.total_seats, self.vip_seats
        )

if __name__ == "__main__":  

    Base.metadata.create_all(engine)
    session = Session()

    objects_to_add = []
    if session.query(Customer).count() == 0:
        with open("customers_.csv", "r") as customers_file:
            next(customers_file)
            lines = csv.reader(customers_file)
            for line in lines:
                realname, username, email, password, is_vip, balance, customer_id, is_admin = line
                new_customer = Customer(customer_id=customer_id, realname=realname, username=username, email=email, password=password, is_vip=bool(int(is_vip)), balance=balance, is_admin=bool(int(is_admin)))
                objects_to_add.append(new_customer)

    if session.query(Screen).count() == 0:
        with open("screens.csv", "r") as screens_file:
            next(screens_file)
            lines = csv.reader(screens_file)
            for line in lines:
                screen_id, total_seats, vip_seats = line
                new_screen = Screen(screen_id=screen_id, total_seats=total_seats, vip_seats=vip_seats)
                objects_to_add.append(new_screen)

    if session.query(Movie).count() == 0:
        with open("movies.csv", "r") as movies_file:
            next(movies_file)
            lines = csv.reader(movies_file, delimiter='$')
            for line in lines:
                movie_id, movie_title, movie_genre, length, director, cast, viewing_price, description = line
                new_movie = Movie(movie_id=movie_id, movie_title=movie_title, movie_genre=movie_genre, length=length, director=director, cast=cast, viewing_price=viewing_price, description=description)
                objects_to_add.append(new_movie)

    session.add_all(objects_to_add)
    session.commit()