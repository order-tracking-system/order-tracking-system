from sqlalchemy import func, extract
from datetime import datetime
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "erp_secret_key_2026"


import os

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = (
    DATABASE_URL or "sqlite:///database.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Customer(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    mobile = db.Column(db.String(20), unique=True)

    password = db.Column(db.String(100))


class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    order_no = db.Column(db.String(50))

    client_name = db.Column(db.String(100))

    mobile = db.Column(db.String(20))

    product = db.Column(db.String(100))

    size = db.Column(db.String(100))

    quantity = db.Column(db.Integer)

    inside_process = db.Column(db.String(50))
    inside_gsm = db.Column(db.String(50))
    inside_color = db.Column(db.String(50))

    outside_process = db.Column(db.String(50))
    outside_gsm = db.Column(db.String(50))
    outside_color = db.Column(db.String(50))

    staff_name = db.Column(db.String(100))

    remarks = db.Column(db.Text)

    order_date = db.Column(db.String(50))

    order_date = db.Column(db.Date)

    delivery_date = db.Column(db.String(50))

    transport_name = db.Column(db.String(100))

    lr_number = db.Column(db.String(100))

    invoice_number = db.Column(db.String(100))

    dispatch_date = db.Column(db.String(50))

    status = db.Column(db.String(50))

    amount = db.Column(db.Float, default=0)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "pingax" and password == "pingax@123":
            session['user'] = username
            return redirect('/dashboard')

        return render_template(
            'login.html',
            error="Invalid Username or Password"
        )

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/customer-register', methods=['GET', 'POST'])
def customer_register():

    if request.method == 'POST':

        customer = Customer(
            name=request.form['name'],
            mobile=request.form['mobile'],
            password=request.form['password']
        )

        db.session.add(customer)
        db.session.commit()

        return redirect('/customer-login')

    return render_template('customer_register.html')
@app.route('/customer-login', methods=['GET', 'POST'])
def customer_login():

    if request.method == 'POST':

        mobile = request.form['mobile']
        password = request.form['password']

        customer = Customer.query.filter_by(
            mobile=mobile,
            password=password
        ).first()

        if customer:

            session['customer_id'] = customer.id

            return redirect('/customer-dashboard')

    return render_template('customer_login.html')

@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/add', methods=['GET', 'POST'])
def add_order():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        order_no = "ORD" + str(Order.query.count() + 1)
        order = Order(
            order_no=order_no,
            client_name=request.form['client_name'],
            mobile=request.form['mobile'],
            product=request.form['product'],
            size=request.form['size'],
            quantity=int(request.form['quantity'] or 0),
            inside_process=request.form['inside_process'],
            inside_gsm=request.form['inside_gsm'], # Matches HTML name
            inside_color=request.form['inside_color'],
            outside_process=request.form['outside_process'],
            outside_gsm=request.form['outside_gsm'], # Matches HTML name
            outside_color=request.form['outside_color'],
            staff_name=request.form['staff_name'],
            remarks=request.form['remarks'],
            order_date=datetime.strptime(
    request.form['order_date'],
    "%Y-%m-%d"
).date(),
            delivery_date=request.form['delivery_date'],
            status='Design',
            amount=0
        )

        db.session.add(order)
        db.session.commit()
        return redirect('/dashboard')

    return render_template('add_order.html')

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    orders = Order.query.all()

    total_orders = Order.query.count()

    design = Order.query.filter_by(status="Design").count()

    jobcard = Order.query.filter_by(status="Job Card").count()

    printing = Order.query.filter_by(status="Printing").count()

    packing = Order.query.filter_by(status="Packing").count()

    dispatched = Order.query.filter_by(status="Dispatched").count()

    total_revenue = sum(
        float(order.amount or 0)
        for order in orders
    )

    return render_template(
        'dashboard.html',
        orders=orders,
        total_orders=total_orders,
        design=design,
        jobcard=jobcard,
        printing=printing,
        packing=packing,
        dispatched=dispatched,
        total_revenue=total_revenue
    )
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_order(id):

    if 'user' not in session:
        return redirect('/login')

    order = Order.query.get_or_404(id)

    if request.method == 'POST':

        order.client_name = request.form['client_name']
        order.mobile = request.form['mobile']
        order.product = request.form['product']
        order.size = request.form['size']
        order.quantity = request.form['quantity']

        order.inside_process = request.form['inside_process']
        order.inside_gsm = request.form['inside_gsm']
        order.inside_color = request.form['inside_color']

        order.outside_process = request.form['outside_process']
        order.outside_gsm = request.form['outside_gsm']
        order.outside_color = request.form['outside_color']

        order.staff_name = request.form['staff_name']
        order.remarks = request.form['remarks']
        order.order_date = datetime.strptime(
    request.form['order_date'],
    "%Y-%m-%d"
).date()

        db.session.commit()

        return redirect('/order/' + str(id))

    return render_template(
        'edit_order.html',
        order=order
    )

@app.route('/delete/<int:id>')
def delete_order(id):

    if 'user' not in session:
        return redirect('/login')

    order = Order.query.get_or_404(id)

    db.session.delete(order)
    db.session.commit()

    return redirect('/dashboard')

@app.route('/update/<int:id>/<status>')
def update_status(id, status):

    order = Order.query.get_or_404(id)

    order.status = status

    db.session.commit()

    return redirect(f'/order/{id}')
@app.route('/search')
def search():

    q = request.args.get('q', '')

    orders = Order.query.filter(
        (Order.order_no.contains(q)) |
        (Order.client_name.contains(q))
    ).all()

    design = sum(1 for o in orders if o.status == "Design")
    jobcard = sum(1 for o in orders if o.status == "Job Card")
    printing = sum(1 for o in orders if o.status == "Printing")
    packing = sum(1 for o in orders if o.status == "Packing")
    dispatched = sum(1 for o in orders if o.status == "Dispatched")

    return render_template(
        'dashboard.html',
        orders=orders,
        total_orders=len(orders),
        design=design,
        jobcard=jobcard,
        printing=printing,
        packing=packing,
        dispatched=dispatched,
        total_revenue=0
    )
@app.route('/dispatch/<int:id>', methods=['GET', 'POST'])
def dispatch(id):

    order = Order.query.get_or_404(id)

    if request.method == 'POST':

        order.transport_name = request.form['transport_name']

        order.lr_number = request.form['lr_number']

        order.invoice_number = request.form['invoice_number']

        order.dispatch_date = request.form['dispatch_date']

        order.status = "Dispatched"

        db.session.commit()

        return redirect('/order/' + str(id))

    return render_template(
        'dispatch.html',
        order=order
    )

@app.route('/production-board')
def production_board():

    if 'user' not in session:
        return redirect('/login')

    design_orders = Order.query.filter_by(
        status="Design"
    ).all()

    jobcard_orders = Order.query.filter_by(
        status="Job Card"
    ).all()

    printing_orders = Order.query.filter_by(
        status="Printing"
    ).all()

    packing_orders = Order.query.filter_by(
        status="Packing"
    ).all()

    dispatch_orders = Order.query.filter(
        Order.status.in_(
            ["Ready Dispatch", "Dispatched"]
        )
    ).all()

    return render_template(
        'production_board.html',
        design_orders=design_orders,
        jobcard_orders=jobcard_orders,
        printing_orders=printing_orders,
        packing_orders=packing_orders,
        dispatch_orders=dispatch_orders
    )
@app.route('/reports')
def reports():

    if 'user' not in session:
        return redirect('/login')

    month = request.args.get("month", datetime.now().month, type=int)
    year = request.args.get("year", datetime.now().year, type=int)

    total_orders = Order.query.count()

    delivered = Order.query.filter_by(status="Delivered").count()

    dispatched = Order.query.filter_by(status="Dispatched").count()

    pending = total_orders - delivered

    staff_report = db.session.query(
        Order.staff_name,
        func.count(Order.id)
    ).filter(
        extract('month', Order.order_date) == month,
        extract('year', Order.order_date) == year
    ).group_by(
        Order.staff_name
    ).order_by(
        func.count(Order.id).desc()
    ).all()

    return render_template(
        "reports.html",
        total_orders=total_orders,
        delivered=delivered,
        dispatched=dispatched,
        pending=pending,
        staff_report=staff_report,
        month=month,
        year=year
    )
@app.route('/track/<order_no>')
def track(order_no):

    order = Order.query.filter_by(
        order_no=order_no
    ).first_or_404()

    return render_template(
        'track.html',
        order=order
    )
@app.route('/order/<int:id>')
def order_detail(id):

    if 'user' not in session:
        return redirect('/login')

    order = Order.query.get_or_404(id)

    return render_template(
        'order_detail.html',
        order=order
    )

with app.app_context():
    db.create_all() 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)