with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
# Check if btn-start-questions exists
if "btn-start-questions" in text:
    idx = text.find("btn-start-questions")
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-100):idx+200])
    print("Found:", safe)
else:
    print("btn-start-questions NOT FOUND - need to add")
    
    # Add it to the live panel before the phase banner
    old = """        <div id="live-panel" style="display:none;margin-bottom:28px">
          <div style="text-align:center; margin-bottom:16px;">
            <button class="btn btn-danger" style="font-size:1.2rem;font-weight:900;padding:12px 32px;letter-spacing:1px;box-shadow:0 0 15px rgba(230,36,41,0.5);" onclick="startQuestions()" id="btn-start-questions">
              &#9654;&#65039; ARRANCAR PREGUNTAS (TODOS LISTOS)
            </button>
          </div>"""
    
    if old in text:
        print("Already has the button div")
    else:
        old2 = """        <div id="live-panel" style="display:none;margin-bottom:28px">
          <div id="live-phase-banner" """
        new2 = """        <div id="live-panel" style="display:none;margin-bottom:28px">
          <div style="text-align:center;margin-bottom:16px">
            <button class="btn btn-danger" onclick="startQuestions()" id="btn-start-questions"
              style="font-size:1.2rem;font-weight:900;padding:14px 36px;letter-spacing:1px;display:none">
              ARRANCAR PREGUNTAS
            </button>
          </div>
          <div id="live-phase-banner" """
        if old2 in text:
            text = text.replace(old2, new2)
            with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
                f.write(text)
            print("Added btn-start-questions OK")
        else:
            print("Could not add button, checking panel...")
            idx = text.find("live-panel")
            safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-20):idx+300])
            print(safe)
