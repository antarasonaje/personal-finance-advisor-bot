from datetime import datetime, timedelta
from database import db
from models import User, Income, Expense, BudgetLimit, SavingGoal, AIAdviceLog

class SeedService:
    @staticmethod
    def seed_all_scenarios():
        """Seeds the database with all 4 comprehensive personas from user requirements"""
        # Clear existing data
        db.session.query(AIAdviceLog).delete()
        db.session.query(SavingGoal).delete()
        db.session.query(BudgetLimit).delete()
        db.session.query(Expense).delete()
        db.session.query(Income).delete()
        db.session.query(User).delete()
        db.session.commit()

        # =========================================================
        # Scenario 1: Salaried Professional (Alex Johnson)
        # =========================================================
        u1 = User(
            name="Alex Johnson",
            persona_type="salaried",
            tagline="Senior Software Engineer • Corporate Tech",
            monthly_target_income=5800.0,
            monthly_savings_target=1500.0,
            currency="$",
            avatar_color="#6366f1"
        )
        db.session.add(u1)
        db.session.flush()

        # Incomes for Alex
        db.session.add(Income(user_id=u1.id, source="Tech Corp Monthly Salary", amount=5500.0, category="salary", date="2026-09-01", is_recurring=True, notes="Direct deposit net paycheck"))
        db.session.add(Income(user_id=u1.id, source="Weekend Mentoring / Side Gig", amount=300.0, category="other", date="2026-09-12", is_recurring=False, notes="Advisory call"))

        # Expenses for Alex
        db.session.add(Expense(user_id=u1.id, title="Downtown Apartment Rent", amount=1800.0, category="rent", date="2026-09-02", is_essential=True, notes="Fixed lease"))
        db.session.add(Expense(user_id=u1.id, title="Whole Foods & Supermarket", amount=520.0, category="food", date="2026-09-05", is_essential=True, notes="Groceries"))
        db.session.add(Expense(user_id=u1.id, title="Artisan Dining & Cafes", amount=230.0, category="food", date="2026-09-14", is_essential=False, notes="Weekend dinners"))
        db.session.add(Expense(user_id=u1.id, title="Subway Pass & Rideshare", amount=350.0, category="transport", date="2026-09-08", is_essential=True, notes="Commute"))
        db.session.add(Expense(user_id=u1.id, title="Concerts, Clubs & VIP Lounge", amount=580.0, category="entertainment", date="2026-09-18", is_essential=False, notes="Overspent on weekend events"))
        db.session.add(Expense(user_id=u1.id, title="Electricity, Water & Internet", amount=220.0, category="utilities", date="2026-09-10", is_essential=True, notes="Monthly utility bills"))
        db.session.add(Expense(user_id=u1.id, title="Fall Apparel & Tech Gadgets", amount=320.0, category="shopping", date="2026-09-21", is_essential=False, notes="Online purchase"))
        db.session.add(Expense(user_id=u1.id, title="Gym Membership & Health Supplement", amount=150.0, category="healthcare", date="2026-09-06", is_essential=True, notes="Fitness"))

        # Budget Limits for Alex
        db.session.add(BudgetLimit(user_id=u1.id, category="rent", monthly_limit=1800.0))
        db.session.add(BudgetLimit(user_id=u1.id, category="food", monthly_limit=700.0))
        db.session.add(BudgetLimit(user_id=u1.id, category="transport", monthly_limit=400.0))
        db.session.add(BudgetLimit(user_id=u1.id, category="entertainment", monthly_limit=400.0)) # Overspent! 580 vs 400
        db.session.add(BudgetLimit(user_id=u1.id, category="utilities", monthly_limit=250.0))
        db.session.add(BudgetLimit(user_id=u1.id, category="shopping", monthly_limit=300.0)) # Overspent! 320 vs 300
        db.session.add(BudgetLimit(user_id=u1.id, category="healthcare", monthly_limit=200.0))

        # Goals for Alex
        db.session.add(SavingGoal(user_id=u1.id, title="Emergency Fund (6 Months)", target_amount=15000.0, current_amount=9800.0, target_date="2027-04-30", category="emergency_fund", icon="shield"))
        db.session.add(SavingGoal(user_id=u1.id, title="Vacation to Tokyo & Kyoto", target_amount=4500.0, current_amount=2900.0, target_date="2026-12-15", category="vacation", icon="plane"))
        db.session.add(SavingGoal(user_id=u1.id, title="Stock Investment Portfolio", target_amount=10000.0, current_amount=5400.0, target_date="2027-01-31", category="investment", icon="trending-up"))

        # Sample AI Log
        db.session.add(AIAdviceLog(user_id=u1.id, role="assistant", message="Welcome Alex! I noticed you are over your Entertainment and Shopping budgets by $200. Let's redirect surplus back into your Tokyo Vacation fund.", category="alert"))

        # =========================================================
        # Scenario 2: College Student (Maya Chen)
        # =========================================================
        u2 = User(
            name="Maya Chen",
            persona_type="student",
            tagline="Undergraduate Junior • Computer Science",
            monthly_target_income=1150.0,
            monthly_savings_target=200.0,
            currency="$",
            avatar_color="#10b981"
        )
        db.session.add(u2)
        db.session.flush()

        # Incomes for Maya
        db.session.add(Income(user_id=u2.id, source="Monthly Family College Allowance", amount=800.0, category="allowance", date="2026-09-01", is_recurring=True, notes="Parental support for rent & food"))
        db.session.add(Income(user_id=u2.id, source="Campus CS Tutoring Lab", amount=350.0, category="salary", date="2026-09-15", is_recurring=True, notes="15 hrs/week peer tutoring"))

        # Expenses for Maya
        db.session.add(Expense(user_id=u2.id, title="Shared Student Apartment (Room)", amount=450.0, category="rent", date="2026-09-02", is_essential=True, notes="Shared with roommate"))
        db.session.add(Expense(user_id=u2.id, title="Campus Groceries & Meal Prep", amount=160.0, category="food", date="2026-09-04", is_essential=True, notes="Staples"))
        db.session.add(Expense(user_id=u2.id, title="Late Night Boba & Cafes", amount=95.0, category="food", date="2026-09-16", is_essential=False, notes="Study sessions at cafes"))
        db.session.add(Expense(user_id=u2.id, title="Algorithms Textbook & Lab Access", amount=110.0, category="education", date="2026-09-07", is_essential=True, notes="Required textbook code"))
        db.session.add(Expense(user_id=u2.id, title="Campus Bus Pass", amount=55.0, category="transport", date="2026-09-03", is_essential=True, notes="Student discounted transit"))
        db.session.add(Expense(user_id=u2.id, title="Weekend Movies & Student Club", amount=75.0, category="entertainment", date="2026-09-19", is_essential=False, notes="Campus events"))
        db.session.add(Expense(user_id=u2.id, title="Spotify Student & Mobile Data", amount=45.0, category="utilities", date="2026-09-11", is_essential=True, notes="Student plan"))

        # Budget Limits for Maya
        db.session.add(BudgetLimit(user_id=u2.id, category="rent", monthly_limit=450.0))
        db.session.add(BudgetLimit(user_id=u2.id, category="food", monthly_limit=220.0)) # Warning: spent 255 vs 220 limit!
        db.session.add(BudgetLimit(user_id=u2.id, category="education", monthly_limit=120.0))
        db.session.add(BudgetLimit(user_id=u2.id, category="transport", monthly_limit=60.0))
        db.session.add(BudgetLimit(user_id=u2.id, category="entertainment", monthly_limit=70.0))
        db.session.add(BudgetLimit(user_id=u2.id, category="utilities", monthly_limit=50.0))

        # Goals for Maya
        db.session.add(SavingGoal(user_id=u2.id, title="New Coding Laptop (M4)", target_amount=1200.0, current_amount=750.0, target_date="2027-01-15", category="tech", icon="laptop"))
        db.session.add(SavingGoal(user_id=u2.id, title="Emergency Student Cushion", target_amount=800.0, current_amount=480.0, target_date="2026-12-31", category="emergency_fund", icon="shield"))

        db.session.add(AIAdviceLog(user_id=u2.id, role="assistant", message="Hey Maya! You're doing well keeping essential rent low. Trimming $35 from cafe visits will help you reach your Laptop goal 1 month earlier!", category="advice"))

        # =========================================================
        # Scenario 3: Freelancer with Variable Income (David Rivera)
        # =========================================================
        u3 = User(
            name="David Rivera",
            persona_type="freelancer",
            tagline="Independent UI/UX Designer & Consultant",
            monthly_target_income=5400.0,
            monthly_savings_target=1600.0,
            currency="$",
            avatar_color="#8b5cf6"
        )
        db.session.add(u3)
        db.session.flush()

        # Incomes for David (Variable multiple clients)
        db.session.add(Income(user_id=u3.id, source="FinTech Client - Design Retainer", amount=2400.0, category="freelance", date="2026-09-03", is_recurring=True, notes="Monthly contract"))
        db.session.add(Income(user_id=u3.id, source="E-Commerce App Redesign Milestone", amount=1800.0, category="freelance", date="2026-09-14", is_recurring=False, notes="Sprint 2 completion payout"))
        db.session.add(Income(user_id=u3.id, source="Design System Consulting Hours", amount=1200.0, category="freelance", date="2026-09-22", is_recurring=False, notes="Billed 20 hrs at $60/hr"))

        # Expenses for David
        db.session.add(Expense(user_id=u3.id, title="Live-Work Studio Apartment", amount=1400.0, category="rent", date="2026-09-02", is_essential=True, notes="Home office space"))
        db.session.add(Expense(user_id=u3.id, title="Figma, Adobe CC, AI Tools & Webflow", amount=380.0, category="work_project", date="2026-09-05", is_essential=True, notes="Professional software tools"))
        db.session.add(Expense(user_id=u3.id, title="Groceries & Home Meals", amount=440.0, category="food", date="2026-09-09", is_essential=True, notes="Household food"))
        db.session.add(Expense(user_id=u3.id, title="Client Dinners & Coffee Meetings", amount=210.0, category="food", date="2026-09-17", is_essential=False, notes="Business networking"))
        db.session.add(Expense(user_id=u3.id, title="Self-Employed Health & Dental Care", amount=390.0, category="healthcare", date="2026-09-08", is_essential=True, notes="Private health coverage"))
        db.session.add(Expense(user_id=u3.id, title="High-Speed Fiber & Cell Phone", amount=180.0, category="utilities", date="2026-09-11", is_essential=True, notes="Gigabit internet for client asset uploads"))
        db.session.add(Expense(user_id=u3.id, title="Coworking Passes & Transit", amount=150.0, category="transport", date="2026-09-15", is_essential=True, notes="Client site visits"))
        db.session.add(Expense(user_id=u3.id, title="Streaming & Weekend Leisure", amount=140.0, category="entertainment", date="2026-09-20", is_essential=False, notes="Relaxation"))

        # Budget Limits for David
        db.session.add(BudgetLimit(user_id=u3.id, category="rent", monthly_limit=1400.0))
        db.session.add(BudgetLimit(user_id=u3.id, category="work_project", monthly_limit=450.0))
        db.session.add(BudgetLimit(user_id=u3.id, category="food", monthly_limit=600.0)) # Warning: spent 650 vs 600 limit
        db.session.add(BudgetLimit(user_id=u3.id, category="healthcare", monthly_limit=400.0))
        db.session.add(BudgetLimit(user_id=u3.id, category="utilities", monthly_limit=200.0))
        db.session.add(BudgetLimit(user_id=u3.id, category="transport", monthly_limit=200.0))
        db.session.add(BudgetLimit(user_id=u3.id, category="entertainment", monthly_limit=180.0))

        # Goals for David
        db.session.add(SavingGoal(user_id=u3.id, title="6-Month Emergency Runway", target_amount=18000.0, current_amount=12400.0, target_date="2027-03-31", category="emergency_fund", icon="shield"))
        db.session.add(SavingGoal(user_id=u3.id, title="Quarterly Tax Vault (Q3/Q4)", target_amount=6000.0, current_amount=4600.0, target_date="2026-10-15", category="general", icon="lock"))
        db.session.add(SavingGoal(user_id=u3.id, title="Studio Equipment Upgrade", target_amount=3000.0, current_amount=1800.0, target_date="2026-12-15", category="tech", icon="monitor"))

        db.session.add(AIAdviceLog(user_id=u3.id, role="assistant", message="David, great job billing $5,400 across 3 clients this month. Remember to hold back 25% ($1,350) for your quarterly tax vault before spending!", category="freelance"))

        # =========================================================
        # Scenario 4: Household Manager (The Sharma Family)
        # =========================================================
        u4 = User(
            name="The Sharma Family",
            persona_type="household",
            tagline="Household Family of Four • Dual Income",
            monthly_target_income=8200.0,
            monthly_savings_target=2000.0,
            currency="$",
            avatar_color="#06b6d4"
        )
        db.session.add(u4)
        db.session.flush()

        # Incomes for Family
        db.session.add(Income(user_id=u4.id, source="Primary Salary (Rahul)", amount=5400.0, category="shared_family", date="2026-09-01", is_recurring=True, notes="Monthly take-home salary"))
        db.session.add(Income(user_id=u4.id, source="Partner Salary (Priya)", amount=2800.0, category="shared_family", date="2026-09-05", is_recurring=True, notes="Monthly take-home salary"))

        # Expenses for Family
        db.session.add(Expense(user_id=u4.id, title="Family Home Mortgage", amount=2400.0, category="rent", date="2026-09-02", is_essential=True, notes="Primary mortgage payment"))
        db.session.add(Expense(user_id=u4.id, title="Costco & Supermarket Groceries", amount=1320.0, category="groceries", date="2026-09-06", is_essential=True, notes="Family food & household essentials (Overspent!)"))
        db.session.add(Expense(user_id=u4.id, title="Kids School Tuition & Music Classes", amount=950.0, category="education", date="2026-09-08", is_essential=True, notes="Private schooling & violin lessons"))
        db.session.add(Expense(user_id=u4.id, title="Family Gas, Electricity, Water & Internet", amount=480.0, category="utilities", date="2026-09-12", is_essential=True, notes="Household utility bills"))
        db.session.add(Expense(user_id=u4.id, title="Family Health Insurance & Pediatrician", amount=420.0, category="healthcare", date="2026-09-15", is_essential=True, notes="Healthcare & medicine"))
        db.session.add(Expense(user_id=u4.id, title="Minivan Fuel & Car Insurance", amount=460.0, category="transport", date="2026-09-14", is_essential=True, notes="Family commuting and school drop-offs"))
        db.session.add(Expense(user_id=u4.id, title="Weekend Family Dinners & Zoo Outing", amount=340.0, category="entertainment", date="2026-09-19", is_essential=False, notes="Family weekend outing"))
        db.session.add(Expense(user_id=u4.id, title="Home Hardware & Garden Supplies", amount=210.0, category="other", date="2026-09-21", is_essential=False, notes="Maintenance"))

        # Budget Limits for Family
        db.session.add(BudgetLimit(user_id=u4.id, category="rent", monthly_limit=2400.0))
        db.session.add(BudgetLimit(user_id=u4.id, category="groceries", monthly_limit=1100.0)) # Overspent! 1320 vs 1100 limit
        db.session.add(BudgetLimit(user_id=u4.id, category="education", monthly_limit=1000.0))
        db.session.add(BudgetLimit(user_id=u4.id, category="utilities", monthly_limit=450.0)) # Overspent! 480 vs 450 limit
        db.session.add(BudgetLimit(user_id=u4.id, category="healthcare", monthly_limit=450.0))
        db.session.add(BudgetLimit(user_id=u4.id, category="transport", monthly_limit=500.0))
        db.session.add(BudgetLimit(user_id=u4.id, category="entertainment", monthly_limit=350.0))
        db.session.add(BudgetLimit(user_id=u4.id, category="other", monthly_limit=250.0))

        # Goals for Family
        db.session.add(SavingGoal(user_id=u4.id, title="Children's College 529 Fund", target_amount=50000.0, current_amount=28500.0, target_date="2030-08-31", category="education", icon="book-open"))
        db.session.add(SavingGoal(user_id=u4.id, title="Annual Family Vacation", target_amount=6000.0, current_amount=3600.0, target_date="2027-06-30", category="vacation", icon="sun"))
        db.session.add(SavingGoal(user_id=u4.id, title="Rooftop Solar & Home Battery", target_amount=12000.0, current_amount=7800.0, target_date="2027-02-28", category="home", icon="home"))

        db.session.add(AIAdviceLog(user_id=u4.id, role="assistant", message="Hello Sharma family! You are maintaining a healthy 19.8% family savings rate. Noticeable overspend in Groceries (+$220) can be addressed via bi-weekly bulk purchasing.", category="household"))

        db.session.commit()
        return u1.id
