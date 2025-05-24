# I used VUE website for movie images and most other data

from flask import Flask, render_template, redirect, url_for, session, request
from schema import Customer, Movie, Viewing, Booking, Screen, Review
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, TimeField, FloatField, FileField, IntegerField, DateTimeField #BooleanField
from flask_sqlalchemy import SQLAlchemy
import datetime
import random
import os.path

#$envFLASK='app.py'
#python -m flask run

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'GFJHGFCHJC'
app.debug = True
db = SQLAlchemy(app)

class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True)
    realname = db.Column(db.String(40))
    username = db.Column(db.String(40))
    email = db.Column(db.String(40))
    password = db.Column(db.String(30))
    is_vip = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)
    balance = db.Column(db.Float)

    def __repr__(self):
        return "Customer {0}, id {6}, username {1}, email {2}, password {3}, is_vip {4}, balance {5}, is_admin {6}.".format(
            self.realname, self.username, self.email, self.password, self.is_vip, self.balance, self.customer_id, self.is_admin
        )

class Movie(db.Model):
    __tablename__ = 'movies'

    movie_id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column(db.String(50))
    movie_genre = db.Column(db.String(40))
    viewing_price = db.Column(db.Float)
    length = db.Column(db.Integer)
    director = db.Column(db.String(50))
    cast = db.Column(db.String(100))
    description = db.Column(db.String(1000))

    def __repr__(self):
        return "id {6}, movie {0}, genre {1}, viewing_price {2}, length {3}, director {4}, cast {5}, description {7}".format(
            self.movie_title, self.movie_genre, self.viewing_price, self.length, self.director, self.cast, self.movie_id, self.description
        )

class Review(db.Model):
    __tablename__ = 'reviews'

    review_id = db.Column(db.Integer, primary_key=True)
    post_time = db.Column(db.Time)
    post_date = db.Column(db.Date)
    comment = db.Column(db.String(500))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))

    def __repr__(self):
        return "id {0}, post_time {1}, post_date {2}, comment {3}, customer_id {4}".format(
            self.review_id, self.post_time, self.post_date, self.comment, self.customer_id
        )

class Viewing(db.Model):
    __tablename__ = 'viewings'

    viewing_id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime)
    screen_id = db.Column(db.Integer, db.ForeignKey('screens.screen_id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    seats_available = db.Column(db.Integer)
    vip_seats_available = db.Column(db.Integer)

    def __repr__(self):
        return "id {3} Viewing on {0}, at screen {1} of movie id {2}, number of seats available {4}, number of VIP seats available {5}".format(
            self.start_datetime, self.screen_id, self.movie_id, self.viewing_id, self.seats_available, self.vip_seats_available
        )

class Booking(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    viewing_id = db.Column(db.Integer, db.ForeignKey('viewings.viewing_id'))
    price = db.Column(db.Float)
    vip_seat = db.Column(db.Boolean)

    def __repr__(self):
        return "Booking, id {0}, customer_id {1}, viewing_id {2}, price {3}, vip_seat {4}".format(
            self.booking_id, self.customer_id, self.viewing_id, self.price, self.vip_seat
        )

class Screen(db.Model):
    __tablename__ = 'screens'

    screen_id = db.Column(db.Integer, primary_key=True)
    total_seats = db.Column(db.Integer)
    vip_seats = db.Column(db.Integer)

    def __repr__(self):
        return "Screen {0} with {1} total seats and {2} VIP seats".format(
            self.id, self.total_seats, self.vip_seats
        )

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Log in')

class RegisterForm(FlaskForm):
    realname = StringField('Real name')
    username = StringField('Username')
    email = StringField('Email')
    password = PasswordField('Password')
    re_enter_password = PasswordField('Re-enter Password')
    submit = SubmitField('Register')

class SearchFilterForm(FlaskForm):
    minimum_date = DateField('Minimum date')
    maximum_date = DateField('Maximum date')
    minimum_time = TimeField('Minimum time')
    maximum_time = TimeField('Maximum time')
    maximum_price = FloatField('Maximum price')
    movie_title = StringField('Movie title')
    movie_genre = StringField('Movie genre')
    submit = SubmitField('Search')

class AddMovieForm(FlaskForm):
    movie_title = StringField('Movie title')
    movie_genre = StringField('Movie genre')
    viewing_price = FloatField('Viewing price')
    length = IntegerField('Length')
    director = StringField('Director')
    cast = StringField('Cast')
    description = StringField('Description')
    movie_image = FileField()
    submit = SubmitField('Add movie')

class MovieForm(FlaskForm):
    submit1 = SubmitField('Book')
    submit2 = SubmitField('Submit review')
    comment = StringField('Comment')

def create_viewings():
    global date
    now = datetime.datetime.now()
    viewing_day_span = 7 - (datetime.datetime(year=date.year, month=date.month, day=date.day) - datetime.datetime(year=now.year, month=now.month, day=now.day)).days # number of days in advance (including current day) that viewings are made for
    opening_hour, opening_minute = 10, 0 # opening times for each day
    closing_hour, closing_minute = 22, 30 # closing times for each day, a movie will not run past the closing time
    viewing_creation_intervals = 15 # time between the end of a viewing and the start of the next viewing for a screen (measured in minutes)
    number_of_screens = len(Screen.query.all())
    for i in range(viewing_day_span):
        if i == 0: # only relevant for the first day for if the current time is less than the opening time
            if (date.hour < opening_hour) or (date.hour == opening_hour and date.minute < opening_minute):
                date = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=opening_hour, minute=opening_minute)
        for s in range(1,number_of_screens+1):
            time = date
            while True:
                movie = Movie.query.filter(Movie.movie_id == random.randint(1,len(Movie.query.all()))).first()
                start_time = time
                time = time + datetime.timedelta(minutes=movie.length)
                if ((time.hour < closing_hour) or (time.hour == closing_hour and time.minute < closing_minute)) and (time.day == date.day):
                    screen = Screen.query.filter(Screen.screen_id == s).first()
                    new_viewing = Viewing(start_datetime=start_time, screen_id=s, movie_id=movie.movie_id, seats_available=screen.total_seats, vip_seats_available=screen.vip_seats)
                    db.session.add(new_viewing)
                    db.session.commit()
                    time = time + datetime.timedelta(minutes = viewing_creation_intervals)
                else:
                    break
        date = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=opening_hour, minute=opening_minute) + datetime.timedelta(days=1)
        print(date)

def is_valid_customer():
    customer_id = session.get('customer', -1)
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    return not(customer is None)

def is_valid_admin():
    if is_valid_customer() == True:
        customer_id = session.get('customer')
        customer = Customer.query.filter_by(customer_id=customer_id).first()
        return customer.is_admin
    return False

with app.app_context():
    db.create_all()
    global date
    date = datetime.datetime.now()
    date = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=date.hour, minute=date.minute)
    need_to_initialise = (len(Viewing.query.all()) == 0)
    if need_to_initialise == 1:
        create_viewings()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.is_submitted():
        realname = form.realname.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        re_enter_password = form.re_enter_password.data
        if Customer.query.filter_by(username=username).first() != None:
            print('Username not unique')
            return render_template('register.html', form=form)
        if Customer.query.filter_by(email=email).first() != None:
            print('Email may only be associated with one account')
            return render_template('register.html', form=form)
        if re_enter_password != password:
            print('Passwords not indentical')
            return render_template('register.html', form=form)
        else:
            new_customer = Customer(realname=realname, username=username, email=email, password=password, is_vip=0, is_admin=0, balance=30.00) # register and get £30.00 to be spent on movies
            db.session.add(new_customer)
            db.session.commit()
            print('User registered')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    create_viewings()
    form = LoginForm()
    if form.is_submitted():
        username = form.username.data
        password = form.password.data
        customer = Customer.query.filter_by(username=username, password=password).first()
        if customer is None:
            print('Login failed')
            return render_template('login.html', form=form)
        if customer.is_admin == True:
            print('admin access')
            session['customer'] = customer.customer_id
            return redirect(url_for('admin'))
        else:
            print('Login successful')
            session['customer'] = customer.customer_id
            return redirect(url_for('movies'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if is_valid_admin() == False:
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/customer_data', methods=['GET', 'POST'])
def customer_data():
    if is_valid_admin() == False:
        return redirect(url_for('login'))
    return render_template('customer_data.html', customers=Customer.query.order_by(Customer.username).all())

@app.route('/delete_customer/<customer_id_>', methods=['GET', 'POST'])
def delete_customer(customer_id_):
    if is_valid_admin() == False:
        return redirect(url_for('login'))
    customer_id = (Customer.query.filter(Customer.customer_id == customer_id_).first()).customer_id
    bookings = Booking.query.filter(Booking.customer_id == customer_id).all()
    for booking in bookings:
        viewing = Viewing.query.filter(Viewing.viewing_id == booking.viewing_id).first()
        viewing.seats_available += 1
        db.session.commit()
        if booking.vip_seat == True:
            viewing.vip_seats_available += 1
            db.session.commit()
        Booking.query.filter(Booking.booking_id == booking.booking_id).delete()
        db.session.commit()
    Review.query.filter(Review.customer_id == customer_id).delete()
    db.session.commit()
    Customer.query.filter(Customer.customer_id == customer_id).delete()
    db.session.commit()
    return redirect(url_for('customer_data'))

@app.route('/make_admin/<customer_id_>', methods=['GET', 'POST'])
def make_admin(customer_id_):
    if is_valid_admin() == False:
        return redirect(url_for('login'))
    Customer.query.get(int(customer_id_)).is_admin = True
    db.session.commit()
    return redirect(url_for('customer_data'))

@app.route('/movie_data/', methods=['GET', 'POST'])
def movie_data():
    if is_valid_admin() == False:
        return redirect(url_for('login'))
    return render_template('movie_data.html', movies=Movie.query.order_by(Movie.movie_title).all())

@app.route('/delete_movie/<movie_id_>', methods=['GET', 'POST'])
def delete_movie(movie_id_):
    if is_valid_admin() == False:
        return redirect(url_for('login'))
    Movie.query.filter(Movie.movie_id == movie_id_).delete()
    db.session.commit()
    return redirect(url_for('movie_data'))

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if is_valid_admin() == False:
        return redirect(url_for('login'))
    form = AddMovieForm()
    if form.is_submitted():
        image = form.movie_image.data
        title = form.movie_title.data
        genre = form.movie_genre.data
        viewing_price = form.viewing_price.data
        length = form.length.data
        description = form.description.data
        director = form.director.data
        cast = form.cast.data
        new_movie = Movie(movie_title=title,movie_genre=genre,viewing_price=viewing_price,length=length,description=description,director=director,cast=cast)
        db.session.add(new_movie)
        db.session.commit()
        save_path = './static/images'
        name_of_file = str(new_movie.movie_id) + ".jpg"
        image.save(os.path.join(save_path, name_of_file))
        return render_template('add_movie.html', form=form)
    return render_template('add_movie.html', form=form)

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    if is_valid_customer() == False:
        return redirect(url_for('login'))
    create_viewings()
    form = SearchFilterForm()
    movies = Movie.query.all()
    booking_viewing_ids = [booking.viewing_id for booking in Booking.query.filter(session['customer'] == Booking.customer_id).all()]
    viewings = Viewing.query.filter(Viewing.seats_available > 0).order_by(Viewing.start_datetime).all()
    i = 0
    while i < len(viewings):
        if viewings[i].viewing_id in booking_viewing_ids:
            del viewings[i]
            continue
        i += 1
    if form.is_submitted():
        minimum_date = form.minimum_date.data
        maximum_date = form.maximum_date.data
        minimum_time = form.minimum_time.data
        maximum_time = form.maximum_time.data
        maximum_price = form.maximum_price.data
        movie_title = form.movie_title.data
        movie_genre = form.movie_genre.data
        i = 0
        while i < len(viewings):
            movie = Movie.query.filter(viewings[i].movie_id == Movie.movie_id).first()
            if maximum_price != None:
                if movie.viewing_price > maximum_price:
                    del viewings[i]
                    continue
            if minimum_date != None:
                if (viewings[i].start_datetime).date() < minimum_date:
                    del viewings[i]
                    continue
            if minimum_time != None:
                if (viewings[i].start_datetime).time() < minimum_time:
                    del viewings[i]
                    continue
            if maximum_date != None:
                if (viewings[i].start_datetime).date() > maximum_date:
                    del viewings[i]
                    continue
            if maximum_time != None:
                if (viewings[i].start_datetime).time() > maximum_time:
                    del viewings[i]
                    continue
            if movie_title != None:
                title_movie_ids = [movie.movie_id for movie in Movie.query.filter(Movie.movie_title.like("%{}%".format(movie_title))).all()]
                if viewings[i].movie_id not in title_movie_ids:
                    del viewings[i]
                    continue
            if movie_genre != None:
                genre_movie_ids = [movie.movie_id for movie in Movie.query.filter(Movie.movie_genre.like("%{}%".format(movie_genre))).all()]
                if viewings[i].movie_id not in genre_movie_ids:
                    del viewings[i]
                    continue 
            i += 1
        return render_template('movies.html', viewings=viewings, movies=movies, is_admin=Customer.query.filter_by(customer_id=session['customer']).first().is_admin)
    return render_template('movies.html', viewings=viewings, movies=movies, is_admin=Customer.query.filter_by(customer_id=session['customer']).first().is_admin)

@app.route('/account_details', methods=['GET', 'POST'])
def account_details():
    if is_valid_customer() == False:
        return redirect(url_for('login'))
    return render_template('account_details.html', customer=Customer.query.filter_by(customer_id=session['customer']).first())

@app.route('/customer_booking_data', methods=['GET', 'POST'])
def customer_booking_data():
    if is_valid_customer() == False:
        return redirect(url_for('login'))
    return render_template('customer_booking_data.html')

@app.route('/current_bookings', methods=['GET', 'POST'])
def current_bookings():
    if is_valid_customer() == False:
        return redirect(url_for('login'))
    booking_booking_ids = [booking.booking_id for booking in Booking.query.filter(session['customer'] == Booking.customer_id).all()]
    booking_viewing_ids = [booking.viewing_id for booking in Booking.query.filter(session['customer'] == Booking.customer_id).all()]
    booking_prices = [booking.price for booking in Booking.query.filter(session['customer'] == Booking.customer_id).all()]
    booking_vip_seat = [booking.vip_seat for booking in Booking.query.filter(session['customer'] == Booking.customer_id).all()]
    viewing_movie_ids = []
    viewing_screen_ids = []
    viewing_start_times = []
    for i in range(len(booking_viewing_ids)):
        n = Viewing.query.filter(Viewing.viewing_id == booking_viewing_ids[i]).first()
        viewing_movie_ids.append(n.movie_id)
        viewing_screen_ids.append(n.screen_id)
        viewing_start_times.append(n.start_datetime)
    movie_titles = []
    for i in range(len(viewing_movie_ids)):
        movie_titles.append((Movie.query.filter(Movie.movie_id == viewing_movie_ids[i]).first()).movie_title)
    info=[]
    for i in range(len(booking_viewing_ids)):   
        info.append((movie_titles[i],viewing_screen_ids[i],viewing_start_times[i],booking_prices[i],booking_vip_seat[i],booking_booking_ids[i]))
    return render_template('current_bookings.html',info=info)

@app.route('/delete_booking/<booking_id>')
def delete_booking(booking_id):
    if is_valid_customer() == False:
        return redirect(url_for('login'))
    customer = Customer.query.filter(Customer.customer_id == session['customer']).first()
    booking = Booking.query.filter(Booking.booking_id == booking_id).first()
    if customer.customer_id != booking.customer_id:
        return redirect(url_for('movies'))
    viewing = Viewing.query.filter(Viewing.viewing_id == booking.viewing_id).first()
    viewing.seats_available += 1
    db.session.commit()
    if booking.vip_seat == True:
        viewing.vip_seats_available += 1
        db.session.commit()
    if datetime.datetime.now() + datetime.timedelta(days=1) < viewing.start_datetime: # refund if deleted more than a day before the booking
        customer = Customer.query.filter(Customer.customer_id == session['customer']).first()
        customer.balance += booking.price
        db.session.commit()
    Booking.query.filter(Booking.booking_id == booking_id).delete()
    db.session.commit()
    return redirect(url_for('current_bookings'))

@app.route('/movie/<viewing_id_>', methods=['GET', 'POST'])
def movie(viewing_id_):
    if is_valid_customer() == False:
        return redirect(url_for('login'))
    viewing_ = Viewing.query.filter_by(viewing_id=viewing_id_).first()
    if viewing_ is None:
        return redirect(url_for('movies'))
    session['viewing'] = viewing_id_
    vip_seat_cost = 3
    viewing = Viewing.query.filter(Viewing.viewing_id == session['viewing']).first()
    movie = Movie.query.filter(Movie.movie_id == viewing.movie_id).first()
    logged_in_customer = Customer.query.filter(Customer.customer_id == session['customer']).first()
    movie_form = MovieForm()
    vip_seats = 0
    if movie_form.is_submitted():
        customer_bookings = [booking.viewing_id for booking in Booking.query.filter(session['customer'] == Booking.customer_id).all()]
        if request.form.getlist("submit1") and (int(session["viewing"]) not in customer_bookings):
            if logged_in_customer.balance >= movie.viewing_price:
                if request.form.getlist("vip_seats_booking") == []:
                    pass
                else:
                    vip_seats = 1
                if viewing.seats_available <= viewing.vip_seats_available:
                    vip_seats = 1
                price = movie.viewing_price + vip_seat_cost*vip_seats*int(logged_in_customer.is_vip==False) # vip seats only charged if customer selects them and they are not a VIP
                logged_in_customer.balance = round((logged_in_customer.balance - price),2)
                db.session.commit()
                viewing.seats_available -= 1
                db.session.commit()
                if vip_seats == 1:
                    viewing.vip_seats_available -= 1
                    db.session.commit()
                new_booking = Booking(customer_id=session['customer'], viewing_id=session['viewing'], price=price, vip_seat=vip_seats)
                db.session.add(new_booking)
                db.session.commit()
                return redirect(url_for('booking_confirmation', viewing_id_=viewing.viewing_id))
            else:
                return redirect(url_for('movie', viewing_id_ = viewing.viewing_id))
        if request.form.getlist("submit2"):
            comment = movie_form.comment.data
            now = datetime.datetime.now()
            new_review = Review(customer_id=session['customer'], post_date=datetime.date(now.year,now.month,now.day), post_time=datetime.time(now.hour,now.minute,now.second), comment=comment, movie_id=movie.movie_id)
            db.session.add(new_review)
            db.session.commit()
    customers = Customer.query.all()
    reviews = Review.query.filter(Review.movie_id == movie.movie_id).all()
    return render_template('movie.html',viewing=viewing,movie=movie,image_id=str(movie.movie_id),reviews=reviews,customers=customers,is_empty=(len(reviews)==0),logged_in_customer=logged_in_customer,vip_seat_cost=vip_seat_cost)

@app.route('/booking_confirmation/<viewing_id_>', methods=['GET', 'POST'])
def booking_confirmation(viewing_id_):
    if is_valid_customer() == False:
        return redirect(url_for('login'))
    bookings = Booking.query.filter_by(customer_id=session['customer']).all()
    viewing = ''
    price = 0
    for booking in bookings:
        if int(viewing_id_) == booking.viewing_id:
            viewing = viewing_id_
            price = booking.price
            break
    if viewing == '':
        return redirect(url_for('movies'))
    viewing = Viewing.query.filter(Viewing.viewing_id == session['viewing']).first()
    movie = Movie.query.filter(Movie.movie_id == viewing.movie_id).first()
    logged_in_customer = Customer.query.filter(Customer.customer_id == session['customer']).first()
    return render_template('booking_confirmation.html',viewing=viewing,movie=movie,logged_in_customer=logged_in_customer,price=price)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if is_valid_customer() == False:
        return redirect(url_for('login'))
    del session['customer']
    return redirect(url_for('login'))


