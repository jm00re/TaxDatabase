import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect('test.db')
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/", methods=['GET'])
def select():
	db = get_db()
	#bottom = request.args.get('min','')
	#top = request.args.get('max','')
	#cur = db.execute('select * from first where salary between ? and ?', [bottom, top])
	#entries = cur.fetchall()
	return render_template("display.html")

@app.route("/add_employee", methods=['POST'])
def add_employee():
	return

@app.route("/update_employee", methods=['POST'])
def update_employee():
	return

@app.route("/view_employee", methods=['GET'])
def view_employee():
	return

@app.route("/employee_payroll", methods=['POST'])
def employee_payroll():
	return

@app.route("/add_insurance", methods=['POST'])
def add_insurance():
	return


#@app.route('/add', methods=['POST'])
#def update():
#	db = get_db()
#	n = request.form['name']
#	s = int(request.form['salary'])
#	db.execute('insert into first (NAME, SALARY) values (?, ?)', [n, s])
#	db.commit()
#	return redirect(url_for('show'))

if __name__ == "__main__":
    app.run(debug=True)
