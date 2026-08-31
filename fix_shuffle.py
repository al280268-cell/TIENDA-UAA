import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace _shuffle_choices to handle elements without 'text' (like 'name')
patch = r'''
def _shuffle_choices(options, correct_id):
    if not options: return [], ""
    # Find the correct item text/name
    correct_val = ""
    for o in options:
        if str(o.get("id")) == str(correct_id):
            correct_val = o.get("text") or o.get("name") or str(o.get("id"))
            break
            
    opts = options[:]
    random.shuffle(opts)
    
    # After shuffle, find the new index/id of the correct item
    new_correct = ""
    for idx, o in enumerate(opts):
        val = o.get("text") or o.get("name") or str(o.get("id"))
        if val == correct_val:
            new_correct = o.get("id", str(idx))
            break
            
    # Assign alphabetical IDs if they don't have them
    for i, o in enumerate(opts):
        o["id"] = chr(65 + i)
        if (o.get("text") or o.get("name") or str(o.get("id"))) == correct_val:
            new_correct = o["id"]
            
    return opts, new_correct
'''

text = re.sub(r'def _shuffle_choices\(options, correct_id\):.*?(?=\ndef )', patch.strip(), text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed _shuffle_choices")
