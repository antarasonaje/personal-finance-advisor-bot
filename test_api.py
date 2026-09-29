import urllib.request
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_tests():
    base_url = 'http://127.0.0.1:5000'
    
    # 1. Scenarios
    with urllib.request.urlopen(f'{base_url}/api/scenarios') as resp:
        data = json.loads(resp.read().decode())
        print(f"Scenarios loaded: {len(data['scenarios'])} | Active ID: {data['active_user_id']}")
        for s in data['scenarios']:
            print(f"  • ID {s['id']}: {s['name']} [{s['persona_type']}]")

    # 2. Analytics for Alex (Scenario 1)
    with urllib.request.urlopen(f'{base_url}/api/analytics') as resp:
        analytics = json.loads(resp.read().decode())
        summary = analytics['summary']
        print(f"\nScenario 1 Check:")
        print(f"  User: {analytics['user']['name']} ({analytics['user']['persona_type']})")
        print(f"  Income: ${summary['total_income']:,.2f} | Outflow: ${summary['total_expense']:,.2f} | Net Savings: ${summary['net_savings']:,.2f}")
        print(f"  Health Score: {summary['health_score']}/100 ({summary['health_rating']})")
        print(f"  Overspent Categories: {[o['category'] for o in summary['overspent_categories']]}")

    # 3. AI Budget Plan
    with urllib.request.urlopen(f'{base_url}/api/ai/budget-plan') as resp:
        plan = json.loads(resp.read().decode())
        print(f"\nAI Budget Plan Check:")
        print(f"  Model: {plan['model_name']}")
        print(f"  Needs: {plan['needs']['percentage']}% (${plan['needs']['amount']:,.2f})")
        print(f"  Wants: {plan['wants']['percentage']}% (${plan['wants']['amount']:,.2f})")
        print(f"  Savings: {plan['savings']['percentage']}% (${plan['savings']['amount']:,.2f})")

    # 4. AI Chat Bot
    chat_payload = json.dumps({'message': 'Analyze my overspending and suggest fixes'}).encode()
    chat_req = urllib.request.Request(
        f'{base_url}/api/ai/chat',
        data=chat_payload,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(chat_req) as resp:
        chat_data = json.loads(resp.read().decode())
        print(f"\nAI FinAura Chat Check:")
        print("  Snippet:", chat_data['reply'].split('\n')[0])
        print("  Full advice length:", len(chat_data['reply']), "characters")

    # 5. Monthly Report
    with urllib.request.urlopen(f'{base_url}/api/ai/monthly-report') as resp:
        report = json.loads(resp.read().decode())
        print(f"\nMonthly Report Check:")
        print(f"  Month: {report['report_month']} for {report['user_name']}")
        print(f"  Action items count: {len(report['action_items'])}")

    print("\n✅ ALL API TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
