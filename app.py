import os
from flask import Flask, render_template, request, jsonify, session
from config import Config
from database import db
from models import User, Income, Expense, BudgetLimit, SavingGoal, AIAdviceLog
from services.analytics_service import AnalyticsService
from services.ai_advisor_service import AIAdvisorService
from services.seed_service import SeedService

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def get_current_user():
    user_id = request.args.get("user_id", type=int) or request.headers.get("X-User-Id", type=int)
    if not user_id:
        user_id = session.get("current_user_id")
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            session["current_user_id"] = user.id
            return user
    user = User.query.first()
    if not user:
        default_id = SeedService.seed_all_scenarios()
        user = db.session.get(User, default_id)
    session["current_user_id"] = user.id
    return user

@app.route("/")
def index():
    user = get_current_user()
    return render_template("index.html", current_user=user)

# ----------------- Scenario & User APIs -----------------
@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    users = User.query.order_by(User.id).all()
    active_user = get_current_user()
    return jsonify({
        "active_user_id": active_user.id,
        "scenarios": [u.to_dict() for u in users]
    })

@app.route("/api/switch-user/<int:user_id>", methods=["POST"])
def switch_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User scenario not found"}), 404
    session["current_user_id"] = user.id
    return jsonify({"success": True, "user": user.to_dict()})

@app.route("/api/user", methods=["GET", "POST"])
def user_profile():
    user = get_current_user()
    if request.method == "POST":
        data = request.json or {}
        if "name" in data:
            user.name = data["name"]
        if "monthly_target_income" in data:
            user.monthly_target_income = float(data["monthly_target_income"])
        if "monthly_savings_target" in data:
            user.monthly_savings_target = float(data["monthly_savings_target"])
        if "currency" in data:
            user.currency = data["currency"]
        db.session.commit()
    return jsonify(user.to_dict())

# ----------------- Income APIs -----------------
@app.route("/api/incomes", methods=["GET", "POST"])
def manage_incomes():
    user = get_current_user()
    if request.method == "POST":
        data = request.json or {}
        source = data.get("source", "").strip()
        amount = float(data.get("amount", 0.0))
        category = data.get("category", "salary")
        date_str = data.get("date")
        is_recurring = bool(data.get("is_recurring", True))
        notes = data.get("notes", "").strip()

        if not source or amount <= 0:
            return jsonify({"error": "Valid source and positive amount are required"}), 400

        income = Income(
            user_id=user.id,
            source=source,
            amount=amount,
            category=category,
            date=date_str,
            is_recurring=is_recurring,
            notes=notes
        )
        db.session.add(income)
        db.session.commit()
        return jsonify(income.to_dict()), 201

    incomes = Income.query.filter_by(user_id=user.id).order_by(Income.date.desc()).all()
    return jsonify([i.to_dict() for i in incomes])

@app.route("/api/incomes/<int:income_id>", methods=["DELETE"])
def delete_income(income_id):
    user = get_current_user()
    income = Income.query.filter_by(id=income_id, user_id=user.id).first()
    if not income:
        return jsonify({"error": "Income not found"}), 404
    db.session.delete(income)
    db.session.commit()
    return jsonify({"success": True})

# ----------------- Expense APIs -----------------
@app.route("/api/expenses", methods=["GET", "POST"])
def manage_expenses():
    user = get_current_user()
    if request.method == "POST":
        data = request.json or {}
        title = data.get("title", "").strip()
        amount = float(data.get("amount", 0.0))
        category = data.get("category", "food")
        date_str = data.get("date")
        is_essential = bool(data.get("is_essential", True))
        notes = data.get("notes", "").strip()

        if not title or amount <= 0:
            return jsonify({"error": "Valid title and positive amount are required"}), 400

        expense = Expense(
            user_id=user.id,
            title=title,
            amount=amount,
            category=category,
            date=date_str,
            is_essential=is_essential,
            notes=notes
        )
        db.session.add(expense)
        db.session.commit()
        return jsonify(expense.to_dict()), 201

    expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).all()
    return jsonify([e.to_dict() for e in expenses])

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    user = get_current_user()
    expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"success": True})

# ----------------- Budget APIs -----------------
@app.route("/api/budgets", methods=["GET", "POST"])
def manage_budgets():
    user = get_current_user()
    if request.method == "POST":
        data = request.json or {}
        category = data.get("category")
        monthly_limit = float(data.get("monthly_limit", 0.0))
        if not category or monthly_limit <= 0:
            return jsonify({"error": "Valid category and limit required"}), 400

        b = BudgetLimit.query.filter_by(user_id=user.id, category=category).first()
        if b:
            b.monthly_limit = monthly_limit
        else:
            b = BudgetLimit(user_id=user.id, category=category, monthly_limit=monthly_limit)
            db.session.add(b)
        db.session.commit()
        return jsonify(b.to_dict())

    budgets = BudgetLimit.query.filter_by(user_id=user.id).all()
    return jsonify([b.to_dict() for b in budgets])

# ----------------- Saving Goals APIs -----------------
@app.route("/api/goals", methods=["GET", "POST"])
def manage_goals():
    user = get_current_user()
    if request.method == "POST":
        data = request.json or {}
        title = data.get("title", "").strip()
        target_amount = float(data.get("target_amount", 0.0))
        current_amount = float(data.get("current_amount", 0.0))
        target_date = data.get("target_date")
        category = data.get("category", "general")
        icon = data.get("icon", "target")

        if not title or target_amount <= 0:
            return jsonify({"error": "Title and target amount are required"}), 400

        goal = SavingGoal(
            user_id=user.id,
            title=title,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date,
            category=category,
            icon=icon
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify(goal.to_dict()), 201

    goals = SavingGoal.query.filter_by(user_id=user.id).order_by(SavingGoal.id).all()
    return jsonify([g.to_dict() for g in goals])

@app.route("/api/goals/<int:goal_id>/deposit", methods=["POST"])
def deposit_goal(goal_id):
    user = get_current_user()
    goal = SavingGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found"}), 404
    data = request.json or {}
    amount = float(data.get("amount", 0.0))
    if amount <= 0:
        return jsonify({"error": "Deposit amount must be positive"}), 400
    goal.current_amount += amount
    db.session.commit()
    return jsonify(goal.to_dict())

@app.route("/api/goals/<int:goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    user = get_current_user()
    goal = SavingGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found"}), 404
    db.session.delete(goal)
    db.session.commit()
    return jsonify({"success": True})

# ----------------- Analytics API -----------------
@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    user = get_current_user()
    incomes = Income.query.filter_by(user_id=user.id).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    budget_limits = BudgetLimit.query.filter_by(user_id=user.id).all()
    saving_goals = SavingGoal.query.filter_by(user_id=user.id).all()

    summary = AnalyticsService.calculate_summary(user, incomes, expenses, budget_limits, saving_goals)
    return jsonify({
        "user": user.to_dict(),
        "summary": summary
    })

# ----------------- AI Features APIs -----------------
@app.route("/api/ai/budget-plan", methods=["GET"])
def get_ai_budget_plan():
    user = get_current_user()
    incomes = Income.query.filter_by(user_id=user.id).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    budget_limits = BudgetLimit.query.filter_by(user_id=user.id).all()
    saving_goals = SavingGoal.query.filter_by(user_id=user.id).all()
    summary = AnalyticsService.calculate_summary(user, incomes, expenses, budget_limits, saving_goals)
    plan = AIAdvisorService.generate_personalized_budget(user, summary)
    return jsonify(plan)

@app.route("/api/ai/apply-budget-plan", methods=["POST"])
def apply_ai_budget_plan():
    user = get_current_user()
    incomes = Income.query.filter_by(user_id=user.id).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    budget_limits = BudgetLimit.query.filter_by(user_id=user.id).all()
    saving_goals = SavingGoal.query.filter_by(user_id=user.id).all()
    summary = AnalyticsService.calculate_summary(user, incomes, expenses, budget_limits, saving_goals)
    plan = AIAdvisorService.generate_personalized_budget(user, summary)

    # Apply category limits to database
    for category, limit_val in plan["category_limits"].items():
        existing = BudgetLimit.query.filter_by(user_id=user.id, category=category).first()
        if existing:
            existing.monthly_limit = limit_val
        else:
            db.session.add(BudgetLimit(user_id=user.id, category=category, monthly_limit=limit_val))
    db.session.commit()
    return jsonify({"success": True, "applied_limits": plan["category_limits"]})

@app.route("/api/ai/monthly-report", methods=["GET"])
def get_ai_monthly_report():
    user = get_current_user()
    incomes = Income.query.filter_by(user_id=user.id).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    budget_limits = BudgetLimit.query.filter_by(user_id=user.id).all()
    saving_goals = SavingGoal.query.filter_by(user_id=user.id).all()
    summary = AnalyticsService.calculate_summary(user, incomes, expenses, budget_limits, saving_goals)
    report = AIAdvisorService.generate_monthly_report(user, summary, saving_goals)
    return jsonify(report)

@app.route("/api/ai/chat/history", methods=["GET"])
def get_chat_history():
    user = get_current_user()
    logs = AIAdviceLog.query.filter_by(user_id=user.id).order_by(AIAdviceLog.timestamp.asc()).all()
    return jsonify([l.to_dict() for l in logs])

@app.route("/api/ai/chat", methods=["POST"])
def send_ai_chat():
    user = get_current_user()
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Save user message
    user_log = AIAdviceLog(user_id=user.id, role="user", message=message, category="query")
    db.session.add(user_log)
    db.session.commit()

    # Generate response
    incomes = Income.query.filter_by(user_id=user.id).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    budget_limits = BudgetLimit.query.filter_by(user_id=user.id).all()
    saving_goals = SavingGoal.query.filter_by(user_id=user.id).all()
    summary = AnalyticsService.calculate_summary(user, incomes, expenses, budget_limits, saving_goals)

    reply_text = AIAdvisorService.generate_chat_response(user, message, summary, saving_goals)

    # Save assistant message
    ai_log = AIAdviceLog(user_id=user.id, role="assistant", message=reply_text, category="response")
    db.session.add(ai_log)
    db.session.commit()

    return jsonify({
        "reply": reply_text,
        "log": ai_log.to_dict()
    })

@app.route("/api/reset-data", methods=["POST"])
def reset_seed_data():
    default_id = SeedService.seed_all_scenarios()
    session["current_user_id"] = default_id
    user = db.session.get(User, default_id)
    return jsonify({"success": True, "message": "Database reset to initial scenario seeds.", "user": user.to_dict()})

with app.app_context():
    db.create_all()
    if not User.query.first():
        SeedService.seed_all_scenarios()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
