import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()

old_iv = """let timeLeft = 30;
const numEl  = document.getElementById('countdown-num');
const wrapEl = document.getElementById('countdown-wrap');

// Load prizes first, then start countdown
loadPrizes().then(() => {
  const countdownInterval = setInterval(() => {"""

new_iv = """let timeLeft = 30;
const numEl  = document.getElementById('countdown-num');
const wrapEl = document.getElementById('countdown-wrap');
let countdownInterval;

// Load prizes first, then start countdown
loadPrizes().then(() => {
  countdownInterval = setInterval(() => {"""

text = text.replace(old_iv, new_iv)
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated prize.html")
