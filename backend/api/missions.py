import time
import uuid
import random
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List, Optional
from backend.core.database import get_db
from backend.core.game_state import update_score, get_game
from backend.app import publish_to_ably

router = APIRouter(prefix="/api/missions", tags=["missions"])

# ── Catálogo de productos educativos ─────────────────────────────────────────
PRODUCTS = [
    {"id":"p1",  "name":"Audífonos Bluetooth Pro",  "category":"Electrónica", "price":899,  "rating":4.8, "emoji":"🎧", "stock":12},
    {"id":"p2",  "name":"Mochila Tech UAA",          "category":"Accesorios",  "price":599,  "rating":4.6, "emoji":"🎒", "stock":8},
    {"id":"p3",  "name":"Termo Premium 750ml",       "category":"Lifestyle",   "price":349,  "rating":4.9, "emoji":"🥤", "stock":20},
    {"id":"p4",  "name":"Webcam Full HD 1080p",      "category":"Electrónica", "price":1299, "rating":4.7, "emoji":"📷", "stock":5},
    {"id":"p5",  "name":"Teclado Mecánico RGB",      "category":"Electrónica", "price":2499, "rating":4.5, "emoji":"⌨️", "stock":3},
    {"id":"p6",  "name":"Ratón Inalámbrico",         "category":"Electrónica", "price":449,  "rating":4.7, "emoji":"🖱️", "stock":15},
    {"id":"p7",  "name":"Lámpara LED Escritorio",    "category":"Lifestyle",   "price":289,  "rating":4.4, "emoji":"💡", "stock":18},
    {"id":"p8",  "name":"Hub USB-C 7 en 1",         "category":"Electrónica", "price":799,  "rating":4.6, "emoji":"🔌", "stock":9},
    {"id":"p9",  "name":"Soporte Laptop Ergonómico", "category":"Accesorios",  "price":549,  "rating":4.8, "emoji":"💻", "stock":11},
    {"id":"p10", "name":"Altavoz Bluetooth Mini",    "category":"Electrónica", "price":699,  "rating":4.6, "emoji":"🔊", "stock":7},
    {"id":"p11", "name":"Libreta Ejecutiva",         "category":"Accesorios",  "price":189,  "rating":4.5, "emoji":"📒", "stock":25},
    {"id":"p12", "name":"Mouse Pad XL",             "category":"Accesorios",  "price":229,  "rating":4.3, "emoji":"🖥️", "stock":30},
]

# Las 5 misiones educativas de e-commerce
POOL_TYPES = ["ecom_decision", "fraud_detect", "speed_search", "checkout_debug", "store_mission"]

MISSION_META = {
    "ecom_decision":  {"emoji": "💼", "title": "Decisión de Negocio",    "desc": "Analiza el caso real y elige la mejor estrategia de e-commerce", "topic": "Estrategia Digital"},
    "fraud_detect":   {"emoji": "🔎", "title": "Detective E-Commerce",   "desc": "Detecta señales de fraude o malas prácticas en estas tiendas", "topic": "Seguridad y Confianza"},
    "store_mission":  {"emoji": "🛍️", "title": "La Tienda",              "desc": "Explora el e-commerce, elige productos, completa el checkout y aprende el Customer Journey", "topic": "Customer Journey"},
    "speed_search":   {"emoji": "📈", "title": "Estrategia de Marketing", "desc": "Toma la mejor decisión para atraer clientes y aumentar tus ventas", "topic": "Marketing Digital"},
    "checkout_debug": {"emoji": "🧪", "title": "Rescata el Checkout",    "desc": "Identifica qué está fallando en este proceso de compra", "topic": "Optimización de Conversión"},
    # Compatibilidad con nombres viejos
    "store_cart":     {"emoji": "🛒", "title": "Construye tu Carrito",   "desc": "Arma el carrito perfecto dentro del presupuesto objetivo", "topic": "Experiencia de Compra"},
}


# ── BANCO DE PREGUNTAS DE E-COMMERCE ─────────────────────────────────────────

ECOM_DECISION_BANK = [
    {"difficulty":"media","scenario":"Muchos usuarios en México llegan al pago pero no completan la compra.","question":"¿Qué acción sube más la conversión?","options":[
        {"id":"A","text":"Agregar pago en OXXO y transferencia SPEI"},
        {"id":"B","text":"Aceptar únicamente tarjeta de crédito"},
        {"id":"C","text":"Cobrar una comisión por usar tarjeta"},
        {"id":"D","text":"Pedir un depósito bancario manual"}],
     "correct":"A","explanation":"En México mucha gente no usa tarjeta en línea; OXXO y SPEI capturan esas ventas.","concept":"Localiza los métodos de pago a tu mercado.","topic":"Pagos digitales"},
    {"difficulty":"facil","scenario":"Un usuario llena el carrito pero se va sin pagar.","question":"¿Qué táctica recupera esa venta?","options":[
        {"id":"A","text":"Enviarle un correo recordatorio con incentivo"},
        {"id":"B","text":"Eliminar su carrito tras una hora"},
        {"id":"C","text":"Subir el precio para que se apure"},
        {"id":"D","text":"Ocultar el botón de pago"}],
     "correct":"A","explanation":"Los correos de carrito abandonado recuperan un porcentaje importante de ventas.","concept":"Recuperación de carrito abandonado.","topic":"Abandono de carrito"},
    {"difficulty":"media","scenario":"Tu tienda recibe 10,000 visitas pero solo 100 compras.","question":"¿Qué métrica mide mejor el problema?","options":[
        {"id":"A","text":"La tasa de conversión del sitio"},
        {"id":"B","text":"El número de empleados del negocio"},
        {"id":"C","text":"El tamaño del almacén central"},
        {"id":"D","text":"La antigüedad del dominio web"}],
     "correct":"A","explanation":"La conversión (compras entre visitas) mide qué tan bien el tráfico se vuelve ventas.","concept":"Tasa de conversión.","topic":"Conversión"},
    {"difficulty":"media","scenario":"Vendes tus productos junto a cientos de negocios en una misma plataforma.","question":"¿Qué tipo de plataforma usas?","options":[
        {"id":"A","text":"Un marketplace de terceros"},
        {"id":"B","text":"Un sistema ERP interno"},
        {"id":"C","text":"Un gestor de correo masivo"},
        {"id":"D","text":"Una red social privada"}],
     "correct":"A","explanation":"Un marketplace reúne a muchos vendedores en una sola plataforma (Amazon, Mercado Libre).","concept":"Marketplaces.","topic":"Modelos de negocio"},
    {"difficulty":"dificil","scenario":"Tu tienda de ropa tiene 40% de devoluciones, muy por encima del sector.","question":"¿Cuál es la causa más probable?","options":[
        {"id":"A","text":"Guías de tallas poco claras"},
        {"id":"B","text":"Precios demasiado bajos"},
        {"id":"C","text":"Exceso de métodos de pago"},
        {"id":"D","text":"Carga muy rápida del sitio"}],
     "correct":"A","explanation":"En moda la causa principal de devoluciones es el ajuste o talla.","concept":"Gestión de devoluciones.","topic":"Devoluciones"},
    {"difficulty":"media","scenario":"Quieres aparecer primero en Google sin pagar por anuncios.","question":"¿Qué estrategia aplicas?","options":[
        {"id":"A","text":"Optimización SEO del sitio"},
        {"id":"B","text":"Un sistema CRM de clientes"},
        {"id":"C","text":"Un ERP de inventario"},
        {"id":"D","text":"Publicidad impresa local"}],
     "correct":"A","explanation":"El SEO mejora el posicionamiento orgánico en buscadores.","concept":"SEO.","topic":"Marketing digital"},
    {"difficulty":"facil","scenario":"Quieres guardar el historial de compras para recomendar productos.","question":"¿Qué herramienta usas?","options":[
        {"id":"A","text":"Un CRM de clientes"},
        {"id":"B","text":"Un editor de imágenes"},
        {"id":"C","text":"Una hoja de cálculo impresa"},
        {"id":"D","text":"Un reproductor de video"}],
     "correct":"A","explanation":"El CRM guarda el historial para personalizar ofertas y fidelizar.","concept":"CRM.","topic":"CRM"},
    {"difficulty":"dificil","scenario":"Un competidor baja sus precios de forma agresiva.","question":"¿Cuál respuesta es más sólida?","options":[
        {"id":"A","text":"Diferenciarte por servicio y valor"},
        {"id":"B","text":"Bajar tu precio por debajo del suyo"},
        {"id":"C","text":"Cerrar la tienda por unos días"},
        {"id":"D","text":"Ocultar tus precios al público"}],
     "correct":"A","explanation":"Competir solo por precio erosiona el margen; diferenciarte es más sostenible.","concept":"Estrategia de precios.","topic":"Precios"},
    {"difficulty":"media","scenario":"Tus clientes son jóvenes que compran casi siempre desde el celular.","question":"¿Qué decisión es la más lógica?","options":[
        {"id":"A","text":"Optimizar la experiencia móvil"},
        {"id":"B","text":"Vender solo en tienda física"},
        {"id":"C","text":"Ignorar el canal de celular"},
        {"id":"D","text":"Subir los precios a ese grupo"}],
     "correct":"A","explanation":"Si el segmento es móvil, priorizar esa experiencia sube ventas.","concept":"Segmentación y datos.","topic":"Comportamiento del consumidor"},
    {"difficulty":"dificil","scenario":"Una fábrica vende por mayoreo a otras empresas mediante una plataforma.","question":"¿Qué modelo de negocio representa?","options":[
        {"id":"A","text":"B2B, de negocio a negocio"},
        {"id":"B","text":"B2C, de negocio a consumidor"},
        {"id":"C","text":"C2C, entre consumidores"},
        {"id":"D","text":"P2P, entre particulares"}],
     "correct":"A","explanation":"Vender en volumen a otras empresas es B2B.","concept":"Modelos B2B/B2C.","topic":"Modelos de negocio"},
    {"difficulty":"media","scenario":"Un correo pide tu contraseña para 'no bloquear tu cuenta'.","question":"¿Qué es esto?","options":[
        {"id":"A","text":"Un intento de phishing"},
        {"id":"B","text":"Una promoción legítima"},
        {"id":"C","text":"Un aviso normal del banco"},
        {"id":"D","text":"Una actualización del sistema"}],
     "correct":"A","explanation":"Pedir datos sensibles con urgencia es phishing; nunca los compartas.","concept":"Seguridad y phishing.","topic":"Seguridad"},
    {"difficulty":"facil","scenario":"El cliente quiere saber dónde va su paquete tras comprar.","question":"¿Qué le ofreces?","options":[
        {"id":"A","text":"Rastreo del pedido en tiempo real"},
        {"id":"B","text":"Un descuento en su próxima compra"},
        {"id":"C","text":"Una encuesta de satisfacción"},
        {"id":"D","text":"Un catálogo de nuevos productos"}],
     "correct":"A","explanation":"El rastreo en tiempo real reduce dudas y mejora la satisfacción post-compra.","concept":"Logística y post-venta.","topic":"Logística"},
]

FRAUD_DETECT_BANK = [
    {
        "intro": "Un comprador reportó estas 3 tiendas online. Una de ellas tiene claras señales de fraude o práctica deshonesta.",
        "question": "¿Cuál de estas tiendas tiene señales de alerta?",
        "listings": [
            {"id":"L1", "name":"TechStore Pro", "price":"$899 MXN", "rating":"4.7/5 (234 reseñas)", "vendor":"Verificado", "payment":"Visa, MC, PayPal, OXXO", "policy":"30 días devolución", "alert": False},
            {"id":"L2", "name":"SUPER OFERTAS MX", "price":"$45 MXN (Laptop Gaming)", "rating":"5.0/5 (2 reseñas)", "vendor":"Nuevo vendedor", "payment":"Solo transferencia bancaria", "policy":"Sin devoluciones", "alert": True},
            {"id":"L3", "name":"ElectroDigital", "price":"$1,299 MXN", "rating":"4.5/5 (89 reseñas)", "vendor":"Verificado 3 años", "payment":"Múltiples métodos", "policy":"15 días devolución", "alert": False},
        ],
        "correct_id": "L2",
        "explanation": "SUPER OFERTAS MX tiene múltiples señales de fraude: (1) Precio imposiblemente bajo para una laptop gaming ($45 MXN vs $15,000+ real), (2) Solo acepta transferencia bancaria (sin protección al comprador), (3) Sin política de devoluciones, (4) Solo 2 reseñas todas perfectas (5.0/5) como vendedor nuevo.",
        "concept": "Señales de fraude: precio irreal, solo transferencia, sin devoluciones, reseñas falsas.",
        "topic": "Seguridad en E-Commerce",
    },
    {
        "intro": "Analiza estos 3 procesos de pago. Un e-commerce tiene una práctica que viola estándares de seguridad.",
        "question": "¿Cuál práctica representa un riesgo de seguridad grave?",
        "listings": [
            {"id":"L1", "name":"Pago con Stripe", "price":"Cifrado SSL, PCI DSS", "rating":"", "vendor":"", "payment":"Certificado de seguridad visible, candado en URL", "policy":"Datos cifrados end-to-end", "alert": False},
            {"id":"L2", "name":"Checkout de TiendaX", "price":"", "rating":"", "vendor":"", "payment":"Campo de texto libre: 'Escribe tu número de tarjeta y CVV en los comentarios del pedido'", "policy":"", "alert": True},
            {"id":"L3", "name":"Mercado Pago", "price":"Protección al comprador", "rating":"", "vendor":"", "payment":"Pasarela certificada, múltiples métodos", "policy":"Garantía de devolución", "alert": False},
        ],
        "correct_id": "L2",
        "explanation": "Pedir datos de tarjeta en campo de comentarios es una práctica extremadamente peligrosa y fraudulenta. Los datos de tarjeta NUNCA deben capturarse fuera de una pasarela de pago certificada (PCI DSS). Las tiendas legítimas usan pasarelas especializadas (Stripe, Conekta, Mercado Pago) que cifran los datos directamente.",
        "concept": "Los datos de tarjeta solo deben ingresarse en pasarelas certificadas PCI DSS, nunca en campos de texto libre.",
        "topic": "Seguridad en Pagos Digitales",
    },
    {
        "intro": "Tres tiendas de ropa online compiten por el mismo cliente. Analiza sus características.",
        "question": "¿Cuál tienda demuestra mejores prácticas de e-commerce confiable?",
        "listings": [
            {"id":"L1", "name":"ModaFast", "price":"Precios claros + IVA incluido", "rating":"4.6/5 (1,240 reseñas verificadas)", "vendor":"7 años en línea", "payment":"Múltiples métodos seguros", "policy":"30 días sin preguntas, guía de tallas", "alert": False},
            {"id":"L2", "name":"TrendShop24", "price":"'OFERTA: 95% descuento HOY SOLAMENTE'", "rating":"5.0/5 (6 reseñas)", "vendor":"Sin información del vendedor", "payment":"Solo Zelle o transferencia", "policy":"No se aceptan devoluciones ni cambios", "alert": True},
            {"id":"L3", "name":"StyleMX", "price":"Comparativa con precio original", "rating":"4.3/5 (456 reseñas)", "vendor":"3 años, IMSS verificado", "payment":"Visa, MC, PayPal", "policy":"15 días para cambios", "alert": False},
        ],
        "correct_id": "L2",
        "explanation": "TrendShop24 tiene múltiples banderas rojas: urgencia artificial ('solo hoy'), descuento imposible del 95%, solo 6 reseñas todas perfectas, sin información del vendedor, solo Zelle/transferencia (sin protección), y sin devoluciones. Esta combinación es el patrón clásico de una tienda fraudulenta.",
        "concept": "E-commerce confiable: transparencia de precios, reseñas verificadas, múltiples métodos de pago, política de devoluciones.",
        "topic": "Indicadores de Confianza en E-Commerce",
    },
    {
        "intro": "Recibes tres correos que dicen ser de tu banco/tienda. Uno es un intento de phishing.",
        "question": "¿Cuál mensaje es un fraude (phishing)?",
        "listings": [
            {"id":"L1", "name":"Correo de confirmación de compra", "price":"Remitente: pedidos@tienda.com", "rating":"", "vendor":"Dominio oficial verificado", "payment":"Enlaces al dominio oficial", "policy":"No pide contraseñas", "alert": False},
            {"id":"L2", "name":"'Tu cuenta será bloqueada en 24h'", "price":"Remitente: seguridad@tienda-mx.info", "rating":"", "vendor":"Dominio raro (.info)", "payment":"'Haz clic aquí y confirma tu contraseña y CVV'", "policy":"Urgencia + amenaza", "alert": True},
            {"id":"L3", "name":"Boletín de ofertas semanales", "price":"Remitente: news@tienda.com", "rating":"", "vendor":"Dominio oficial", "payment":"Botón 'Ver ofertas' al sitio real", "policy":"Opción de darse de baja", "alert": False},
        ],
        "correct_id": "L2",
        "explanation": "El mensaje L2 es phishing clásico: (1) crea urgencia y miedo ('bloqueo en 24h'), (2) usa un dominio sospechoso (.info en vez del oficial), (3) pide contraseña y CVV, algo que ninguna empresa legítima solicita por correo. Nunca ingreses datos desde enlaces de correos; escribe la dirección del sitio tú mismo.",
        "concept": "Phishing = urgencia + dominio falso + pedir datos sensibles. Verifica el remitente y nunca des tu CVV/contraseña por correo.",
        "topic": "Seguridad y Phishing",
    },
    {
        "intro": "Comparas tres vendedores del mismo producto en un marketplace.",
        "question": "¿Cuál vendedor presenta señales de fraude?",
        "listings": [
            {"id":"L1", "name":"AudioPro MX", "price":"$1,499 (precio de mercado)", "rating":"4.8/5 (980 reseñas)", "vendor":"Tienda oficial, 5 años", "payment":"Pago protegido del marketplace", "policy":"Devolución 30 días", "alert": False},
            {"id":"L2", "name":"GangaTech", "price":"$1,350", "rating":"4.4/5 (210 reseñas)", "vendor":"2 años en el sitio", "payment":"Pago protegido del marketplace", "policy":"Devolución 14 días", "alert": False},
            {"id":"L3", "name":"OfertaFlash", "price":"$199 (¡87% OFF!)", "rating":"5.0/5 (3 reseñas)", "vendor":"'Escríbeme a WhatsApp para pagar por fuera'", "payment":"Pide pago fuera de la plataforma", "policy":"Sin devoluciones", "alert": True},
        ],
        "correct_id": "L3",
        "explanation": "OfertaFlash muestra el fraude típico de marketplace: precio irreal, pocas reseñas perfectas de vendedor nuevo y, sobre todo, pedir pagar FUERA de la plataforma (por WhatsApp/transferencia). Pagar fuera elimina la protección al comprador. Regla de oro: siempre paga dentro del sistema del marketplace.",
        "concept": "Nunca pagues fuera de la plataforma. La protección al comprador solo aplica si usas el pago oficial del marketplace.",
        "topic": "Seguridad en Marketplaces",
    },

    {
        "intro": "El sistema antifraude marcó 3 pedidos recientes. Analiza los patrones de cada uno.",
        "question": "¿Cuál pedido tiene señales claras de fraude con tarjeta robada?",
        "listings": [
            {"id":"L1", "name":"Pedido #1042", "price":"$1,200 MXN", "rating":"", "vendor":"Cliente con 6 compras previas", "payment":"Misma tarjeta y dirección de siempre", "policy":"Envío a su domicilio habitual", "alert": False},
            {"id":"L2", "name":"Pedido #1043", "price":"$18,500 MXN", "rating":"", "vendor":"Cuenta creada hace 4 minutos", "payment":"3 tarjetas distintas probadas en 2 minutos, envío urgente", "policy":"Envío a país distinto al de facturación", "alert": True},
            {"id":"L3", "name":"Pedido #1044", "price":"$650 MXN", "rating":"", "vendor":"Cliente recurrente", "payment":"Tarjeta guardada y verificada", "policy":"Recoge en tienda", "alert": False},
        ],
        "correct_id": "L2",
        "explanation": "El pedido #1043 combina señales de tarjeta robada: cuenta recién creada, varias tarjetas probadas en poco tiempo ('card testing'), monto alto, envío urgente y dirección de envío que no coincide con la de facturación (otro país). Estas señales juntas justifican verificación manual o bloqueo.",
        "concept": "Fraude con tarjeta: cuenta nueva + varias tarjetas probadas + monto alto + envío urgente + envío distinto a facturación.",
        "topic": "Prevención de Fraude con Tarjeta",
    },
    {
        "intro": "Analizas las reseñas de tres productos para detectar manipulación (reseñas falsas).",
        "question": "¿Cuál producto muestra señales de reseñas falsas?",
        "listings": [
            {"id":"L1", "name":"Producto A", "price":"4.6/5", "rating":"320 reseñas en 2 años", "vendor":"Mezcla de 4 y 5 estrellas, con críticas", "payment":"Reseñas con fotos y compra verificada", "policy":"Redacción variada y natural", "alert": False},
            {"id":"L2", "name":"Producto B", "price":"5.0/5", "rating":"90 reseñas casi todas el mismo día", "vendor":"Todas 5 estrellas, textos casi idénticos", "payment":"Cuentas nuevas sin otras compras", "policy":"'Excelente producto, lo recomiendo' repetido", "alert": True},
            {"id":"L3", "name":"Producto C", "price":"4.3/5", "rating":"150 reseñas", "vendor":"Distribución normal de estrellas", "payment":"Compras verificadas", "policy":"Comentarios con pros y contras", "alert": False},
        ],
        "correct_id": "L2",
        "explanation": "El Producto B tiene el patrón típico de reseñas falsas: muchas 5 estrellas publicadas casi el mismo día, textos casi idénticos, cuentas nuevas sin historial y ausencia total de críticas. Las reseñas reales tienen distribución variada, redacción distinta y compras verificadas a lo largo del tiempo.",
        "concept": "Reseñas falsas: picos de 5 estrellas el mismo día, textos repetidos, cuentas nuevas y sin críticas ni compra verificada.",
        "topic": "Detección de Reseñas Falsas",
    },
    {
        "intro": "Tres inicios de sesión en cuentas de clientes. Uno es un robo de cuenta (account takeover).",
        "question": "¿Cuál caso es un robo de cuenta?",
        "listings": [
            {"id":"L1", "name":"Acceso 1", "price":"Dispositivo y ciudad habituales", "rating":"", "vendor":"Contraseña correcta al primer intento", "payment":"Sin cambios en la cuenta", "policy":"Horario habitual", "alert": False},
            {"id":"L2", "name":"Acceso 2", "price":"Dispositivo y país nuevos", "rating":"", "vendor":"15 intentos fallidos y luego éxito", "payment":"Cambian correo, contraseña y dirección al entrar", "policy":"Piden envío urgente de productos caros", "alert": True},
            {"id":"L3", "name":"Acceso 3", "price":"Teléfono del cliente", "rating":"", "vendor":"Login con verificación en dos pasos", "payment":"Sin cambios sensibles", "policy":"Solo consulta su historial", "alert": False},
        ],
        "correct_id": "L2",
        "explanation": "El Acceso 2 es un robo de cuenta: múltiples intentos fallidos (fuerza bruta), dispositivo y país nuevos y cambios inmediatos de correo, contraseña y dirección seguidos de compras urgentes. La defensa: verificación en dos pasos (2FA), alertas de acceso nuevo y bloquear 'cambio de datos + compra' en la misma sesión sospechosa.",
        "concept": "Account takeover: intentos fallidos + dispositivo nuevo + cambio de datos y compra inmediata. Defensa: 2FA y alertas.",
        "topic": "Robo de Cuentas (Account Takeover)",
    },
    {
        "intro": "Comparas la seguridad de tres sitios antes de pagar. En uno NO deberías ingresar tu tarjeta.",
        "question": "¿En cuál NO deberías ingresar los datos de tu tarjeta?",
        "listings": [
            {"id":"L1", "name":"tienda-a.com", "price":"https:// con candado", "rating":"", "vendor":"Certificado SSL válido", "payment":"Pasarela certificada (Stripe/Conekta)", "policy":"Política de privacidad clara", "alert": False},
            {"id":"L2", "name":"tienda-b.com", "price":"http:// sin candado", "rating":"", "vendor":"El navegador la marca 'No seguro'", "payment":"Formulario propio que pide tarjeta, CVV y NIP", "policy":"Sin política de privacidad ni contacto", "alert": True},
            {"id":"L3", "name":"tienda-c.com", "price":"https:// con candado", "rating":"", "vendor":"SSL válido y sello de seguridad", "payment":"Redirige a la pasarela del banco", "policy":"Contacto y devoluciones visibles", "alert": False},
        ],
        "correct_id": "L2",
        "explanation": "tienda-b.com usa HTTP (sin cifrado), el navegador la marca 'No seguro', pide datos sensibles como el NIP (que nunca se solicita en compras en línea) en su propio formulario y no tiene política de privacidad ni contacto. Nunca ingreses datos de tarjeta en sitios sin HTTPS ni en formularios que no usan una pasarela certificada.",
        "concept": "Nunca ingreses tu tarjeta en sitios HTTP (sin candado) o que pidan tu NIP: solo HTTPS con pasarela certificada.",
        "topic": "Seguridad SSL y Pagos",
    },

]

CHECKOUT_DEBUG_BANK = [
    {"difficulty":"media","scenario":"El checkout obliga a crear una cuenta antes de pagar.","problem_display":{"title":"Registro forzado","issues":["Sin opción de compra como invitado","Pide muchos datos antes de pagar","Muchos abandonan en ese paso"]},"question":"¿Qué reduce el abandono aquí?","options":[
        {"id":"A","text":"Permitir la compra como invitado"},
        {"id":"B","text":"Pedir aún más datos al registrarse"},
        {"id":"C","text":"Quitar el resumen del pedido"},
        {"id":"D","text":"Ocultar el costo del envío"}],
     "correct":"A","explanation":"La compra como invitado quita fricción y sube la conversión.","concept":"Checkout sin fricción.","topic":"Checkout"},
    {"difficulty":"media","scenario":"El total sorprende al usuario con impuestos y envío al final.","problem_display":{"title":"Costos sorpresa","issues":["Impuestos y envío solo al final","Sin estimador en el carrito","El total cambia de golpe"]},"question":"¿Cuál es la mejor práctica?","options":[
        {"id":"A","text":"Mostrar el costo total desde antes"},
        {"id":"B","text":"Revelar el envío hasta el final"},
        {"id":"C","text":"Sumar cargos extra sin avisar"},
        {"id":"D","text":"Cobrar el envío tras el pago"}],
     "correct":"A","explanation":"Los costos sorpresa son la causa principal de abandono; muestra el total antes.","concept":"Transparencia de costos.","topic":"Checkout"},
    {"difficulty":"dificil","scenario":"El checkout tarda 7 segundos en cargar en el celular.","problem_display":{"title":"Rendimiento lento","issues":["Imágenes sin comprimir","Scripts que bloquean la carga","Sin caché ni CDN"]},"question":"¿Qué priorizas para arreglarlo?","options":[
        {"id":"A","text":"Comprimir imágenes y usar CDN"},
        {"id":"B","text":"Agregar más animaciones"},
        {"id":"C","text":"Subir imágenes más pesadas"},
        {"id":"D","text":"Aumentar el número de pasos"}],
     "correct":"A","explanation":"Cada segundo extra baja la conversión; comprime, usa CDN y difiere scripts.","concept":"Rendimiento y velocidad.","topic":"Experiencia de usuario"},
    {"difficulty":"media","scenario":"La tienda solo acepta un método de pago.","problem_display":{"title":"Pago limitado","issues":["Solo tarjeta de crédito","Sin billeteras digitales","Sin efectivo ni transferencia"]},"question":"¿Qué sube la conversión?","options":[
        {"id":"A","text":"Ofrecer varios métodos de pago"},
        {"id":"B","text":"Dejar un solo método activo"},
        {"id":"C","text":"Cobrar comisión por método"},
        {"id":"D","text":"Pedir el pago por teléfono"}],
     "correct":"A","explanation":"Más métodos de pago capturan a más compradores.","concept":"Métodos de pago.","topic":"Pagos digitales"},
    {"difficulty":"facil","scenario":"El sitio de pago no muestra ninguna señal de seguridad.","problem_display":{"title":"Sin confianza","issues":["Sin candado visible","Sin sellos de seguridad","El usuario duda al pagar"]},"question":"¿Qué genera confianza?","options":[
        {"id":"A","text":"Mostrar candado HTTPS y sellos"},
        {"id":"B","text":"Usar colores mucho más vivos"},
        {"id":"C","text":"Agregar música de fondo suave"},
        {"id":"D","text":"Ampliar mucho el logo del sitio"}],
     "correct":"A","explanation":"HTTPS y sellos de seguridad reducen el abandono en el pago.","concept":"Confianza y seguridad.","topic":"Seguridad"},
    {"difficulty":"media","scenario":"Muchos usuarios se equivocan al escribir su domicilio.","problem_display":{"title":"Errores de dirección","issues":["Sin autocompletado","Sin validación de código postal","Errores hasta el final"]},"question":"¿Qué mejora reduce los errores?","options":[
        {"id":"A","text":"Autocompletar y validar el CP"},
        {"id":"B","text":"Un solo campo enorme de texto"},
        {"id":"C","text":"Pedir la dirección tres veces"},
        {"id":"D","text":"Quitar el campo de dirección"}],
     "correct":"A","explanation":"El autocompletado y la validación en tiempo real evitan errores y entregas fallidas.","concept":"Formularios y validación.","topic":"Experiencia de usuario"},
    {"difficulty":"dificil","scenario":"El 70% del tráfico es móvil, pero casi nadie cierra la compra ahí.","problem_display":{"title":"Móvil deficiente","issues":["Botones diminutos","Hay que hacer zoom","Teclados equivocados"]},"question":"¿Cuál es la causa más probable?","options":[
        {"id":"A","text":"El checkout no es responsive"},
        {"id":"B","text":"Los productos son muy caros"},
        {"id":"C","text":"Faltan más fotos de producto"},
        {"id":"D","text":"El logo es demasiado chico"}],
     "correct":"A","explanation":"Un checkout no optimizado para móvil genera muchísima fricción.","concept":"Diseño responsive.","topic":"Experiencia de usuario"},
    {"difficulty":"media","scenario":"Los usuarios abandonan el carrito y nunca regresan.","problem_display":{"title":"Sin recuperación","issues":["No se guarda el carrito","Sin recordatorio por correo","Sin incentivo para volver"]},"question":"¿Qué recupera esas ventas?","options":[
        {"id":"A","text":"Correos de carrito abandonado"},
        {"id":"B","text":"Borrar el carrito cada hora"},
        {"id":"C","text":"Subir el precio si el usuario duda"},
        {"id":"D","text":"Quitar el botón de pagar"}],
     "correct":"A","explanation":"La secuencia de carrito abandonado recupera ventas que casi se cerraban.","concept":"Recuperación de carrito.","topic":"Abandono de carrito"},
]

def _shuffle_choices(options, correct_id):
    if not options: return [], ""
    # Find the correct item text/name
    correct_val = ""
    for o in options:
        if str(o.get("id")) == str(correct_id):
            correct_val = o.get("text") or o.get("name") or str(o.get("id"))
            break
            
    opts = options[:]
    random.shuffle(opts)
    
    # After shuffle, find the new index/id of the correct item
    new_correct = ""
    for idx, o in enumerate(opts):
        val = o.get("text") or o.get("name") or str(o.get("id"))
        if val == correct_val:
            new_correct = o.get("id", str(idx))
            break
            
    # Assign alphabetical IDs if they don't have them
    for i, o in enumerate(opts):
        o["id"] = chr(65 + i)
        if (o.get("text") or o.get("name") or str(o.get("id"))) == correct_val:
            new_correct = o["id"]
            
    return opts, new_correct
def _gen_ecom_decision():
    import random
    qs = random.sample(ECOM_DECISION_BANK, min(2, len(ECOM_DECISION_BANK)))
    questions = []
    for q in qs:
        opts, correct = _shuffle_choices(q['options'], q.get('correct') or q.get('correct_id', ''))
        questions.append({
            'scenario': q.get('scenario', q.get('intro', '')),
            'question': q.get('question', ''),
            'options': opts,
            'correct': correct,
            'explanation': q.get('explanation', ''),
            'concept': q.get('concept', ''),
            'listings': q.get('listings', q.get('products', []))
        })
    return {
        'is_multi': True,
        'questions': questions,
        'topic': qs[0].get('topic', 'E-Commerce')
    }



def _gen_fraud_detect():
    import random
    qs = random.sample(FRAUD_DETECT_BANK, min(2, len(FRAUD_DETECT_BANK)))
    questions = []
    for q in qs:
        correct_id = q.get('correct') or q.get('correct_id', '')
        listings_source = q.get('listings') or q.get('products') or []
        listings, correct = _shuffle_choices(listings_source, correct_id)
        questions.append({
            'scenario': q.get('scenario', q.get('intro', '')),
            'question': q.get('question', ''),
            'options': [],
            'correct': correct,
            'explanation': q.get('explanation', ''),
            'concept': q.get('concept', ''),
            'listings': listings
        })
    return {
        'is_multi': True,
        'questions': questions,
        'topic': qs[0].get('topic', 'E-Commerce')
    }


def _gen_store_cart():
    """Genera un ejercicio de construcción de carrito."""
    budget = random.choice([1200, 1500, 1800, 2000, 2500])
    prods  = random.sample(PRODUCTS, 8)
    lo     = int(budget * 0.65)
    hi     = budget
    return {
        "budget":      budget,
        "products":    prods,
        "target_range": [lo, hi],
        "required_categories": 2,
        "max_items": 4,
        "hint": f"Elige hasta 4 productos. El total debe estar entre ${lo} y ${hi} MXN.",
        "explanation": f"El objetivo es maximizar el valor de compra dentro del presupuesto. Un buen comprador digital busca la mejor relación calidad-precio sin exceder su límite.",
        "concept": "Gestión de presupuesto y carrito en e-commerce.",
        "topic": "Experiencia de Compra",
    }


MARKETING_BANK = [
    {"difficulty":"media","scenario":"Tu tienda tiene muchas visitas pero pocas ventas.","question":"¿Qué métrica de marketing debes revisar primero?","options":[
        {"id":"A","text":"La tasa de conversión (CRO)"},
        {"id":"B","text":"El número de seguidores en Instagram"},
        {"id":"C","text":"El costo por clic (CPC) de tus anuncios"},
        {"id":"D","text":"El tiempo de carga de tu logo"}],
     "correct":"A","explanation":"La tasa de conversión te indica si tu tráfico está encontrando lo que busca y comprando.","concept":"Conversión"},
    {"difficulty":"media","scenario":"Quieres lanzar un producto nuevo para jóvenes universitarios.","question":"¿Qué canal de marketing es más efectivo?","options":[
        {"id":"A","text":"TikTok Ads y campañas de influencers"},
        {"id":"B","text":"Anuncios en el periódico local"},
        {"id":"C","text":"Llamadas telefónicas en frío (Telemarketing)"},
        {"id":"D","text":"Banners estáticos en sitios de noticias corporativas"}],
     "correct":"A","explanation":"El público universitario consume mayormente redes sociales dinámicas como TikTok.","concept":"Segmentación"},
    {"difficulty":"facil","scenario":"Tus clientes añaden productos pero abandonan el carrito.","question":"¿Qué acción de marketing es ideal aquí?","options":[
        {"id":"A","text":"Enviar un correo de 'Carrito Abandonado' con un descuento"},
        {"id":"B","text":"Borrar sus cuentas por inactividad"},
        {"id":"C","text":"Cambiar el logo de la tienda"},
        {"id":"D","text":"Imprimir folletos"}],
     "correct":"A","explanation":"El retargeting y los correos automáticos recuperan ventas perdidas.","concept":"Retargeting"}
]


def _gen_speed_search():
    import random
    qs = random.sample(MARKETING_BANK, min(2, len(MARKETING_BANK)))
    questions = []
    for q in qs:
        opts, correct = _shuffle_choices(q['options'], q.get('correct') or q.get('correct_id', ''))
        questions.append({
            'scenario': q.get('scenario', q.get('intro', '')),
            'question': q.get('question', ''),
            'options': opts,
            'correct': correct,
            'explanation': q.get('explanation', ''),
            'concept': q.get('concept', ''),
            'listings': q.get('listings', q.get('products', []))
        })
    return {
        'is_multi': True,
        'questions': questions,
        'topic': qs[0].get('topic', 'E-Commerce')
    }


def _gen_checkout_debug():
    import random
    qs = random.sample(CHECKOUT_DEBUG_BANK, min(2, len(CHECKOUT_DEBUG_BANK)))
    questions = []
    for q in qs:
        opts, correct = _shuffle_choices(q['options'], q.get('correct') or q.get('correct_id', ''))
        questions.append({
            'scenario': q.get('scenario', q.get('intro', '')),
            'question': q.get('question', ''),
            'options': opts,
            'correct': correct,
            'explanation': q.get('explanation', ''),
            'concept': q.get('concept', ''),
            'listings': q.get('listings', q.get('products', []))
        })
    return {
        'is_multi': True,
        'questions': questions,
        'topic': qs[0].get('topic', 'E-Commerce')
    }


def _gen_store_mission():
    """Genera datos para la misión de tienda (el jugador completa el checkout real)."""
    return {
        "type": "store_mission",
        "explanation": "Completaste el flujo de compra de e-commerce: exploraste el catálogo, seleccionaste productos, gestionaste el carrito y finalizaste el checkout. Este es el Customer Journey completo.",
        "concept": "Customer Journey: Descubrimiento → Consideración → Decisión → Compra → Post-compra.",
        "topic": "Customer Journey Completo",
        "concepts_practiced": [
            "Catálogo y búsqueda de productos",
            "Selección y comparación de productos",
            "Gestión del carrito de compras",
            "Proceso de checkout en múltiples etapas",
            "Métodos de pago digitales",
            "Confirmación de pedido",
        ],
    }

def _gen_data(mtype: str) -> dict:
    """Genera datos para una misión según su tipo."""
    generators = {
        "ecom_decision":  _gen_ecom_decision,
        "fraud_detect":   _gen_fraud_detect,
        "store_mission":  _gen_store_mission,  # Tienda completa
        "store_cart":     _gen_store_cart,     # Compatibilidad
        "speed_search":   _gen_speed_search,
        "checkout_debug": _gen_checkout_debug,
        # Compatibilidad con tipos viejos
        "detective":  _gen_fraud_detect,
        "find_error": _gen_checkout_debug,
        "store":      _gen_store_cart,
        "speed":      _gen_speed_search,
        "decision":   _gen_ecom_decision,
    }
    gen = generators.get(mtype, _gen_ecom_decision)
    return gen()

# Cache en memoria: {player_id: [missions_list]}
_pool_cache: dict = {}

# ── Modelos ──────────────────────────────────────────────────────────────────
class StartMissionRequest(BaseModel):
    player_id: str
    game_code:  str
    mission_id: str

class ValidateRequest(BaseModel):
    player_id:    str
    game_code:    str
    mission_id:   str
    mission_type: str
    answer:       Any
    time_taken_ms: int = 3000


# ── GET pool ─────────────────────────────────────────────────────────────────
@router.get("/pool/{game_code}/{player_id}")
async def get_pool(game_code: str, player_id: str):
    """Devuelve las 5 misiones del jugador, creándolas si no existen."""
    cache_key = f"{game_code}:{player_id}"

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, mission_type, status, points_earned FROM player_missions "
            "WHERE player_id = ? AND game_code = ? ORDER BY rowid",
            (player_id, game_code)
        )
        rows = await cursor.fetchall()

        if not rows:
            # Generar datos de todas las misiones de una vez
            # Baraja las misiones normales, pero "La Tienda" (store_mission)
            # SIEMPRE va al final: al completarla se muestra la posición final.
            others = [t for t in POOL_TYPES if t != "store_mission"]
            
            random.shuffle(others)
            types = others + (["store_mission"] if "store_mission" in POOL_TYPES else [])
            missions_to_insert = []
            for mtype in types:
                mid   = str(uuid.uuid4())
                mdata = _gen_data(mtype)
                missions_to_insert.append(
                    (mid, player_id, game_code, 1, mtype, json.dumps(mdata, ensure_ascii=False))
                )
            # UN SOLO commit con todos los INSERTs (mucho más rápido)
            await db.executemany(
                "INSERT INTO player_missions "
                "(id, player_id, game_code, round_number, mission_type, mission_data, status) "
                "VALUES (?, ?, ?, ?, ?, ?, 'available')",
                missions_to_insert
            )
            await db.commit()
            cursor = await db.execute(
                "SELECT id, mission_type, status, points_earned FROM player_missions "
                "WHERE player_id = ? AND game_code = ? ORDER BY rowid",
                (player_id, game_code)
            )
            rows = await cursor.fetchall()


    missions = []
    all_done  = True
    for r in rows:
        meta   = MISSION_META.get(r["mission_type"], MISSION_META.get("ecom_decision", {}))
        status = r["status"] or "available"
        if status != "completed":
            all_done = False
        missions.append({
            "mission_id":    r["id"],
            "mission_type":  r["mission_type"],
            "status":        status,
            "points_earned": r["points_earned"] or 0,
            "emoji":         meta.get("emoji", "🎯"),
            "title":         meta.get("title", r["mission_type"]),
            "description":   meta.get("desc", ""),
            "topic":         meta.get("topic", "E-Commerce"),
        })

    return {"missions": missions, "all_complete": all_done}


# ── POST start ───────────────────────────────────────────────────────────────
@router.post("/start")
async def start_mission(req: StartMissionRequest):
    """Marca misión como 'in_progress' y devuelve mission_data completo."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT mission_type, mission_data, status FROM player_missions WHERE id = ? AND player_id = ?",
            (req.mission_id, req.player_id)
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(404, "Mission not found")
        if row["status"] == "completed":
            raise HTTPException(400, "Mission already completed")

        await db.execute(
            "UPDATE player_missions SET status = 'in_progress', started_at = ? WHERE id = ?",
            (time.time(), req.mission_id)
        )
        await db.commit()

    mdata = json.loads(row["mission_data"])
    meta  = MISSION_META.get(row["mission_type"], MISSION_META.get("ecom_decision", {}))
    return {
        "mission_id":    req.mission_id,
        "mission_type":  row["mission_type"],
        "mission_data":  mdata,
        "title":         meta.get("title", row["mission_type"]),
        "emoji":         meta.get("emoji", "🎯"),
        "topic":         meta.get("topic", "E-Commerce"),
        "description":   meta.get("desc", ""),
    }


# ── Generadores con la FORMA que espera el frontend (game.js / missions.js) ───
# El frontend llama POST /api/missions/generate y renderiza según mission_type.
# Estos 5 tipos son los que el frontend sabe pintar Y que /validate sabe puntuar.
FRONTEND_TYPES = ["detective", "find_error", "best_cart", "decision", "speed"]

def _fe_detective():
    picks = random.sample(PRODUCTS, 3)
    suspicious = random.choice(picks)
    fake_price = max(1, int(suspicious["price"] * 0.1))
    products = []
    for p in picks:
        q = {"id": p["id"], "name": p["name"], "emoji": p["emoji"],
             "price": p["price"], "rating": p["rating"], "category": p["category"]}
        if p["id"] == suspicious["id"]:
            q["price"]  = fake_price
            q["rating"] = 2.1
            q["name"]   = p["name"] + " ¡REMATE!"
        products.append(q)
    return {
        "products": products,
        "correct_id": suspicious["id"],
        "explanation": f"Precio sospechosamente bajo (${fake_price} vs ~${suspicious['price']}) y rating malo: señal clara de fraude.",
        "concept": "Precios muy por debajo del mercado suelen indicar fraude o falsificación.",
        "topic": "Seguridad y Confianza",
    }

def _fe_find_error():
    items_src = random.sample(PRODUCTS, random.choice([2, 3]))
    items = [{"id": p["id"], "name": p["name"], "emoji": p["emoji"], "price": p["price"]} for p in items_src]
    subtotal = sum(i["price"] for i in items)
    shipping = random.choice([0, 49, 99])
    correct_total = subtotal + shipping
    surcharge = random.choice([30, 50, 70, 100])
    total_shown = correct_total + surcharge
    return {
        "order_data": {"items": items, "subtotal": subtotal, "shipping": shipping, "total_shown": total_shown},
        "correct_total": correct_total,
        "error_description": f"{subtotal} + {shipping} = {correct_total}, no {total_shown}. Hay un cargo extra de ${surcharge} no declarado.",
        "concept": "Verifica siempre que subtotal + envío = total. Cargos ocultos = mala práctica.",
        "topic": "Transparencia en Checkout",
    }

def _fe_best_cart():
    budget = random.choice([1200, 1500, 1800, 2000, 2500])
    lo = int(budget * 0.65)
    return {
        "budget": budget,
        "target_range": [lo, budget],
        "required_categories": 2,
        "max_items": 4,
        "concept": "Gestión de presupuesto: maximiza el valor de compra sin exceder el límite.",
        "topic": "Experiencia de Compra",
    }

def _fe_decision():
    opts_src = random.sample(PRODUCTS, 4)
    budget = max(p["price"] for p in opts_src)
    best = max(opts_src, key=lambda p: p["rating"])
    options = [{"id": p["id"], "name": p["name"], "emoji": p["emoji"],
                "price": p["price"], "rating": p["rating"], "category": p["category"]} for p in opts_src]
    return {
        "scenario": "Quieres la mejor relación calidad-precio dentro del presupuesto.",
        "budget": budget,
        "options": options,
        "correct": best["id"],
        "correct_option_id": best["id"],
        "explanation": f"La mejor opción es {best['name']} por su rating de {best['rating']}★ cabiendo en el presupuesto.",
        "concept": "Una buena decisión de compra equilibra precio, calidad (rating) y necesidad.",
        "topic": "Toma de Decisiones",
    }

def _fe_speed():
    target = random.choice(PRODUCTS)
    distract = random.sample([p for p in PRODUCTS if p["id"] != target["id"]], 5)
    pool = [target] + distract
    random.shuffle(pool)
    products = [{"id": p["id"], "name": p["name"], "emoji": p["emoji"], "price": p["price"]} for p in pool]
    return {
        "target_description": f"Encuentra lo más rápido posible: {target['emoji']} {target['name']}",
        "target_product_id": target["id"],
        "time_limit_seconds": 12,
        "products": products,
        "explanation": f"El producto era {target['emoji']} {target['name']}.",
        "concept": "Un catálogo bien organizado reduce el tiempo de búsqueda y mejora la conversión.",
        "topic": "Catálogo y UX",
    }

_FE_GENERATORS = {
    "detective":  _fe_detective,
    "find_error": _fe_find_error,
    "best_cart":  _fe_best_cart,
    "decision":   _fe_decision,
    "speed":      _fe_speed,
}

class GenerateRequest(BaseModel):
    player_id:    str
    game_code:    str
    round_number: int = 1

@router.post("/generate")
async def generate_mission(req: GenerateRequest):
    """Genera UNA misión con la forma que espera el frontend y la persiste.
    Cada ronda pide una misión distinta; se juega en streaming hasta que
    el cronómetro llega a cero.
    """
    # Se juega en streaming: cada llamada devuelve un tipo al azar para dar variedad.
    mtype = random.choice(FRONTEND_TYPES)

    data = _FE_GENERATORS[mtype]()
    mid  = str(uuid.uuid4())
    async with get_db() as db:
        await db.execute(
            "INSERT INTO player_missions "
            "(id, player_id, game_code, round_number, mission_type, mission_data, status, started_at) "
            "VALUES (?, ?, ?, ?, ?, ?, 'in_progress', ?)",
            (mid, req.player_id, req.game_code, req.round_number, mtype,
             json.dumps(data, ensure_ascii=False), time.time())
        )
        await db.commit()

    return {"mission_id": mid, "mission_type": mtype, "mission_data": data}


# ── POST validate ─────────────────────────────────────────────────────────────
@router.post("/validate")
async def validate_mission(req: ValidateRequest):
    """Valida la respuesta de una misión. NUNCA hace crash."""
    MIN_TIME_MS = 400
    if req.time_taken_ms < MIN_TIME_MS:
        req = req.model_copy(update={"time_taken_ms": MIN_TIME_MS})

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT mission_type, mission_data, status FROM player_missions WHERE id = ?",
            (req.mission_id,)
        )
        row = await cursor.fetchone()

        if not row:
            return {"correct": False, "points": 0, "penalty": 0, "net": 0,
                    "explanation": "Misión no encontrada.", "all_complete": False,
                    "total_points": 0, "streak": 0, "new_rank": 0,
                    "concept": "", "topic": "E-Commerce"}

        if row["status"] == "completed":
            return {"correct": True, "points": 0, "penalty": 0, "net": 0,
                    "explanation": "Ya completaste esta misión.", "all_complete": False,
                    "total_points": 0, "streak": 0, "new_rank": 0,
                    "concept": "", "topic": "E-Commerce"}

        data    = json.loads(row["mission_data"])
        mtype   = row["mission_type"]
        correct = False
        explanation = "Inténtalo de nuevo en otra misión."
        concept     = data.get("concept", "")
        topic       = data.get("topic", "E-Commerce")

        try:
            # store_mission — la tienda completa. Siempre correcto si el checkout fue completado
            if mtype == "store_mission":
                correct     = True  # El solo hecho de llegar aquí = checkout completado
                explanation = data.get("explanation", "Completaste el Customer Journey de e-commerce. ¡Excelente!")
                concept     = data.get("concept", "Customer Journey: Descubrimiento → Consideración → Compra → Post-compra.")
                topic       = data.get("topic", "Customer Journey Completo")

            # ecom_decision y tipos legacy compatibles
            elif mtype in ("ecom_decision", "decision"):
                answer_id = str(req.answer).strip().upper()
                correct_id = str(data.get("correct", "A")).strip().upper()
                correct     = (answer_id == correct_id)
                explanation = data.get("explanation", "Analiza el caso con más detalle.")

            # fraud_detect y tipos legacy compatibles
            elif mtype in ("fraud_detect", "detective"):
                correct     = (str(req.answer) == str(data.get("correct_id", "")))
                explanation = data.get("explanation", "Una de las opciones tenía señales claras de fraude.")


            # store_cart y tipos legacy
            elif mtype in ("store_cart", "store", "best_cart"):
                if isinstance(req.answer, list):
                    total = sum(p.get("price", 0) for p in req.answer if isinstance(p, dict))
                elif isinstance(req.answer, (int, float)):
                    total = float(req.answer)
                else:
                    total = 0
                lo, hi  = data.get("target_range", [0, data.get("budget", 9999)])
                correct = (lo <= total <= hi)
                explanation = data.get("explanation", f"Tu carrito sumó ${total} MXN. El objetivo era ${lo}-${hi} MXN.")

            # speed_search y tipos legacy
            elif mtype in ("speed_search", "speed"):
                correct     = (str(req.answer) == str(data.get("target_product_id", "")))
                explanation = data.get("explanation", f"El producto era: {data.get('target_name', '')}.")

            # checkout_debug y tipos legacy
            elif mtype in ("checkout_debug", "find_error"):
                answer_id  = str(req.answer).strip().upper()
                correct_id = str(data.get("correct", "A")).strip().upper()
                # También acepta respuesta numérica (legacy)
                try:
                    if answer_id not in ["A","B","C","D"]:
                        answer_num  = float(answer_id)
                        correct_num = float(str(data.get("correct_total", data.get("correct", 0))))
                        correct = abs(answer_num - correct_num) < 1
                    else:
                        correct = (answer_id == correct_id)
                except (ValueError, TypeError):
                    correct = (answer_id == correct_id)
                explanation = data.get("explanation", "Revisa los indicadores de un checkout óptimo.")

            else:
                correct     = True
                explanation = "¡Misión completada!"

        except Exception:
            correct     = False
            explanation = "Respuesta procesada. Revisa el concepto para aprender más."

        # ── Calcular puntos ─────────────────────────────────────────────────
        if mtype == "store_mission":
            # La misión de tienda siempre da 150 pts planos al completar
            base_pts    = 150
            speed_bonus = 0
            penalty     = 0
        else:
            base_pts    = 100 if correct else 0
            speed_bonus = 0
            if correct and req.time_taken_ms > 0:
                speed_bonus = max(0, 50 - int(req.time_taken_ms / 1000) * 5)
            penalty = 20 if not correct else 0
        points  = base_pts + speed_bonus
        net     = points - penalty

        # ── Guardar en DB ───────────────────────────────────────────────────
        await db.execute(
            "UPDATE player_missions SET status='completed', answer_submitted=?, is_correct=?, "
            "points_earned=?, time_taken_ms=?, completed_at=? WHERE id=?",
            (json.dumps(req.answer, ensure_ascii=False), int(correct), net,
             req.time_taken_ms, time.time(), req.mission_id)
        )
        await db.commit()

        # ── Actualizar score en memoria ─────────────────────────────────────
        if net != 0:
            try:
                update_score(req.game_code, req.player_id, net, correct)
            except Exception:
                pass

        # ── Verificar si todas las misiones están completas ─────────────────
        cursor2 = await db.execute(
            "SELECT COUNT(*) as total, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as done "
            "FROM player_missions WHERE player_id=? AND game_code=?",
            (req.player_id, req.game_code)
        )
        counts       = await cursor2.fetchone()
        all_complete = (counts["done"] or 0) >= (counts["total"] or 5)

        if all_complete:
            try:
                await db.execute(
                    "UPDATE players SET finished_at=COALESCE(finished_at, ?) WHERE id=? AND game_code=?",
                    (time.time(), req.player_id, req.game_code)
                )
                await db.commit()
            except Exception:
                pass

        # ── Datos del jugador en memoria ────────────────────────────────────
        total_pts = 0
        streak    = 0
        rank      = 0
        try:
            gs = get_game(req.game_code)
            if gs and gs.players.get(req.player_id):
                p         = gs.players[req.player_id]
                total_pts = p.points
                streak    = p.streak
                rank      = p.rank or 0
        except Exception:
            pass

        # ── Publicar eventos Ably ───────────────────────────────────────────
        try:
            await publish_to_ably(f"game:{req.game_code}", "score_update", {
                "player_id": req.player_id, "points": total_pts, "rank": rank
            })
            if all_complete:
                await publish_to_ably(f"game:{req.game_code}", "player_finished", {
                    "player_id": req.player_id, "total_points": total_pts
                })
        except Exception:
            pass

        return {
            "correct":      correct,
            "points":       points,
            "penalty":      penalty,
            "net":          net,
            "explanation":  explanation,
            "concept":      concept,
            "topic":        topic,
            "all_complete": all_complete,
            "total_points": total_pts,
            "streak":       streak,
            "new_rank":     rank,
        }
