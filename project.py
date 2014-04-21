import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect('tax.db')
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
	return render_template("select.html")

@app.route("/add_employee", methods=['POST','GET'])
def add_employee():
	db = get_db()
	if request.method == 'POST':
		#Gather all Parameters
		FirstName = str(request.form['FirstName'])
		LastName = str(request.form['LastName'])
		Address = str(request.form['Address'])
		City = str(request.form['City'])
		State = str(request.form['State'])
		ZipCode = int(request.form['ZipCode'])
		City = str(request.form['City'])
		Benefits = str(request.form['Benefits'])
		JobTitle = str(request.form['JobTitle'])
		FedTaxRate = float(request.form['FedTaxRate'])
		#Insert Address
		db.execute('INSERT INTO address (Street, City, State, ZipCode) VALUES (?, ?, ?, ?)', [Address, City, State, ZipCode])
		db.commit()
		AddressID = db.execute('select last_insert_rowid();').fetchone()[0]
	titles = db.execute('select * from job_title').fetchall()
	return render_template("add_employee.html", titles=titles)

#Employee Stuff
@app.route("/update_employee", methods=['POST', 'GET'])
def update_employee():
	return 

@app.route("/update_employee_benefits", methods=['POST', 'GET'])
def update_employee_benefits():
	return

@app.route("/view_employee", methods=['GET', 'POST'])
def view_employee():
	return

@app.route("/add_job_title", methods=['POST', 'GET'])
def add_job_title():
	db = get_db()
	if request.method == 'POST':
		Title = str(request.form['Title'])
		Salary = int(request.form['Salary'])
		db.execute('insert into job_title (JobTitleName, JobTitleSalary) values (?, ?)',[Title, Salary])
		db.commit()
	return render_template("add_job_title.html")

@app.route("/employee_payroll", methods=['POST', 'GET'])
def employee_payroll():
	return 

#Insurance Stuff
@app.route("/add_life_insurance", methods=['POST', 'GET'])
def add_life_insurance():
	db = get_db()
	if request.method == 'POST':
		Name = str(request.form['Name']
		Desc = str(request.form['Description']
		Amt = str(request.form['Amount']
		pMonth = str(request.form['PerMonth']
		
		#Insert Company First Then the rest of the Info
		db.execute('INSERT INTO insurance_company (Name) values (?)',[Name])
		db.commit()		
	return render_template("add_life_insurance.html")

@app.route("/add_health_insurance", methods=['POST', 'GET'])
def add_health_insurance():
	return

@app.route("/add_disability_plan", methods=['POST', 'GET'])
def add_disability_plan():
	return

@app.route("/add_401k_plan", methods=['POST', 'GET'])
def add_401k_plan():
	return

@app.route("/generate_w2", methods=['POST', 'GET'])
def generate_w2():
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
