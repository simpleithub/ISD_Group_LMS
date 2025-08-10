from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure secret key for session management

# File paths
USERS_FILE = "data/users.txt"
CONTACT_FILE = "data/contact.txt"

# Ensure data directory exists
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
os.makedirs(os.path.dirname(CONTACT_FILE), exist_ok=True)

def init_data_files():
    """Initialize data files if they don't exist"""
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, 'a').close()
    if not os.path.exists(CONTACT_FILE):
        open(CONTACT_FILE, 'a').close()

@app.route("/", methods=["GET", "POST"])
def landing():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Simple user authentication
        with open(USERS_FILE, "r") as f:
            users = [line.strip().split(",") for line in f.readlines()]
            
        user = next((u for u in users if u[0] == username), None)
        
        if user and check_password_hash(user[1], password):
            session['username'] = username
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")
            
    return render_template("landing.html")

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]
    
    # Check if username already exists
    with open(USERS_FILE, "r") as f:
        if any(line.startswith(f"{username},") for line in f):
            flash("Username already exists", "error")
            return redirect(url_for("landing"))
    
    # Hash password before storing
    hashed_password = generate_password_hash(password)
    
    with open(USERS_FILE, "a") as f:
        f.write(f"{username},{hashed_password}\n")
    
    session['username'] = username
    return redirect(url_for("home"))

@app.route("/home")
def home():
    if 'username' not in session:
        return redirect(url_for("landing"))
    return render_template("home.html")

@app.route("/contact", methods=["POST"])
def contact():
    if 'username' not in session:
        return redirect(url_for("landing"))
        
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]
    
    # Basic input validation
    if not all([name, email, message]):
        flash("All fields are required", "error")
        return redirect(url_for("home"))
    
    # Store contact message
    with open(CONTACT_FILE, "a") as f:
        f.write(f"{name},{email},{message}\n")
    
    flash("Message sent successfully!", "success")
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("landing"))

if __name__ == "__main__":
    init_data_files()
    app.run(debug=True)
