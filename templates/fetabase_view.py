from flask import Flask, render_template, session, flash, redirect, url_for, request, g
import model
import jinja2
 
 
app = Flask(__name__) 
app.secret_key = ')V\xaf\xdb\x9e\xf7k\xccm\x1f\xec\x13\x7fc\xc5\xfe\xb0\x1dc\xf9\xcfz\x92\xe8'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route('/')
def index():
    print session

    return render_template("index.html")


if __name__ == "__main__":
	app.debug = True
	app.run()