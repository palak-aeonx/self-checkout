from flask import Flask, request, jsonify
from detect import detect_product, draw_boxes
from database import init_db, add_to_cart, get_cart, update_quantity, delete_from_cart
from flask_cors import CORS
import config

app = Flask(__name__)
app.config.from_object(config)
CORS(app)

# Initialize the database
with app.app_context():
    init_db(app)

@app.route('/scan', methods=['POST'])
def scan():
    if 'image' in request.files:
        image = request.files['image']
    elif 'image' in request.json:
        image = request.json['image']
    else:
        return jsonify({'error': 'No image provided'}), 400

    product = detect_product(image)
    
    if product:
        add_to_cart(product)
        
        return jsonify({
            'product': {
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'confidence': product['confidence']
            }
        })
    else:
        return jsonify({'error': 'No product detected'}), 404

@app.route('/cart', methods=['GET'])
def get_cart_contents():
    return jsonify(get_cart())

@app.route('/update_quantity', methods=['POST'])
def update_product_quantity():
    product_id = request.json['product_id']
    quantity = request.json['quantity']
    action = request.json.get('action', 'set')  
    
    current_cart = get_cart()
    current_quantity = next((item['quantity'] for item in current_cart['items'] if item['id'] == product_id), 0)
    
    if action == 'increase':
        new_quantity = current_quantity + quantity
    elif action == 'decrease':
        new_quantity = max(0, current_quantity - quantity)
    else:  
        new_quantity = quantity
    
    if new_quantity == 0:
        delete_from_cart(product_id)
    else:
        update_quantity(product_id, new_quantity)
    
    return jsonify(get_cart())

@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_id = request.json['product_id']
    delete_from_cart(product_id)
    return jsonify(get_cart())


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
