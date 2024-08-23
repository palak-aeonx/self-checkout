from dotenv import load_dotenv
import os

load_dotenv() 

DATABASE_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'user': os.getenv('DATABASE_USER', 'root'),
    'password': os.getenv('DATABASE_PASSWORD', ''),
    'database': os.getenv('DATABASE_NAME', 'cart_db')
}

DEBUG = True

PRODUCT_PRICES = {
    'apple': 20,
    'orange': 80,
    'broccoli': 40,
    'carrot': 90,
    'hot dog': 60,
    'pizza': 50,
    'donut': 90,
    'cake': 40,
    'book': 20,
    'cup': 50,
    'scissors': 20
}

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'retail-store-inventory')
AWS_REGION = os.getenv('AWS_REGION', 'ap-northeast-3')

RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_SECRET_KEY = os.getenv('RAZORPAY_SECRET_KEY')
