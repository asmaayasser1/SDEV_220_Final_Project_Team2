from app import app, db, Product
import os

with app.app_context():
    # Create database tables
    db.create_all()
    print("Database tables created.")

    # Clear existing products (optional)
    Product.query.delete()

    # Add sample products
    products = [
        {"name": "Textbook", "description": "Math textbook for algebra", "price": 50.00},
        {"name": "Calculator", "description": "Scientific calculator", "price": 15.00},
        {"name": "Notebook", "description": "100-page notebook", "price": 3.00},
    ]
    for prod in products:
        product = Product(**prod)
        db.session.add(product)
    db.session.commit()
    print("Products added.")

    # Modify a template
    template_path = 'templates/products.html'
    with open(template_path, 'r') as file:
        content = file.read()
    new_content = content.replace('<h2>Products</h2>', '<h2>SDEV 220 School Store</h2>')
    with open(template_path, 'w') as file:
        file.write(new_content)
    print("Template updated.")