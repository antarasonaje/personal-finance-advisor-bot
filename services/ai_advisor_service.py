import os
import json
from services.analytics_service import AnalyticsService

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class AIAdvisorService:
    @staticmethod
    def get_financial_context(user, summary, saving_goals):
        """Construct a structured summary of the user's finances for the AI model"""
        goals_text = ", ".join([f"{g.title}: {user.currency}{g.current_amount:,.2f}/{user.currency}{g.target_amount:,.2f} ({g.to_dict()['progress_pct']}%)" for g in saving_goals])
        overspent_text = ", ".join([f"{o['category'].capitalize()} (+{user.currency}{o['over_by']:,.2f} over limit {user.currency}{o['limit']:,.2f})" for o in summary['overspent_categories']]) or "None"
        warning_text = ", ".join([f"{w['category'].capitalize()} ({w['percent']}% of limit)" for w in summary['warning_categories']]) or "None"

        return f"""
Profile Name: {user.name}
Persona: {user.persona_type.upper()} ({user.tagline})
Monthly Income: {user.currency}{summary['total_income']:,.2f}
Monthly Expenses: {user.currency}{summary['total_expense']:,.2f}
Net Savings: {user.currency}{summary['net_savings']:,.2f} (Savings Rate: {summary['savings_rate']}%)
Essential Expenses: {user.currency}{summary['essential_expenses']:,.2f} ({summary['essential_ratio']}% of income)
Discretionary Expenses: {user.currency}{summary['discretionary_expenses']:,.2f} ({summary['discretionary_ratio']}% of income)
Financial Health Score: {summary['health_score']}/100 ({summary['health_rating']})
Emergency Runway: {summary.get('runway_months', 0.0)} months of expenses
Overspent Categories: {overspent_text}
Near-Limit Categories: {warning_text}
Active Saving Goals: {goals_text or 'None'}
"""

    @classmethod
    def generate_chat_response(cls, user, user_message, summary, saving_goals, chat_history=None):
        """Generates AI financial advice either through Gemini API or the built-in financial heuristics engine"""
        api_key = os.getenv("GEMINI_API_KEY")
        
        # Try Gemini API if key is present
        if api_key and GENAI_AVAILABLE:
            try:
                client = genai.Client(api_key=api_key)
                context = cls.get_financial_context(user, summary, saving_goals)
                system_instruction = f"""You are 'FinAura', an elite AI Personal Finance Advisor built into a modern personal finance management platform.
You are counseling {user.name}, who is categorized as a {user.persona_type}.
Current Financial Snapshot:
{context}

Guidelines:
1. Provide personalized, highly quantitative, empathetic, and actionable advice.
2. Directly reference their actual income, expenses, category leaks, or savings goals.
3. Keep answers concise, visually formatted with bullet points and bold highlights.
4. If they ask about spending cuts, prioritize discretionary vs essential items and calculate real monetary savings.
5. If they are a freelancer, focus on income volatility and emergency buffer. If a student, focus on student discounts, cafe/subscription limits. If household, focus on bulk groceries, utility efficiency, and education funds. If salaried, focus on automated savings and capping entertainment.
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{system_instruction}\n\nUser Question: {user_message}"
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"[AI Advisor] Gemini API call failed: {e}. Falling back to internal heuristic engine.")

        # Fallback to rich persona-aware AI engine
        return cls._generate_heuristic_response(user, user_message, summary, saving_goals)

    @classmethod
    def _generate_heuristic_response(cls, user, message, summary, saving_goals):
        """Intelligent contextual financial reasoning engine"""
        msg_lower = message.lower()
        curr = user.currency
        persona = user.persona_type.lower()
        
        # Scenario 1: Salaried Professional or general overspending
        if "overspend" in msg_lower or "budget" in msg_lower or "leak" in msg_lower or "entertainment" in msg_lower or "dining" in msg_lower:
            if summary['overspent_categories']:
                over = summary['overspent_categories'][0]
                return f"""### 📊 Overspending Analysis for {user.name}

Our financial engine has detected that you've exceeded your monthly allowance in **{over['category'].capitalize()}**:
* **Current Spend:** {curr}{over['spent']:,.2f} (Limit: {curr}{over['limit']:,.2f})
* **Over Budget by:** `{curr}{over['over_by']:,.2f}` (+{over['percent'] - 100:.1f}%)

#### 🎯 Actionable Remediation Plan:
1. **The 48-Hour Discretionary Rule:** Delay non-essential weekend outings or luxury purchases by 48 hours to curb impulse spending.
2. **Category Cap Rebalancing:** Reallocate {curr}{over['over_by']:,.2f} from your discretionary buffer for the remaining days of the month.
3. **Automate Savings First:** Schedule an automated transfer of {curr}{user.monthly_savings_target:,.2f} right on payday before discretionary spending occurs.

With this adjustment, your monthly savings will rebound to **{curr}{summary['net_savings'] + over['over_by']:,.2f}**!"""

        # Scenario 2: Student
        if "student" in persona or "allowance" in msg_lower or "coffee" in msg_lower or "discretionary" in msg_lower or "cafe" in msg_lower:
            return f"""### 🎓 Student Financial Discipline Strategy

Hey {user.name}! With a monthly allowance/income of **{curr}{summary['total_income']:,.2f}**, preserving capital while enjoying student life requires smart boundaries:

* **Discretionary Spending:** Currently **{summary['discretionary_ratio']}%** of your total budget ({curr}{summary['discretionary_expenses']:,.2f}).
* **Essential Needs (Rent, Books, Basic Food):** Consuming **{summary['essential_ratio']}%** ({curr}{summary['essential_expenses']:,.2f}).

#### 💡 Smart Student Savings Moves:
1. **Campus Subscriptions Audit:** Audit shared Spotify, Netflix, or cloud storage plans—switch to verified Student ID discounts to instantly save **{curr}15-{curr}25/mo**.
2. **The "Coffee & Dining" Rule:** Swap 3 takeout/cafe meals per week for home prep or campus dining. Potential monthly savings: **{curr}90 - {curr}140**.
3. **Micro-Savings Goal:** Direct just {curr}15 weekly into your reserve fund to graduate with an emergency cushion!"""

        # Scenario 3: Freelancer
        if "freelance" in persona or "variable" in msg_lower or "client" in msg_lower or "buffer" in msg_lower or "tax" in msg_lower or "emergency" in msg_lower or "runway" in msg_lower:
            avg_expense = summary['total_expense']
            recommended_buffer = avg_expense * 6
            return f"""### 💼 Variable Income & Cash Flow Buffer Advisory

Hello {user.name}! As a freelancer with variable project payouts, your priority is smoothing the peaks and valleys of irregular cash flow:

* **Current Monthly Inflow:** {curr}{summary['total_income']:,.2f} across active client streams.
* **Monthly Operating & Living Burn:** {curr}{summary['total_expense']:,.2f}.
* **Current Net Surplus:** {curr}{summary['net_savings']:,.2f} (Savings Rate: **{summary['savings_rate']}%**).
* **Current Emergency Runway:** **{summary.get('runway_months', 0.0)} months** of basic living expenses.

#### 🛡️ Stability Framework:
1. **Tax Holdback Reserve (25% Rule):** Immediately escrow 25% of every invoice into a dedicated high-yield tax vault before taking distributions.
2. **6-Month Emergency Runway Target:** For your monthly baseline of {curr}{avg_expense:,.2f}, your optimal safety cushion is **{curr}{recommended_buffer:,.2f}**.
3. **Lean Month Buffer:** During high-earning months, cap personal spending at {curr}{avg_expense:,.2f} and route 100% of overflow into your project continuity fund."""

        # Scenario 4: Household Manager
        if "household" in persona or "family" in msg_lower or "groceries" in msg_lower or "utilities" in msg_lower or "shared" in msg_lower or "tuition" in msg_lower:
            return f"""### 🏡 Household Budget & Shared Resource Optimization

Hello {user.name}! Managing shared household finances across multiple family members requires structured category allocations:

* **Consolidated Family Income:** {curr}{summary['total_income']:,.2f}
* **Combined Outflow:** {curr}{summary['total_expense']:,.2f} ({summary['essential_ratio']}% essential needs)
* **Monthly Family Savings Surplus:** {curr}{summary['net_savings']:,.2f}

#### 📋 Household Action Recommendations:
1. **Grocery & Meal Prep Batching:** Meal planning in bi-weekly cycles and wholesale purchasing can reduce food waste by 18%, saving approximately **{curr}160 - {curr}220/mo**.
2. **Utility Conservation:** Programmable thermostats and off-peak appliance schedules typically reduce monthly utility bills by 10-15%.
3. **Dedicated Education & Emergency Buckets:** Automate contributions toward children's college education and medical emergency reserves at the start of each billing cycle."""

        # 50/30/20 or personalized budget request
        if "50/30/20" in msg_lower or "recommend budget" in msg_lower or "budget plan" in msg_lower:
            budget = cls.generate_personalized_budget(user, summary)
            return f"""### 📐 Generated Budget Plan: {budget['model_name']}

Based on your current monthly income of **{curr}{budget['income']:,.2f}**, here is your optimal allocation:

* **Needs ({budget['needs']['percentage']}%):** `{curr}{budget['needs']['amount']:,.2f}` (Housing, groceries, utilities, transit)
* **Wants ({budget['wants']['percentage']}%):** `{curr}{budget['wants']['amount']:,.2f}` (Dining out, entertainment, shopping)
* **Savings & Investments ({budget['savings']['percentage']}%):** `{curr}{budget['savings']['amount']:,.2f}` (Emergency fund, goals)

**Rationale:** {budget['rationale']}

*You can click **"Apply Recommended Budget"** in the Budget tab to apply these category limits automatically!*"""

        # Can I afford
        if "afford" in msg_lower or "can i" in msg_lower or "buy" in msg_lower:
            surplus = summary['net_savings']
            if surplus > 300:
                verdict = f"✅ **Yes, you can afford reasonable discretionary purchases this month.** You currently have a net cash buffer of **{curr}{surplus:,.2f}**."
            elif surplus > 0:
                verdict = f"⚠️ **Proceed with caution.** You have a modest surplus of **{curr}{surplus:,.2f}**, but approaching category thresholds."
            else:
                verdict = f"🛑 **Hold off on non-essential purchases.** You are running a deficit of **{curr}{abs(surplus):,.2f}** this billing cycle."

            return f"""### 💳 Affordability Check

{verdict}

* **Total Income:** {curr}{summary['total_income']:,.2f}
* **Committed Expenses:** {curr}{summary['total_expense']:,.2f}
* **Safe Spending Buffer Remaining:** {curr}{max(0.0, surplus):,.2f}

*Tip: Before purchasing, check if the expense fits within your category allowance or if it encroaches upon your savings target.*"""

        # General savings question
        if "save" in msg_lower or "how to" in msg_lower or "more" in msg_lower:
            return f"""### 🚀 Wealth Acceleration & Savings Plan

Here is your tailored strategy to boost your monthly savings rate from **{summary['savings_rate']}%** to **{min(50, summary['savings_rate'] + 10)}%**:

1. **Trim Discretionary Outflows:** Your discretionary spending is currently **{curr}{summary['discretionary_expenses']:,.2f}**. Trimming just 15% here yields an immediate **+{curr}{summary['discretionary_expenses'] * 0.15:,.2f}** in monthly cash flow.
2. **Review Category Limits:** You have {len(summary['overspent_categories'])} category overruns. Eliminating these deficits will retain **{curr}{sum(o['over_by'] for o in summary['overspent_categories']):,.2f}** in your bank account.
3. **Compound Goal Allocation:** Channel surplus directly into your active goals ({', '.join([g.title for g in saving_goals]) or 'Emergency Fund'}).

Ask me: *"Generate a 50/30/20 budget"* to automatically calculate optimal category limits!"""

        # Default comprehensive briefing
        return f"""### 🤖 FinAura Financial Health Assessment

Hello {user.name}! Here is the current financial diagnostic for your profile:

* **Financial Health Score:** **{summary['health_score']}/100** ({summary['health_rating']})
* **Monthly Cash Flow:** Inflow of **{curr}{summary['total_income']:,.2f}** vs Outflow of **{curr}{summary['total_expense']:,.2f}**
* **Net Savings Rate:** **{summary['savings_rate']}%** (Target: {curr}{user.monthly_savings_target:,.2f})
* **Essential vs Discretionary:** {summary['essential_ratio']}% Essential / {summary['discretionary_ratio']}% Discretionary
* **Emergency Buffer Runway:** {summary.get('runway_months', 0.0)} months

**Suggested Actions:**
1. Check overspent categories: {", ".join([o['category'].capitalize() for o in summary['overspent_categories']]) or "All categories within limit!"}
2. Review your savings goals and keep your monthly streak alive.
3. Try asking: *"How can I optimize my spending?"* or *"Generate 50/30/20 budget"*"""

    @classmethod
    def generate_personalized_budget(cls, user, summary):
        """Generates a customized 50/30/20 or persona-tailored budget recommendation"""
        income = summary['total_income'] if summary['total_income'] > 0 else user.monthly_target_income
        curr = user.currency
        persona = user.persona_type.lower()

        if persona == 'student':
            # Needs 60%, Discretionary 25%, Savings 15%
            needs_pct, wants_pct, savings_pct = 60, 25, 15
        elif persona == 'freelancer':
            # Needs 45%, Discretionary 25%, Savings/Emergency Buffer 30%
            needs_pct, wants_pct, savings_pct = 45, 25, 30
        elif persona == 'household':
            # Needs 65%, Discretionary 15%, Savings/Education 20%
            needs_pct, wants_pct, savings_pct = 65, 15, 20
        else: # Salaried default 50/30/20
            needs_pct, wants_pct, savings_pct = 50, 30, 20

        needs_val = round(income * (needs_pct / 100), 2)
        wants_val = round(income * (wants_pct / 100), 2)
        savings_val = round(income * (savings_pct / 100), 2)

        # Category specific recommendations based on persona
        categories = {}
        if persona == 'salaried':
            categories = {
                "rent": round(income * 0.32, 2),
                "food": round(income * 0.12, 2),
                "transport": round(income * 0.06, 2),
                "entertainment": round(income * 0.08, 2),
                "utilities": round(income * 0.05, 2),
                "shopping": round(income * 0.07, 2),
                "healthcare": round(income * 0.05, 2),
                "other": round(income * 0.05, 2)
            }
        elif persona == 'student':
            categories = {
                "rent": round(income * 0.40, 2),
                "food": round(income * 0.25, 2),
                "transport": round(income * 0.08, 2),
                "education": round(income * 0.10, 2),
                "entertainment": round(income * 0.10, 2),
                "other": round(income * 0.07, 2)
            }
        elif persona == 'freelancer':
            categories = {
                "rent": round(income * 0.28, 2),
                "work_project": round(income * 0.12, 2),
                "food": round(income * 0.12, 2),
                "transport": round(income * 0.05, 2),
                "entertainment": round(income * 0.08, 2),
                "utilities": round(income * 0.05, 2),
                "other": round(income * 0.05, 2)
            }
        elif persona == 'household':
            categories = {
                "rent": round(income * 0.30, 2),
                "groceries": round(income * 0.16, 2),
                "education": round(income * 0.14, 2),
                "utilities": round(income * 0.08, 2),
                "healthcare": round(income * 0.08, 2),
                "transport": round(income * 0.06, 2),
                "other": round(income * 0.04, 2)
            }
        else:
            categories = {
                "rent": round(income * 0.30, 2),
                "food": round(income * 0.15, 2),
                "transport": round(income * 0.08, 2),
                "entertainment": round(income * 0.10, 2),
                "utilities": round(income * 0.07, 2),
                "other": round(income * 0.10, 2)
            }

        return {
            "model_name": f"{needs_pct}/{wants_pct}/{savings_pct} Personalized Plan ({persona.capitalize()} Profile)",
            "income": income,
            "needs": {"percentage": needs_pct, "amount": needs_val},
            "wants": {"percentage": wants_pct, "amount": wants_val},
            "savings": {"percentage": savings_pct, "amount": savings_val},
            "category_limits": categories,
            "rationale": f"Based on your profile as a {persona}, this plan balances necessary fixed expenditures with a robust {savings_pct}% monthly savings allocation."
        }

    @classmethod
    def generate_monthly_report(cls, user, summary, saving_goals):
        """Generates a structured comprehensive monthly financial report"""
        curr = user.currency
        persona = user.persona_type.lower()
        
        # Determine persona highlight
        persona_advice = ""
        if persona == "salaried":
            persona_advice = (
                f"**Salaried Executive Review:** Total income of {curr}{summary['total_income']:,.2f} yielded "
                f"{curr}{summary['net_savings']:,.2f} in savings ({summary['savings_rate']}% rate). "
                f"Overspending in entertainment should be curbed by automating transfer of {curr}{user.monthly_savings_target:,.2f} on salary day."
            )
        elif persona == "student":
            persona_advice = (
                f"**Student Cashflow Review:** Managed limited monthly allowance of {curr}{summary['total_income']:,.2f}. "
                f"Discretionary spending represents {summary['discretionary_ratio']}% of total funds. "
                "Switching campus dining and leveraging student discounts will unlock up to 15% more monthly savings."
            )
        elif persona == "freelancer":
            persona_advice = (
                f"**Freelance Variable Cashflow Review:** Aggregated {curr}{summary['total_income']:,.2f} from multiple client invoices. "
                f"Current cash runway stands at {summary.get('runway_months', 0.0)} months. Maintain the 25% tax escrow rule "
                "and channel excess earnings during peak months into the 6-month emergency reserve."
            )
        elif persona == "household":
            persona_advice = (
                f"**Household Family Review:** Consolidated family income reached {curr}{summary['total_income']:,.2f} with "
                f"{summary['essential_ratio']}% allocated to essential family needs (groceries, school tuition, healthcare). "
                "Implementing bi-weekly bulk grocery purchase schedules can trim kitchen overhead by 15-18%."
            )
        else:
            persona_advice = f"Strong financial foundation with a savings rate of {summary['savings_rate']}%."

        # Strategic Action Items
        actions = []
        if summary['overspent_categories']:
            for over in summary['overspent_categories']:
                actions.append(f"Trim spend in **{over['category'].capitalize()}** by {curr}{over['over_by']:,.2f} to return within allocated limit.")
        else:
            actions.append("All category expenses stayed within designated budget caps.")

        if summary['savings_rate'] < 20:
            actions.append("Increase monthly savings rate to at least 20% by cutting non-essential subscriptions and entertainment.")
        else:
            actions.append(f"Maintain commendable {summary['savings_rate']}% savings velocity into long-term wealth assets.")

        if saving_goals:
            top_goal = saving_goals[0]
            actions.append(f"Target milestone for **{top_goal.title}**: Add {curr}{max(50.0, (top_goal.target_amount - top_goal.current_amount) * 0.1):,.2f} next month.")

        return {
            "report_month": "September 2026",
            "user_name": user.name,
            "persona_type": user.persona_type,
            "currency": curr,
            "financial_health_score": summary['health_score'],
            "financial_health_rating": summary['health_rating'],
            "total_income": summary['total_income'],
            "total_expense": summary['total_expense'],
            "net_savings": summary['net_savings'],
            "savings_rate": summary['savings_rate'],
            "essential_ratio": summary['essential_ratio'],
            "discretionary_ratio": summary['discretionary_ratio'],
            "overspent_categories": summary['overspent_categories'],
            "warning_categories": summary['warning_categories'],
            "persona_advice": persona_advice,
            "action_items": actions,
            "goals_summary": [g.to_dict() for g in saving_goals]
        }
