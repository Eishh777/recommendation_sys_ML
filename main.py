from flask import Flask, request, render_template, redirect, url_for, session,send_file
from flask_mail import Mail, Message
import numpy as np
import pandas as pd
import pickle
import MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import google.generativeai as genai
import os
from flask import jsonify

app = Flask(__name__)
app.secret_key = "b533a778180b087b72a27d7f186e8930"  # Change this to a secure key
# Set up Google Gemini API
API_KEY = "AIzaSyB7WocdSen88ywMhOd4nuBKy0sfgICVF6o"  # Replace with your actual Gemini API key
genai.configure(api_key=API_KEY)

# Use the correct model
MODEL_NAME = "gemini-1.5-pro-latest"
model = genai.GenerativeModel(MODEL_NAME)


# MySQL Database Configuration
db = MySQLdb.connect(host="localhost", user="root", passwd="eish777", db="disease_db")
cursor = db.cursor()

# Load datasets
sym_des = pd.read_csv("symtoms_df.csv")
precautions = pd.read_csv("precautions_df.csv")
workout = pd.read_csv("workout_df.csv")
description = pd.read_csv("description.csv")
medications = pd.read_csv('medications.csv')
diets = pd.read_csv("diets.csv")

# Load model
svc = pickle.load(open('svc.pkl', 'rb'))

# Initialize database
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255)
)''')
db.commit()

# Helper function
def helper(dis):
    desc = description[description['Disease'] == dis]['Description'].values[0]
    pre = precautions[precautions['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']].values.tolist()[0]
    med = medications[medications['Disease'] == dis]['Medication'].tolist()
    die = diets[diets['Disease'] == dis]['Diet'].tolist()
    wrkout = workout[workout['disease'] == dis]['workout'].tolist()
    return desc, pre, med, die, wrkout


symptoms_dict = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}
diseases_list = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'}

def get_predicted_value(patient_symptoms):
    input_vector = np.zeros(len(symptoms_dict))
    for symptom in patient_symptoms:
        if symptom in symptoms_dict:
            input_vector[symptoms_dict[symptom]] = 1
    return diseases_list.get(svc.predict([input_vector])[0], "Unknown Disease")

# Routes
@app.route("/")
def index():
    return render_template("index.html", name=session.get("name"))
# -----------------------------------------------------------------------------------------------------------------
# user login and everything about user
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["name"] = user[1]
            return redirect(url_for("home"))
        else:
            return render_template("login.html", message="Invalid email or password")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template("register.html", message="Passwords do not match")

        hashed_password = generate_password_hash(password)

        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                           (name, email, hashed_password))
            db.commit()
            return redirect(url_for("login"))
        except MySQLdb.IntegrityError:
            return render_template("register.html", message="Email already registered")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("name", None)
    return redirect(url_for("login"))

@app.route('/predict', methods=['GET', 'POST'])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == 'POST':
        symptoms = request.form.get('symptoms')

        if not symptoms:
            return render_template('index.html', message="Please enter symptoms", name=session["name"])

        # Normalize user input
        user_symptoms = [s.strip().lower().replace(" ", "_") for s in symptoms.split(',')]
        valid_symptoms = [symptom for symptom in user_symptoms if symptom in symptoms_dict]

        if not valid_symptoms:
            return render_template('index.html', message="Invalid symptoms entered", name=session["name"])

        predicted_disease = get_predicted_value(valid_symptoms)
        dis_des, precautions, medications, rec_diet, workout = helper(predicted_disease)

        return render_template('index.html', predicted_disease=predicted_disease, dis_des=dis_des,
                               my_precautions=precautions, medications=medications, my_diet=rec_diet,
                               workout=workout, name=session["name"])

    return render_template('index.html', name=session["name"])

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/developer")
def developer():
    return render_template("developer.html")

@app.route("/healthcare")
def healthcare():
    return render_template("healthcare.html")   

@app.route("/lab_test")
def lab_test():
    return render_template("lab_test.html")  
#----------------------------------------------------------CHAT BOT 

def chat_with_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text if response.text else "I'm not sure how to respond."
    except Exception as e:
        return f"Error: {e}"

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    bot_response = chat_with_gemini(user_message)
    return jsonify({"response": bot_response})

#----------------------------------------------------------CHAT BOT END

@app.route('/buy_medicine')
def buy_medicine():
    if "user_id" not in session:
        return redirect(url_for("login"))

    disease = request.args.get('disease', '').strip()
    user_name = session.get("name", "Guest")
    cursor.execute("SELECT DISTINCT disease FROM medicines")
    diseases = [row[0] for row in cursor.fetchall()]
    print("Received Disease:", disease)  # ✅ Check what Flask receives

    if not disease:
        return redirect(url_for("index"))

    try:
        # Check database connection
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        print("Connected to Database:", db_name)

        # Fetch medicines related to the disease
        if disease == "all" or not disease:
        # Fetch random medicines (limit to 10 for better UX)
            cursor.execute("SELECT id, name, price, stock, image FROM medicines ORDER BY RAND() LIMIT 10")
        else:
        # Fetch medicines related to the selected disease
            cursor.execute("SELECT id, name, price, stock, image FROM medicines WHERE TRIM(LOWER(disease)) = %s", (disease,))
        medicines = cursor.fetchall()
        print("Fetched Medicines:", medicines)  # ✅ Check if query returns data

    except Exception as e:
        print("Database Error:", e)  # ✅ Catch any SQL errors

    return render_template("store.html", disease=disease, user_name=user_name, medicines=medicines, diseases=diseases)


# update user info in profile
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        
        if password:
            hashed_password = generate_password_hash(password)
            cursor.execute("UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s", (name, email, hashed_password, user_id))
        else:
            cursor.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (name, email, user_id))
        
        db.commit()
        session["name"] = name
        return redirect(url_for("profile"))
    
    cursor.execute("SELECT name, email FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    return render_template("profile.html", user=user)

# get an email of report
from flask import send_file

@app.route('/download_report')
def download_report():
    if "user_id" not in session:
        return redirect(url_for("login"))

    disease = request.args.get('disease', 'Unknown Disease')

    # Fetch real data using helper function
    try:
        description, precautions, medications, rec_diet, workout = helper(disease)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return "Error fetching data for the report."

    pdf_path = f"reports/{disease}_report.pdf"

    # Ensure the 'reports' directory exists
    if not os.path.exists("reports"):
        os.makedirs("reports")

    # Generate PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Health Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Disease: {disease}")
    c.drawString(100, 700, f"Description: {description}")

    y = 670
    c.drawString(100, y, "Precautions:")
    y -= 20
    for prec in precautions:
        c.drawString(120, y, f"- {prec}")
        y -= 20

    c.drawString(100, y - 20, "Medications:")
    y -= 40
    for med in medications:
        c.drawString(120, y, f"- {med}")
        y -= 20

    c.drawString(100, y - 20, "Diet Recommendations:")
    y -= 40
    for diet in rec_diet:
        c.drawString(120, y, f"- {diet}")
        y -= 20

    c.drawString(100, y - 20, "Workout Suggestions:")
    y -= 40
    for wrk in workout:
        c.drawString(120, y, f"- {wrk}")
        y -= 20

    c.save()

    return send_file(pdf_path, as_attachment=True)

@app.route("/doctor_consultant")
def doctor_consultant():
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    return render_template("doctors_consultant.html", doctors=doctors)




#add to cart function

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    medicine_id = request.form["medicine_id"]
    medicine_name = request.form["medicine_name"]
    price = request.form["price"]
    quantity = request.form["quantity"]

    cursor.execute("SELECT * FROM cart WHERE user_id = %s AND medicine_id = %s", (user_id, medicine_id))
    existing_item = cursor.fetchone()

    if existing_item:
        cursor.execute(
            "UPDATE cart SET quantity = quantity + %s WHERE user_id = %s AND medicine_id = %s",
            (quantity, user_id, medicine_id),
        )
    else:
        cursor.execute(
            "INSERT INTO cart (user_id, medicine_id, medicine_name, price, quantity) VALUES (%s, %s, %s, %s, %s)",
            (user_id, medicine_id, medicine_name, price, quantity),
        )

    db.commit()
    return redirect(url_for("show_cart"))



#show cart 
@app.route('/cart')
def show_cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    
    # Ensure correct column order (medicine_id, medicine_name, price, quantity)
    cursor.execute("SELECT medicine_id, medicine_name, price, quantity FROM cart WHERE user_id = %s", (user_id,))
    cart_items = cursor.fetchall()

    # Convert price (index 2) to float and quantity (index 3) to int
    cart_items = [(item[0], item[1], float(item[2]), int(item[3])) for item in cart_items]

    return render_template("cart.html", cart_items=cart_items)





# Update cart (increase quantity, remove item)
@app.route('/update_cart', methods=['POST'])
def update_cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    medicine_id = request.form["medicine_id"]
    action = request.form["action"]

    if action == "increase":
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id = %s AND medicine_id = %s", (user_id, medicine_id))
    elif action == "decrease":
        cursor.execute("UPDATE cart SET quantity = GREATEST(quantity - 1, 1) WHERE user_id = %s AND medicine_id = %s", (user_id, medicine_id))
    elif action == "delete":
        cursor.execute("DELETE FROM cart WHERE user_id = %s AND medicine_id = %s", (user_id, medicine_id))

    db.commit()
    return redirect(url_for("show_cart"))

#buy medicines from cart and render it to payment.html 
@app.route('/buy_now')
def buy_now():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Fetch cart items for the user
    cursor.execute("SELECT medicine_id, medicine_name, price, quantity FROM cart WHERE user_id = %s", (user_id,))
    cart_items = cursor.fetchall()

    if not cart_items:  # If cart is empty, redirect to cart page
        return redirect(url_for("show_cart"))

    return render_template("payments.html", cart_items=cart_items, user_name=session.get("name"))






#further payment processes 
@app.route('/process_payment', methods=['POST'])
def process_payment():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Retrieve cart items
    cursor.execute("SELECT medicine_id, medicine_name FROM cart WHERE user_id = %s", (user_id,))
    cart_items = cursor.fetchall()

    print(f"🛒 Cart Items for user {user_id}: {cart_items}")  # ✅ Check if cart items are retrieved

    if not cart_items:
        print("🚨 No items in the cart, redirecting to cart page!")
        return redirect(url_for("cart"))

    # Insert order into database with 'pending' state
    for item in cart_items:
        medicine_id = item[0]
        medicine_name = item[1]

        # Fetch disease from the medicines table
        cursor.execute("SELECT disease FROM medicines WHERE id = %s", (medicine_id,))
        disease_result = cursor.fetchone()

        print(f"🔍 Fetching disease for medicine {medicine_id}: {disease_result}")  # ✅ Check disease data

        disease = disease_result[0] if disease_result else "Unknown"

        print(f"📝 Inserting Order: user_id={user_id}, disease={disease}, medicine={medicine_name}, status=pending")  # ✅ Debug before inserting

        try:
            cursor.execute(
                "INSERT INTO orders (user_id, disease, medicine, order_status, order_date) VALUES (%s, %s, %s, %s, NOW())",
                (user_id, disease, medicine_name, "pending")
            )
            db.commit()
            print("✅ Order successfully inserted!")  # ✅ Check if order insertion works

        except MySQLdb.Error as e:
            print(f"❌ Error inserting order: {e}")  # ✅ Capture SQL errors

    # Clear cart after payment
    cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    db.commit()
    print("🗑️ Cart cleared after payment.")
    cursor.execute("UPDATE orders SET order_status = 'paid' WHERE user_id = %s AND order_status = 'pending'", (user_id,))
    db.commit()
    return redirect(url_for("payment_success"))


@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Update all 'pending' orders to 'paid'
    cursor.execute("UPDATE orders SET order_status = 'paid' WHERE user_id = %s AND order_status = 'pending'", (user_id,))
    
    
    db.commit()

    return redirect(url_for("payment_success"))


# succesful payment
@app.route('/payment_success')
def payment_success():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("checkout_success.html")
# ---------------------------------------------------------------------------------------------------------------
# admin
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "eishvaish" and password == "1234":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin/admin_login.html", message="Invalid credentials")

    return render_template("admin/admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    return render_template("admin/admin.html")



# this needs debugging 
@app.route("/admin/orders")
def admin_orders():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    cursor.execute("SELECT order_id, user_id, disease, medicine, order_date, order_status FROM orders")
    orders = cursor.fetchall()

    def get_user_name(user_id):
        cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return user[0] if user else "Unknown"

    orders = [
        {
            "order_id": row[0],
            "user_name": get_user_name(row[1]),
            "disease": row[2],
            "medicine": row[3],
            "order_date": row[4],
            "order_status": row[5],
        }
        for row in orders
    ]

    print("Fetched Orders:", orders) #debug+
    return render_template("admin/orders.html", orders=orders)

@app.route("/admin/medicines")
def admin_medicines():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()
    return render_template("admin/medicines.html", medicines=medicines)

@app.route('/admin/update_medicine', methods=['POST'])
def update_medicine():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    medicine_id = request.form.get("medicine_id")
    medicine_name = request.form.get("medicine_name")
    disease = request.form.get("disease")
    price = request.form.get("price")
    stock = request.form.get("stock")

    if medicine_id and medicine_name and disease and price and stock:
        cursor.execute(
            "UPDATE medicines SET name=%s, disease=%s, price=%s, stock=%s WHERE id=%s",
            (medicine_name, disease, price, stock, medicine_id)
        )
        db.commit()

    return redirect(url_for("admin_medicines"))   

@app.route('/admin/add_medicine', methods=['POST'])
def add_medicine():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    medicine_name = request.form.get("medicine_name")
    disease = request.form.get("disease")
    price = request.form.get("price")
    stock = request.form.get("stock")

    if medicine_name and disease and price and stock:
        try:
            cursor.execute(
                "INSERT INTO medicines (name, disease, price, stock) VALUES (%s, %s, %s, %s)",
                (medicine_name, disease, price, stock),
            )
            db.commit()
            message = "Medicine added successfully!"
        except Exception as e:
            db.rollback()
            message = f"Error adding medicine: {str(e)}"
    else:
        message = "All fields are required."

    return redirect(url_for("admin_medicines"))


@app.route('/admin/delete_medicine', methods=['POST'])
def delete_medicine():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    medicine_id = request.form.get("medicine_id")

    if medicine_id:
        try:
            cursor.execute("DELETE FROM medicines WHERE id = %s", (medicine_id,))
            db.commit()
            message = "Medicine deleted successfully!"
        except Exception as e:
            db.rollback()
            message = f"Error deleting medicine: {str(e)}"
    else:
        message = "Invalid medicine ID."

    return redirect(url_for("admin_medicines"))

@app.route('/admin/update_order_status', methods=['POST'])
def update_order_status():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    order_id = request.form.get("order_id")
    new_status = request.form.get("new_status")

    if order_id and new_status:
        try:
            cursor.execute("UPDATE orders SET order_status = %s WHERE order_id = %s", (new_status, order_id))
            db.commit()
            print(f"order {order_id} updated to {new_status}") #debug shit
        except MySQLdb.Error as e:
            db.rollback()
            print(f"Error updating order: {e}")

    return redirect(url_for("admin_orders"))


@app.route("/admin/users")
def admin_users():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()

    return render_template("admin/users.html", users=users)

@app.route("/admin/doctors")
def admin_doctors():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    return render_template("admin/doctors.html", doctors=doctors)


@app.route("/admin/add_doctor", methods=["POST"])
def add_doctor():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    name = request.form["name"]
    specialization = request.form["specialization"]
    email = request.form["email"]
    contact = request.form["contact"]
    availability = request.form["availability"]
    
    cursor.execute("INSERT INTO doctors (name, specialization, email, contact, availability) VALUES (%s, %s, %s, %s, %s)", 
                   (name, specialization, email, contact, availability))
    db.commit()
    
    return redirect(url_for("admin_doctors"))


@app.route("/admin/update_doctor", methods=["POST"])
def update_doctor():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    doctor_id = request.form["doctor_id"]
    name = request.form["name"]
    specialization = request.form["specialization"]
    email = request.form["email"]
    contact = request.form["contact"]
    availability = request.form["availability"]
    
    cursor.execute("UPDATE doctors SET name=%s, specialization=%s, email=%s, contact=%s, availability=%s WHERE id=%s", 
                   (name, specialization, email, contact, availability, doctor_id))
    db.commit()
    
    return redirect(url_for("admin_doctors"))
@app.route("/admin/delete_doctor", methods=["POST"])
def delete_doctor():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    doctor_id = request.form["doctor_id"]

    cursor.execute("DELETE FROM doctors WHERE id = %s", (doctor_id,))
    db.commit()

    return redirect(url_for("admin_doctors"))



@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))



if __name__ == '__main__':
    app.run(debug=True)

