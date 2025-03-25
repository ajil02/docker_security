from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect users to login page if not logged in

# Mock user database
users = {'admin': {'password': 'admin123'}}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username in users:
        return User(username)
    return None

# Make current_user available in all templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

def load_inventory():
    inventory = []
    try:
        with open('inventory.csv', mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                inventory.append(row)
    except FileNotFoundError:
        print("Error: The inventory file does not exist.")
    return inventory

def save_inventory(inventory):
    with open('inventory.csv', mode='w', newline='') as file:
        fieldnames = ['Product ID', 'Product Name', 'Category', 'Price', 'Stock', 'Total Sales']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)

@app.route('/')
@login_required
def home():
    inventory = load_inventory()
    return render_template('index.html', inventory=inventory)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        inventory = load_inventory()
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        category = request.form['category']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        total_sales = price * stock

        if any(product['Product ID'] == product_id for product in inventory):
            flash("Error: Product ID already exists.", "danger")
            return redirect(url_for('add_product'))

        new_product = {
            'Product ID': product_id,
            'Product Name': product_name,
            'Category': category,
            'Price': price,
            'Stock': stock,
            'Total Sales': total_sales
        }
        inventory.append(new_product)
        save_inventory(inventory)
        flash("Product added successfully!", "success")
        return redirect(url_for('home'))
    return render_template('add.html')

@app.route('/update/<product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    inventory = load_inventory()
    product = next((prod for prod in inventory if prod['Product ID'] == product_id), None)
    if not product:
        flash("Error: Product ID not found.", "danger")
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        product['Price'] = float(request.form['price'])
        product['Stock'] = int(request.form['stock'])
        product['Total Sales'] = product['Price'] * product['Stock']
        save_inventory(inventory)
        flash("Product updated successfully!", "success")
        return redirect(url_for('home'))
    
    return render_template('update.html', product=product)

@app.route('/delete/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    inventory = load_inventory()
    inventory = [prod for prod in inventory if prod['Product ID'] != product_id]
    save_inventory(inventory)
    flash("Product deleted successfully!", "success")
    return redirect(url_for('home'))

@app.route('/record_sale/<product_id>', methods=['POST'])
@login_required
def record_sale(product_id):
    inventory = load_inventory()
    product = next((prod for prod in inventory if prod['Product ID'] == product_id), None)
    if not product:
        flash("Error: Product ID not found.", "danger")
        return redirect(url_for('home'))
    
    sale_quantity = int(request.form['sale_quantity'])
    stock = int(product['Stock'])
    if sale_quantity > stock:
        flash("Error: Not enough stock available.", "danger")
        return redirect(url_for('home'))
    
    product['Stock'] = stock - sale_quantity
    product['Total Sales'] = float(product['Price']) * (stock - product['Stock'])
    save_inventory(inventory)
    flash("Sale recorded successfully!", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
