// FinAura Personal Finance Advisor - Application Script
let currentUserId = null;
let currentUser = null;
let currentSummary = null;
let charts = {};
let activeDepositGoalId = null;

// Currency Formatter
function formatCurrency(amount, currency = "$") {
    if (amount === undefined || amount === null || isNaN(amount)) return `${currency}0.00`;
    return `${currency}${Number(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Initialize Application on Page Load
document.addEventListener('DOMContentLoaded', async () => {
    // Set default dates in modals to today
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = ['incomeDate', 'expenseDate', 'goalTargetDate'];
    dateInputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = today;
    });

    await loadScenarios();
    await refreshAllData();
});

// Tab Navigation
function showTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick')?.includes(`'${tabId}'`));
    if (activeBtn) activeBtn.classList.add('active');

    const targetPane = document.getElementById(`tab-${tabId}`);
    if (targetPane) targetPane.classList.add('active');

    if (tabId === 'dashboard') {
        renderCharts();
    } else if (tabId === 'monthly-report') {
        loadMonthlyReport();
    } else if (tabId === 'ai-chat') {
        loadChatHistory();
    }
}

// Scenarios Handling
async function loadScenarios() {
    try {
        const res = await fetch('/api/scenarios');
        const data = await res.json();
        const selector = document.getElementById('scenarioSelector');
        selector.innerHTML = '';

        data.scenarios.forEach(sc => {
            const opt = document.createElement('option');
            opt.value = sc.id;
            opt.textContent = `${sc.name} (${sc.persona_type.toUpperCase()})`;
            if (sc.id === data.active_user_id) {
                opt.selected = true;
                currentUserId = sc.id;
            }
            selector.appendChild(opt);
        });
    } catch (e) {
        console.error("Failed to load scenarios:", e);
    }
}

async function switchScenario(userId) {
    try {
        const res = await fetch(`/api/switch-user/${userId}`, { method: 'POST' });
        if (res.ok) {
            currentUserId = userId;
            await refreshAllData();
            // Automatically switch back to Dashboard tab
            showTab('dashboard');
        }
    } catch (e) {
        console.error("Failed to switch scenario:", e);
    }
}

async function resetDemoData() {
    if (!confirm("Reset all 4 personas back to their pristine demonstration data?")) return;
    try {
        const res = await fetch('/api/reset-data', { method: 'POST' });
        if (res.ok) {
            await loadScenarios();
            await refreshAllData();
            alert("Demo data successfully reset!");
        }
    } catch (e) {
        console.error("Reset data error:", e);
    }
}

// Master Refresh Function
async function refreshAllData() {
    await loadAnalytics();
    await loadIncomes();
    await loadExpenses();
    await loadBudgets();
    await loadGoals();
}

// Analytics and Dashboard KPIs
async function loadAnalytics() {
    try {
        const res = await fetch('/api/analytics');
        const data = await res.json();
        currentUser = data.user;
        currentSummary = data.summary;

        updatePersonaBanner(currentUser);
        updateKPIs(currentUser, currentSummary);
        renderCharts();
    } catch (e) {
        console.error("Error loading analytics:", e);
    }
}

function updatePersonaBanner(user) {
    document.getElementById('personaName').textContent = user.name;
    const badge = document.getElementById('personaBadge');
    badge.textContent = user.persona_type;
    document.getElementById('personaTagline').textContent = user.tagline || 'Personal Budgeting';

    const avatar = document.getElementById('personaAvatar');
    avatar.style.backgroundColor = user.avatar_color || '#6366f1';
    const initials = user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    avatar.textContent = initials;

    document.getElementById('personaTargetIncome').textContent = formatCurrency(user.monthly_target_income, user.currency);
    document.getElementById('personaSavingsTarget').textContent = formatCurrency(user.monthly_savings_target, user.currency);
}

function updateKPIs(user, summary) {
    const curr = user.currency || "$";
    document.getElementById('kpiIncome').textContent = formatCurrency(summary.total_income, curr);
    document.getElementById('kpiExpense').textContent = formatCurrency(summary.total_expense, curr);
    document.getElementById('kpiNetSavings').textContent = formatCurrency(summary.net_savings, curr);

    const savingsRateEl = document.getElementById('kpiSavingsRate');
    savingsRateEl.textContent = `${summary.savings_rate}%`;
    savingsRateEl.className = summary.savings_rate >= 20 ? 'text-success' : (summary.savings_rate >= 10 ? 'text-warning' : 'text-danger');

    document.getElementById('kpiHealthScore').textContent = `${summary.health_score}/100`;
    const ratingBadge = document.getElementById('kpiHealthRating');
    ratingBadge.textContent = summary.health_rating;
    ratingBadge.style.backgroundColor = `${summary.health_color}33`;
    ratingBadge.style.color = summary.health_color;
    ratingBadge.style.border = `1px solid ${summary.health_color}`;

    document.getElementById('kpiRunway').textContent = `${summary.runway_months || 0.0} mo`;

    // Global Overspending Alert Banner
    const alertBanner = document.getElementById('globalAlertBanner');
    const alertText = document.getElementById('globalAlertText');
    if (summary.overspent_categories && summary.overspent_categories.length > 0) {
        const over = summary.overspent_categories[0];
        alertText.innerHTML = `<strong>Overspending Alert:</strong> You are <strong>${formatCurrency(over.over_by, curr)}</strong> over your monthly limit in <strong>${over.category.toUpperCase()}</strong>!`;
        alertBanner.className = 'alert-banner danger';
        alertBanner.style.display = 'flex';
    } else if (summary.warning_categories && summary.warning_categories.length > 0) {
        const warn = summary.warning_categories[0];
        alertText.innerHTML = `<strong>Notice:</strong> <strong>${warn.category.toUpperCase()}</strong> is at <strong>${warn.percent}%</strong> of its monthly limit.`;
        alertBanner.className = 'alert-banner warning';
        alertBanner.style.display = 'flex';
    } else {
        alertBanner.style.display = 'none';
    }
}

// Chart.js Visualizations
function renderCharts() {
    if (!currentSummary) return;

    // 1. Daily Spending Timeline
    const timelineCtx = document.getElementById('timelineChart')?.getContext('2d');
    if (timelineCtx) {
        if (charts.timeline) charts.timeline.destroy();
        const labels = currentSummary.timeline.map(t => t.date.substring(5)); // MM-DD
        const dataValues = currentSummary.timeline.map(t => t.amount);

        charts.timeline = new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: labels.length ? labels : ['No expenses'],
                datasets: [{
                    label: 'Daily Outflow ($)',
                    data: dataValues.length ? dataValues : [0],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.15)',
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.35,
                    pointRadius: 4,
                    pointBackgroundColor: '#818cf8'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                    y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }

    // 2. Category Donut Chart
    const donutCtx = document.getElementById('categoryDonutChart')?.getContext('2d');
    if (donutCtx) {
        if (charts.donut) charts.donut.destroy();
        const categories = currentSummary.categories.filter(c => c.spent > 0);
        const labels = categories.map(c => c.category.toUpperCase());
        const dataValues = categories.map(c => c.spent);
        const palette = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#06b6d4', '#8b5cf6', '#f43f5e', '#3b82f6'];

        charts.donut = new Chart(donutCtx, {
            type: 'doughnut',
            data: {
                labels: labels.length ? labels : ['No data'],
                datasets: [{
                    data: dataValues.length ? dataValues : [1],
                    backgroundColor: palette.slice(0, labels.length || 1),
                    borderWidth: 2,
                    borderColor: '#111827'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', boxWidth: 10, font: { size: 11 } }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 3. Essential vs Discretionary Chart
    const ratioCtx = document.getElementById('essentialRatioChart')?.getContext('2d');
    if (ratioCtx) {
        if (charts.ratio) charts.ratio.destroy();
        charts.ratio = new Chart(ratioCtx, {
            type: 'pie',
            data: {
                labels: [`Essential Needs ($${currentSummary.essential_expenses})`, `Discretionary Wants ($${currentSummary.discretionary_expenses})`],
                datasets: [{
                    data: [currentSummary.essential_expenses || 1, currentSummary.discretionary_expenses || 0],
                    backgroundColor: ['#10b981', '#f43f5e'],
                    borderWidth: 2,
                    borderColor: '#111827'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#cbd5e1', boxWidth: 12, font: { size: 12 } }
                    }
                }
            }
        });
    }

    // 4. Cash Flow Comparison Bar Chart
    const cashflowCtx = document.getElementById('cashflowBarChart')?.getContext('2d');
    if (cashflowCtx) {
        if (charts.cashflow) charts.cashflow.destroy();
        charts.cashflow = new Chart(cashflowCtx, {
            type: 'bar',
            data: {
                labels: ['Monthly Inflow', 'Monthly Outflow', 'Net Savings'],
                datasets: [{
                    data: [currentSummary.total_income, currentSummary.total_expense, Math.max(0, currentSummary.net_savings)],
                    backgroundColor: ['#6366f1', '#f43f5e', '#10b981'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#cbd5e1' } },
                    y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }
}

// Incomes Management
async function loadIncomes() {
    try {
        const res = await fetch('/api/incomes');
        const incomes = await res.json();
        const tbody = document.getElementById('incomesTableBody');
        tbody.innerHTML = '';
        document.getElementById('incomeCountBadge').textContent = `${incomes.length} records`;

        const curr = currentUser ? currentUser.currency : "$";

        if (incomes.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No income entries recorded yet.</td></tr>`;
            return;
        }

        incomes.forEach(inc => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="font-weight-600 text-white">${inc.source}</td>
                <td><span class="badge-tag" style="background: rgba(99, 102, 241, 0.15); color: #a5b4fc;">${inc.category}</span></td>
                <td>${inc.date}</td>
                <td>${inc.is_recurring ? '<span style="color: var(--accent-emerald);">● Recurring</span>' : '<span style="color: var(--text-muted);">One-time</span>'}</td>
                <td style="max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${inc.notes || '—'}</td>
                <td class="font-mono font-weight-700 text-success">${formatCurrency(inc.amount, curr)}</td>
                <td>
                    <button class="btn-secondary" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;" onclick="deleteIncome(${inc.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error loading incomes:", e);
    }
}

async function submitIncome() {
    const source = document.getElementById('incomeSource').value.trim();
    const amount = parseFloat(document.getElementById('incomeAmount').value);
    const category = document.getElementById('incomeCategory').value;
    const date = document.getElementById('incomeDate').value;
    const is_recurring = document.getElementById('incomeRecurring').checked;
    const notes = document.getElementById('incomeNotes').value.trim();

    if (!source || isNaN(amount) || amount <= 0) {
        alert("Please provide a valid source name and positive amount.");
        return;
    }

    try {
        const res = await fetch('/api/incomes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source, amount, category, date, is_recurring, notes })
        });
        if (res.ok) {
            closeModal('incomeModal');
            document.getElementById('incomeSource').value = '';
            document.getElementById('incomeAmount').value = '';
            document.getElementById('incomeNotes').value = '';
            await refreshAllData();
        }
    } catch (e) {
        console.error("Submit income error:", e);
    }
}

async function deleteIncome(id) {
    if (!confirm("Are you sure you want to remove this income entry?")) return;
    try {
        const res = await fetch(`/api/incomes/${id}`, { method: 'DELETE' });
        if (res.ok) await refreshAllData();
    } catch (e) {
        console.error("Delete income error:", e);
    }
}

// Expenses Management
async function loadExpenses() {
    try {
        const res = await fetch('/api/expenses');
        const expenses = await res.json();
        const tbody = document.getElementById('expensesTableBody');
        tbody.innerHTML = '';
        document.getElementById('expenseCountBadge').textContent = `${expenses.length} records`;

        const curr = currentUser ? currentUser.currency : "$";

        if (expenses.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No expenses recorded yet.</td></tr>`;
            return;
        }

        expenses.forEach(exp => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="font-weight-600 text-white">${exp.title}</td>
                <td><span class="badge-tag" style="background: rgba(30, 41, 59, 0.8);">${exp.category}</span></td>
                <td>
                    <span class="badge-tag ${exp.is_essential ? 'badge-essential' : 'badge-discretionary'}">
                        ${exp.is_essential ? 'Essential' : 'Discretionary'}
                    </span>
                </td>
                <td>${exp.date}</td>
                <td style="max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${exp.notes || '—'}</td>
                <td class="font-mono font-weight-700 text-danger">${formatCurrency(exp.amount, curr)}</td>
                <td>
                    <button class="btn-secondary" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;" onclick="deleteExpense(${exp.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error loading expenses:", e);
    }
}

async function submitExpense() {
    const title = document.getElementById('expenseTitle').value.trim();
    const amount = parseFloat(document.getElementById('expenseAmount').value);
    const category = document.getElementById('expenseCategory').value;
    const date = document.getElementById('expenseDate').value;
    const is_essential = document.getElementById('expenseEssential').checked;
    const notes = document.getElementById('expenseNotes').value.trim();

    if (!title || isNaN(amount) || amount <= 0) {
        alert("Please provide an expense title and positive amount.");
        return;
    }

    try {
        const res = await fetch('/api/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, amount, category, date, is_essential, notes })
        });
        if (res.ok) {
            closeModal('expenseModal');
            document.getElementById('expenseTitle').value = '';
            document.getElementById('expenseAmount').value = '';
            document.getElementById('expenseNotes').value = '';
            await refreshAllData();
        }
    } catch (e) {
        console.error("Submit expense error:", e);
    }
}

async function deleteExpense(id) {
    if (!confirm("Are you sure you want to remove this expense entry?")) return;
    try {
        const res = await fetch(`/api/expenses/${id}`, { method: 'DELETE' });
        if (res.ok) await refreshAllData();
    } catch (e) {
        console.error("Delete expense error:", e);
    }
}

// Budgets Management
async function loadBudgets() {
    try {
        if (!currentSummary) return;
        const tbody = document.getElementById('budgetsTableBody');
        tbody.innerHTML = '';
        const curr = currentUser ? currentUser.currency : "$";

        currentSummary.categories.forEach(cat => {
            const tr = document.createElement('tr');
            const pct = cat.percent ? `${cat.percent}%` : 'No limit set';
            let barFillClass = 'progress-fill-healthy';
            let statusBadge = '<span class="badge-tag" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">On Track</span>';
            let remainingText = cat.limit ? formatCurrency(Math.max(0, cat.limit - cat.spent), curr) : '—';

            if (cat.status === 'overspent') {
                barFillClass = 'progress-fill-danger';
                statusBadge = '<span class="badge-tag" style="background: rgba(239, 68, 68, 0.2); color: #f87171;">Over Budget!</span>';
                remainingText = `<span class="text-danger">+${formatCurrency(cat.spent - cat.limit, curr)} over</span>`;
            } else if (cat.status === 'warning') {
                barFillClass = 'progress-fill-warning';
                statusBadge = '<span class="badge-tag" style="background: rgba(245, 158, 11, 0.2); color: #fbbf24;">Near Limit</span>';
            }

            const fillWidth = cat.percent ? Math.min(100, cat.percent) : 0;

            tr.innerHTML = `
                <td class="font-weight-600 text-white" style="text-transform: capitalize;">${cat.category}</td>
                <td class="font-mono text-white">${formatCurrency(cat.spent, curr)}</td>
                <td class="font-mono text-secondary">${cat.limit ? formatCurrency(cat.limit, curr) : 'Not Capped'}</td>
                <td style="min-width: 220px;">
                    <div class="budget-progress-container">
                        <div class="budget-progress-labels">
                            <span>${statusBadge}</span>
                            <span class="font-mono" style="font-size: 0.75rem;">${pct}</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill ${barFillClass}" style="width: ${fillWidth}%;"></div>
                        </div>
                    </div>
                </td>
                <td class="font-mono">${remainingText}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error loading budgets:", e);
    }
}

async function submitBudgetLimit() {
    const category = document.getElementById('budgetCategory').value;
    const monthly_limit = parseFloat(document.getElementById('budgetLimitAmount').value);

    if (isNaN(monthly_limit) || monthly_limit <= 0) {
        alert("Please enter a positive limit amount.");
        return;
    }

    try {
        const res = await fetch('/api/budgets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, monthly_limit })
        });
        if (res.ok) {
            closeModal('budgetModal');
            document.getElementById('budgetLimitAmount').value = '';
            await refreshAllData();
        }
    } catch (e) {
        console.error("Submit budget limit error:", e);
    }
}

// AI Budget Planner
async function generateAiBudgetPlan() {
    try {
        const res = await fetch('/api/ai/budget-plan');
        const plan = await res.json();
        const curr = currentUser ? currentUser.currency : "$";

        document.getElementById('aiPlanModelName').textContent = plan.model_name;
        document.getElementById('aiPlanRationale').textContent = plan.rationale;

        document.getElementById('aiPlanNeedsPct').textContent = `${plan.needs.percentage}%`;
        document.getElementById('aiPlanNeedsAmt').textContent = formatCurrency(plan.needs.amount, curr);

        document.getElementById('aiPlanWantsPct').textContent = `${plan.wants.percentage}%`;
        document.getElementById('aiPlanWantsAmt').textContent = formatCurrency(plan.wants.amount, curr);

        document.getElementById('aiPlanSavingsPct').textContent = `${plan.savings.percentage}%`;
        document.getElementById('aiPlanSavingsAmt').textContent = formatCurrency(plan.savings.amount, curr);

        document.getElementById('aiBudgetPlanContainer').style.display = 'block';
    } catch (e) {
        console.error("Generate AI budget plan error:", e);
    }
}

async function applyAiBudgetPlan() {
    try {
        const res = await fetch('/api/ai/apply-budget-plan', { method: 'POST' });
        if (res.ok) {
            alert("AI Recommended Budget limits successfully applied to your active profile!");
            await refreshAllData();
        }
    } catch (e) {
        console.error("Apply budget plan error:", e);
    }
}

// Goals Management
async function loadGoals() {
    try {
        const res = await fetch('/api/goals');
        const goals = await res.json();
        const grid = document.getElementById('goalsGrid');
        grid.innerHTML = '';
        const curr = currentUser ? currentUser.currency : "$";

        if (goals.length === 0) {
            grid.innerHTML = `<p style="grid-column: 1 / -1; color: var(--text-muted); text-align: center; padding: 2rem;">No saving goals configured yet.</p>`;
            return;
        }

        goals.forEach(g => {
            const card = document.createElement('div');
            card.className = 'goal-card';
            card.innerHTML = `
                <div>
                    <div class="goal-card-header">
                        <div>
                            <div class="goal-title">${g.title}</div>
                            <div class="goal-meta">Target: ${g.target_date} • ${g.category.replace('_', ' ')}</div>
                        </div>
                        <button class="btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.7rem;" onclick="deleteGoal(${g.id})">✕</button>
                    </div>
                    <div class="goal-amounts">
                        <span class="goal-current">${formatCurrency(g.current_amount, curr)}</span>
                        <span class="goal-target">of ${formatCurrency(g.target_amount, curr)}</span>
                    </div>
                    <div class="budget-progress-container">
                        <div class="budget-progress-labels">
                            <span style="font-size: 0.72rem; color: var(--text-muted);">Progress</span>
                            <span class="font-mono font-weight-700 text-white" style="font-size: 0.75rem;">${g.progress_pct}%</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill progress-fill-healthy" style="width: ${g.progress_pct}%;"></div>
                        </div>
                    </div>
                </div>
                <div class="goal-card-actions">
                    <span style="font-size: 0.78rem; color: var(--text-secondary);">
                        ${g.current_amount >= g.target_amount ? '🎉 Goal Achieved!' : `${formatCurrency(g.target_amount - g.current_amount, curr)} remaining`}
                    </span>
                    <button class="btn-primary" style="padding: 0.35rem 0.75rem; font-size: 0.78rem;" onclick="openDepositModal(${g.id}, '${g.title}')">+ Deposit</button>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (e) {
        console.error("Error loading goals:", e);
    }
}

async function submitGoal() {
    const title = document.getElementById('goalTitle').value.trim();
    const target_amount = parseFloat(document.getElementById('goalTargetAmount').value);
    const current_amount = parseFloat(document.getElementById('goalCurrentAmount').value || 0);
    const target_date = document.getElementById('goalTargetDate').value;

    if (!title || isNaN(target_amount) || target_amount <= 0) {
        alert("Please specify a goal title and target amount.");
        return;
    }

    try {
        const res = await fetch('/api/goals', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, target_amount, current_amount, target_date })
        });
        if (res.ok) {
            closeModal('goalModal');
            document.getElementById('goalTitle').value = '';
            document.getElementById('goalTargetAmount').value = '';
            document.getElementById('goalCurrentAmount').value = '';
            await refreshAllData();
        }
    } catch (e) {
        console.error("Submit goal error:", e);
    }
}

function openDepositModal(goalId, title) {
    activeDepositGoalId = goalId;
    document.getElementById('depositGoalTitle').textContent = `Depositing into: ${title}`;
    document.getElementById('depositAmount').value = '';
    openModal('depositModal');
}

async function submitDeposit() {
    const amount = parseFloat(document.getElementById('depositAmount').value);
    if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid deposit amount.");
        return;
    }

    try {
        const res = await fetch(`/api/goals/${activeDepositGoalId}/deposit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount })
        });
        if (res.ok) {
            closeModal('depositModal');
            await refreshAllData();
        }
    } catch (e) {
        console.error("Deposit error:", e);
    }
}

async function deleteGoal(id) {
    if (!confirm("Remove this saving goal?")) return;
    try {
        const res = await fetch(`/api/goals/${id}`, { method: 'DELETE' });
        if (res.ok) await refreshAllData();
    } catch (e) {
        console.error("Delete goal error:", e);
    }
}

// Monthly Report
async function loadMonthlyReport() {
    try {
        const res = await fetch('/api/ai/monthly-report');
        const report = await res.json();
        const curr = report.currency;

        document.getElementById('reportUserName').textContent = `${report.user_name} (${report.persona_type.toUpperCase()})`;
        document.getElementById('reportInflow').textContent = formatCurrency(report.total_income, curr);
        document.getElementById('reportOutflow').textContent = formatCurrency(report.total_expense, curr);
        document.getElementById('reportSavingsRate').textContent = `${report.savings_rate}%`;

        document.getElementById('reportPersonaAdvice').innerHTML = report.persona_advice;

        const overspentContainer = document.getElementById('reportOverspentList');
        if (report.overspent_categories && report.overspent_categories.length > 0) {
            overspentContainer.innerHTML = report.overspent_categories.map(o => `
                <div style="margin-bottom: 0.35rem;">
                    ⚠️ <strong style="color: var(--accent-rose);">${o.category.toUpperCase()}</strong>: 
                    Spent ${formatCurrency(o.spent, curr)} vs limit of ${formatCurrency(o.limit, curr)} 
                    (+${formatCurrency(o.over_by, curr)} over limit)
                </div>
            `).join('');
        } else {
            overspentContainer.innerHTML = `<span style="color: var(--accent-emerald);">✅ All categories operated strictly within allocated caps!</span>`;
        }

        const actionsList = document.getElementById('reportActionItems');
        actionsList.innerHTML = report.action_items.map(act => `
            <li class="report-action-item">
                <span class="icon">➔</span>
                <span>${act}</span>
            </li>
        `).join('');
    } catch (e) {
        console.error("Load monthly report error:", e);
    }
}

// AI Chatbot
async function loadChatHistory() {
    try {
        const res = await fetch('/api/ai/chat/history');
        const history = await res.json();
        const container = document.getElementById('chatMessages');
        container.innerHTML = '';

        if (history.length === 0) {
            container.innerHTML = `
                <div class="chat-bubble assistant">
                    <strong>FinAura Financial AI:</strong><br>
                    Hello! I'm your dedicated personal finance intelligence engine. I have real-time visibility into your income, expenses, category spending limits, and savings targets. Ask me how to optimize your cash flow, curb overspending, or plan for next month!
                </div>
            `;
            return;
        }

        history.forEach(item => {
            appendChatBubble(item.role, item.message, item.timestamp);
        });
        scrollChatToBottom();
    } catch (e) {
        console.error("Load chat error:", e);
    }
}

function appendChatBubble(role, message, timestamp = '') {
    const container = document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    // Format markdown-like headers and bullets simply
    let formatted = message
        .replace(/### (.*?)\n/g, '<h4 style="color:#a5b4fc;margin:0.5rem 0 0.2rem 0;">$1</h4>')
        .replace(/#### (.*?)\n/g, '<h5 style="color:#93c5fd;margin:0.4rem 0 0.2rem 0;">$1</h5>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n\* /g, '<br>• ');

    bubble.innerHTML = `
        <div>${formatted}</div>
        ${timestamp ? `<div class="chat-bubble-time">${timestamp}</div>` : ''}
    `;
    container.appendChild(bubble);
    scrollChatToBottom();
}

function scrollChatToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    appendChatBubble('user', message, nowTime);

    // Show temporary thinking bubble
    const container = document.getElementById('chatMessages');
    const loadingBubble = document.createElement('div');
    loadingBubble.id = 'chatLoadingBubble';
    loadingBubble.className = 'chat-bubble assistant';
    loadingBubble.innerHTML = `<em>FinAura is analyzing your financial transactions...</em>`;
    container.appendChild(loadingBubble);
    scrollChatToBottom();

    try {
        const res = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await res.json();
        const loadEl = document.getElementById('chatLoadingBubble');
        if (loadEl) loadEl.remove();

        if (data.reply) {
            appendChatBubble('assistant', data.reply, data.log?.timestamp || nowTime);
        }
    } catch (e) {
        console.error("Chat error:", e);
        const loadEl = document.getElementById('chatLoadingBubble');
        if (loadEl) loadEl.remove();
        appendChatBubble('assistant', "I encountered a communication issue. Please try again.");
    }
}

function handleChatKey(e) {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
}

function sendQuickPrompt(promptText) {
    document.getElementById('chatInput').value = promptText;
    sendChatMessage();
}

function clearChat() {
    const container = document.getElementById('chatMessages');
    container.innerHTML = `
        <div class="chat-bubble assistant">
            <strong>FinAura Financial AI:</strong><br>
            Chat history cleared. How can I assist you with your budget today?
        </div>
    `;
}

// Modal Helpers
function openModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.add('active');
}

function closeModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.remove('active');
}

function openIncomeModal() { openModal('incomeModal'); }
function openExpenseModal() { openModal('expenseModal'); }
function openBudgetModal() { openModal('budgetModal'); }
function openGoalModal() { openModal('goalModal'); }
