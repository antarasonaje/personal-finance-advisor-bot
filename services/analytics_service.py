from collections import defaultdict
from datetime import datetime

class AnalyticsService:
    @staticmethod
    def calculate_summary(user, incomes, expenses, budget_limits, saving_goals):
        total_income = sum(inc.amount for inc in incomes)
        total_expense = sum(exp.amount for exp in expenses)
        net_savings = total_income - total_expense
        savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

        # Essential vs Discretionary breakdown
        essential_expenses = sum(exp.amount for exp in expenses if exp.is_essential)
        discretionary_expenses = sum(exp.amount for exp in expenses if not exp.is_essential)

        essential_ratio = round((essential_expenses / total_income * 100), 1) if total_income > 0 else 0.0
        discretionary_ratio = round((discretionary_expenses / total_income * 100), 1) if total_income > 0 else 0.0

        # Category spending aggregation
        category_spending = defaultdict(float)
        category_counts = defaultdict(int)
        for exp in expenses:
            category_spending[exp.category] += exp.amount
            category_counts[exp.category] += 1

        # Budget limits map
        limit_map = {b.category: b.monthly_limit for b in budget_limits}

        # Categories analysis
        categories_data = []
        overspent_categories = []
        warning_categories = []

        all_categories = sorted(set(list(category_spending.keys()) + list(limit_map.keys())))
        for cat in all_categories:
            spent = round(category_spending.get(cat, 0.0), 2)
            limit = limit_map.get(cat, None)
            pct = round((spent / limit * 100), 1) if (limit and limit > 0) else None

            status = "normal"
            if limit:
                if spent > limit:
                    status = "overspent"
                    overspent_categories.append({
                        "category": cat,
                        "spent": spent,
                        "limit": limit,
                        "over_by": round(spent - limit, 2),
                        "percent": pct
                    })
                elif spent >= (limit * 0.85):
                    status = "warning"
                    warning_categories.append({
                        "category": cat,
                        "spent": spent,
                        "limit": limit,
                        "remaining": round(limit - spent, 2),
                        "percent": pct
                    })

            categories_data.append({
                "category": cat,
                "spent": spent,
                "limit": limit,
                "percent": pct,
                "status": status,
                "count": category_counts.get(cat, 0)
            })

        # Calculate Financial Health Score (0 - 100)
        # Factors:
        # 1. Savings rate (ideal >= 20%): up to 35 pts
        # 2. Budget adherence (no overspending): up to 30 pts
        # 3. Essential vs discretionary balance (discretionary <= 30%): up to 20 pts
        # 4. Emergency & Goal progress: up to 15 pts
        score = 0

        # Savings rate score (max 35)
        if savings_rate >= 25:
            score += 35
        elif savings_rate >= 15:
            score += 28
        elif savings_rate >= 5:
            score += 20
        elif savings_rate >= 0:
            score += 10
        else:
            score += 0 # Negative cash flow

        # Budget adherence score (max 30)
        if len(overspent_categories) == 0 and len(warning_categories) == 0:
            score += 30
        elif len(overspent_categories) == 0:
            score += 24
        elif len(overspent_categories) == 1:
            score += 14
        elif len(overspent_categories) == 2:
            score += 8
        else:
            score += 3

        # Essential vs discretionary (max 20)
        if total_income > 0:
            if discretionary_ratio <= 25:
                score += 20
            elif discretionary_ratio <= 35:
                score += 15
            elif discretionary_ratio <= 45:
                score += 8
            else:
                score += 2
        else:
            score += 5

        # Goal progress score (max 15)
        total_goal_target = sum(g.target_amount for g in saving_goals)
        total_goal_current = sum(g.current_amount for g in saving_goals)
        if total_goal_target > 0:
            avg_progress = (total_goal_current / total_goal_target) * 100
            score += min(15, int(avg_progress * 0.15))
        else:
            score += 10

        health_rating = "Excellent"
        health_color = "#10b981" # Emerald
        if score < 50:
            health_rating = "Needs Attention"
            health_color = "#ef4444" # Red
        elif score < 70:
            health_rating = "Fair"
            health_color = "#f59e0b" # Amber
        elif score < 85:
            health_rating = "Good"
            health_color = "#3b82f6" # Blue

        # Spending by date / timeline
        daily_expenses = defaultdict(float)
        for exp in expenses:
            daily_expenses[exp.date] += exp.amount
        
        sorted_dates = sorted(daily_expenses.keys())
        timeline = [{
            "date": d,
            "amount": round(daily_expenses[d], 2)
        } for d in sorted_dates]

        # Calculate emergency runway in months (using current total saved in goals vs monthly expense)
        runway_months = round(total_goal_current / total_expense, 1) if total_expense > 0 else 0.0

        return {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_savings": round(net_savings, 2),
            "savings_rate": savings_rate,
            "essential_expenses": round(essential_expenses, 2),
            "discretionary_expenses": round(discretionary_expenses, 2),
            "essential_ratio": essential_ratio,
            "discretionary_ratio": discretionary_ratio,
            "categories": categories_data,
            "overspent_categories": overspent_categories,
            "warning_categories": warning_categories,
            "health_score": score,
            "health_rating": health_rating,
            "health_color": health_color,
            "timeline": timeline,
            "total_goal_saved": round(total_goal_current, 2),
            "total_goal_target": round(total_goal_target, 2),
            "runway_months": runway_months
        }
