from flask import Flask, render_template, request, jsonify,redirect,url_for,flash
from pymongo import MongoClient
import random
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = 'jinfjvjhsfvjhes'

# MongoDB connection
client = MongoClient("mongodb+srv://vinit_dubey:1860Amul@cluster0.zjwfiov.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['Garden']
user_collection = db['login_and_register']  # Single collection for login and registration\
plant_collection = db["plant_collection"]
normal_plant_search = db["normal_plant_search"]
quiz_collection = db['quiz']
bookmarks_collection = db["bookmarks"]
plant_coll=db['advanced_search']
recived_Data=plant_coll.find({'_id':'plant'})
plants_data=recived_Data[0]['plant_data']

#global user
current_user=None

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
        return render_template("plant_search_detail.html", plant_data=plant_data,plant_name=plant_name)
    else:
        return render_template("plant_search_detail.html", error="Plant not found")

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
    language = request.form.get('language', '').lower()
    print(language)

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

    lang_code = language_codes.get(language, "")
    print(f"Selected language: {lang_code}")  # For debugging or logging

    # Redirect to the homepage
    return render_template('main_home.html')


@app.route('/plant_data_upload')
def form():
    return render_template('plant_data_upload.html')

@app.route('/submit_plant_data', methods=['POST'])
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
    else:
    # by default if none is found
        random_plant="Neem"

    
    plant_data = normal_plant_search.find_one({"_id": random_plant})

    if plant_data:
        return render_template("plant_moment.html", plant_data=plant_data,plant_name=random_plant)
    else:
        return render_template("plant_moment.html", error="Plant not found")
    

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

# Route to display detailed information about the plant
@app.route('/plant_detail/<plant_name>')
def plant_detail(plant_name):
    plant = next((plant for plant in plants_data if plant['name'] == plant_name), None)
    return render_template('plant_search_detail copy.html', plant=plant)

if __name__ == "__main__":
    app.run(debug=True)
