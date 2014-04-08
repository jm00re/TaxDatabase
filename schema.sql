CREATE TABLE payroll(
	PayrollEmpID INTEGER AUTOINCREMENT PRIMARY KEY,
	FOREIGN KEY (EmployeeID) REFRENCES employee(EmployeeID), 
	PayPeriod INTEGER, 
	LocalTax REAL,
	CityTax REAL,
	StateTax REAL,
	FedTax REAL, 
	SSTax REAL,
	MedicareTax REAL,
	LifeInsuranceAmt REAL,
	401kAmt REAL,
	DisabilityAmt REAL,
	HealthInsuranceAmt REAL
);

CREATE TABLE employee(
	EmployeeID INTEGER AUTOINCREMENT PRIMARY KEY,
	FOREIGN KEY(AddressID) REFRENCES address(AddressID),
	FOREIGN KEY(WithholdingID) REFRENCES withholding(WithholdingID),
	FOREIGN KEY(JobTitleID) REFRENCES job_title(JobTitleID),
	FOREIGN KEY(TaxRateID) REFRENCES tax_rate(TaxRateID),
	FOREIGN KEY(EmployeeBenefitsID) REFRENCES employee_benefits(EmployeeBenefitsID)
); 

CREATE TABLE address(
	AddressID INTEGER AUTOINCREMENT PRIMARY KEY,
	StreetNumber INTEGER,
	Street TEXT,
	FOREIGN KEY(ZipCode) REFRENCES zip_code(ZipCode)
);

CREATE TABLE zip_code(
	ZipCode INTEGER AUTOINCREMENT PRIMARY KEY, 
	City TEXT,
	State TEXT
);

CREATE TABLE withholding(
	WithholdingID INTEGER AUTOINCREMENT PRIMARY KEY,
	Description TEXT
);

CREATE TABLE fed_tax_rate(
	FedTaxRateID INTEGER AUTOINCREMENT PRIMARY KEY,
	FOREIGN KEY(WithholdingID) REFRENCES Withholding(WithholdingID),
	Upperlimit INTEGER,
	FedTaxRate REAL
); 

CREATE TABLE job_title(
	JobTitleID INTEGER AUTOINCREMENT PRIMARY KEY,
	JobTitleName TEXT,
	JOBTitleSalary
);

CREATE TABLE insurance_company(
	InsuranceCoID INTEGER AUTOINCREMENT PRIMARY KEY,
	InsuranceName TEXT
);

CREATE TABLE employee_benefits(
	EmployeeBenefitsID INTEGER AUTOINCREMENT PRIMARY KEY,
	FOREIGN KEY(401kPlanID) REFRENCES 401k_plan(401kPlanID),
	FOREIGN KEY(LifeInsPlanID) REFRENCES life_insurance_plan(LifeInsPlanID),
	FOREIGN KEY(DisabilityPlanID) REFRENCES disability_plan(DisabilityPlanID),
	FOREIGN KEY(HealthInsPlanID) REFRENCES health_insurance_plan(HealthInsPlanID)
); 

CREATE TABLE 401k_plan(
	401kPlanID INTEGER AUTOINCREMENT PRIMARY KEY,
	FOREIGN KEY (InsuranceCoID) REFRENCES insurance_company(InsuranceCoID), 
	401kPlanDescription INTEGER,
	401kPercentOfSalary REAL
);

CREATE TABLE disability_plan(
	DisabilityPlanId INTEGER AUTOINCREMENT PRIMARY KEY,
	FOREIGN KEY (InsuranceCoID) REFRENCES insurance_company(InsuranceCoID), 
	DisabilityPlanDescription TEXT,
	CostPerMonthDisability REAL
);

CREATE TABLE life_insurance_plan(
	LifeInsPlanID INTEGER AUTOINCREMENT PRIMARY KEY,
	FOREIGN KEY (InsuranceCoID) REFRENCES insurance_company(InsuranceCoID), 
	LifeInsDescription TEXT,
	LifeInsAmt REAL,
	CostPerMonthLifeIns REAL
);

CREATE TABLE health_insurance_plan(
	HealthInsPlanID INTEGER AUTOINCREMENT PRIMARY KEY,
	FOREIGN KEY (InsuranceCoID) REFRENCES insurance_company(InsuranceCoID), 
	InsPlanDescription TEXT,
	FamilyRate REAL,
	SingleRate REAL, 
	CostPerMonthHealthIns REAL
);




