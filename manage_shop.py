from app import app, db, Product
import os

with app.app_context():
    # Create database tables
    db.create_all()
    print("Database tables created.")

    # Add sample products
    products = [
        {"name": "Garlic", "description": "One Whole Garlic Bulb", "price": 00.72},
        {"name": "Apple", "description": "One Red Apple", "price": 00.85},
        {"name": "Green Apple", "description": "One Green Apple", "price": 00.92},
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