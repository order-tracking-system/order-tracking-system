from sqlalchemy import func, extract
from datetime import datetime
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)

app.secret_key = "erp_secret_key_2026"


# ==============================
# DATABASE
# ==============================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = (
    DATABASE_URL or "sqlite:///" + os.path.join(
        app.root_path,
        "database.db"
    )
)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    DATABASE_URL or "sqlite:///" + os.path.join(
        app.root_path,
        "database.db"
    )
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

<<<<<<< HEAD
=======

# ==============================
# CUSTOMER MODEL
# ==============================

>>>>>>> 5d8381a (Update Production Board)
class Customer(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100)
    )

    mobile = db.Column(
        db.String(20),
        unique=True
    )

    password = db.Column(
        db.String(100)
    )


# ==============================
# USER MODEL
# ==============================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        nullable=False
    )


# ==============================
# ORDER MODEL
# ==============================

class Order(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_no = db.Column(
        db.String(50)
    )

    client_name = db.Column(
        db.String(100)
    )

    mobile = db.Column(
        db.String(20)
    )

    product = db.Column(
        db.String(100)
    )

    size = db.Column(
        db.String(100)
    )

    quantity = db.Column(
        db.Integer
    )

    inside_process = db.Column(
        db.String(50)
    )

    inside_gsm = db.Column(
        db.String(50)
    )

    inside_color = db.Column(
        db.String(50)
    )

    outside_process = db.Column(
        db.String(50)
    )

    order_date = db.Column(db.Date)

    outside_gsm = db.Column(
        db.String(50)
    )

    outside_color = db.Column(
        db.String(50)
    )
    # This stores designer username
    staff_name = db.Column(
        db.String(100)
    )

    remarks = db.Column(
        db.Text
    )

    order_date = db.Column(
        db.Date
    )

    delivery_date = db.Column(
        db.String(50)
    )

    transport_name = db.Column(
        db.String(100)
    )

    lr_number = db.Column(
        db.String(100)
    )

    invoice_number = db.Column(
        db.String(100)
    )

    dispatch_date = db.Column(
        db.String(50)
    )

    status = db.Column(
        db.String(50)
    )

    # Financial information
    amount = db.Column(
        db.Float,
        default=0
    )

    # Date when order became Delivered
    completed_date = db.Column(
        db.Date,
        nullable=True
    )


# ==============================
# LOGIN
# ==============================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session['user_id'] = user.id
            session['user'] = user.username
            session['role'] = user.role

            if user.role == 'production':
                return redirect('/production-dashboard')

            return redirect('/dashboard')

        return render_template(
            'login.html',
            error="Invalid Username or Password"
        )

    return render_template('login.html')


# ==============================
# LOGOUT
# ==============================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


# ==============================
# CUSTOMER REGISTER
# ==============================

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

    return render_template(
        'customer_register.html'
    )


# ==============================
# CUSTOMER LOGIN
# ==============================

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

    return render_template(
        'customer_login.html'
    )


# ==============================
# HOME
# ==============================

@app.route('/')
def home():

    if 'user' in session:

        return redirect('/dashboard')

    return redirect('/login')


# ==============================
# ADD ORDER
# ==============================

@app.route('/add', methods=['GET', 'POST'])
def add_order():

    if 'user_id' not in session:

        return redirect('/login')

    # Get all designers
    designers = User.query.filter_by(
        role='designer'
    ).all()

    if request.method == 'POST':

        order_no = (
            "ORD" +
            str(Order.query.count() + 1)
        )

        order = Order(

            order_no=order_no,

            client_name=request.form['client_name'],

            mobile=request.form['mobile'],

            product=request.form['product'],

            size=request.form['size'],

            quantity=int(
                request.form['quantity'] or 0
            ),

            inside_process=request.form[
                'inside_process'
            ],

            inside_gsm=request.form[
                'inside_gsm'
            ],

            inside_color=request.form[
                'inside_color'
            ],

            outside_process=request.form[
                'outside_process'
            ],

            outside_gsm=request.form[
                'outside_gsm'
            ],

            outside_color=request.form[
                'outside_color'
            ],

            # Designer assignment
            staff_name=request.form[
                'staff_name'
            ],

            remarks=request.form[
                'remarks'
            ],

            order_date=datetime.strptime(
                request.form['order_date'],
                "%Y-%m-%d"
            ).date(),

            delivery_date=request.form[
                'delivery_date'
            ],

            status='Design',

            amount=0
        )

        db.session.add(order)

        db.session.commit()

        return redirect('/dashboard')

    return render_template(
        'add_order.html',
        designers=designers
    )


# ==================================================
# DESIGNER - MY TOTAL ORDERS
# ==================================================

@app.route('/my-orders')
def my_orders():

    if 'user_id' not in session:

        return redirect('/login')

    if session.get('role') != 'designer':

        return "Access Denied", 403

    username = session.get('user')

    orders = Order.query.filter_by(
        staff_name=username
    ).order_by(
        Order.id.desc()
    ).all()

    return render_template(
        'my_orders.html',
        orders=orders,
        username=username,
        page_title="My Total Orders"
    )


# ==================================================
# DESIGNER - MY PENDING ORDERS
# ==================================================

@app.route('/my-pending-orders')
def my_pending_orders():

    if 'user_id' not in session:

        return redirect('/login')

    if session.get('role') != 'designer':

        return "Access Denied", 403

    username = session.get('user')

    orders = Order.query.filter(
        Order.staff_name == username,
        Order.status != "Delivered"
    ).order_by(
        Order.id.desc()
    ).all()

    return render_template(
        'my_orders.html',
        orders=orders,
        username=username,
        page_title="My Pending Orders"
    )


# ==================================================
# DESIGNER - MY COMPLETED ORDERS
# ==================================================

@app.route('/my-completed-orders')
def my_completed_orders():

    if 'user_id' not in session:

        return redirect('/login')

    if session.get('role') != 'designer':

        return "Access Denied", 403

    username = session.get('user')

    orders = Order.query.filter(
        Order.staff_name == username,
        Order.status == "Delivered"
    ).order_by(
        Order.id.desc()
    ).all()

    return render_template(
        'my_orders.html',
        orders=orders,
        username=username,
        page_title="My Completed Orders"
    )


# ==============================
# DASHBOARD
# ==============================

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:

        return redirect('/login')

    role = session.get('role')

    username = session.get('user')


    # OWNER
    if role == 'owner':

        orders = Order.query.all()


    # DESIGNER
    # ONLY THEIR ASSIGNED ORDERS
    elif role == 'designer':

        orders = Order.query.filter_by(
            staff_name=username
        ).all()


    # OTHER STAFF
    else:

        orders = []


    # ==============================
    # COUNTS
    # ==============================

    total_orders = len(orders)


    design = sum(
        1
        for order in orders
        if order.status == "Design"
    )


    jobcard = sum(
        1
        for order in orders
        if order.status == "Job Card"
    )


    printing = sum(
        1
        for order in orders
        if order.status == "Printing"
    )


    packing = sum(
        1
        for order in orders
        if order.status == "Packing"
    )


    dispatched = sum(
        1
        for order in orders
        if order.status == "Dispatched"
    )


    completed = sum(
        1
        for order in orders
        if order.status == "Delivered"
    )


    pending = total_orders - completed


    # ==============================
    # FINANCIAL INFORMATION
    # ONLY OWNER
    # ==============================

    if role == 'owner':

        total_revenue = sum(
            float(order.amount or 0)
            for order in orders
        )

    else:

        total_revenue = 0


    return render_template(

        'dashboard.html',

        orders=orders,

        total_orders=total_orders,

        design=design,

        jobcard=jobcard,

        printing=printing,

        packing=packing,

        dispatched=dispatched,

        completed=completed,

        pending=pending,

        total_revenue=total_revenue,

        role=role,

        username=username
    )


# ==============================
# EDIT ORDER
# ==============================

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_order(id):

    if 'user' not in session:

        return redirect('/login')

    order = Order.query.get_or_404(id)


    if request.method == 'POST':

        order.client_name = request.form[
            'client_name'
        ]

        order.mobile = request.form[
            'mobile'
        ]

        order.product = request.form[
            'product'
        ]

        order.size = request.form[
            'size'
        ]

        order.quantity = request.form[
            'quantity'
        ]


        order.inside_process = request.form[
            'inside_process'
        ]

        order.inside_gsm = request.form[
            'inside_gsm'
        ]

        order.inside_color = request.form[
            'inside_color'
        ]


        order.outside_process = request.form[
            'outside_process'
        ]

        order.outside_gsm = request.form[
            'outside_gsm'
        ]

        order.outside_color = request.form[
            'outside_color'
        ]


        order.staff_name = request.form[
            'staff_name'
        ]

        order.remarks = request.form[
            'remarks'
        ]


        order.order_date = datetime.strptime(
            request.form['order_date'],
            "%Y-%m-%d"
        ).date()


        db.session.commit()

        return redirect(
            '/order/' + str(id)
        )


    return render_template(
        'edit_order.html',
        order=order
    )


# ==============================
# DELETE ORDER
# ==============================

@app.route('/delete/<int:id>')
def delete_order(id):

    if 'user' not in session:

        return redirect('/login')

    order = Order.query.get_or_404(id)

    db.session.delete(order)

    db.session.commit()

    return redirect('/dashboard')


# ==============================
# UPDATE ORDER STATUS
# ==============================

@app.route('/update/<int:id>/<status>')
def update_status(id, status):

    if 'user_id' not in session:

        return redirect('/login')

    order = Order.query.get_or_404(id)

    role = session.get('role')

    username = session.get('user')


    # ==============================
    # DESIGNER SECURITY
    # ==============================

    if role == 'designer':

        # Only own order
        if order.staff_name != username:

            return "Access Denied", 403


        # Designer can only move
        # Design -> Job Card
        if status != "Job Card":

            return "Access Denied", 403


    # ==============================
    # UPDATE STATUS
    # ==============================

    order.status = status


    # ==============================
    # COMPLETION DATE
    # ==============================

    if status == "Delivered":

        order.completed_date = (
            datetime.now().date()
        )


    db.session.commit()

    return redirect(
        f'/order/{id}'
    )


# ==============================
# SEARCH
# ==============================

@app.route('/search')
def search():

    if 'user_id' not in session:

        return redirect('/login')

    q = request.args.get(
        'q',
        ''
    )


    role = session.get('role')

    username = session.get('user')


    # OWNER SEARCH
    if role == 'owner':

        orders = Order.query.filter(
            (Order.order_no.contains(q)) |
            (Order.client_name.contains(q))
        ).all()


    # DESIGNER SEARCH
    elif role == 'designer':

        orders = Order.query.filter(
            Order.staff_name == username,
            (
                Order.order_no.contains(q) |
                Order.client_name.contains(q)
            )
        ).all()


    else:

        orders = []


    design = sum(
        1
        for o in orders
        if o.status == "Design"
    )


    jobcard = sum(
        1
        for o in orders
        if o.status == "Job Card"
    )


    printing = sum(
        1
        for o in orders
        if o.status == "Printing"
    )


    packing = sum(
        1
        for o in orders
        if o.status == "Packing"
    )


    dispatched = sum(
        1
        for o in orders
        if o.status == "Dispatched"
    )


    completed = sum(
        1
        for o in orders
        if o.status == "Delivered"
    )


    pending = len(orders) - completed


    return render_template(

        'dashboard.html',

        orders=orders,

        total_orders=len(orders),

        design=design,

        jobcard=jobcard,

        printing=printing,

        packing=packing,

        dispatched=dispatched,

        completed=completed,

        pending=pending,

        total_revenue=0,

        role=role,

        username=username
    )


# ==============================
# DISPATCH
# ==============================

@app.route('/dispatch/<int:id>', methods=['GET', 'POST'])
def dispatch(id):

    if 'user_id' not in session:

        return redirect('/login')

    order = Order.query.get_or_404(id)


    if request.method == 'POST':

        order.transport_name = request.form[
            'transport_name'
        ]

        order.lr_number = request.form[
            'lr_number'
        ]

        order.invoice_number = request.form[
            'invoice_number'
        ]

        order.dispatch_date = request.form[
            'dispatch_date'
        ]

        order.status = "Dispatched"


        db.session.commit()

        return redirect(
            '/order/' + str(id)
        )


    return render_template(
        'dispatch.html',
        order=order
    )
# ==============================
# PRODUCTION DASHBOARD
# ==============================

@app.route('/production-dashboard')
def production_dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') not in ['production', 'owner']:
        return "Access Denied", 403

    jobcard_orders = Order.query.filter_by(
        status="Job Card"
    ).order_by(
        Order.id.desc()
    ).all()

    printing_orders = Order.query.filter_by(
        status="Printing"
    ).order_by(
        Order.id.desc()
    ).all()

    packing_orders = Order.query.filter_by(
        status="Packing"
    ).order_by(
        Order.id.desc()
    ).all()

    ready_dispatch_orders = Order.query.filter_by(
        status="Ready Dispatch"
    ).order_by(
        Order.id.desc()
    ).all()

    return render_template(
        'production_dashboard.html',
        jobcard_orders=jobcard_orders,
        printing_orders=printing_orders,
        packing_orders=packing_orders,
        ready_dispatch_orders=ready_dispatch_orders,
        username=session.get('user'),
        role=session.get('role')
    )

# ==============================
# PRODUCTION BOARD
# ==============================

# ==============================
# PRODUCTION BOARD
# ==============================

@app.route('/production-board')
def production_board():

    if 'user_id' not in session:
        return redirect('/login')

    design_orders = Order.query.filter_by(
        status="Design"
    ).order_by(
        Order.id.desc()
    ).all()

    jobcard_orders = Order.query.filter_by(
        status="Job Card"
    ).order_by(
        Order.id.desc()
    ).all()

    printing_orders = Order.query.filter_by(
        status="Printing"
    ).order_by(
        Order.id.desc()
    ).all()

    packing_orders = Order.query.filter_by(
        status="Packing"
    ).order_by(
        Order.id.desc()
    ).all()

    dispatch_orders = Order.query.filter(
        Order.status.in_(["Ready Dispatch", "Dispatched"])
    ).order_by(
        Order.id.desc()
    ).all()

    return render_template(
        'production_board.html',

        design_orders=design_orders,
        jobcard_orders=jobcard_orders,
        printing_orders=printing_orders,
        packing_orders=packing_orders,
        dispatch_orders=dispatch_orders,

        username=session.get('user'),
        role=session.get('role')
    )

# ==============================
# REPORTS
# ==============================

@app.route('/reports')
def reports():

    if 'user' not in session:

        return redirect('/login')


    month = request.args.get(
        "month",
        datetime.now().month,
        type=int
    )


    year = request.args.get(
        "year",
        datetime.now().year,
        type=int
    )


    total_orders = Order.query.count()


    delivered = Order.query.filter_by(
        status="Delivered"
    ).count()


    dispatched = Order.query.filter_by(
        status="Dispatched"
    ).count()


    pending = total_orders - delivered


    staff_report = db.session.query(

        Order.staff_name,

        func.count(Order.id)

    ).filter(

        extract(
            'month',
            Order.order_date
        ) == month,

        extract(
            'year',
            Order.order_date
        ) == year

    ).group_by(

        Order.staff_name

    ).order_by(

        func.count(
            Order.id
        ).desc()

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


# ==============================
# PUBLIC ORDER TRACKING
# ==============================

@app.route('/track/<order_no>')
def track(order_no):

    order = Order.query.filter_by(
        order_no=order_no
    ).first_or_404()


    return render_template(
        'track.html',
        order=order
    )


# ==============================
# ORDER DETAIL
# ==============================

@app.route('/order/<int:id>')
def order_detail(id):

    if 'user_id' not in session:

        return redirect('/login')


    order = Order.query.get_or_404(id)

    role = session.get('role')

    username = session.get('user')


    # ==============================
    # DESIGNER SECURITY
    # ==============================

    if role == 'designer':

        if order.staff_name != username:

            return "Access Denied", 403


    return render_template(

        'order_detail.html',

        order=order,

        role=role,

        username=username
    )


# ==============================
# CREATE DATABASE + USERS
# ==============================

with app.app_context():

    db.create_all()


    # ==============================
    # OWNER
    # ==============================

    owner = User.query.filter_by(
        username="pingax"
    ).first()


    if not owner:

        owner = User(

            name="Owner",

            username="pingax",

            password="pingax@123",

            role="owner"
        )

        db.session.add(owner)

        db.session.commit()


    # ==============================
    # DESIGNER 1
    # ==============================

    designer1 = User.query.filter_by(
        username="designer1"
    ).first()


    if not designer1:

        designer1 = User(

            name="Designer One",

            username="designer1",

            password="designer@123",

            role="designer"
        )

        db.session.add(designer1)

        db.session.commit()


    # ==============================
    # DESIGNER 2
    # ==============================

    designer2 = User.query.filter_by(
        username="designer2"
    ).first()


    if not designer2:

        designer2 = User(

            name="Designer Two",

            username="designer2",

            password="designer2@123",

            role="designer"
        )

        db.session.add(designer2)

        db.session.commit()


    # ==============================
    # DESIGNER 3
    # ==============================

    designer3 = User.query.filter_by(
        username="designer3"
    ).first()


    if not designer3:

        designer3 = User(

            name="Designer Three",

            username="designer3",

            password="designer3@123",

            role="designer"
        )

        db.session.add(designer3)

        db.session.commit()

# ==============================
# PRODUCTION STAFF
# ==============================

    production1 = User.query.filter_by(
        username="production1"
    ).first()

    if not production1:

        production1 = User(
            name="Production Staff",
            username="production1",
            password="production@123",
            role="production"
        )

        db.session.add(production1)
        db.session.commit()
# ==============================
# RUN APP
# ==============================

if __name__ == '__main__':

    app.run(

        host='0.0.0.0',

        port=5000,

        debug=True
    )