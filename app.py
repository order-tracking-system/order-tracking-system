from datetime import datetime, date
from io import BytesIO
import os

from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
import openpyxl


app = Flask(__name__)

app.secret_key = "erp_secret_key_2026"


# ==================================================
# DATABASE
# ==================================================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = (
    DATABASE_URL
    or "sqlite:///" + os.path.join(
        app.root_path,
        "database.db"
    )
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==================================================
# CUSTOMER MODEL
# ==================================================

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


# ==================================================
# USER MODEL
# ==================================================

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


# ==================================================
# ORDER MODEL
# ==================================================

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

    # -----------------------------
    # INSIDE PRINTING
    # -----------------------------

    inside_process = db.Column(
        db.String(50)
    )

    inside_gsm = db.Column(
        db.String(50)
    )

    inside_color = db.Column(
        db.String(50)
    )

    # -----------------------------
    # OUTSIDE PRINTING
    # -----------------------------

    outside_process = db.Column(
        db.String(50)
    )

    outside_gsm = db.Column(
        db.String(50)
    )

    outside_color = db.Column(
        db.String(50)
    )

    # -----------------------------
    # DESIGNER
    # -----------------------------

    staff_name = db.Column(
    db.String(100)
    )

    order_by = db.Column(
    db.String(100)
    )

    rate = db.Column(
    db.Float,
    default=0
    )

    remarks = db.Column(
    db.Text
    )

    # -----------------------------
    # DATES
    # -----------------------------

    order_date = db.Column(
        db.Date
    )

    delivery_date = db.Column(
        db.String(50)
    )

    completed_date = db.Column(
        db.Date,
        nullable=True
    )

    dispatch_date = db.Column(
        db.String(50)
    )

    # -----------------------------
    # DISPATCH
    # -----------------------------

    transport_name = db.Column(
        db.String(100)
    )

    lr_number = db.Column(
        db.String(100)
    )

    invoice_number = db.Column(
        db.String(100)
    )

    # -----------------------------
    # STATUS
    # -----------------------------

    status = db.Column(
        db.String(50)
    )

    # -----------------------------
    # FINANCIAL
    # -----------------------------

    amount = db.Column(
        db.Float,
        default=0
    )


# ==================================================
# DATABASE SETUP / SAFE MIGRATION
# ==================================================

with app.app_context():

    try:

        # ------------------------------------------
        # CREATE TABLES IF THEY DO NOT EXIST
        # ------------------------------------------

        db.create_all()

        # ------------------------------------------
        # CHECK ORDER TABLE
        # ------------------------------------------

        inspector = inspect(db.engine)

        tables = inspector.get_table_names()

        print("DATABASE DRIVER:", db.engine.url.drivername)
        print("DATABASE TABLES:", tables)

        if "order" in tables:

            # --------------------------------------
            # GET CURRENT ORDER COLUMNS
            # --------------------------------------

            columns = [
                column["name"]
                for column in inspector.get_columns("order")
            ]

            print("ORDER COLUMNS BEFORE MIGRATION:")
            print(columns)

            # --------------------------------------
            # MIGRATIONS
            # --------------------------------------

            migrations = {
                "completed_date": "DATE",
                "order_by": "VARCHAR(100)",
                "rate": "FLOAT"
            }

            for column_name, column_type in migrations.items():

                if column_name not in columns:

                    print(
                        f"{column_name} column missing."
                    )

                    if db.engine.url.drivername.startswith(
                        "sqlite"
                    ):

                        db.session.execute(
                            text(
                                f'ALTER TABLE "order" '
                                f'ADD COLUMN {column_name} '
                                f'{column_type}'
                            )
                        )

                    else:

                        db.session.execute(
                            text(
                                f'ALTER TABLE "order" '
                                f'ADD COLUMN IF NOT EXISTS '
                                f'{column_name} '
                                f'{column_type}'
                            )
                        )

                    db.session.commit()

                    print(
                        f"{column_name} column added successfully."
                    )

                else:

                    print(
                        f"{column_name} column already exists."
                    )

    except Exception as e:

        db.session.rollback()

        print(
            "DATABASE MIGRATION ERROR:",
            repr(e)
        )
# ==================================================
# LOGIN
# ==================================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get(
            'username',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session['user_id'] = user.id
            session['user'] = user.username
            session['role'] = user.role

            if user.role == 'production':

                return redirect(
                    '/production-dashboard'
                )

            return redirect(
                '/dashboard'
            )

        return render_template(
            'login.html',
            error="Invalid Username or Password"
        )

    return render_template(
        'login.html'
    )


# ==================================================
# LOGOUT
# ==================================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


# ==================================================
# CUSTOMER REGISTER
# ==================================================

@app.route(
    '/customer-register',
    methods=['GET', 'POST']
)
def customer_register():

    if request.method == 'POST':

        customer = Customer(
            name=request.form['name'],
            mobile=request.form['mobile'],
            password=request.form['password']
        )

        db.session.add(customer)
        db.session.commit()

        return redirect(
            '/customer-login'
        )

    return render_template(
        'customer_register.html'
    )


# ==================================================
# CUSTOMER LOGIN
# ==================================================

@app.route(
    '/customer-login',
    methods=['GET', 'POST']
)
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

            return redirect(
                '/customer-dashboard'
            )

    return render_template(
        'customer_login.html'
    )


# ==================================================
# HOME
# ==================================================

@app.route('/')
def home():

    if 'user' in session:

        return redirect(
            '/dashboard'
        )

    return redirect(
        '/login'
    )


# ==================================================
# ADD ORDER
# ==================================================

@app.route(
    '/add',
    methods=['GET', 'POST']
)
def add_order():

    if 'user_id' not in session:

        return redirect('/login')

    designers = User.query.filter_by(
        role='designer'
    ).all()

    if request.method == 'POST':

        last_order = Order.query.order_by(
            Order.id.desc()
        ).first()

        if last_order:

            order_no = "ORD" + str(
                last_order.id + 1
            )

        else:

            order_no = "ORD1"

        order_date_value = request.form.get(
            'order_date'
        )

        if order_date_value:

            order_date_value = datetime.strptime(
                order_date_value,
                "%Y-%m-%d"
            ).date()

        else:

           order_date_value = date.today()

        quantity_value = request.form.get(
            'quantity',
            '0'
        )

        quantity_value = request.form.get(
            'quantity',
            '0'
        )

        try:

            quantity_value = int(
                quantity_value or 0
            )

        except ValueError:

            quantity_value = 0

        order = Order(

            order_no=order_no,

            client_name=request.form.get(
                'client_name'
            ),

            mobile=request.form.get(
                'mobile'
            ),

            product=request.form.get(
                'product'
            ),

            size=request.form.get(
                'size'
            ),

            quantity=quantity_value,

            inside_process=request.form.get(
                'inside_process'
            ),

            inside_gsm=request.form.get(
                'inside_gsm'
            ),

            inside_color=request.form.get(
                'inside_color'
            ),

            outside_process=request.form.get(
                'outside_process'
            ),

            outside_gsm=request.form.get(
                'outside_gsm'
            ),

            outside_color=request.form.get(
                'outside_color'
            ),

            staff_name=request.form.get(
                'staff_name'
            ),

            order_by=request.form.get(
                'order_by'
            ),

            rate=float(
                request.form.get('rate') or 0
            ),

            remarks=request.form.get(
                'remarks'
            ),

            order_date=order_date_value,

            delivery_date=request.form.get(
                'delivery_date'
            ),

            status='Design',

            amount=0
        )
        order = Order(

            order_no=order_no,

            client_name=request.form.get(
                'client_name'
            ),

            mobile=request.form.get(
                'mobile'
            ),

            product=request.form.get(
                'product'
            ),

            size=request.form.get(
                'size'
            ),

            quantity=quantity_value,

            inside_process=request.form.get(
                'inside_process'
            ),

            inside_gsm=request.form.get(
                'inside_gsm'
            ),

            inside_color=request.form.get(
                'inside_color'
            ),

            outside_process=request.form.get(
                'outside_process'
            ),

            outside_gsm=request.form.get(
                'outside_gsm'
            ),

            outside_color=request.form.get(
                'outside_color'
            ),

            staff_name=request.form.get(
            'staff_name'
            ),

            order_by=request.form.get(
            'order_by'
            ),

            rate=float(
            request.form.get('rate') or 0
            ),

            remarks=request.form.get(
            'remarks'
            ),

            order_date=order_date_value,

            delivery_date=request.form.get(
                'delivery_date'
            ),

            status='Design',

            amount=0
        )

        db.session.add(order)
        db.session.commit()

        return redirect(
            '/dashboard'
        )

    return render_template(
        'add_order.html',
        designers=designers
    )


# ==================================================
# DESIGNER - TOTAL ORDERS
# ==================================================

@app.route('/my-orders')
def my_orders():

    if 'user_id' not in session:

        return redirect('/login')

    if session.get('role') != 'designer':

        return "Access Denied", 403

    username = session.get(
        'user'
    )

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
# DESIGNER - PENDING ORDERS
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
        Order.status == "Design"
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
# DESIGNER - COMPLETED ORDERS
# ==================================================

@app.route('/my-job-card-orders')
def my_job_card_orders():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'designer':
        return "Access Denied", 403

    username = session.get('user')

    orders = Order.query.filter(
        Order.staff_name == username,
        Order.status == "Job Card"
    ).order_by(
        Order.id.desc()
    ).all()

    return render_template(
        'my_orders.html',
        orders=orders,
        username=username,
        page_title="My Job Card Orders"
    )
@app.route('/my-completed-orders')
def my_completed_orders():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'designer':
        return "Access Denied", 403

    username = session.get('user')

    # Design complete hone ke baad Job Card
    # se aage ke saare orders Completed me aayenge
    orders = Order.query.filter(
        Order.staff_name == username,
        Order.status.in_([
            "Job Card",
            "Printing",
            "Packing",
            "Ready Dispatch",
            "Dispatched",
            "Delivered"
        ])
    ).order_by(
        Order.id.desc()
    ).all()

    return render_template(
        'my_orders.html',
        orders=orders,
        username=username,
        page_title="My Completed Orders"
    )
# ==================================================
# DASHBOARD
# ==================================================

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    role = session.get('role')
    username = session.get('user')
    

    # Friendly name shown in the dashboard greeting.
    designer_names = {
        'designer1': 'Latif Makwana',
        'designer2': 'Dolly Kesharwani',
        'designer3': 'Anu Gaynar'
    }
    display_name = designer_names.get(username, username)

    # ------------------------------------------
    # PRODUCTION STAFF
    # ------------------------------------------

    if role == 'production':

        return redirect('/production-dashboard')


    # ------------------------------------------
    # OWNER
    # ------------------------------------------

    if role == 'owner':

        orders = Order.query.order_by(
            Order.id.desc()
        ).all()


    # ------------------------------------------
    # DESIGNER
    # ------------------------------------------

    elif role == 'designer':

        orders = Order.query.filter(
            Order.staff_name == username
        ).order_by(
            Order.id.desc()
        ).all()


    else:

        orders = []


    # ------------------------------------------
    # COUNTS
    # ------------------------------------------

    total_orders = len(orders)


    # DESIGN PENDING
    design = sum(
        1
        for order in orders
        if order.status == "Design"
    )


    # JOB CARD
    jobcard = sum(
        1
        for order in orders
        if order.status == "Job Card"
    )


    # PRINTING
    printing = sum(
        1
        for order in orders
        if order.status == "Printing"
    )


    # PACKING
    packing = sum(
        1
        for order in orders
        if order.status == "Packing"
    )


    # READY DISPATCH
    ready_dispatch = sum(
        1
        for order in orders
        if order.status == "Ready Dispatch"
    )


    # DISPATCHED
    dispatched = sum(
        1
        for order in orders
        if order.status == "Dispatched"
    )


    # DELIVERED
    delivered = sum(
        1
        for order in orders
        if order.status == "Delivered"
    )


    # ------------------------------------------
    # DESIGNER PENDING
    # ONLY DESIGN STATUS
    # ------------------------------------------

    pending = design


    # ------------------------------------------
    # COMPLETED ORDERS
    # AFTER JOB CARD
    # ------------------------------------------

    completed = (
        printing
        + packing
        + ready_dispatch
        + dispatched
        + delivered
    )


    # ------------------------------------------
    # REVENUE
    # ------------------------------------------

    if role == 'owner':

        total_revenue = sum(
            float(order.amount or 0)
            for order in orders
        )

    else:

        total_revenue = 0


    # ------------------------------------------
    # DASHBOARD
    # ------------------------------------------

    return render_template(

        'dashboard.html',

        orders=orders,

        total_orders=total_orders,

        design=design,

        jobcard=jobcard,

        printing=printing,

        packing=packing,

        ready_dispatch=ready_dispatch,

        dispatched=dispatched,

        delivered=delivered,

        completed=completed,

        pending=pending,

        total_revenue=total_revenue,

        role=role,

        username=username,

        display_name=display_name,

    )

# ==================================================
# EDIT ORDER
# ==================================================

@app.route(
    '/edit/<int:id>',
    methods=['GET', 'POST']
)
def edit_order(id):

    if 'user_id' not in session:

        return redirect('/login')

    order = Order.query.get_or_404(id)

    if request.method == 'POST':

        order.client_name = request.form.get(
            'client_name'
        )

        order.mobile = request.form.get(
            'mobile'
        )

        order.product = request.form.get(
            'product'
        )

        order.size = request.form.get(
            'size'
        )

        try:

            order.quantity = int(
                request.form.get(
                    'quantity',
                    0
                )
            )

        except ValueError:

            order.quantity = 0

        order.inside_process = request.form.get(
            'inside_process'
        )

        order.inside_gsm = request.form.get(
            'inside_gsm'
        )

        order.inside_color = request.form.get(
            'inside_color'
        )

        order.outside_process = request.form.get(
            'outside_process'
        )

        order.outside_gsm = request.form.get(
            'outside_gsm'
        )

        order.outside_color = request.form.get(
            'outside_color'
        )

        order.staff_name = request.form.get(
        'staff_name'
        )

        order.order_by = request.form.get(
        'order_by'
        )

        try:

            order.rate = float(
                request.form.get('rate') or 0
            )

        except ValueError:

            order.rate = 0

        order.remarks = request.form.get(
        'remarks'
        )

        if request.form.get('order_date'):

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


# ==================================================
# DELETE ORDER
# ==================================================

@app.route('/delete/<int:id>')
def delete_order(id):

    if 'user_id' not in session:

        return redirect('/login')

    order = Order.query.get_or_404(id)

    db.session.delete(order)

    db.session.commit()

    return redirect(
        '/dashboard'
    )


# ==================================================
# UPDATE ORDER STATUS
# ==================================================

@app.route('/update/<int:id>/<path:status>')
def update_status(id, status):

    if 'user_id' not in session:
        return redirect('/login')

    order = Order.query.get_or_404(id)

    role = session.get('role')
    username = session.get('user')

    status = status.strip()

    if role == 'designer':

        if order.staff_name != username:
            return "Access Denied", 403

        if order.status != "Design":
            return "Access Denied", 403

        if status != "Job Card":
            return "Access Denied", 403

    order.status = status

    if status == "Delivered":

        order.completed_date = datetime.now().date()

    db.session.commit()

    print(
        "STATUS UPDATED:",
        order.order_no,
        "=>",
        order.status
    )

    return redirect(
        f'/order/{id}'
    )

# ==================================================
# SEARCH
# ==================================================

@app.route('/search')
def search():

    if 'user_id' not in session:

        return redirect('/login')

    q = request.args.get(
        'q',
        ''
    )

    role = session.get(
        'role'
    )

    username = session.get(
        'user'
    )

    if role == 'owner':

        orders = Order.query.filter(
            (Order.order_no.contains(q)) |
            (Order.client_name.contains(q))
        ).order_by(
            Order.id.desc()
        ).all()

    elif role == 'designer':

        orders = Order.query.filter(
            Order.staff_name == username,
            (
                Order.order_no.contains(q) |
                Order.client_name.contains(q)
            )
        ).order_by(
            Order.id.desc()
        ).all()

    else:

        orders = []

    design = sum(
        1 for o in orders
        if o.status == "Design"
    )

    jobcard = sum(
        1 for o in orders
        if o.status == "Job Card"
    )

    printing = sum(
        1 for o in orders
        if o.status == "Printing"
    )

    packing = sum(
        1 for o in orders
        if o.status == "Packing"
    )

    dispatched = sum(
        1 for o in orders
        if o.status == "Dispatched"
    )

    completed = sum(
        1 for o in orders
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


# ==================================================
# DISPATCH
# ==================================================

@app.route(
    '/dispatch/<int:id>',
    methods=['GET', 'POST']
)
def dispatch(id):

    if 'user_id' not in session:

        return redirect('/login')

    order = Order.query.get_or_404(id)

    if request.method == 'POST':

        order.transport_name = request.form.get(
            'transport_name'
        )

        order.lr_number = request.form.get(
            'lr_number'
        )

        order.invoice_number = request.form.get(
            'invoice_number'
        )

        order.dispatch_date = request.form.get(
            'dispatch_date'
        )

        order.status = "Dispatched"

        db.session.commit()

        return redirect(
            '/order/' + str(id)
        )

    return render_template(
        'dispatch.html',
        order=order
    )


# ==================================================
# PRODUCTION DASHBOARD
# ==================================================

# ==================================================
# PRODUCTION DASHBOARD
# ==================================================

@app.route('/production-dashboard')
def production_dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') not in [
        'production',
        'owner'
    ]:
        return "Access Denied", 403

    # -----------------------------
    # DESIGN ORDERS
    # -----------------------------

    design_orders = Order.query.filter_by(
        status="Design"
    ).order_by(
        Order.id.desc()
    ).all()

    # -----------------------------
    # JOB CARD ORDERS
    # -----------------------------

    jobcard_orders = Order.query.filter_by(
        status="Job Card"
    ).order_by(
        Order.id.desc()
    ).all()

    # -----------------------------
    # PRINTING ORDERS
    # -----------------------------

    printing_orders = Order.query.filter_by(
        status="Printing"
    ).order_by(
        Order.id.desc()
    ).all()

    # -----------------------------
    # PACKING ORDERS
    # -----------------------------

    packing_orders = Order.query.filter_by(
        status="Packing"
    ).order_by(
        Order.id.desc()
    ).all()

    # -----------------------------
    # READY DISPATCH
    # -----------------------------

    ready_dispatch_orders = Order.query.filter_by(
        status="Ready Dispatch"
    ).order_by(
        Order.id.desc()
    ).all()

    # -----------------------------
    # SHOW DASHBOARD
    # -----------------------------

    return render_template(
        'production_dashboard.html',

        design_orders=design_orders,

        jobcard_orders=jobcard_orders,

        printing_orders=printing_orders,

        packing_orders=packing_orders,

        ready_dispatch_orders=ready_dispatch_orders,

        username=session.get('user'),

        role=session.get('role')
    )
# ==================================================
# PRODUCTION BOARD
# ==================================================

@app.route('/production-board')
def production_board():

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') not in ['production', 'owner']:
        return "Access Denied", 403

    # ------------------------------------------
    # GET ALL ORDERS
    # ------------------------------------------

    all_orders = Order.query.order_by(
        Order.id.desc()
    ).all()

    # ------------------------------------------
    # DEBUG - CHECK STATUS
    # ------------------------------------------

    print("========== PRODUCTION BOARD ==========")

    for order in all_orders:
        print(
            order.order_no,
            "|",
            order.client_name,
            "| STATUS =",
            repr(order.status)
        )

    # ------------------------------------------
    # FILTER ORDERS
    # ------------------------------------------

    design_orders = [
        order for order in all_orders
        if (order.status or "").strip().lower() == "design"
    ]

    jobcard_orders = [
        order for order in all_orders
        if (order.status or "").strip().lower() == "job card"
    ]

    printing_orders = [
        order for order in all_orders
        if (order.status or "").strip().lower() == "printing"
    ]

    packing_orders = [
        order for order in all_orders
        if (order.status or "").strip().lower() == "packing"
    ]

    dispatch_orders = [
        order for order in all_orders
        if (order.status or "").strip().lower()
        in ["ready dispatch", "dispatched"]
    ]

    print("DESIGN ORDERS:", len(design_orders))
    print("JOB CARD ORDERS:", len(jobcard_orders))
    print("PRINTING ORDERS:", len(printing_orders))
    print("PACKING ORDERS:", len(packing_orders))
    print("DISPATCH ORDERS:", len(dispatch_orders))

    print("======================================")

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

# ==================================================
# REPORTS DASHBOARD
# ==================================================

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

    if month < 1 or month > 12:

        month = datetime.now().month

    # -----------------------------
    # DATE RANGE
    # -----------------------------

    start_date = datetime(
        year,
        month,
        1
    ).date()

    if month == 12:

        end_date = datetime(
            year + 1,
            1,
            1
        ).date()

    else:

        end_date = datetime(
            year,
            month + 1,
            1
        ).date()

    # -----------------------------
    # MONTH ORDERS
    # -----------------------------

    orders = Order.query.filter(
        Order.order_date >= start_date,
        Order.order_date < end_date
    ).order_by(
        Order.id.desc()
    ).all()

    # -----------------------------
    # COUNTS
    # -----------------------------

    total_orders = len(orders)

    pending = sum(
        1
        for order in orders
        if order.status != "Delivered"
    )

    delivered = sum(
        1
        for order in orders
        if order.status == "Delivered"
    )

    ready_dispatch = sum(
        1
        for order in orders
        if order.status == "Ready Dispatch"
    )

    complete_ready = (
        delivered + ready_dispatch
    )

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

    clipping = sum(
        1
        for order in orders
        if order.status == "Clipping"
    )

    # PROCESS =
    # Job Card + Printing + Packing + Clipping

    process = sum(
        1
        for order in orders
        if order.status in [
            "Job Card",
            "Printing",
            "Packing",
            "Clipping"
        ]
    )

    dispatched = sum(
        1
        for order in orders
        if order.status == "Dispatched"
    )

    return render_template(

        'reports.html',

        total_orders=total_orders,

        pending=pending,

        delivered=delivered,

        ready_dispatch=ready_dispatch,

        complete_ready=complete_ready,

        process=process,

        design=design,

        jobcard=jobcard,

        printing=printing,

        packing=packing,

        clipping=clipping,

        dispatched=dispatched,

        month=month,

        year=year
    )


# ==================================================
# REPORT ORDERS
# ==================================================

@app.route('/reports/orders')
def report_orders():

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

    report_type = request.args.get(
        "type",
        "total"
    )

    report_type = report_type.lower().strip()

    # -----------------------------
    # TYPE ALIASES
    # -----------------------------

    if report_type == "all":

        report_type = "total"

    type_aliases = {

        "design": "design",

        "job card": "jobcard",

        "jobcard": "jobcard",

        "printing": "printing",

        "packing": "packing",

        "clipping": "clipping",

        "ready dispatch": "ready_dispatch",

        "ready_dispatch": "ready_dispatch",

        "dispatched": "dispatched",

        "delivered": "delivered",

        "pending": "pending",

        "complete_ready": "complete_ready",

        "process": "process"
    }

    report_type = type_aliases.get(
        report_type,
        report_type
    )

    # -----------------------------
    # DATE RANGE
    # -----------------------------

    start_date = datetime(
        year,
        month,
        1
    ).date()

    if month == 12:

        end_date = datetime(
            year + 1,
            1,
            1
        ).date()

    else:

        end_date = datetime(
            year,
            month + 1,
            1
        ).date()

    # -----------------------------
    # MONTH ORDERS
    # -----------------------------

    orders = Order.query.filter(
        Order.order_date >= start_date,
        Order.order_date < end_date
    ).order_by(
        Order.id.desc()
    ).all()

    # -----------------------------
    # FILTER
    # -----------------------------

    if report_type == "pending":

        orders = [
            order
            for order in orders
            if order.status != "Delivered"
        ]

    elif report_type == "delivered":

        orders = [
            order
            for order in orders
            if order.status == "Delivered"
        ]

    elif report_type == "complete_ready":

        orders = [
            order
            for order in orders
            if order.status in [
                "Delivered",
                "Ready Dispatch"
            ]
        ]

    elif report_type == "process":

        orders = [
            order
            for order in orders
            if order.status in [
                "Job Card",
                "Printing",
                "Packing",
                "Clipping"
            ]
        ]

    elif report_type == "design":

        orders = [
            order
            for order in orders
            if order.status == "Design"
        ]

    elif report_type == "jobcard":

        orders = [
            order
            for order in orders
            if order.status == "Job Card"
        ]

    elif report_type == "printing":

        orders = [
            order
            for order in orders
            if order.status == "Printing"
        ]

    elif report_type == "packing":

        orders = [
            order
            for order in orders
            if order.status == "Packing"
        ]

    elif report_type == "clipping":

        orders = [
            order
            for order in orders
            if order.status == "Clipping"
        ]

    elif report_type == "ready_dispatch":

        orders = [
            order
            for order in orders
            if order.status == "Ready Dispatch"
        ]

    elif report_type == "dispatched":

        orders = [
            order
            for order in orders
            if order.status == "Dispatched"
        ]

    # -----------------------------
    # TITLES
    # -----------------------------

    titles = {

        "total": "All Orders",

        "pending": "Pending Orders",

        "delivered": "Completed Orders",

        "complete_ready":
            "Complete Order / Ready for Dispatch",

        "process":
            "Process Orders",

        "design":
            "Design Orders",

        "jobcard":
            "Job Card Orders",

        "printing":
            "Printing Orders",

        "packing":
            "Packing Orders",

        "clipping":
            "Clipping Orders",

        "ready_dispatch":
            "Ready Dispatch Orders",

        "dispatched":
            "Dispatched Orders"
    }

    title = titles.get(
        report_type,
        "Orders"
    )

    return render_template(

        'report_orders.html',

        orders=orders,

        title=title,

        month=month,

        year=year,

        report_type=report_type
    )


# ==================================================
# REPORT EXCEL EXPORT
# ==================================================

def generate_report_export():

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

    report_type = request.args.get(
        "type",
        "total"
    )

    report_type = report_type.lower().strip()

    if report_type == "all":

        report_type = "total"

    type_aliases = {

        "job card": "jobcard",

        "ready dispatch": "ready_dispatch",

        "process": "process"
    }

    report_type = type_aliases.get(
        report_type,
        report_type
    )

    # -----------------------------
    # DATE RANGE
    # -----------------------------

    start_date = datetime(
        year,
        month,
        1
    ).date()

    if month == 12:

        end_date = datetime(
            year + 1,
            1,
            1
        ).date()

    else:

        end_date = datetime(
            year,
            month + 1,
            1
        ).date()

    # -----------------------------
    # QUERY
    # -----------------------------

    query = Order.query.filter(
        Order.order_date >= start_date,
        Order.order_date < end_date
    )

    if report_type == "pending":

        query = query.filter(
            Order.status != "Delivered"
        )

    elif report_type == "delivered":

        query = query.filter(
            Order.status == "Delivered"
        )

    elif report_type == "complete_ready":

        query = query.filter(
            Order.status.in_([
                "Delivered",
                "Ready Dispatch"
            ])
        )

    elif report_type == "process":

        query = query.filter(
            Order.status.in_([
                "Job Card",
                "Printing",
                "Packing",
                "Clipping"
            ])
        )

    elif report_type == "design":

        query = query.filter(
            Order.status == "Design"
        )

    elif report_type == "jobcard":

        query = query.filter(
            Order.status == "Job Card"
        )

    elif report_type == "printing":

        query = query.filter(
            Order.status == "Printing"
        )

    elif report_type == "packing":

        query = query.filter(
            Order.status == "Packing"
        )

    elif report_type == "clipping":

        query = query.filter(
            Order.status == "Clipping"
        )

    elif report_type == "ready_dispatch":

        query = query.filter(
            Order.status == "Ready Dispatch"
        )

    elif report_type == "dispatched":

        query = query.filter(
            Order.status == "Dispatched"
        )

    orders = query.order_by(
        Order.id.desc()
    ).all()

    # -----------------------------
    # CREATE EXCEL
    # -----------------------------

    workbook = openpyxl.Workbook()

    sheet = workbook.active

    sheet.title = "Order Report"

    # -----------------------------
    # HEADERS
    # -----------------------------

    headers = [

        "Order No",

        "Client Name",

        "Contact Number",

        "Product",

        "Size",

        "Rate per piece ",

        "Quantity",

        "order by",
        
        "Designer",

        "Order Date",

        "Delivery Date",

        "Status",

        "Remarks"
    ]

    sheet.append(headers)

    # -----------------------------
    # DATA
    # -----------------------------

    for order in orders:

       sheet.append([

    order.order_no,

    order.client_name,

    order.mobile,

    order.product,

    order.size,

    order.rate,

    order.quantity,

    order.order_by,

    order.staff_name,

    order.order_date,

    order.delivery_date,

    order.status,

    order.remarks
])

    # -----------------------------
    # COLUMN WIDTH
    # -----------------------------

    widths = {

        "A": 15,
        "B": 25,
        "C": 18,
        "D": 20,
        "E": 15,
        "F": 12,
        "G": 18,
        "H": 15,
        "I": 15,
        "J": 20,
        "K": 35
    }

    for column, width in widths.items():

        sheet.column_dimensions[
            column
        ].width = width

    # -----------------------------
    # HEADER STYLE
    # -----------------------------

    for cell in sheet[1]:

        cell.font = openpyxl.styles.Font(
            bold=True
        )

        cell.alignment = openpyxl.styles.Alignment(
            horizontal="center"
        )

    # -----------------------------
    # SAVE MEMORY
    # -----------------------------

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    filename = (

        f"Order_Report_"
        f"{year}_"
        f"{month:02d}_"
        f"{report_type}.xlsx"
    )

    return send_file(

        output,

        as_attachment=True,

        download_name=filename,

        mimetype=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )


# ==================================================
# EXPORT ROUTE
# ==================================================

@app.route('/reports/export')
def reports_export():

    return generate_report_export()


# ==================================================
# PUBLIC ORDER TRACKING
# ==================================================

@app.route('/track/<order_no>')
def track(order_no):

    order = Order.query.filter_by(
        order_no=order_no
    ).first_or_404()

    return render_template(
        'track.html',
        order=order
    )


# ==================================================
# ORDER DETAIL
# ==================================================

@app.route('/order/<int:id>')
def order_detail(id):

    if 'user_id' not in session:

        return redirect('/login')

    order = Order.query.get_or_404(id)

    role = session.get(
        'role'
    )

    username = session.get(
        'user'
    )

    if role == 'designer':

        if order.staff_name != username:

            return "Access Denied", 403

    return render_template(

        'order_detail.html',

        order=order,

        role=role,

        username=username
    )


# ==================================================
# CREATE DEFAULT USERS
# ==================================================

with app.app_context():

    # OWNER
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

    # DESIGNER 1 - LATIF MAKWANA
    designer1 = User.query.filter_by(
        username="designer1"
    ).first()

    if not designer1:
        designer1 = User(
            name="Latif Makwana",
            username="designer1",
            password="designer@123",
            role="designer"
        )
        db.session.add(designer1)
    else:
        designer1.name = "Latif Makwana"

    # DESIGNER 2 - DOLLY KESHWARWANI
    designer2 = User.query.filter_by(
        username="designer2"
    ).first()

    if not designer2:
        designer2 = User(
            name="Dolly Kesharwani",
            username="designer2",
            password="designer2@123",
            role="designer"
        )
        db.session.add(designer2)
    else:
        designer2.name = "Dolly Kesharwani"

    # DESIGNER 3 - ANU GAYNAR
    designer3 = User.query.filter_by(
        username="designer3"
    ).first()

    if not designer3:
        designer3 = User(
            name="Anu Gaynar",
            username="designer3",
            password="designer3@123",
            role="designer"
        )
        db.session.add(designer3)
    else:
        designer3.name = "Anu Gaynar"

    db.session.commit()

    # PRODUCTION
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


# ==================================================
# RUN APP
# ==================================================

if __name__ == '__main__':

    app.run(

        host='0.0.0.0',

        port=5000,

        debug=True
    )