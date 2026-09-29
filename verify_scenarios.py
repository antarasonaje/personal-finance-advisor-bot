import urllib.request
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_all_scenarios():
    base_url = 'http://127.0.0.1:5000'
    scenarios_to_test = [
        (1, "Alex Johnson", "salaried"),
        (2, "Maya Chen", "student"),
        (3, "David Rivera", "freelancer"),
        (4, "The Sharma Family", "household")
    ]

    print("=" * 65)
    print("FINAURA ALL 4 SCENARIOS DETAILED VERIFICATION")
    print("=" * 65)

    for uid, expected_name, expected_persona in scenarios_to_test:
        # Check analytics with user_id
        with urllib.request.urlopen(f'{base_url}/api/analytics?user_id={uid}') as resp:
            data = json.loads(resp.read().decode())
            user = data['user']
            summary = data['summary']

            assert user['name'] == expected_name
            assert user['persona_type'] == expected_persona

            print(f"\n[Scenario {uid}] {user['name']} ({user['persona_type'].upper()})")
            print(f"  • Tagline: {user['tagline']}")
            print(f"  • Total Income: ${summary['total_income']:,.2f}")
            print(f"  • Total Expense: ${summary['total_expense']:,.2f}")
            print(f"  • Net Savings: ${summary['net_savings']:,.2f} (Savings Rate: {summary['savings_rate']}%)")
            print(f"  • Health Score: {summary['health_score']}/100 [{summary['health_rating']}]")
            print(f"  • Emergency Runway: {summary['runway_months']} months")
            print(f"  • Essential / Discretionary Ratio: {summary['essential_ratio']}% / {summary['discretionary_ratio']}%")
            print(f"  • Overspent: {[o['category'] for o in summary['overspent_categories']] or 'None'}")
            print(f"  • Near Limit: {[w['category'] for w in summary['warning_categories']] or 'None'}")

        # Check AI Monthly Report with user_id
        with urllib.request.urlopen(f'{base_url}/api/ai/monthly-report?user_id={uid}') as resp:
            rep = json.loads(resp.read().decode())
            print(f"  • Monthly Report Focus: {rep['persona_advice'][:130]}...")

        # Check AI Chat response with user_id
        chat_payload = json.dumps({'message': f'How can I improve my savings as a {expected_persona}?'}).encode()
        chat_req = urllib.request.Request(
            f'{base_url}/api/ai/chat?user_id={uid}',
            data=chat_payload,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(chat_req) as resp:
            chat_data = json.loads(resp.read().decode())
            print(f"  • AI FinAura Bot Advice Preview: {chat_data['reply'].splitlines()[0]}")

    print("\n" + "=" * 65)
    print("ALL 4 REAL-WORLD SCENARIOS VERIFIED 100% SUCCESSFULLY!")
    print("=" * 65)

if __name__ == '__main__':
    test_all_scenarios()
