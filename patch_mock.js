const fs = require('fs');
let text = fs.readFileSync('frontend/game.html', 'utf8');

text = text.replace(
  "if (type === 'fraud_detect') return {",
  if (type === 'checkout_debug') return {
        context: "La tienda tiene un error en el proceso de pago.",
        question: "¿Qué deberías hacer?",
        options: [{id:'a', text:'Revisar los logs'}, {id:'b', text:'Ignorar el problema'}]
      };
      if (type === 'speed_search') return {
        context: "Marketing digital en curso.",
        question: "¿Qué acción tomas?",
        options: [{id:'a', text:'Invertir en Ads'}, {id:'b', text:'Pausar campañas'}]
      };
      if (type === 'fraud_detect') return {
);

fs.writeFileSync('frontend/game.html', text);
