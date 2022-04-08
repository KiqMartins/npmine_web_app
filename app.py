# import the Flask class from the flask module
from flask import Flask, render_template

# create the application object
app = Flask(__name__)

# use decorators to link the function to a url
@app.route('/index')
def index():
    return render_template('index.html')  

@app.route('/login')
def login():
    return render_template('login.html') 

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)