import json
import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Revert get_pool duplication
text = text.replace('others = others + others', '')
text = text.replace('# 2 misiones de cada tipo', '')

# 2. Update generators to return is_multi
def make_multi(bank_name, func_name):
    replacement = f'''
def {func_name}():
    import random
    qs = random.sample({bank_name}, min(2, len({bank_name})))
    questions = []
    for q in qs:
        opts, correct = _shuffle_choices(q['options'], q.get('correct') or q.get('correct_id', ''))
        questions.append({{
            'scenario': q.get('scenario', q.get('intro', '')),
            'question': q.get('question', ''),
            'options': opts,
            'correct': correct,
            'explanation': q.get('explanation', ''),
            'concept': q.get('concept', ''),
            'listings': q.get('listings', q.get('products', []))
        }})
    return {{
        'is_multi': True,
        'questions': questions,
        'topic': qs[0].get('topic', 'E-Commerce')
    }}
'''
    global text
    text = re.sub(rf'def {func_name}\(\):.*?(?=def _gen_|\n\ndef |\Z)', replacement, text, flags=re.DOTALL)

make_multi('ECOM_DECISION_BANK', '_gen_ecom_decision')
make_multi('FRAUD_DETECT_BANK', '_gen_fraud_detect')
make_multi('CHECKOUT_DEBUG_BANK', '_gen_checkout_debug')
make_multi('MARKETING_BANK', '_gen_speed_search')

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'w', encoding='utf-8') as f:
    f.write(text)
