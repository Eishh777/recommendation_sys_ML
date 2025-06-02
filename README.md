# recommendation_sys_ML
Machine Learning project with frontend in python (flask)
# Features
# Machine Learning
Predicts diseases from symptoms using a trained Support Vector Classifier (SVC).

Utilizes datasets like symptoms_df, medications.csv, workout_df.csv, etc.

Provides detailed disease description, precautions, medications, diet, and workout suggestions.

# User System
Register/login with password hashing using Werkzeug.

Profile management with update functionality.

Generates downloadable PDF health reports.

# E-Commerce
Shop for medicines related to predicted diseases.

Add-to-cart, update quantity, and checkout functionality.

View order history (admin side) and payment simulation.

# Doctor Consultation
List of doctors with specialization, contact info, and availability.

Admin can manage doctors (CRUD operations).

# Admin Dashboard
Login-protected admin panel.

Manage users, medicines, doctors, and orders.

Update order status and stock inventory.

# AI Chatbot
Chat with a healthcare assistant powered by Google Gemini API.

| Tech           | Description                                |
| ---------------| ------------------------------------------ |
| Flask          | Python web framework                       |
| MySQL          | Database to store users, orders, medicines |
| SVC (ML)       | Model for disease prediction               |
| Pandas & Numpy | Data handling and preprocessing            |
| ReportLab      | PDF report generation                      |
| Google Gemini  | Chatbot integration                        |
| HTML/CSS/JS    | Frontend rendering via Jinja templates     |


# Database setup
MySQL DB: disease_db
Create tables: users, medicines, orders, doctors, cart.
