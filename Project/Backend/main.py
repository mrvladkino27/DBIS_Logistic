from flask import Flask, request, flash, url_for, redirect, render_template
from hashlib import sha256
from flask_sqlalchemy import SQLAlchemy
import math


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234567890@localhost/Logistic'

# uri = os.environ['DATABASE_URL']
# if uri.startswith("postgres://"):
#     uri = uri.replace("postgres://", "postgresql://", 1)

# app.config['SQLALCHEMY_DATABASE_URI'] = uri

app.config['SECRET_KEY'] = "string"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

SESSION_USER = None

class Department(db.Model):
    __tablename__ = "department"
    adress = db.Column(db.String(256), primary_key = True)

    def __init__(self, adress):
        self.adress = adress

class User(db.Model):
    __tablename__ = "user"
    email = db.Column(db.String(64), primary_key = True)
    password = db.Column(db.String(64), nullable = False)
    name = db.Column(db.String(64))
    department = db.Column(db.String(256), db.ForeignKey("department.adress"), nullable = False)
    role = db.Column(db.String(32), nullable = False)

    def __init__(self, email, password, name, department, role):
        self.email = email
        self.password = password
        self.name = name
        self.department = department
        self.role = role

class Distance(db.Model):
    __tablename__ = "distance"
    first_dep = db.Column(db.String(256), primary_key = True)
    second_dep = db.Column(db.String(256), primary_key = True)
    distance = db.Column(db.Integer, nullable = False)

    def __init__(self, first_dep, second_dep, distance):
        self.first_dep = first_dep
        self.second_dep = second_dep
        self.distance = distance

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.BigInteger, primary_key = True)
    sender = db.Column(db.String(64),  db.ForeignKey("user.email"), nullable = False)
    reciever = db.Column(db.String(64),  db.ForeignKey("user.email"), nullable = False)
    send_dep = db.Column(db.String(256),  db.ForeignKey("department.adress"), nullable = False)
    recieve_dep = db.Column(db.String(256),  db.ForeignKey("department.adress"), nullable = False)
    size = db.Column(db.String(4), nullable = False)
    price = db.Column(db.Numeric, nullable = False)
    status = db.Column(db.Boolean, nullable = False)

    def __init__(self, id, sender, reciever, send_dep, recieve_dep, size, status):
        self.id = id
        self.sender = sender
        self.reciever = reciever
        self.send_dep = send_dep
        self.recieve_dep = recieve_dep
        self.size = size
        self.status = status

def update_orders_status(from_dep, to_dep):
    orders = Order.query.filter_by(send_dep = from_dep, recieve_dep = to_dep).all()
    counter = 0
    for row in orders:
        if counter == 32:
            row


@app.route('/')
def index():
	return render_template('main_page.html')


@app.route('/user/registrate_user', methods=['POST'])
def registrate_user():
    if request.method == 'POST':
        if not request.form['email'] or not request.form['password'] or not request.form['department']:
            flash('Please, enter all the required fields', 'Error')
        elif User.query.filter_by(email=request.form['email']).first() is not None:
            flash('User with this e-mail already exists', 'Error')
        else:
            try:
                email = request.form['email']
                password = sha256(request.form['password'].encode())
                if request.form['name']:
                    name = request.form['name']
                else:
                    name = None
                department = request.form['department']
                role = "User"
                user = User(email, password, name, department, role)
                db.session.add(user)
            except:
                flash('Something went wrong with registration.', 'Error')
        db.session.commit()
        return redirect(url_for("index"))
    return redirect(url_for("registrate_user"))

@app.route('/user/registrate_worker', methods=['POST'])
def registrate_worker():
    if request.method == 'POST':
        if not request.form['email'] or not request.form['password'] or not request.form['department']:
            flash('Please, enter all the required fields', 'Error')
        elif User.query.filter_by(email=request.form['email']).first() is not None:
            flash('User with this e-mail already exists', 'Error')
        else:
            try:
                email = request.form['email']
                password = sha256(request.form['password'].encode())
                if request.form['name']:
                    name = request.form['name']
                department = request.form['department']
                role = "Worker"
                worker = User(email, password, name, department, role)
                db.session.add(worker)
            except:
                flash('Something went wrong with registration.', 'Error')
        db.session.commit()
        return redirect(url_for("index"))
    return redirect(url_for("registrate_user"))

@app.route('/user/login', methods=['GET'])
def login():
    if request.method == 'GET':
        if not request.form['email'] or not request.form['password']:
            flash('Please, enter all the required fields', 'Error')
        else:
            try:
                email = request.form['email']
                password = sha256(request.form['password'].encode())
                user = User.query.filter_by(email = email)
                if user:
                    if user.password == password:
                        SESSION_USER = user
                        return redirect(url_for("index"))
                    else:
                        flash('Wrong password.', 'Error')
                else:
                    flash('There is no user with such email.', 'Error')
            except:
                flash('Something went wrong with authentification.', 'Error')
        return redirect(url_for("index"))
    return redirect(url_for("login"))	

@app.route('/user/create_order', methods=['POST'])
def create_order():
    if request.method == 'POST':
        if not request.form['sender'] or not request.form['reciever'] or not request.form['send_dep'] or not request.form['recieve_dep'] or not request.form['size']:
            flash('Please, enter all the required fields', 'Error')
        else:
            try:
                sender = request.form['sender']
                reciever = request.form['reciever']
                send_dep = request.form['send_dep']
                recieve_dep = request.form['recieve_dep']
                size = request.form['size']
                price = Distance.query.filter_by(first_dep = send_dep, second_dep=recieve_dep).distance * 10 * math.log2(size)
                order = Order(sender, reciever, send_dep, recieve_dep, size, False)
                db.session.add(order)
            except:
                flash('Something went wrong with order creation.', 'Error')
        db.session.commit()
        return redirect(url_for("index"))
    return redirect(url_for("order_create"))

if __name__ == "__main__":
    db.create_all()