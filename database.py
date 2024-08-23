from flask_sqlalchemy import SQLAlchemy
from flask import current_app

db = SQLAlchemy()

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

def init_db(app):
    # Construct the database URI from the DATABASE_CONFIG
    db_config = app.config['DATABASE_CONFIG']
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    with app.app_context():
        db.create_all()

def add_to_cart(product):
    item = Cart.query.get(product['id'])
    if item:
        item.quantity += 1
    else:
        item = Cart(id=product['id'], name=product['name'], price=product['price'], quantity=1)
        db.session.add(item)
    db.session.commit()

def update_quantity(product_id, quantity):
    item = Cart.query.get(product_id)
    if item:
        if quantity > 0:
            item.quantity = quantity
        else:
            db.session.delete(item)
    db.session.commit()

def delete_from_cart(product_id):
    item = Cart.query.get(product_id)
    if item:
        db.session.delete(item)
        db.session.commit()

def get_cart():
    items = Cart.query.all()
    total = sum(item.quantity * item.price for item in items)
    return {'items': [item.to_dict() for item in items], 'total': total}

def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'price': self.price,
        'quantity': self.quantity
    }

Cart.to_dict = to_dict