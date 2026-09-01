with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Remove the old "else if inventory" line since we removed that section
text = text.replace(
    "      else if (Admin.activeSection === 'inventory') loadInventory();\n",
    ""
)
# Also remove "Inventario (v1)" nav item if still there
text = text.replace(
    '\n        <button class="nav-item" data-section="inventory" onclick="navTo(\'inventory\')">Inventario (v1)</button>',
    ""
)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Cleaned up old inventory references")
