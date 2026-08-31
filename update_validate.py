import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'r', encoding='utf-8') as f:
    text = f.read()

validation_logic = '''
            if data.get("is_multi"):
                answers = req.answer if isinstance(req.answer, list) else []
                correct_count = 0
                for i, q in enumerate(data["questions"]):
                    if i < len(answers) and str(answers[i]).strip().upper() == str(q.get("correct", "A")).strip().upper():
                        correct_count += 1
                
                correct = (correct_count == len(data["questions"]))
                explanation = f"Acertaste {correct_count} de {len(data['questions'])}. " + data["questions"][-1].get("explanation", "")
                concept = data["questions"][-1].get("concept", "")
                
                # Modificar puntos proporcionales? O solo si aciertas todo? 
                # Simplificamos: damos correcta si correct_count >= 1 (mitad de puntos) o 2 (full)
                # Pero el sistema de juegos da puntos si 'correct' == True. 
                # Vamos a decir que es correcta si acertó al menos la mitad.
                if correct_count > 0:
                    correct = True
                    if correct_count < len(data["questions"]):
                        explanation = "Aprobaste con algunas dudas. " + explanation
                else:
                    correct = False
            
            # store_mission - la tienda completa. Siempre correcto si el checkout fue completado
            elif mtype == "store_mission":
'''

text = re.sub(r'# store_mission - la tienda completa\..*?elif mtype == "store_mission":', validation_logic.strip(), text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'w', encoding='utf-8') as f:
    f.write(text)
