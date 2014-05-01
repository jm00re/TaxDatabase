import os
import pprint
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
	life = db.execute('select * from life_insurance_plan').fetchall()
	health = db.execute('select * from health_insurance_plan').fetchall()
	dis = db.execute('select * from disability_plan').fetchall()
	return render_template("add_employee.html", titles=titles, plans=plan, LifeInsurance=life, HealthInsurance=health, DisInsurance=dis) 

#Employee Stuff
@app.route("/update_employee", methods=['POST', 'GET'])
def update_employee():
	db = get_db()
	employee_display_list = []
	if request.method == 'GET' and not request.args.get('match','') == '':
		match = request.args.get('match','').lower()
		cur = db.execute('SELECT LastName FROM employee')
		emp_qry = 'SELECT * FROM employee WHERE LastName LIKE ? OR LastName LIKE ? OR LastName LIKE ? OR LastName LIKE ?'
		cur = db.execute(emp_qry, ['%'+match, match+'%', '%'+match+'%', match])
		emp_list = cur.fetchall()
		for emp in emp_list:
			disp_emp = [] 
			AddressID = emp[3]
			JobTitleID = emp[4]
			FedTaxRateID = emp[5]
			BenefitsID = emp[6]
			#Append everything to e_d_l
			address_qry = 'SELECT * FROM address WHERE AddressID=?'
			job_qry = 'SELECT * FROM job_title WHERE JobTitleID=?'
			fed_qry = 'SELECT * FROM fed_tax_rate WHERE FedTaxRateID=?'
			ben_qry = 'SELECT * FROM employee_benefits WHERE EmployeeBenefitsID=?'
			address = db.execute(address_qry, [AddressID]).fetchone()
			jobtitle = db.execute(job_qry,[JobTitleID]).fetchone()
			fed = db.execute(fed_qry,[FedTaxRateID]).fetchone()
			ben = db.execute(ben_qry,[BenefitsID]).fetchall()
			#Emp ID, Add First and Last Name
			#Emp ID
			disp_emp.append(emp[0])
			#First Name
			disp_emp.append(emp[1])
			#Last NAme
			disp_emp.append(emp[2])
			#Address 
			#Number+Street
			disp_emp.append(address[1])
			#City
			disp_emp.append(address[2])
			#State
			disp_emp.append(address[3])
			#Zip
			disp_emp.append(address[4])
			#Job Title
			disp_emp.append(jobtitle[1])
			#Salary
			#disp_emp.append(jobtitle[2])
			b = ben[0]
			#status
			disp_emp.append(b[5])
			#for b in ben:
			k_id = b[1]
			dis_id = b[2]
			life_id = b[3]
			health_id = b[4]
			k_qry =	'SELECT * FROM [401k_plan] WHERE [401kPlanID]=?'
			dis_qry = 'SELECT * FROM disability_plan WHERE DisabilityPlanID=?'
			life_qry = 'SELECT * FROM life_insurance_plan WHERE LifeInsPlanID=?'
			health_qry = 'SELECT * FROM health_insurance_plan WHERE HealthInsPlanID=?'
			kplan = db.execute(k_qry, [k_id]).fetchone()
			displan = db.execute(dis_qry, [dis_id]).fetchone()
			lifeplan = db.execute(life_qry, [life_id]).fetchone()
			healthplan = db.execute(health_qry, [health_id]).fetchone()
			ins_qry = 'SELECT * from insurance_company where InsuranceCoID=?'
			k_ins = db.execute(ins_qry, [kplan[1]]).fetchone()
			dis_ins = db.execute(ins_qry, [displan[1]]).fetchone()
			life_ins = db.execute(ins_qry, [lifeplan[1]]).fetchone()
			health_ins = db.execute(ins_qry, [healthplan[1]]).fetchone()
			#Append ins info to list
			disp_emp.append(healthplan[0])
			disp_emp.append(lifeplan[0])
			disp_emp.append(displan[0])
			disp_emp.append(kplan[0])
			#disp_emp.append(health_ins)
			disp_emp.append(fed[3])
			disp_emp.append(fed[1])
			desc = db.execute('select * from Withholding where WithholdingID=?', [fed[2]])
			desc = desc.fetchone()[1]
			disp_emp.append(desc)
			disp_emp.append(emp[0])
			employee_display_list.append(disp_emp)
	if request.method == 'POST':
	#if request.method == 'POST':
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
		PlanID = str(request.form['401kPlan'])
		DisIns = str(request.form['DisIns'])
		LifeIns = str(request.form['LifeIns'])
		HealthIns = str(request.form['HealthIns'])
		Status = str(request.form['Status'])
		ID = int(request.form['ID'])
		#Update Employee
		update_name_qry = 'update employee set FirstName=?, LastName=?, JobTitleID=? where EmployeeID=?'
		db.execute(update_name_qry, [FirstName, LastName, JobTitleID, ID])
		db.commit()
		#Update Address
		employee_qry = 'Select * from employee where EmployeeID=?'
		employee = db.execute(employee_qry, [ID]).fetchone()
		print employee
		address_id = employee[3]
		add_addres = 'UPDATE address SET Street=?, City=?, State=?, ZipCode=? WHERE AddressID=?'
		db.execute(add_addres, [Address, City, State, ZipCode, address_id])
		db.commit()
		#Update Benefits
		emp_ben_id=employee[6]
		emp_ben_qry = 'update employee_benefits set [401kPlanID]=?, DisabilityPlanID=?, LifeInsPlanID=?, HealthInsPlanID=?, FilingStatus=? where EmployeeBenefitsID=?'
		db.execute(emp_ben_qry, [PlanID, DisIns, LifeIns, HealthIns, Status, emp_ben_id]).fetchone()
		#Update Tax
		temp = employee[5]
		tax_id_qry = "select * from fed_tax_rate where FedTaxRateID=?"
		fed_tax = db.execute(tax_id_qry, [temp]).fetchone()
		with_id=fed_tax[2]
		fed_tax_update = 'update fed_tax_rate set Upperlimit=?, FedTaxRate=? where FedTaxRateID=?'
		if FedTaxRate > fed_tax[3]:
			db.execute(fed_tax_update, [Upperlimit, FedTaxRate, temp])
			db.commit()
		withholding_qry = "update withholding set Description=? where WithholdingID=?"
		db.execute(withholding_qry, [Withholding, with_id])
		db.commit()
	titles = db.execute('select * from job_title').fetchall()
	plan = db.execute('select * from [401k_plan]').fetchall()
	life = db.execute('select * from life_insurance_plan').fetchall()
	health = db.execute('select * from health_insurance_plan').fetchall()
	dis = db.execute('select * from disability_plan').fetchall()
	return render_template("update_employee.html", titles=titles, plans=plan, LifeInsurance=life, HealthInsurance=health, DisInsurance=dis, emps=employee_display_list) 

@app.route("/view_employee", methods=['GET', 'POST'])
def view_employee():
	db = get_db()
	employee_display_list = []
	if request.method == 'GET' and not request.args.get('match','') == '':
		match = request.args.get('match','').lower()
		cur = db.execute('SELECT LastName FROM employee')
		emp_qry = 'SELECT * FROM employee WHERE LastName LIKE ? OR LastName LIKE ? OR LastName LIKE ? OR LastName LIKE ?'
		cur = db.execute(emp_qry, ['%'+match, match+'%', '%'+match+'%', match])
		emp_list = cur.fetchall()
		for emp in emp_list:
			disp_emp = [] 
			AddressID = emp[3]
			JobTitleID = emp[4]
			FedTaxRateID = emp[5]
			BenefitsID = emp[6]
			#Append everything to e_d_l
			address_qry = 'SELECT * FROM address WHERE AddressID=?'
			job_qry = 'SELECT * FROM job_title WHERE JobTitleID=?'
			fed_qry = 'SELECT * FROM fed_tax_rate WHERE FedTaxRateID=?'
			ben_qry = 'SELECT * FROM employee_benefits WHERE EmployeeBenefitsID=?'
			address = db.execute(address_qry, [AddressID]).fetchone()
			jobtitle = db.execute(job_qry,[JobTitleID]).fetchone()
			fed = db.execute(fed_qry,[FedTaxRateID]).fetchone()
			ben = db.execute(ben_qry,[BenefitsID]).fetchall()
			#Emp ID, Add First and Last Name
			#Emp ID
			disp_emp.append(emp[0])
			#First Name
			disp_emp.append(emp[1])
			#Last NAme
			disp_emp.append(emp[2])
			#Address 
			#Number+Street
			disp_emp.append(address[1])
			#City
			disp_emp.append(address[2])
			#State
			disp_emp.append(address[3])
			#Zip
			disp_emp.append(address[4])
			#Job Title
			disp_emp.append(jobtitle[1])
			#Salary
			#disp_emp.append(jobtitle[2])
			b = ben[0]
			#status
			disp_emp.append(b[5])
			#for b in ben:
			k_id = b[1]
			dis_id = b[2]
			life_id = b[3]
			health_id = b[4]
			k_qry =	'SELECT * FROM [401k_plan] WHERE [401kPlanID]=?'
			dis_qry = 'SELECT * FROM disability_plan WHERE DisabilityPlanID=?'
			life_qry = 'SELECT * FROM life_insurance_plan WHERE LifeInsPlanID=?'
			health_qry = 'SELECT * FROM health_insurance_plan WHERE HealthInsPlanID=?'
			kplan = db.execute(k_qry, [k_id]).fetchone()
			displan = db.execute(dis_qry, [dis_id]).fetchone()
			lifeplan = db.execute(life_qry, [life_id]).fetchone()
			healthplan = db.execute(health_qry, [health_id]).fetchone()
			ins_qry = 'SELECT * from insurance_company where InsuranceCoID=?'
			k_ins = db.execute(ins_qry, [kplan[1]]).fetchone()
			dis_ins = db.execute(ins_qry, [displan[1]]).fetchone()
			life_ins = db.execute(ins_qry, [lifeplan[1]]).fetchone()
			health_ins = db.execute(ins_qry, [healthplan[1]]).fetchone()
			#Append ins info to list
			disp_emp.append(healthplan[0])
			disp_emp.append(lifeplan[0])
			disp_emp.append(displan[0])
			disp_emp.append(kplan[0])
			#disp_emp.append(health_ins)
			disp_emp.append(fed[3])
			disp_emp.append(fed[1])
			desc = db.execute('select * from Withholding where WithholdingID=?', [fed[2]])
			desc = desc.fetchone()[1]
			disp_emp.append(desc)
			disp_emp.append(emp[0])
			employee_display_list.append(disp_emp)
	titles = db.execute('select * from job_title').fetchall()
	plan = db.execute('select * from [401k_plan]').fetchall()
	life = db.execute('select * from life_insurance_plan').fetchall()
	health = db.execute('select * from health_insurance_plan').fetchall()
	dis = db.execute('select * from disability_plan').fetchall()
	return render_template("view_employee.html", titles=titles, plans=plan, LifeInsurance=life, HealthInsurance=health, DisInsurance=dis, emps=employee_display_list) 

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

@app.route("/add_hours", methods=['POST', 'GET'])
def add_hours():
	db = get_db()
	if request.method == 'POST':
		print "hey"
	emp_list = db.execute('SELECT * FROM employee').fetchall()
	return render_template("add_hours.html", emp_list=emp_list)
		
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
		db.execute('INSERT INTO disability_plan (InsuranceCoID, DisabilityPlanDescription, CostPerMonthDisability) values (?,?,?)',[insuranceID, Desc,pMonth])
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
		db.execute('INSERT INTO [401k_plan] (InsuranceCoID, [401kPlanDescription],[401kPercentOfSalary]) values (?,?,?)',[insuranceID,Desc,pSalary])
		db.commit()
	return render_template("add_401k_plan.html")

@app.route("/generate_w2", methods=['POST', 'GET'])
def generate_w2():
	return

if __name__ == "__main__":
    app.run(debug=True)
