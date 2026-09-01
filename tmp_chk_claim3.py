import os
for root, dirs, files in os.walk(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api"):
    for file in files:
        if file.endswith(".py"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                content = f.read()
                if "class ClaimRewardRequest" in content:
                    print("Found in:", file)
                    idx = content.find("class ClaimRewardRequest")
                    print(content[idx:idx+300])
