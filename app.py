from flask import Flask, render_template, request, jsonify,redirect,url_for,flash,session,Response
from pymongo import MongoClient
import random
from bson.objectid import ObjectId
import google.generativeai as genai
from googletrans import Translator
import random
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from ultralytics import YOLO  # Use YOLOv8
import torch
import os
import math
import smtplib
import yagmail
from MODEL.YOLO_vedio import video_detection

app = Flask(__name__)
app.secret_key = 'jinfjvjhsfvjhes'

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['Garden']
user_collection = db['login_and_register']  # Single collection for login and registration\
plant_collection = db["plant_collection"]
normal_plant_search = db["normal_plant_search"]
quiz_collection = db['quiz']
bookmarks_collection = db["bookmarks"]
plant_coll=db['advanced_search']
recived_Data=plant_coll.find({'_id':'plant'})
plants_data=recived_Data[0]['plant_data']


# Flask-Mail Configuration 
EMAIL_ADDRESS = "major2025vii@gmail.com"
APP_PASSWORD = "qzho fbab zswv oaoi"  # Your 16-character App Password

def send_email(recipient_email, subject, message):
    try:
        yag = yagmail.SMTP(EMAIL_ADDRESS, APP_PASSWORD)
        yag.send(to=recipient_email, subject=subject, contents=message)
        return "Email sent successfully!"
    except Exception as e:
        return f"Email failed to send. Error: {e}"


#global user and language
current_user=None
selected_language = "en"

#Translator initiation

translator = Translator()

def translate_text(text, lang):
    """Recursively translates text while skipping URLs and file paths."""
    if isinstance(text, str):
        try:
            if text.strip():  # Ensure text is not empty
                return translator.translate(text, dest=lang).text
            return text  # Return original if empty
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original text on failure
    elif isinstance(text, list):
        return [translate_text(item, lang) for item in text]
    elif isinstance(text, dict):
        return {key: translate_text(value, lang) for key, value in text.items()}
    return text  # Return as is if not str, list, or dict

#default welcome page
@app.route('/',methods=['GET', 'POST'])
def welcome():
    return render_template('index.html')

@app.route("/plant_search")
def index():
    categories_doc = plant_collection.find_one({}, {"_id": 0})  # Fetch the categories document
    categories = categories_doc.get("categories", {})  # Get the 'categories' dictionary
    return render_template("plant_search.html", categories=categories)

@app.route('/submit_quiz_data')
def quiz_form():
    return render_template('quiz_form.html')


@app.route("/search_plant", methods=["POST"])
def search():
    category = request.form.get("category")
    plant_name = request.form.get("plant_name")
    plant_data = normal_plant_search.find_one({"_id": plant_name})

    if plant_data:
        plant_details = plant_data[plant_name]

        if len(plant_details) >= 2:
            images = plant_details[:2]  # Keep images
            text_data = plant_details[2:]  # Translate only text
        else:
            images = plant_details
            text_data = []

        translated_data = images + translate_text(text_data, selected_language)
        final_data={
            "_id":plant_name,
            plant_name:translated_data
        }
        return render_template("plant_search_detail.html", plant_data=final_data, plant_name=plant_name)
    
    else:
        error_message = translate_text("Plant not found", selected_language)
        return render_template("plant_search_detail.html", error=error_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global current_user
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = user_collection.find_one({"email": email, "password": password})
        if user:
            current_user=email
            return render_template('language.html')
        return jsonify({"message": "Invalid credentials"})
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user already exists
        user = user_collection.find_one({"email": email})
        if user:
            return jsonify({"message": "User already exists"})
        
        # Insert new user into the collection
        user_collection.insert_one({"fullname": fullname, "email": email, "password": password})
        return jsonify({"message": "Registration successful"})
    return render_template('register.html')


@app.route('/set_language', methods=['POST'])
def set_language():
    global selected_language
    selected_language = request.form.get('language', '').lower()
    print(selected_language)

    # Language code mapping
    language_codes = {
        "hi":"hindi",
        "en":"english",
        "mr":"marathi",
        "bn":"bengali",
        "ru":"russian",
        "es":"spanish",
        "te":"telugu",
        "ta":"tamil",
        
    }

    lang_code = language_codes.get(selected_language, "")
    print(f"Selected language: {lang_code}")  # For debugging or logging

    # Redirect to the homepage
    return render_template('main_home.html')

@app.route('/mainpage')
def mainpage():
    return render_template('main_home.html')
@app.route('/plant_data_upload')
def form():
    return render_template('plant_data_upload.html')

@app.route('/submit_plant_data', methods=['GET','POST'])
def submit():
    try:
        # Collect form data
        data = {
            "_id": request.form['plant_name'],
            request.form['plant_name']: [
                request.form['full_tree_image'],
                request.form['leaf_image'],
                request.form['botanical_name'],
                request.form.getlist('common_names'),
                {
                    "habitat": {
                        "Regions": request.form['regions'],
                        "Soil Type": request.form['soil_type'],
                        "Climate": request.form['climate'],
                        "Altitude": request.form['altitude'],
                        "Common Locations": request.form['common_locations'],
                    }
                },
                {
                    "medicinal uses": {
                        "Skin Health": request.form['skin_health'],
                        "Oral Hygiene": request.form['oral_hygiene'],
                        "Blood Purification": request.form['blood_purification'],
                        "Immune Booster": request.form['immune_booster'],
                        "Digestive Aid": request.form['digestive_aid'],
                    }
                },
                {
                    "methods of cultivation": {
                        "Climate and Soil Requirements": request.form['climate_soil'],
                        "Propagation": request.form['propagation'],
                        "Sowing": request.form['sowing'],
                        "Irrigation": request.form['irrigation'],
                        "Fertilization": request.form['fertilization'],
                        "Harvesting": request.form['harvesting'],
                        "Additional Care": request.form['additional_care'],
                        "vedio link": request.form['video_link']
                    }
                }
            ]
        }

        # Insert data into MongoDB
        normal_plant_search.insert_one(data)
        flash('Data uploaded successfully!', 'success')
        return redirect(url_for('form'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('form'))
    





@app.route('/submit_quiz', methods=['GET','POST'])
def submit_quiz():
    try:
        # Collect form data
        quiz_data = {
            '_id': request.form['quiz_id'],
            'ques': request.form['question'],
            'option1': request.form['option1'],
            'option2': request.form['option2'],
            'option3': request.form['option3'],
            'option4': request.form['option4'],
            'correct_option': request.form['correct_option'],
            'Explanation': request.form['explanation']
        }

        # Insert data into MongoDB
        quiz_collection.insert_one(quiz_data)
        flash('Quiz data uploaded successfully!', 'success')
        return redirect(url_for('quiz_form'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('quiz_form'))
    

@app.route('/quiz')
def quiz_page():
    # Fetch all question IDs from the database
    all_questions = list(quiz_collection.find({}, {'_id': 1}))
    all_ids = [question['_id'] for question in all_questions]

    # Randomly select 10 unique question IDs
    selected_ids = random.sample(all_ids, min(10, len(all_ids)))

    # Fetch the questions corresponding to the selected IDs
    selected_questions = list(quiz_collection.find({'_id': {'$in': selected_ids}}))

    return render_template('quiz_page.html', questions=selected_questions)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    question = request.form['question']
    selected_option = request.form['selected_option']
    correct_option = request.form['correct_option']
    explanation = request.form['explanation']

    if selected_option == correct_option:
        result = f"Correct! {explanation}"
        status = "correct"
    else:
        result = f"Incorrect. {explanation}"
        status = "incorrect"

    return {'result': result, 'status': status}




@app.route("/plant_moment", methods=["GET","POST"])
def plant_moment():

    categories_doc = plant_collection.find_one({}, {"_id": 0})  # Fetch the categories document
    categories = categories_doc.get("categories", {})  # Get the 'categories' dictionary
    if categories:
    # Randomly select one category
        random_category = random.choice(list(categories.keys()))
    # Randomly select one plant from the chosen category
        random_plant = random.choice(categories[random_category])
    

    
    plant_data = normal_plant_search.find_one({"_id": random_plant})
    if not(plant_data):
        random_plant="Neem"
        plant_data = normal_plant_search.find_one({"_id": random_plant})

    if plant_data:

        plant_details = plant_data[random_plant]

        if len(plant_details) >= 2:
            images = plant_details[:2]  # Keep images
            text_data = plant_details[2:]  # Translate only text
        else:
            images = plant_details
            text_data = []

        translated_data = images + translate_text(text_data, selected_language)
        final_data={
            "_id":random_plant,
            random_plant:translated_data
        }
        return render_template("plant_moment.html", plant_data=final_data, plant_name=random_plant)
    
    else:
        error_message = translate_text("Plant not found", selected_language)
        return render_template("plant_moment.html", error=error_message)

@app.route("/bookmarks")
def bookmarks():
    bookmarks = list(
        bookmarks_collection.find({"user_email": current_user}, {"_id": 1, "plant_name": 1, "notes": 1})
    )
    return render_template("bookmarks.html", bookmarks=bookmarks)

@app.route("/delete_bookmark/<bookmark_id>", methods=["DELETE"])
def delete_bookmark(bookmark_id):
    try:
        result = bookmarks_collection.delete_one({"_id": ObjectId(bookmark_id)})
        if result.deleted_count > 0:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Bookmark not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/bookmark_plant",methods=["POST"])
def bookmark_plant():
    plant_name = request.form.get("plant_name")
    notes = request.form.get("notes")

    if plant_name and notes:
        # Save the bookmark in the database
        bookmark = {
            "user_email": current_user,
            "plant_name": plant_name,
            "notes": notes
        }
        bookmarks_collection.insert_one(bookmark)
        flash("Plant bookmarked successfully!", "success")
    else:
        flash("Failed to bookmark the plant. Please try again.", "danger")

    return render_template("main_home.html")


@app.route('/garden')
def garden():
    return render_template('virtual_garden.html')

@app.route('/advance_search')
def advance_search():
        categories = list(set([plant['category'] for plant in plants_data]))
        return render_template('advance.html', categories=categories)


@app.route('/plants', methods=['POST'])
def plants():
    category = request.form.get('category')
    feature_count = int(request.form.get('feature_count'))
    
    # Collect selected features
    selected_features = [request.form.get(f'feature_{i}') for i in range(feature_count)]
    
    # Filter plants by category and all selected features
    filtered_plants = [
        plant for plant in plants_data
        if category in plant['category'] and all(feature in plant['features'] for feature in selected_features)
    ]
    return render_template('plants.html', plants=filtered_plants)

@app.route('/plant_detail/<plant_name>')
def plant_detail(plant_name):
    plant_data = normal_plant_search.find_one({"_id": plant_name})

    if not plant_data:
        return render_template("plant_search_detail.html", error="Plant not found")

    plant_details = plant_data.get(plant_name, [])

    if not plant_details:
        return render_template("plant_search_detail.html", error="No data available for this plant")

    # Ensure at least two elements before splitting
    images = plant_details[:2] if len(plant_details) >= 2 else plant_details
    text_data = plant_details[2:] if len(plant_details) > 2 else []

    # Correct image paths WITHOUT adding extra '/static/'
    corrected_images = []
    for image_path in images:
        if not image_path.startswith("http"):  # If it's not an external URL
            image_path = image_path.lstrip("./")  # Remove leading "./" to avoid duplicates
            corrected_images.append(url_for('static', filename=image_path.replace("static/", "", 1)))
        else:
            corrected_images.append(image_path)

    translated_data = corrected_images + text_data  # No translation function here to avoid errors

    final_data = {
        "_id": plant_name,
        plant_name: translated_data
    }

    return render_template("plant_search_detail.html", plant_data=final_data, plant_name=plant_name)
    
# Ask Ai starts:

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

@app.route("/ai")
def home():
    return render_template("askai.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_question = data.get("question", "")

    # Convert user question to English
    translated_question = translator.translate(user_question, dest="en").text

    # Get response from Gemini AI
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(translated_question).text

    # Format response (bold headings, spacing, and structure)
    formatted_response = format_response(response)

    # Translate response back to user-selected language
    translated_response = translator.translate(formatted_response, dest="en").text

    return jsonify({"response": translated_response})


import re

def format_response(response):
    """Format AI response to improve readability."""

    # 1. Convert newlines to <br> for HTML rendering
    response = response.replace("\n", "<br>")

    # 2. Convert Markdown-style lists (*, -) to HTML lists (<ul>, <li>)
    response = re.sub(r"^(\*|-|\+) (.*?)$", r"<li>\2</li>", response, flags=re.MULTILINE) # Match at line start
    response = re.sub(r"(<br>(\*|-|\+) (.*?))$", r"<li>\3</li>", response, flags=re.MULTILINE) # Match after line break
    response = re.sub(r"(<li>.*?</li>)(<br><li>|$)", r"\1", response) # Remove extra <br> between list items

    # Wrap the list items in <ul> tags.  Do this *after* the individual <li> conversion.
    response = re.sub(r"(<li>.*?</li>)", r"<ul>\1</ul>", response, flags=re.MULTILINE)

    # 3. Convert bold text (**) to <strong> tags
    response = response.replace("**", "<strong>").replace("**", "</strong>")

    # 4. Add spacing between sections (using <br> tags) - improve readability
    response = response.replace("<br><br><br>", "<br><br>") # Reduce excessive breaks. Adjust as needed.
    response = re.sub(r"(</(ul|strong)>)(?!<br>)", r"\1<br><br>", response) # Add break after lists and bold text, but *not* if there's already a break

    # 5. Add emoji markers for key topics (using <span> for styling)
    response = response.replace("Care", "<span style='font-weight: bold; color: green;'>🪴 Care</span>")
    response = response.replace("watering", "<span style='font-weight: bold; color: blue;'>💧 Watering</span>")
    response = response.replace("sunlight", "<span style='font-weight: bold; color: orange;'>☀️ Sunlight</span>")
    response = response.replace("soil", "<span style='font-weight: bold; color: brown;'>🌱 Soil</span>")
    response = response.replace("Health", "<span style='font-weight: bold; color: red;'>🩺 Health</span>")

    return response


 
#plant store starts

# Sample plant data
plant_data = {}
coll_Store = db["normal_plant_search"]
plants = coll_Store.find()
for plant in plants:
    plant_name = plant["_id"]
    full_image_path = plant[plant_name][0]
    
    # Store in dictionary
    plant_data[plant_name] = [full_image_path]

plant_prices = {plant: random.randint(50, 200) for plant in plant_data}
@app.route('/plant_shop')
def plant_Shop():
    selected_plants = random.sample(list(plant_data.keys()), min(40, len(plant_data)))
    plants = [{"name": plant, "image": plant_data[plant][0], "price": plant_prices[plant]} for plant in selected_plants]
    return render_template("plant_store.html", plants=plants)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    plant_name = request.json.get("plant_name")
    
    if "cart" not in session:
        session["cart"] = {}

    if plant_name in session["cart"]:
        session["cart"][plant_name] += 1
    else:
        session["cart"][plant_name] = 1

    session.modified = True
    return jsonify({"success": True, "cart": session["cart"]})

@app.route('/update_cart', methods=['POST'])
def update_cart():
    plant_name = request.json.get("plant_name")
    action = request.json.get("action")

    if "cart" in session and plant_name in session["cart"]:
        if action == "increase":
            session["cart"][plant_name] += 1
        elif action == "decrease":
            session["cart"][plant_name] -= 1
            if session["cart"][plant_name] <= 0:
                del session["cart"][plant_name]

    session.modified = True
    return jsonify({"success": True, "cart": session["cart"]})

@app.route('/cart')
def cart():
    cart_items = []
    total_price = 0

    if "cart" in session:
        for plant, quantity in session["cart"].items():
            price = plant_prices.get(plant, 0)
            cart_items.append({"name": plant, "quantity": quantity, "price": price})
            total_price += price * quantity

    return render_template("cart.html", cart_items=cart_items, total_price=total_price)

@app.route('/checkout')
def checkout():
    total_price = sum(plant_prices.get(plant, 0) * qty for plant, qty in session.get("cart", {}).items())
    return render_template("checkout.html", total_price=total_price)

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    name = request.form.get("name")
    email = request.form.get("email")
    payment_status = request.form.get("payment_status")  # "Success" or "Failed"

    session.pop("cart", None)  # Clear cart after purchase

    # Send Confirmation Email using yagmail
    try:
        subject = "Payment Confirmation" if payment_status == "Success" else "Payment Failed"
        message_body = f"""
        Dear {name},

        Your payment status: {payment_status}

        Thank you for shopping with us! If your payment was successful, we will process your order soon.

        Best Regards,
        Plant Store 🌿
        """

        send_email(email, subject, message_body) # Use the yagmail function
        
    except Exception as e:  # Catch general exceptions for yagmail
        return f"Payment {payment_status}, but email failed to send. Error: {e}", 500

    return render_template("payment_success.html", name=name, email=email, payment_status=payment_status)
#Plant Detection Starts

#For Local Machine

def generate_frames_web(path_x):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

@app.route("/detect_local", methods=['GET','POST'])

def webcam():
    session.clear()
    return render_template('plant_detect.html')

# To display the Output Video on Webcam page
@app.route('/webapp')
def webapp():
    return Response(generate_frames_web(path_x=0), mimetype='multipart/x-mixed-replace; boundary=frame')



#For Server Machine



@app.route('/detect_server')
def detect():
    return render_template('plant_detect_server.html')


model = YOLO("MODEL/best_garden_final.pt")
classNames = ["Neem", "Tulsi"]

def process_image(image_data):
    try:
        # Decode base64 image
        img_data = image_data.split(',')[1]  # Remove data URI prefix
        decoded_img = base64.b64decode(img_data)
        nparr = np.frombuffer(decoded_img, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        results = model(img, stream=True)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                class_name = classNames[cls] if cls < len(classNames) else "Unknown"
                label = f'{class_name}{conf}'
                t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                c2 = x1 + t_size[0], y1 - t_size[1] - 3
                cv2.rectangle(img, (x1, y1), c2, [255, 0, 255], -1, cv2.LINE_AA)  # filled
                cv2.putText(img, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

        # Encode processed image back to base64
        ret, encoded_img = cv2.imencode('.jpg', img)
        processed_image_data = base64.b64encode(encoded_img).decode('utf-8')
        processed_image_data = "data:image/jpeg;base64," + processed_image_data # Add the data URI prefix
        return processed_image_data

    except Exception as e:
        print(f"Error processing image: {e}")
        return None  # Or handle the error as needed


@app.route('/process_frame', methods=['POST'])
def process_frame_route():
    try:
        data = request.get_json()
        image_data = data.get('image')
        if image_data:
            processed_image = process_image(image_data)
            return jsonify({'processed_image': processed_image})
        else:
            return jsonify({'error': 'No image data received'}), 400
    except Exception as e:
        print(f"Error in /process_frame route: {e}")
        return jsonify({'error': 'An error occurred'}), 500

#subscription

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get("email")

    if not email:
        return "Please enter a valid email address!", 400  # Bad request error

    return "Success", 200  # OK response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Use the assigned PORT or default to 5000
    app.run(host="0.0.0.0", port=port)
