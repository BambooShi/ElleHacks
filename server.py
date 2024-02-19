import json
import os
from os import environ as env
from urllib.parse import quote_plus, urlencode
import uuid

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from werkzeug.utils import secure_filename
from flask import Flask, redirect, render_template, session, url_for, request, send_from_directory, jsonify

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
# app.config["IMAGE_UPLOADS"] = "C:/Flask/Upload/"
app.secret_key = env.get("APP_SECRET_KEY")

STATIC_FOLDER = 'static'
app.config['STATIC_FOLDER'] = STATIC_FOLDER

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/")
def root():
    return render_template("index.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/browse", methods=["GET"])
def browse():
    droplst = ['Winter Hat', 'Jacket', 'Snowpants', 'Boots', 'Mittens', 'Gloves', 'Socks', 'Scarfs', 'Ear Muffs', 'Sweater', 'Other']
    
    return render_template("browse.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4), droplst=droplst)


@app.route("/donate")
def about():
    droplst = ['Winter Hat', 'Jacket', 'Snowpants', 'Boots', 'Mittens', 'Gloves', 'Socks', 'Scarfs', 'Ear Muffs', 'Sweater', 'Other']
    return render_template("donate.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4), droplst = droplst)

@app.route("/user")
def account():
    return render_template("user.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("root", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    droplst = ['Winter Hat', 'Jacket', 'Snowpants', 'Boots', 'Mittens', 'Gloves', 'Socks', 'Scarfs', 'Ear Muffs', 'Sweater', 'Other']
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Save the uploaded file to the UPLOAD_FOLDER
        selected_file = request.form['file-upload']
        if selected_file in droplst:
            # selected_file = secure_filename(selected_file)
            filename = secure_filename(file.filename)
            
            if '.' not in file.filename:
                filename = filename + '.jpg'  # You can modify the extension as needed

            new_filename = str(uuid.uuid4()) + secure_filename(file.filename) 
            # Create a subfolder with the same name as the ID if it doesn't exist
            subfolder_path = os.path.join(app.config['STATIC_FOLDER'], 'uploads', selected_file)
            os.makedirs(subfolder_path, exist_ok=True)
            
            # Save the file into the subfolder
            file.save(os.path.join(subfolder_path, new_filename))

        return render_template('donate.html', filename=new_filename, selected_file = selected_file, droplst=droplst)


@app.route('/uploads/<filename>')
def display_image(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], 'uploads', filename)

@app.route('/get_images/<category>')
def get_images(category):
    folder_path = os.path.join(app.config['STATIC_FOLDER'], "uploads", category)

    if not os.path.exists(folder_path):
        return jsonify(images=[])

    files = os.listdir(folder_path)
    image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    return jsonify(images=image_files)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))