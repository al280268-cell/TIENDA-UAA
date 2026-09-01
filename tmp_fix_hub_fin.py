with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "r", encoding="utf-8") as f:
    text = f.read()

old_fin = """      // Redirect to full results / podium page
      setTimeout(() => { window.location.href = 'results.html'; }, 1500);
      showScreen('screen-podium');
      document.getElementById('podium').innerHTML = '<div style="text-align:center;font-size:2rem;padding:40px">\ud83c\udfc6 Calculando resultados\u2026</div>';"""

new_fin = """      // Redirect to the store simulation mission instead of jumping straight to results
      setTimeout(() => { window.location.href = 'store.html?mission=tienda_final'; }, 1500);
      showScreen('screen-podium');
      document.getElementById('podium').innerHTML = '<div style="text-align:center;font-size:2rem;padding:40px">\ud83d\uded2 Abriendo simulador de tienda\u2026</div>';"""

text = text.replace(old_fin, new_fin)
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated hub.html redirect")
