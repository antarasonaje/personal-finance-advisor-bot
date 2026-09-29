# 🌟 FinAura • AI-Powered Personal Finance Advisor Bot

> **An intelligent, persona-adaptive financial planning assistant developed to help individuals and families take control of their finances with clarity and confidence.**

---

## 📖 Executive Summary & Overview

The **Personal Finance Advisor Bot (FinAura)** is a full-stack financial planning web application powered by **Flask**, **SQLAlchemy**, and an **AI Financial Analysis Engine** (supporting both Google Gemini 2.5 Flash and a built-in heuristic reasoning engine).

The platform eliminates manual spreadsheet tracking by automating budget generation, diagnosing overspending patterns, providing quantitative saving recommendations, calculating cash runway, and delivering structured monthly financial reports.

---

## 🎯 Supported Real-World Scenarios

The system comes pre-seeded with four distinct scenarios demonstrating the breadth of financial situations:

| Scenario | Persona Profile | Key Characteristics | System Focus & AI Strategy |
| :--- | :--- | :--- | :--- |
| **Scenario 1** | **Alex Johnson**<br>*(Salaried Professional)* | $5,800/mo steady income, fixed downtown rent, high dining & entertainment spend | Detects overspending in entertainment ($580 vs $400 limit), suggests automated payday transfers, 50/30/20 rebalancing |
| **Scenario 2** | **Maya Chen**<br>*(College Student)* | $1,150/mo total income (family allowance + campus tutoring), tight budget | Segregates essential vs discretionary expenditures, audits student subscriptions, curbs cafe runs to reach laptop savings goal |
| **Scenario 3** | **David Rivera**<br>*(Freelance Designer)* | $5,400/mo fluctuating income from 3 separate clients, irregular burn | Calculates emergency cash runway (in months), enforces 25% tax vault holdback, stabilizes lean vs flush months |
| **Scenario 4** | **The Sharma Family**<br>*(Household Manager)* | $8,200/mo dual-earner shared income, mortgage, school tuition, healthcare | Consolidated household reporting, identifies grocery overruns, bulk meal-planning optimizations, college 529 fund tracking |

---

## 🏛️ Scalable Architecture

```
d:/Capstone/
├── app.py                      # Flask Application, REST API endpoints, session controller
├── config.py                   # App configurations, SQLite path, secret keys
├── database.py                 # SQLAlchemy db instance
├── models.py                   # Data models: User, Income, Expense, BudgetLimit, SavingGoal, AIAdviceLog
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── services/
│   ├── analytics_service.py    # Financial heuristics, health scoring (0-100), overspending detection
│   ├── ai_advisor_service.py   # AI Engine: Gemini 2.5 Flash API + domain-specific fallback heuristics
│   └── seed_service.py         # Instant database seeding for all 4 scenarios
├── templates/
│   └── index.html              # Modern, accessible single-page interface
└── static/
    ├── css/
    │   └── styles.css          # Dark glassmorphism theme, CSS grid, print stylesheet for PDF export
    └── js/
        └── app.js              # State manager, Chart.js integrations, modal controllers, chat client
```

---

## 🚀 Key Features

1. **Multi-Persona Switcher:** Instantly switch between the 4 real-world user profiles with a single dropdown to experience tailored budgets, warnings, and AI insights.
2. **Real-Time Financial Health Scorecard (0–100):** Evaluates savings rate, budget adherence, essential-to-discretionary ratio, and active goal momentum.
3. **Automated Budget Planner:** Generates custom category caps based on user persona (50/30/20 for Salaried, 60/25/15 for Students, 45/25/30 for Freelancers, 65/15/20 for Households) with 1-click database application.
4. **Intelligent Overspending Alerts:** Real-time banner alerts when any category exceeds or approaches 85% of its monthly cap.
5. **Interactive AI Chatbot (FinAura):** Context-aware conversational assistant that answers quantitative questions ("Can I afford a $250 purchase?", "Analyze my spending leaks", "How to build an emergency fund").
6. **Consolidated Monthly Financial Report:** Executive summary format with cash flow highlights, overspending items, strategic recommendations, and **1-click PDF / Print export**.
7. **Savings Goals & Milestone Tracker:** Interactive progress bars with deposit triggers, days-to-target countdown, and emergency fund runway calculation.

---

## ⚡ Quickstart & Setup Guide

### 1. Requirements
- Python 3.10+ (tested on Python 3.14)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Run the Application
Navigate to the project root and launch `app.py`:

```bash
cd d:/Capstone
python app.py
```

The server starts locally at:
👉 **`http://127.0.0.1:5000`**

### 3. (Optional) Configure Gemini API Key
To enable live Google Gemini 2.5 Flash responses, edit `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(If no API key is provided, the system automatically uses its built-in persona-aware financial heuristics engine without any external dependencies).*

---

## 📊 Testing the 4 Scenarios

1. **Scenario 1 (Salaried):** Select *Alex Johnson* in the top-right persona selector. View the **Overspending Alert** on the Dashboard for Entertainment ($580 spend vs $400 limit). Click "AI Budget Planner" -> "Generate AI Budget Plan" to see how the system balances his discretionary spending.
2. **Scenario 2 (Student):** Switch to *Maya Chen*. Observe how her $800 allowance + $350 tutoring is tracked. Open the AI Chat tab and ask *"How can I save more as a student?"* to receive student-specific advice (campus discounts, cafe budgeting).
3. **Scenario 3 (Freelancer):** Switch to *David Rivera*. Check the **Incomes** tab to view multiple client retainers ($2,400 + $1,800 + $1,200). In the chat or dashboard, review his **Emergency Runway** (in months) and 25% tax vault strategy.
4. **Scenario 4 (Household):** Switch to *The Sharma Family*. Review the **Expenses** tab for shared mortgage, groceries ($1,320 spent vs $1,100 limit), and school tuition. Open the **Monthly Report** tab and click **Print / Save as PDF** to generate a clean family financial briefing.
