# required imports; you may add more in the future
from flask import Flask, render_template, request

# tells Flask that "this" is the current running app
app = Flask(__name__)

# the todo list
# we will store the todos in this list
todo_list = []

# setup the default route
# this is the page the site will load by default (i.e. like the home page)
@app.route('/')
def root():
    """
    TODO: complete the logic to render the main index.html page
    """
    return None

@app.route('/add')
def add_todo():
    """
    TODO: complete the logic to add a new TODO to the list
    """
    global todo_list    # access the todo_list variable above

    # HINT: use request.args.get('') to get the <input></input> fields inside your <form></form> element
    # this function will return the value in the attribute "name"
    return None

# run the app when app.py is run
if __name__ == '__main__':
    # we set debug=True so you don't have to restart the app everything you make changes
    # just refresh the browser after each change
    app.run(debug=True)