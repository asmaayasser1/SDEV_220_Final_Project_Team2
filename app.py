from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SECRET_KEY'] = 'sdev220_team2_secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Prevent caching
db = SQLAlchemy(app)

# Custom Jinja2 filter for fixed two-decimal formatting
def to_fixed(value, decimals=2):
    return f"{value:.{decimals}f}"
app.jinja_env.filters['to_fixed'] = to_fixed

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Forms
class CheckoutForm(FlaskForm):
    customer_name = StringField('Name', validators=[DataRequired()])
    customer_email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Place Order')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Add Product')

# Routes
@app.route('/')
def product_list():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart_item = CartItem.query.filter_by(product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(product_id=product_id)
        db.session.add(cart_item)
    db.session.commit()
    flash('Item added to cart!', 'success')
    return redirect(url_for('product_list'))

@app.route('/cart')
def cart():
    cart_items = CartItem.query.all()
    products = {p.id: p for p in Product.query.all()}
    total = sum(products[item.product_id].price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, products=products, total=total)

@app.route('/remove_from_cart/<int:cart_item_id>')
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = CheckoutForm()
    cart_items = CartItem.query.all()
    products = {p.id: p for p in Product.query.all()}
    total = sum(products[item.product_id].price * item.quantity for item in cart_items)
    
    if form.validate_on_submit():
        order = Order(
            customer_name=form.customer_name.data,
            customer_email=form.customer_email.data,
            total=total
        )
        db.session.add(order)
        db.session.commit()
        
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=products[item.product_id].price
            )
            db.session.add(order_item)
        
        CartItem.query.delete()
        db.session.commit()
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    return render_template('checkout.html', form=form, cart_items=cart_items, products=products, total=total)

@app.route('/order/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    products = {p.id: p for p in Product.query.all()}
    return render_template('order_confirmation.html', order=order, order_items=order_items, products=products)

@app.route('/admin/orders')
def admin_orders():
    orders = Order.query.all()
    order_items = OrderItem.query.all()
    products = {p.id: p for p in Product.query.all()}
    return render_template('admin_orders.html', orders=orders, order_items=order_items, products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.args.get('admin_key') != 'sdev220_team2_admin':
        flash('Unauthorized access!', 'error')
        return redirect(url_for('product_list'))
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('product_list'))
    return render_template('add_product.html', form=form)

@app.route('/delete_product/<int:product_id>', methods=['GET'])
def delete_product(product_id):
    if request.args.get('admin_key') != 'sdev220_team2_admin':
        flash('Unauthorized access!', 'error')
        return redirect(url_for('product_list'))
    product = Product.query.get_or_404(product_id)
    # Remove associated cart items
    CartItem.query.filter_by(product_id=product_id).delete()
    # Note: Existing order items retain historical data
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product.name}" deleted successfully!', 'success')
    return redirect(url_for('product_list'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)