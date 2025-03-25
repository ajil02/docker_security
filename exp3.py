from flask import Flask, render_template, request, redirect, url_for
import csv

app = Flask(__name__)

# Function to load the CSV file into a list of dictionaries
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

# Function to save the updated inventory back to the CSV file
def save_inventory(inventory):
    with open('inventory.csv', mode='w', newline='') as file:
        fieldnames = ['Product ID', 'Product Name', 'Category', 'Price', 'Stock', 'Total Sales']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)

@app.route('/')
def home():
    inventory = load_inventory()
    return render_template('index.html', inventory=inventory)

@app.route('/add', methods=['GET', 'POST'])
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
            return "Error: Product ID already exists."
        
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
        return redirect(url_for('home'))
    return render_template('add.html')

@app.route('/update/<product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    inventory = load_inventory()
    product = next((prod for prod in inventory if prod['Product ID'] == product_id), None)
    if not product:
        return "Error: Product ID not found."
    
    if request.method == 'POST':
        product['Price'] = float(request.form['price'])
        product['Stock'] = int(request.form['stock'])
        product['Total Sales'] = product['Price'] * product['Stock']
        save_inventory(inventory)
        return redirect(url_for('home'))
    
    return render_template('update.html', product=product)

@app.route('/delete/<product_id>', methods=['POST'])
def delete_product(product_id):
    inventory = load_inventory()
    inventory = [prod for prod in inventory if prod['Product ID'] != product_id]
    save_inventory(inventory)
    return redirect(url_for('home'))

@app.route('/record_sale/<product_id>', methods=['POST'])
def record_sale(product_id):
    inventory = load_inventory()
    product = next((prod for prod in inventory if prod['Product ID'] == product_id), None)
    if not product:
        return "Error: Product ID not found."
    
    sale_quantity = int(request.form['sale_quantity'])
    stock = int(product['Stock'])
    if sale_quantity > stock:
        return "Error: Not enough stock available."
    
    product['Stock'] = stock - sale_quantity
    product['Total Sales'] = float(product['Price']) * (stock - product['Stock'])
    save_inventory(inventory)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)