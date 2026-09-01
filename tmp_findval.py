import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("/api/")
import os
for root, dirs, files in os.walk(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api"):
    for file in files:
        if file.endswith(".py"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                content = f.read()
                if "/validate" in content or "def validate" in content:
                    print("Found validate in:", file)
                    
