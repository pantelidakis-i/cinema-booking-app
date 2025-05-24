# 🎬 Cinema Booking App

A full-featured web application for managing cinema bookings, built with **Flask**, **SQLite**, and **WTForms**. Users can register, log in, browse movies, book seats, and manage viewings — with both customer and admin functionality.

---

## 🚀 Features

- 🧾 User registration and login
- 🎞️ View available movies and screenings
- 🎟️ Book seats (normal and VIP)
- 👤 Admin panel for managing movies and viewings
- 📊 Seat availability automatically tracked
- 🧠 Logical session handling and user flow

---

## 🛠️ Tech Stack

- **Python 3**
- **Flask** (routing, views)
- **Flask-WTF** (form handling)
- **Flask-SQLAlchemy** (ORM)
- **SQLite** (database)
- **HTML/CSS** (templates and layout)

---

## 📦 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cinema-booking-app.git
   cd cinema-booking-app

2. **Create and activate a virtual environment**
   python -m venv venv
   .\venv\Scripts\Activate.ps1

3. **Install dependencies**
   pip install -r requirements.txt

4. **Run the app**
   $env:FLASK_APP = "app.py"
   flask run

5. **Open your browser and visit**
   http://localhost:5000

---

<pre> ## 📁 Project Structure ``` cinema-booking-app/ ├── app.py ├── templates/ │ ├── index.html │ ├── login.html │ ├── register.html │ └── ... ├── static/ │ └── style.css ├── *.csv ├── requirements.txt └── README.md ``` </pre>

---

## 🧪 Demo Users

If no bookings exist, the app auto-generates initial screenings on first run.
You can also pre-load customers/admins manually using SQLite or code.

---

## 🙋‍♂️ Author

Created by Ioannis Pantelidakis
GitHub: github.com/pantelidakis_i

---

## 📜 License
This project is provided for educational and portfolio use.
Feel free to build on it — attribution appreciated.





