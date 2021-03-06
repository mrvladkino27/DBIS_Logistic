from flask import Flask, request, flash, url_for, redirect, render_template, send_from_directory
from hashlib import sha256
from config import config
from flask_sqlalchemy import SQLAlchemy
import math
import os
from werkzeug.utils import secure_filename

USE_HEROKU = False

app = Flask(__name__)

if USE_HEROKU:
    uri = os.environ['DATABASE_URL']
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres_db/Logistic'



app.config['SECRET_KEY'] = "string"
app.config['SQLALCHEMY_ECHO'] = True
app.config['UPLOAD_FOLDER'] = 'Download'

db = SQLAlchemy(app)

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
    size = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Numeric(5,2), nullable = False)
    status = db.Column(db.Boolean, nullable = False)

    def __init__(self, id, sender, reciever, send_dep, recieve_dep, size, price, status):
        self.id = id
        self.sender = sender
        self.reciever = reciever
        self.send_dep = send_dep
        self.recieve_dep = recieve_dep
        self.size = size
        self.price = price
        self.status = status

session_user = User('','','','','')
size_text = {2: 'S', 4: 'M', 8:'L', 16:'XL'}
status_text = {False: '?? ??????????????', True: '????????????????????'}

def update_orders_status(from_dep, to_dep):
    orders_dict = []
    orders = Order.query.filter_by(send_dep = from_dep, recieve_dep = to_dep, status=False)
    orders_amount = orders.count()
    i = 0
    for order in orders:
        orders_dict.append(tuple([order.id, tuple([order.size, orders_amount - i])]))
        i += 1

    orders_dict = dict(orders_dict)
    
    volume = []
    value = []
    for item in orders_dict:
        volume.append(orders_dict[item][0])
        value.append(orders_dict[item][1])

    Truck_volume = 32
    V = [[0 for a in range(Truck_volume + 1)] for i in range(orders_amount + 1)]

    for i in range(orders_amount + 1):
        for a in range(Truck_volume + 1):
            if i == 0 or a == 0:
                V[i][a] = 0
            elif volume[i-1] <= a:
                V[i][a] = max(value[i-1] + V[i-1][a-volume[i-1]], V[i-1][a])
            else:
                V[i][a] = V[i-1][a] 

    res = V[orders_amount][Truck_volume]
    a = Truck_volume
    totalvolume = 0
    orders_list = []
    
    for i in range(orders_amount, 0, -1):
        if res <= 0 or totalvolume >= Truck_volume:
            break
        if res == V[i-1][a]:
            continue
        else:
            orders_list.append((volume[i-1], value[i-1]))
            totalvolume += volume[i-1]
            res -= value[i-1]
            a -= volume[i-1]

    if totalvolume == Truck_volume:
        for search in orders_list:
            for key, value in orders_dict.items():
                if value == search:
                    print(key)
                    Order.query.filter_by(id = key).update({'status': True})
        db.session.commit()

def check_new_dep_distance_failed(departments):
    for dep in departments:
        if departments[dep] == '':
            return True
    return False

@app.route('/')
def index():
    if session_user.role != '':
        return redirect(url_for('show_main_page'))
    else:
        return redirect(url_for('show_login'))

@app.route('/user/exit')
def show_exit():
    global session_user
    session_user = User('','','','','')
    return redirect(url_for('show_login'))

@app.route('/user/registrate_user')
def show_reg():
    return render_template('reg.html', TEST_DEPARTMENT_LIST = Department.query)

@app.route('/user/change_department')
def show_change_department():
    return render_template('change_department.html', SESSION_USER = session_user, DEPARTMENT_LIST = Department.query)

@app.route('/main')
def show_main_page():
    return render_template('index.html', SESSION_USER = session_user, DEPARTMENT_LIST = Department.query)

@app.route('/user/update')
def show_update():
    return render_template('update.html', SESSION_USER = session_user, DEPARTMENT_LIST = Department.query)

@app.route('/user/registrate_worker')
def show_reg_del():
    return render_template('reg_del.html', TEST_DEPARTMENT_LIST = Department.query, SESSION_USER = session_user)

@app.route('/user/login')
def show_login():
    return render_template('login.html')

@app.route('/user/cabinet')
def show_cabinet():
    if session_user.role == 'USER':
        return render_template('cabinet.html', SESSION_USER = session_user, SEND_ORDER_LIST = Order.query.filter_by(sender = session_user.email).order_by(Order.id), RECIEVE_ORDER_LIST = Order.query.filter_by(reciever = session_user.email).order_by(Order.id), ORDER_STATUS = status_text)
    elif session_user.role == 'WORKER':
        return render_template('cabinet.html', SESSION_USER = session_user, SEND_ORDER_LIST = Order.query.filter_by(send_dep=session_user.department).order_by(Order.id.desc()), RECIEVE_ORDER_LIST = Order.query.filter_by(recieve_dep = session_user.department).order_by(Order.id.desc()), ORDER_STATUS = status_text)
    else:
        redirect(url_for('show_login'))

@app.route('/user/create_order')
def show_create_ord():
    return render_template('create_ord.html', TEST_DEPARTMENT_LIST = Department.query, SESSION_USER = session_user)

@app.route('/departments')
def show_departments():
    return render_template('NADO DODELATY!', DEPARTMENT_LIST = Department.query)

@app.route('/user/registrate_user', methods=['POST'])
def registrate_user():
    if request.method == 'POST':
        if request.form['password'] == request.form['confirm_password']:
            if not request.form['email'] or not request.form['password'] or not request.form['department']:
                flash('???????? ??????????, ?????????????????? ?????? ?????????????????? ????????.', 'Error')
            elif User.query.filter_by(email=request.form['email']).first() is not None:
                flash('?????????????????????? ?? ?????????? e-mail ?????? ?????????????????????????? ?? ??????????????.', 'Error')
            else:
                try:
                    email = request.form['email']
                    password = sha256(request.form['password'].encode()).hexdigest()
                    if request.form['name']:
                        name = request.form['name']
                    else:
                        name = None
                    department = request.form['department']
                    role = "USER"
                    user = User(email, password, name, department, role)
                    db.session.add(user)
                    db.session.commit()
                    flash("???????????????????? ?????????????? ??????????????.")
                    return redirect(url_for('index'))
                except:
                    flash('?????????????? ?????????? ???????????????? ?? ?????????????????????? ??????????????????????.', 'Error')
            db.session.commit()
            return redirect(url_for("show_reg"))
        else:
            flash("???????????? ???? ???????????????????????? ???????? ????????????", "Error")
    return redirect(url_for("show_reg"))

@app.route('/user/registrate_worker', methods=['POST'])
def registrate_worker():
    if request.method == 'POST':
        if not request.form['email'] or not request.form['password'] or not request.form['department']:
            flash('???????? ??????????, ?????????????????? ?????? ?????????????????? ????????.', 'Error')
        elif User.query.filter_by(email=request.form['email']).first() is not None:
            flash('User with this e-mail already exists', 'Error')
        else:
            try:
                email = request.form['email']
                password = sha256(request.form['password'].encode()).hexdigest()
                if request.form['name']:
                    name = request.form['name']
                else:
                    name = None
                department = request.form['department']
                role = "WORKER"
                worker = User(email, password, name, department, role)
                db.session.add(worker)
            except Exception as err:
                flash(str(err), 'Error')
                return redirect(url_for("registrate_user"))
        db.session.commit()
        return redirect(url_for("index"))
    return redirect(url_for("registrate_user"))


@app.route('/user/update', methods=['POST', 'GET'])
def update_user():
    if request.method == 'POST':
        if not request.form['old_password']:
            flash('???????? ??????????, ?????????????????? ?????? ?????????????????? ????????.', 'Error')
        if sha256(request.form['old_password'].encode()).hexdigest() == session_user.password:
            try:
                email = session_user.email
                if request.form['password']:
                    if request.form['password'] == request.form['confirm_password']:
                        password = sha256(request.form['password'].encode()).hexdigest()
                    else:
                        flash('???????????? ???? ????????????????????')
                        return redirect(url_for('show_update'))
                else:
                    password = session_user.password
                if request.form['name']:
                    name = request.form['name']
                else:
                    name = None
                # user = User(email, password, name, department, session_user.role)
                User.query.filter_by(email = session_user.email).update({'password': password, 'name': name})
                # db.session.delete(session_user)
                # db.session.add(user)
            except Exception as err:
                flash(str(err), 'Error')
                return redirect(url_for('show_cabinet'))
        else:
            flash('You need to log in to edit user info', 'Error')
        db.session.commit()
        return redirect(url_for("show_login"))
    return redirect(url_for("show_main_page"))

@app.route('/user/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' or request.method == 'POST':
        if not request.form['email'] or not request.form['password']:
            flash('???????? ??????????, ?????????????????? ?????? ?????????????????? ????????.', 'Error')
            return render_template('login.html')
        else:
            try:
                email = request.form['email']
                password = sha256(request.form['password'].encode()).hexdigest()
                user = User.query.filter_by(email = email).first()
                if user:
                    if user.password == password:
                        global session_user
                        session_user = user
                        return redirect(url_for('index'))
                    else:
                        flash('Wrong password.', 'Error')
                        return render_template('login.html')
                else:
                    flash('There is no user with such email.', 'Error')
                    return render_template('login.html')
            except Exception as err:
                flash(str(err), 'Error')
                return render_template('login.html')
    return render_template('login.html')


def get_distance(send_dep, recieve_dep):
    distance = Distance.query.filter_by(first_dep = send_dep, second_dep = recieve_dep).first()
    if not distance:
        distance = Distance.query.filter_by(first_dep = recieve_dep, second_dep=send_dep).first()
    return distance


@app.route('/user/create_order', methods=['GET', 'POST'])
def create_order():
    if request.method == 'GET' or request.method == 'POST':
        if not request.form['reciever'] or not request.form['recieve_dep'] or not request.form['size']:
            flash('???????? ??????????, ?????????????????? ?????? ?????????????????? ????????.', 'Error')
            return render_template('create_ord.html', TEST_DEPARTMENT_LIST = Department.query, SESSION_USER = session_user)
        else:
            try:
                last = Order.query.order_by(Order.id.desc()).first()
                if last:
                    id = last.id + 1
                else:
                    id = 1
                sender = session_user.email
                reciever = request.form['reciever']
                db_reciever = User.query.filter_by(email=reciever).first()
                if db_reciever.email == '':
                    flash('?????????????????? ???????????????????? ???? ?????????????? ????????????.', "Error")
                    return render_template('create_ord.html', TEST_DEPARTMENT_LIST = Department.query,SESSION_USER = session_user)
                send_dep = session_user.department
                recieve_dep = request.form['recieve_dep']
                size = int(request.form['size'])
                distance = get_distance(send_dep, recieve_dep)
                if distance.distance:
                    price  = 30 + ( 0.35 * distance.distance * math.log2(size) )
                else:
                    flash("???????????????? ?????? ???????????????? ???????????????????????? ???? ????????????????.", "Error")
                    return render_template('create_ord.html', TEST_DEPARTMENT_LIST = Department.query, SESSION_USER = session_user)
                order = Order(id, sender, reciever, send_dep, recieve_dep, size, price, False)
                db.session.add(order)
                db.session.commit()
                update_orders_status(send_dep, recieve_dep)
                flash("???????????????????????? ???????????????? ?? ??????????????.\n???????????????? ???????????????????? ???? ???????????????????? ?????????? ???????????????? ?? \"???????? ??????????????????????\"")
                return render_template('create_ord.html', TEST_DEPARTMENT_LIST = Department.query, SESSION_USER = session_user)
            except Exception as err:
                flash(str(err), 'Error')
                return render_template('create_ord.html', TEST_DEPARTMENT_LIST = Department.query, SESSION_USER = session_user)
    return render_template('create_ord.html', TEST_DEPARTMENT_LIST = Department.query, SESSION_USER = session_user)

@app.route('/user/cabinet', methods=['GET', 'POST'])
def download_invoice():
    if request.method == 'GET' or request.method == 'POST':
        id = int(request.form['order_id'])
        if not id:
            flash('???????? ??????????, ?????????????? ???????????????????? ?????? ?????????? ???????????????????????? ????????????????.', 'Error')
            return redirect(url_for('show_cabinet'))
        else:
            try:
                order = Order.query.filter_by(id = id).first()
                distance = get_distance(order.send_dep, order.recieve_dep)
                if not distance.distance:
                    flash("?? ???????? ?????????? ?????????????????????? ?????? ???????????????? ?????? ???????????????? ????????????????????????.", "Error")
                    return redirect(url_for('show_cabinet'))
                file_name = secure_filename(f"Invoice_{id}.txt")

                for file in os.listdir(app.config['UPLOAD_FOLDER']):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))

                with open(os.path.join(app.config['UPLOAD_FOLDER'], file_name), encoding='utf-8', mode='w') as download_file:
                    download_file.write(f"\n{'='*60}\n{' '*20}???????????????????? ????????????????{' '*10}\n")
                    download_file.write(f"{'='*16} ???????????????? ???????????????????????? ???{id} {'='*16}\n\n")
                    download_file.write(f"??????: '{order.sender}'\t     ->  \t????????: '{order.reciever}'\n")
                    download_file.write(f"?????????? ????????????????????????: {order.send_dep}    ->  \t?????????? ??????????????????:{order.recieve_dep}\n\n")
                    download_file.write(f"???????????????? ?????? ???????????????? ????????????????????????: {distance.distance}\n")
                    download_file.write(f"???????????? ????????????????????????: {size_text[order.size]}\n")
                    download_file.write(f"???????????? ????????????????????????: {status_text[order.status]}\n")
                    download_file.write(f"{'_'*60}\n???????????????? ??????????????: {order.price}\n")

                return send_from_directory(directory = app.config['UPLOAD_FOLDER'], path = file_name, as_attachment = True)
            except Exception as err:
                flash(str(err), 'Error')
                return redirect(url_for('show_cabinet'))
    return redirect(url_for("show_cabinet"))

@app.route('/user/change_department', methods=['POST'])
def add_department_distance():
    if (request.method == 'POST'):
        if check_new_dep_distance_failed(request.form):
            flash('???????? ??????????, ?????????????????? ?????? ?????????????????? ????????.', 'Error')       
        else:
            department_dict = dict(request.form)
            first_dep = ''
            del department_dict['Submit']

            for department in department_dict:
                try:
                    if department == 'first_adress':
                        first_dep = department_dict[department]
                        new_dep = Department(first_dep)
                        db.session.add(new_dep)
                        second_dep = department_dict[department]
                        distance_1_2 = 0
                    else:
                        second_dep = department
                        distance_1_2 = int(department_dict[department])
                    distance = Distance(first_dep, second_dep, distance_1_2)
                    db.session.add(distance)
                    db.session.commit()
                except Exception as err:
                    flash(str(err), 'Error')
            flash("???????? ???????????????????? ?????????????? ????????????????.???????????? ?????????????????? ?????????? ???????????????? ?? \"?????????? ??????????????????????\"")
        return redirect(url_for('index'))
    return redirect(url_for('show_change_department'))

if __name__ == "__main__":
    # db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port, host="0.0.0.0")