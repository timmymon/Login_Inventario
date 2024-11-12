from flask import Flask, render_template, redirect, request, session
import pymysql
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db_host = 'localhost'
db_user = 'root'
db_password = ''
db_name = 'hospital_db'

def get_db_connection():
    return pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)

def get_all_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
    finally:
        conn.close()
    return products

def create_product(name, description, price, quantity, image):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, description, price, quantity, image) VALUES (%s, %s, %s, %s, %s)", 
                       (name, description, price, quantity, image))
        conn.commit()
    finally:
        conn.close()

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
        finally:
            conn.close()
        if user:
            session['user'] = username
            return redirect('/inventory')
    return render_template('login.html')

@app.route('/inventory', methods=['GET'])
def inventory():
    if 'user' in session:
        products = get_all_products()
        return render_template('inventory.html', products=products)
    else:
        return redirect('/login')

@app.route('/inventory/create', methods=['GET', 'POST'])
def create_product_route():
    if 'user' in session:
        if request.method == 'POST':
            product_name = request.form['product_name']
            description = request.form['description']
            price = request.form['price']
            quantity = request.form['quantity']
            image = request.files['image']
            
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                create_product(product_name, description, price, quantity, filename)
                return redirect('/inventory')
        return render_template('create_product.html')
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
