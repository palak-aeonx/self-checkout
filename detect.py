from ultralytics import YOLO
from flask import current_app
from PIL import Image
import numpy as np
import base64
import io
import cv2
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import uuid
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_to_s3(image, bucket, s3_file):
    try:
        s3 = boto3.client('s3', 
                          aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
                          region_name=current_app.config['AWS_REGION'])

        s3.upload_fileobj(image, bucket, s3_file)
        logger.info(f"Successfully uploaded {s3_file} to {bucket}")
        return True
    except NoCredentialsError:
        logger.error("Credentials not available")
        return False
    except ClientError as e:
        logger.error(f"An error occurred: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False

def detect_product(image_data):
    model = YOLO('yolov8s.pt') 

    
    if isinstance(image_data, str):
        
        image_data = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
    else:
        
        image = Image.open(image_data)

    
    image_np = np.array(image)

    
    results = model(image_np)

    detected_objects = []
    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            class_name = model.names[cls]
            confidence = float(box.conf[0])
            
            
            if confidence > 0.4:
                detected_objects.append({
                    'name': class_name,
                    'confidence': confidence,
                    'box': box.xyxy[0].tolist()
                })
                
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.rectangle(image_np, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(image_np, f'{class_name} {confidence:.2f}', (int(x1), int(y1)-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    
    processed_image = Image.fromarray(image_np)

    
    img_byte_arr = io.BytesIO()
    processed_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    
    filename = f"detected_image_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"

    
    upload_success = upload_to_s3(img_byte_arr, current_app.config['AWS_BUCKET_NAME'], filename)
    if upload_success:
        logger.info(f"Image uploaded to S3: {filename}")
    else:
        logger.warning("Failed to upload image to S3")

    products = current_app.config['PRODUCT_PRICES']

    for obj in detected_objects:
        if obj['name'] in products:
            return {
                'id': detected_objects.index(obj) + 1,
                'name': obj['name'],
                'price': products[obj['name']],
                'confidence': obj['confidence'],
                's3_image': filename if upload_success else None
            }
    
    return None

def draw_boxes(image_data, detections):
    if isinstance(image_data, str):
       
        image_data = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
    else:
        
        image = Image.open(image_data)

    
    frame = np.array(image)

    for detection in detections:
        x1, y1, x2, y2 = detection['box']
        cls = detection['class']
        conf = detection['confidence']
        color = get_colors(cls)
        
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(frame, f'{detection["name"]} {conf:.2f}', (int(x1), int(y1)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # Convert back to PIL Image
    result_image = Image.fromarray(frame)
    
    buffered = io.BytesIO()
    result_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_colors(cls_num):
    base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    color_index = cls_num % len(base_colors)
    increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
    color = [base_colors[color_index][i] + increments[color_index][i] * 
             (cls_num // len(base_colors)) % 256 for i in range(3)]
    return tuple(color)