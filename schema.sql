PRAGMA foreign_keys = ON; 

CREATE TABLE insurance_company(
	InsuranceCoID INTEGER PRIMARY KEY AUTOINCREMENT,
	InsuranceName TEXT
);

CREATE TABLE pay_period(
	PayPeriodID INTEGER PRIMARY KEY AUTOINCREMENT,
	StartDate DATE,
	EndDate DATE,
	Hours INTEGER
);

CREATE TABLE withholding(
	WithholdingID INTEGER PRIMARY KEY AUTOINCREMENT,
	Description TEXT
);

CREATE TABLE fed_tax_rate(
	FedTaxRateID INTEGER PRIMARY KEY AUTOINCREMENT,
	Upperlimit INTEGER,
	WithholdingID INTEGER,
	FedTaxRate REAL,
	FOREIGN KEY(WithholdingID) REFERENCES Withholding(WithholdingID)
); 

CREATE TABLE address(
	AddressID INTEGER PRIMARY KEY AUTOINCREMENT,
	Street TEXT,
	City TEXT,
	State TEXT,
	ZipCode TEXT
);

CREATE TABLE employee(
	EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
	FirstName TEXT,
	LastName TEXT,
	AddressID INTEGER,
	JobTitleID INTEGER,
	FedTaxRateID INTEGER,
	EmployeeBenefitsID INTEGER,
	-- PayPeriodsID INTEGER,
	FOREIGN KEY(AddressID) REFERENCES address(AddressID),
	FOREIGN KEY(JobTitleID) REFERENCES job_title(JobTitleID),
	FOREIGN KEY(FedTaxRateID) REFERENCES fed_tax_rate(FedTaxRateID),
	FOREIGN KEY(EmployeeBenefitsID) REFERENCES employee_benefits(EmployeeBenefitsID)
	-- FOREIGN KEY(PayPeriodsID) REFERENCES PayPeriodID(PayPeriodsID))
);

CREATE TABLE pay_periods(
	PayPeriodsID INTEGER PRIMARY KEY AUTOINCREMENT,
	EmployeeID INTEGER,
	PayPeriodID INTEGER,
	FOREIGN KEY(PayPeriodID) REFERENCES pay_periods(PayPeriodID),
	FOREIGN KEY(EmployeeID) REFERENCES employee(EmployeeID)
);

CREATE TABLE payroll(
	PayrollID INTEGER PRIMARY KEY AUTOINCREMENT,
	PayPeriodsID INTEGER,
	EmployeeID INTEGER,
	LocalTax REAL,
	CityTax REAL,
	StateTax REAL,
	FedTax REAL, 
	SSTax REAL,
	MedicareTax REAL,
	LifeInsuranceAmt REAL,
	[401kAmt] REAL,
	DisabilityAmt REAL,
	HealthInsuranceAmt REAL,
	GrossSalary REAL,
	FOREIGN KEY(EmployeeID) REFERENCES employee(EmployeeID), 
	FOREIGN KEY(PayPeriodsID) REFERENCES pay_periods(PayPeriodsID) 
);

CREATE TABLE job_title(
	JobTitleID INTEGER PRIMARY KEY AUTOINCREMENT,
	JobTitleName TEXT,
	JOBTitleSalary REAL
);

CREATE TABLE [401k_plan](
	[401kPlanID] INTEGER PRIMARY KEY AUTOINCREMENT,
	InsuranceCoID INTEGER,
	[401kPlanDescription] TEXT,
	[401kPercentOfSalary] REAL,
	FOREIGN KEY ([InsuranceCoID]) REFERENCES insurance_company(InsuranceCoID)
);

CREATE TABLE employee_benefits(
	EmployeeBenefitsID INTEGER PRIMARY KEY AUTOINCREMENT,
	[401kPlanID] INTEGER,
	DisabilityPlanID INTEGER,
	LifeInsPlanID INTEGER,
	HealthInsPlanID INTEGER,
	FilingStatus TEXT,
	FOREIGN KEY([401kPlanID]) REFERENCES [401k_plan]([401kPlanID]),
	FOREIGN KEY(LifeInsPlanID) REFERENCES life_insurance_plan(LifeInsPlanID),
	FOREIGN KEY(DisabilityPlanID) REFERENCES disability_plan(DisabilityPlanID),
	FOREIGN KEY(HealthInsPlanID) REFERENCES health_insurance_plan(HealthInsPlanID)
); 

CREATE TABLE disability_plan(
	DisabilityPlanId INTEGER PRIMARY KEY AUTOINCREMENT,
	InsuranceCoID INTEGER,
	DisabilityPlanDescription TEXT,
	CostPerMonthDisability REAL,
	FOREIGN KEY (InsuranceCoID) REFERENCES insurance_company(InsuranceCoID)
);

CREATE TABLE life_insurance_plan(
	LifeInsPlanID INTEGER PRIMARY KEY AUTOINCREMENT,
	InsuranceCoID INTEGER,
	LifeInsDescription TEXT,
	LifeInsAmt REAL,
	CostPerMonthLifeIns REAL,
	FOREIGN KEY (InsuranceCoID) REFERENCES insurance_company(InsuranceCoID)
);

CREATE TABLE health_insurance_plan(
	HealthInsPlanID INTEGER PRIMARY KEY AUTOINCREMENT,
	InsuranceCoID INTEGER,
	InsPlanDescription TEXT,
	FamilyRate REAL,
	SingleRate REAL, 
	CostPerMonthHealthIns REAL,
	FOREIGN KEY (InsuranceCoID) REFERENCES insurance_company(InsuranceCoID)
);

