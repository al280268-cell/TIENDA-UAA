with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Remove "Control en Vivo" from sidebar
text = text.replace(
    '\n        <button class="nav-item" data-section="live" onclick="navTo(\'live\')">🎮 Control en Vivo</button>',
    ""
)

# Rename Analytics to Informes
text = text.replace(
    '>Analítica</button>',
    '>📊 Informes</button>'
)

# Also update dashboard to auto-load on init (so live panel shows right away)
# Find where loadDashboard is called in refreshCurrentSection
text = text.replace(
    "if (Admin.activeSection === 'dashboard') loadDashboard();",
    "if (Admin.activeSection === 'dashboard') { loadDashboard(); livePoll && livePoll(); }"
)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Sidebar cleanup done")
