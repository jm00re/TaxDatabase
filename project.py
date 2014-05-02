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
		#Add payroll
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
		start = str(request.form['start'])
		end = str(request.form['end'])
		hours = int(request.form['hours'])
		ID = int(request.form['emp_number'])
		hour_qry= 'INSERT INTO pay_period ( StartDate, EndDate, Hours) VALUES (?, ?, ?)'
		db.execute(hour_qry, [start, end, hours])
		db.commit()
		ppID = db.execute('select last_insert_rowid();').fetchone()[0]
		periods_qry = 'insert into pay_periods (EmployeeID, PayPeriodID) VALUES (?, ?)'
		db.execute(periods_qry, [ID, ppID])
		db.commit()
	emp_list = db.execute('SELECT * FROM employee').fetchall()
	return render_template("add_hours.html", emp_list=emp_list)

@app.route("/view_payroll", methods=['POST', 'GET'])
def view_payroll():
	db = get_db()
	emp_list = db.execute('SELECT * FROM employee').fetchall()
	period_list = []
	display_list = []
	pp_info = []
	pp1_info = []
	ID = 0
	pp_id = 0
	if request.method == 'GET' and not request.args.get('emp_number','') == '':
		ID = request.args.get('emp_number','')			
		pp_qry = 'select PayPeriodID, StartDate, EndDate, Hours from pay_periods natural join pay_period where EmployeeID=?'
		period_list = db.execute(pp_qry, [ID]).fetchall()
		salary = db.execute('select JobTitleSalary from employee natural join job_title where EmployeeID=?', [ID]).fetchone()
	if request.method == 'GET' and not request.args.get('pp_id','') == '':
		ID = request.args.get('emp_number','')			
		salary = db.execute('select JobTitleSalary from employee natural join job_title where EmployeeID=?', [ID]).fetchone()
		pp_id = request.args.get('pp_id','')
		hours = db.execute('select Hours from pay_period where PayPeriodID=?', [pp_id]).fetchone()[0]
		#Hours in pay period
		week_gross_salary = (salary[0] / 2087)*hours
		hours_list = db.execute('select Hours from pay_period natural join pay_periods where EmployeeID=?', [ID]).fetchall()
		#Total Hours
		hours_to_date = 0
		for i in hours_list:
			hours_to_date += i[0]
		#Find 401k Percent of salary
		plan_qry = 'select [401kPercentOfSalary] from employee natural join employee_benefits natural join [401k_plan] where EmployeeID=?'
		plan = db.execute(plan_qry, [ID]).fetchone()[0]
		#Find Disability Insurance Cost
		dis_qry = 'select CostPerMonthDisability from employee natural join employee_benefits natural join disability_plan where EmployeeID=?'
		dis = db.execute(dis_qry, [ID]).fetchone()[0]
		#Life Insurance Amount
		life_qry = 'select CostPerMonthLifeIns from employee natural join employee_benefits natural join life_insurance_plan where EmployeeID=?'
		life = db.execute(life_qry, [ID]).fetchone()[0]
		#Health Insurance Amount
		health_qry = 'select CostPerMonthHealthIns from employee natural join employee_benefits natural join health_insurance_plan where EmployeeID=?'
		health = db.execute(health_qry, [ID]).fetchone()[0]
		#Fed Tax Arount
		tax_qry = 'select FedTaxRate from employee natural join fed_tax_rate where EmployeeID=?'
		fed = db.execute(tax_qry, [ID]).fetchone()[0]
		numb_qry = 'select count(*) from pay_period natural join pay_periods where EmployeeID=?'
		num_pay_periods = db.execute(numb_qry, [ID]).fetchone()[0]
		city = .02
		state = .03
		local = .01
		medicare = .01
		ss = .015
		unemployment = .005
		avg_hours_per_year = 2087
		#display list
		#pp_info = []
		#Pay Period deduc
		fed_deduc = week_gross_salary*(fed/100)
		plan_deduc = (plan/100)*week_gross_salary
		dis_deduc = dis
		life_deduc = life
		health_deduc = health
		city_deduc = week_gross_salary*city
		state_deduc = week_gross_salary*state
		local_deduc = week_gross_salary*local
		medicare_deduc = week_gross_salary*medicare
		ss_deduc = week_gross_salary*ss
		unemployment_deduc = week_gross_salary*unemployment
		netpay = week_gross_salary
		pp_info.append(netpay)
		deduc_total = 0
		tax_total = 0 
		netpay -= fed_deduc
		netpay -= plan_deduc
		netpay -= dis_deduc
		netpay -= life_deduc
		netpay -= health_deduc
		netpay -= city_deduc
		netpay -= local_deduc
		netpay -= state_deduc
		netpay -= medicare_deduc
		netpay -= ss_deduc
		netpay -= unemployment_deduc
		deduc_total += plan_deduc
		deduc_total += dis_deduc
		deduc_total += life_deduc
		deduc_total += health_deduc

		tax_total += fed_deduc
		tax_total += city_deduc
		tax_total += local_deduc
		tax_total += medicare_deduc
		tax_total += ss_deduc
		tax_total += unemployment_deduc
		tax_total += state_deduc

		#Display stuff
		pp_info.append(netpay)
		pp_info.append(deduc_total)
		pp_info.append(plan_deduc)
		pp_info.append(health_deduc)
		pp_info.append(life_deduc)
		pp_info.append(dis_deduc)

		pp_info.append(tax_total)
		pp_info.append(fed_deduc)
		pp_info.append(state_deduc)
		pp_info.append(city_deduc)
		pp_info.append(local_deduc)
		pp_info.append(ss_deduc)
		pp_info.append(medicare_deduc)
		pp_info.append(unemployment_deduc)

		#Total Period deduc

		total_gross_salary = (salary[0] / 2087)*hours_to_date
		total_fed_deduc = total_gross_salary*(fed/100)
		total_plan_deduc = total_gross_salary*(plan/100)
		total_dis_deduc = num_pay_periods*dis
		total_life_deduc = num_pay_periods*life
		total_health_deduc = num_pay_periods*health
		total_city_deduc = total_gross_salary*city
		total_local_deduc = total_gross_salary*local
		total_medicare_deduc = total_gross_salary*medicare
		total_ss_deduc = total_gross_salary*ss
		total_unemployment_deduc = total_gross_salary*unemployment

		#pp1_info = []
		grosspay = (salary[0] / 2087) * hours_to_date
		pp1_info.append(grosspay)
		grosspay -= total_fed_deduc
		grosspay -= total_plan_deduc
		grosspay -= total_dis_deduc
		grosspay -= total_life_deduc
		grosspay -= total_health_deduc
		grosspay -= total_city_deduc
		grosspay -= total_local_deduc
		grosspay -= total_medicare_deduc
		grosspay -= total_ss_deduc
		grosspay -= total_unemployment_deduc

		pp1_info.append(grosspay)
		pp1_info.append(deduc_total)
		pp1_info.append(plan_deduc)
		pp1_info.append(health_deduc)
		pp1_info.append(life_deduc)
		pp1_info.append(dis_deduc)
		pp1_info.append(tax_total)
		pp1_info.append(fed_deduc)
		pp1_info.append(state_deduc)
		pp1_info.append(city_deduc)
		pp1_info.append(local_deduc)
		pp1_info.append(ss_deduc)
		pp1_info.append(medicare_deduc)
		pp1_info.append(unemployment_deduc)

	emp_list = db.execute('SELECT * FROM employee').fetchall()
	ID = int(ID)
	pp_id = int(pp_id)
	return render_template("view_payroll.html", emp_list=emp_list, period_list=period_list, pp_info=pp_info, pp1_info=pp1_info, ID=ID, pp_id=pp_id)

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
			
		
	return render_template("generate_w2.html", titles=titles, plans=plan, LifeInsurance=life, HealthInsurance=health, DisInsurance=dis, emps=employee_display_list) 

if __name__ == "__main__":
    app.run(debug=True)
