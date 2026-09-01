with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "r", encoding="utf-8") as f:
    text = f.read()

# Replace all updateHUD() calls inside the poll function to pass the phase
# The poll function has the phase variable in scope
text = text.replace(
    "const me = (state.players || []).find(p => p.player_id === P.id);\n  if (me) {\n    if (me.points > P.pts) { P.pts = me.points; sessionStorage.setItem('uaa_my_points', P.pts); }\n    if (me.rank) { P.rank = me.rank; sessionStorage.setItem('uaa_my_rank', me.rank); }\n    updateHUD();\n  }",
    "const me = (state.players || []).find(p => p.player_id === P.id);\n  if (me) {\n    if (me.points > P.pts) { P.pts = me.points; sessionStorage.setItem('uaa_my_points', P.pts); }\n    if (me.rank) { P.rank = me.rank; sessionStorage.setItem('uaa_my_rank', me.rank); }\n    updateHUD(phase);\n  }"
)

# Also update the initial call at the bottom
text = text.replace(
    "updateHUD();\nshowScreen('screen-lobby');",
    "updateHUD('lobby');\nshowScreen('screen-lobby');"
)

# Also update the points update in chooseAnswer
text = text.replace(
    "sessionStorage.setItem('uaa_my_points', P.pts);\n    updateHUD();",
    "sessionStorage.setItem('uaa_my_points', P.pts);\n    updateHUD('active');"
)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "w", encoding="utf-8") as f:
    f.write(text)

print("updateHUD calls patched OK")
