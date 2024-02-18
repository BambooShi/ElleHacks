import json
import os
from os import environ as env
import urllib.parse
from urllib.parse import quote_plus, urlencode
import uuid

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from werkzeug.utils import secure_filename
from flask import Flask, redirect, render_template, session, url_for, request, send_from_directory

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route("/browse", method=["GET"])
def browse():
    # category = request.form['clothing_id']
    # data_received = []
    # data = [('a', 'Socks'), ('b', 'Mittens'), ('c', 'Boots'), ('d', 'Jacket'), ('e', 'Winter Hat')]
    # for item in data:
    #     if item[1] == category:
    #         data_received.append(item)

    try:
        category = request.args['clothing_id']
    except KeyError:
        # Handle the case when 'clothing_id' is not present in the request
        return "Bad Request: 'clothing_id' parameter is missing", 400

    upload_folder = "\uploads"
    category_folder = os.path.join(upload_folder, category)
    files = os.listdir(category_folder)

    droplst = ['Winter Hat', 'Jacket', 'Snowpants', 'Boots', 'Mittens', 'Gloves', 'Socks', 'Scarfs', 'Ear Muffs', 'Sweater', 'Other']
    
    return render_template("browse.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4), droplst=droplst, clothes=data)


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
            subfolder_path = os.path.join(app.config['UPLOAD_FOLDER'], selected_file)
            os.makedirs(subfolder_path, exist_ok=True)
            
            # Save the file into the subfolder
            file.save(os.path.join(subfolder_path, new_filename))

            # Rename the file
            # os.rename(os.path.join(app.config['UPLOAD_FOLDER'], new_filename), os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return render_template('donate.html', filename=file.filename, droplst=droplst)


@app.route('/uploads/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))