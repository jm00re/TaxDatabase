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
		add_addres = 'INSERT INTO address (Street, City, State, ZipCode) VALUES (?, ?, ?, ?)'
		db.execute(add_addres, [Address, City, State, ZipCode])
		db.commit()
		AddressID = db.execute('SELECT last_insert_rowid();').fetchone()[0]
		#Insert Tax Witholding
		db.execute('INSERT INTO Withholding (Description) VALUES (?)',[Withholding])
		db.commit()
		WithholdingID = db.execute('SELECT last_insert_rowid();').fetchone()[0]
		#Insert Fed Tax
		add_fed = 'INSERT INTO fed_tax_rate (FedTaxRate, Upperlimit, WithholdingID) VALUES (?,?,?)'
		db.execute(add_fed, [FedTaxRate, Upperlimit, WithholdingID])
		db.commit()
		FedTaxRateID = db.execute('SELECT last_insert_rowid();').fetchone()[0]
		#Add Employee Benefits
		PlanID = str(request.form['401kPlan'])
		DisIns = str(request.form['DisIns'])
		LifeIns = str(request.form['LifeIns'])
		HealthIns = str(request.form['HealthIns'])
		Status = str(request.form['Status'])
		empben_qry = "INSERT INTO employee_benefits ([401kPlanID], DisabilityPlanID, LifeInsPlanID, HealthInsPlanID, FilingStatus) VALUES (?, ?, ?, ?, ?)"
		db.execute(empben_qry, [PlanID, DisIns, LifeIns, HealthIns, Status])
		db.commit()
		EmployeeBenefitsID = db.execute('SELECT last_insert_rowid();').fetchone()[0]
	    #Add Employee
		emp_qry = 'INSERT INTO employee (FirstName, LastName, AddressID, JobTitleID, FedTaxRateID, EmployeeBenefitsID) values (?, ?, ?, ?, ?, ?)'
		db.execute(emp_qry, [FirstName, LastName, AddressID, JobTitleID, FedTaxRateID, EmployeeBenefitsID])
		db.commit()
	titles = db.execute('select * from job_title').fetchall()
	plan = db.execute('select * from [401k_plan]').fetchall()
	print plan
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
			print emp[1]
			#print AddressID
			#print JobTitleID
			#print FedTaxRateID
			#print BenefitsID
			address_qry = 'SELECT * FROM address WHERE AddressID=?'
			job_qry = 'SELECT * FROM job_title WHERE JobTitleID=?'
			fed_qry = 'SELECT * FROM fed_tax_rate WHERE FedTaxRateID=?'
			ben_qry = 'SELECT * FROM employee_benefits WHERE EmployeeBenefitsID=?'
			address = db.execute(address_qry, [AddressID]).fetchall()
			jobtitle = db.execute(job_qry,[JobTitleID]).fetchall()
			fed = db.execute(fed_qry,[FedTaxRateID]).fetchall()
			ben = db.execute(ben_qry,[BenefitsID]).fetchall()
			#print ben
			for b in ben:
				k_id = emp[1]
				dis_id = emp[2]
				life_id = emp[3]
				health_id = emp[4]
				print k_id
				print dis_id
				print life_id
				print health_id
				k_qry =	'SELECT * FROM [401k_plan] WHERE [401kPlanID]=?'
				dis_qry = 'SELECT * FROM disability_plan WHERE DisabilityPlanID=?'
				life_qry = 'SELECT * FROM life_insurance_plan WHERE LifeInsPlanID=?'
				health_qry = 'SELECT * FROM health_insurance_plan WHERE HealthInsPlanID=?'
				kplan = db.execute(k_qry, [k_id]).fetchall()
				displan = db.execute(dis_qry, [dis_id]).fetchall()
				lifeplan = db.execute(life_qry, [life_id]).fetchall()
				healthplan = db.execute(health_qry, [health_id]).fetchall()
				print kplan
				print displan
				print lifeplan
				print healthplan
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
