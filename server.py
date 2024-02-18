import json
import os
from os import environ as env
import urllib.parse
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from werkzeug.utils import secure_filename
from flask import Flask, redirect, render_template, session, url_for, request, send_from_directory

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
# app.config["IMAGE_UPLOADS"] = "C:/Flask/Upload/"
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

# def search(category):
#     clothes = {('a', 'Socks'), ('b', 'Mittens'), ('c', 'Boots'), ('d', 'Jacket'), ('e', 'Winter Hat')}
#     lstOfClothes = []
#     for i in clothes:
#         if i[1] == category:
#             lstOfClothes.append(i)

#     return render_template("browse.html", clothes = lstOfClothes)

@app.route("/")
def root():
    return render_template("index.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/browse")
def browse():
    # category = request.form['clothing_id']
    # data_received = []
    data = [('a', 'Socks'), ('b', 'Mittens'), ('c', 'Boots'), ('d', 'Jacket'), ('e', 'Winter Hat')]
    
    # for item in data:
    #     if item[1] == category:
    #         data_received.append(item)

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
        return render_template('donate.html', error="No file selected", droplst=droplst)

    file = request.files['file']
    if file.filename == '':
        return render_template('donate.html', error="No file selected", droplst=droplst)

    if file:
        # Save the uploaded file to the UPLOAD_FOLDER
        selected_file = request.form['file-upload']
        if selected_file in droplst:
            selected_file = secure_filename(selected_file)
            filename = file.filename
            new_filename = selected_file + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

            # Rename the file
            os.rename(os.path.join(app.config['UPLOAD_FOLDER'], new_filename), os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return render_template('donate.html', filename=file.filename, droplst=droplst)


@app.route('/uploads/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))