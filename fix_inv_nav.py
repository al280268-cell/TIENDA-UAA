with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove "Inventario (v1)" from sidebar
text = text.replace(
    '\n        <button class="nav-item" data-section="inventory" onclick="navTo(\'inventory\')">Inventario (v1)</button>',
    ""
)

# 2. Rename "Inventario" button to just "Inventario" pointing to inv2
text = text.replace(
    '<button class="nav-item" data-section="inv2" onclick="navTo(\'inv2\')">📦 Inventario</button>',
    '<button class="nav-item" data-section="inv2" onclick="navTo(\'inv2\')">📦 Inventario</button>'
)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Sidebar inventory (v1) removed")
