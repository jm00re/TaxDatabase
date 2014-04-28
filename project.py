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
	#	#Benefits = str(request.form['Benefits'])
		JobTitleID = int(request.form['JobTitle'])
		FedTaxRate = float(request.form['FedTaxRate'])
		Upperlimit = int(request.form['Upperlimit'])
		Withholding = str(request.form['Withholding'])
		#Insert Address
		db.execute('INSERT INTO address (Street, City, State, ZipCode) VALUES (?, ?, ?, ?)', [Address, City, State, ZipCode])
		db.commit()
		AddressID = db.execute('select last_insert_rowid();').fetchone()[0]
		#Insert Tax Witholding
		db.execute('insert into withholding (Description) values (?)',[Withholding])
		db.commit()
		WithholdingID = db.execute('select last_insert_rowid();').fetchone()[0]
		#Insert Fed Tax
		db.execute('insert into fed_tax_rate (FedTaxRate, Upperlimit, WithholdingID) VALUES (?,?,?)', [FedTaxRate, Upperlimit, WithholdingID])
		db.commit()
		FedTaxRateID = db.execute('select last_insert_rowid();').fetchone()[0]
	   #Add Employee
		db.execute('INSERT INTO employee (FirstName, LastName, AddressID, JobTitleID, FedTaxRateID) values (?, ?, ?, ?, ?)', [FirstName, LastName, AddressID, JobTitleID, FedTaxRateID])
		db.commit()
	titles = db.execute('select * from job_title').fetchall()
	plan = db.execute('select * from [401k_plan]').fetchall()
	life = db.execute('select * from life_insurance_plan').fetchall()
	health = db.execute('select * from health_insurance_plan').fetchall()
	dis = db.execute('select * from disability_plan').fetchall()
	return render_template("add_employee.html", titles=titles, plans=plan, LifeInsurance=life, HealthInsurance=health, DisInsurance=dis) 

#Employee Stuff
@app.route("/update_employee", methods=['POST', 'GET'])
def update_employee():
	return 

@app.route("/update_employee_benefits", methods=['POST', 'GET'])
def update_employee_benefits():
	return

@app.route("/view_employee", methods=['GET', 'POST'])
def view_employee():
	db = get_db()
	if request.method == 'GET':
		match = request.args.get('match','').lower()
		cur = db.execute('SELECT LastName FROM employee')
		emp_qry = 'SELECT * FROM employee WHERE LastName LIKE ? OR LastName LIKE ? OR LastName LIKE ? OR LastName LIKE ?'
		cur = db.execute(emp_qry, ['%'+match, match+'%', '%'+match+'%', match])
		emp_list = cur.fetchall()
		for emp in emp_list:
			AddressID = emp[3]
			JobTitleID = emp[4]
			FedTaxRateID = emp[5]
			BenefitsID = emp[6]
			print AddressID
			print JobTitleID
			print FedTaxRateID
			print BenefitsID
			address_qry = 'SELECT * FROM address WHERE AddressID=?'
			job_qry = 'SELECT * FROM job_title WHERE JobTitleID=?'
			fed_qry = 'SELECT * FROM fed_tax_rate WHERE FedTaxRateID=?'
			ben_qry = 'SELECT * FROM employee_benefits WHERE EmployeeBenefitsID=?'
			address = db.execute(address_qry, [AddressID])
			jobtitle = db.execute(job_qry,[JobTitleID])
			fed = db.execute(fed_qry,[FedTaxRateID])
			ben = db.execute(ben_qry,[BenefitsID])
			#for b in ben:
				
		print cur.fetchall()
	return render_template("view_employee.html") 

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
		Name = str(request.form['Name'])
		Desc = str(request.form['Description'])
		Amt = str(request.form['Amount'])
		pMonth = float(request.form['PerMonth'])
		#Insert Company First Then the rest of the Info
		db.execute('INSERT INTO insurance_company (InsuranceName) values (?)',[Name])
		db.commit()	
		insuranceID = db.execute('select last_insert_rowid();').fetchone()[0]
		db.execute('INSERT INTO life_insurance_plan (InsuranceCoID,LifeInsDescription,LifeInsAmt,CostPerMonthLifeIns) values (?,?,?,?)',[insuranceID, Desc, Amt, pMonth])
		db.commit()
	return render_template("add_life_insurance.html")

@app.route("/add_health_insurance", methods=['POST', 'GET'])
def add_health_insurance():
	db = get_db()
	if request.method == 'POST':
		Name = str(request.form['Name'])
		Desc = str(request.form['Description'])
		FRate = float(request.form['FRate'])
		SRate = float(request.form['SRate'])
		pMonth = float(request.form['CostPM'])
		#Insert Company First 
		db.execute('INSERT INTO insurance_company (InsuranceName) values (?)',[Name])
		db.commit()	
		insuranceID = db.execute('select last_insert_rowid();').fetchone()[0]
		db.execute('INSERT INTO health_insurance_plan (InsuranceCoID,InsPlanDescription,FamilyRate,SingleRate,CostPerMonthHealthIns) values (?,?,?,?,?)',[insuranceID, Desc, FRate,SRate,pMonth])
		db.commit()
	return render_template("add_health_insurance.html")

@app.route("/add_disability_plan", methods=['POST', 'GET'])
def add_disability_plan():
	db = get_db()
	if request.method == 'POST':
		Name = str(request.form['Name'])
		Desc = str(request.form['Description'])
		pMonth = float(request.form['PerMonth'])
		
		#Insert Company first
		db.execute('INSERT INTO insurance_company (InsuranceName) values (?)',[Name])
		db.commit()
		insuranceID = db.execute('select last_insert_rowid();').fetchone()[0]
		db.execute('INSERT INTO disability_plan (DisabilityPlanDescription, CostPerMonthDisability) values (?,?)',[Desc,pMonth])
		db.commit()
	return render_template("add_disability_plan.html")

@app.route("/add_401k_plan", methods=['POST', 'GET'])
def add_401k_plan():
	db = get_db()
	if request.method == 'POST':
		Name = str(request.form['Name'])
		Desc = str(request.form['Description'])
		pSalary = float(request.form['Percent'])
		
		#Insert Company first
		db.execute('INSERT INTO insurance_company (InsuranceName) values (?)',[Name])
		db.commit()
		insuranceID = db.execute('select last_insert_rowid();').fetchone()[0]
		db.execute('INSERT INTO [401k_plan] ([401kPlanDescription],[401kPercentOfSalary]) values (?,?)',[Desc,pSalary])
		db.commit()
	return render_template("add_401k_plan.html")

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
