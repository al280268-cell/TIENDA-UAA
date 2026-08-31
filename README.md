# FERIA UAA — RETO E-COMMERCE MULTIJUGADOR

> Aplicación web multijugador competitiva para la Feria Universitaria de la Universidad Autónoma de Aguascalientes. Varios participantes compiten simultáneamente resolviendo misiones de e-commerce, acumulando puntos y compitiendo por premios físicos limitados.

---

## Tabla de Contenidos

1. [Descripción](#descripción)
2. [Arquitectura técnica](#arquitectura-técnica)
3. [Instalación local](#instalación-local)
4. [Configurar Ably (WebSockets)](#configurar-ably)
5. [Despliegue en Vercel](#despliegue-en-vercel)
6. [Opción alternativa: Railway](#opción-alternativa-railway)
7. [Uso del sistema](#uso-del-sistema)
8. [Panel de administrador](#panel-de-administrador)
9. [Sistema de misiones](#sistema-de-misiones)
10. [Sistema de premios](#sistema-de-premios)
11. [Estructura del proyecto](#estructura-del-proyecto)

---

## Descripción

Cada participante escanea un QR, introduce el código de partida, escribe su nombre y compite en tiempo real contra otros jugadores. El juego tiene:

- **10 tipos de misiones** diferentes por ronda
- **Leaderboard en tiempo real** que se actualiza sin recargar
- **Premios físicos limitados** controlados por el servidor
- **Sistema anti-trampa** con validación server-side
- **Panel de administrador** completo
- **Modo demo** con bots simulados

---

## Arquitectura técnica

```
                    ┌─────────────────────┐
                    │   Vercel (Frontend) │
                    │  index.html  game   │
                    │  lobby    results   │
                    │  admin   rewards    │
                    └──────────┬──────────┘
                               │ HTTP REST /api/*
                    ┌──────────▼──────────┐
                    │  Vercel (Backend)   │
                    │  FastAPI Python     │
                    │  Serverless Funcs   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
   ┌──────────▼──────┐  ┌──────▼──────┐  ┌─────▼────────┐
   │   Ably Realtime │  │  SQLite/DB  │  │  Game State  │
   │  WebSocket msgs │  │  Persistent │  │  In-memory   │
   │  player updates │  │  game data  │  │  fast reads  │
   └─────────────────┘  └─────────────┘  └──────────────┘
```

### Por qué Ably y no WebSockets nativos en Vercel

Vercel ejecuta **funciones serverless** con timeout de 60 segundos. Los WebSockets persistentes requieren un servidor siempre activo. Ably actúa como broker de mensajes gestionado: el backend publica eventos via REST a Ably, y Ably los distribuye a todos los clientes conectados en tiempo real.

---

## Instalación local

### Requisitos previos
- Python 3.11+
- pip

### Pasos

```bash
# 1. Clonar / descargar el proyecto
cd "TIENDA UAA"

# 2. Copiar variables de entorno
cp .env.example .env
# Editar .env con tu editor favorito

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Iniciar el backend
uvicorn backend.app:app --reload --port 8000

# 5. En otra terminal: servir el frontend
python -m http.server 3000 --directory frontend

# 6. Abrir en el navegador
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
# Admin:    http://localhost:3000/admin.html
```

---

## Configurar Ably

Ably tiene un **Free Tier** suficiente para la feria (6M mensajes/mes, 200 conexiones).

1. Crear cuenta gratis en [ably.com](https://ably.com)
2. Crear una App nueva: "Feria UAA"
3. Ir a **API Keys**
4. Copiar la key principal (tiene todos los permisos) → `ABLY_API_KEY` en `.env`
5. Crear una segunda API key con solo permiso **subscribe** → `ABLY_CLIENT_KEY`
6. El `ABLY_CLIENT_KEY` va embebido en el HTML del frontend (es seguro — solo puede leer, no escribir)

### Modo sin Ably (desarrollo)

Si `ABLY_API_KEY` está vacío, el sistema usa **polling** automático cada 3 segundos. El juego funciona pero con menor tiempo real. Útil para probar localmente sin configurar Ably.

---

## Despliegue en Vercel

### Primera vez

```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Login
vercel login

# 3. Desplegar
vercel

# 4. Configurar variables de entorno en Vercel Dashboard:
# Settings → Environment Variables → agregar todas las del .env.example
```

### Variables de entorno en Vercel

En el dashboard de Vercel (`vercel.com/tu-usuario/tu-proyecto/settings/environment-variables`), agrega:

| Variable | Valor |
|---|---|
| `REALTIME_PROVIDER` | `ably` |
| `ABLY_API_KEY` | `tu_key_de_ably` |
| `ABLY_CLIENT_KEY` | `tu_client_key` |
| `ADMIN_PASSWORD` | `contraseña_segura` |
| `JWT_SECRET` | `cadena_aleatoria_larga` |
| `DATABASE_URL` | `sqlite+aiosqlite:///./game.db` |

> **Nota importante sobre SQLite en Vercel**: Vercel tiene un filesystem efímero. SQLite funcionará durante la sesión pero los datos no persisten entre deployments. Para producción real, usa **Supabase** o **PlanetScale** y cambia `DATABASE_URL` al string de conexión PostgreSQL.

### Para producción con Supabase (datos persistentes)

1. Crear proyecto gratis en [supabase.com](https://supabase.com)
2. Ir a Settings → Database → Connection string (mode: `asyncpg`)
3. Copiar la URL como `DATABASE_URL` en Vercel

---

## Opción alternativa: Railway

Si prefieres WebSockets nativos sin Ably:

```bash
# 1. Crear cuenta en railway.app
# 2. Nuevo proyecto → Deploy from GitHub
# 3. Agregar las mismas variables de entorno
# 4. Configurar: REALTIME_PROVIDER=native
# 5. Railway asigna una URL pública automáticamente
# 6. El frontend (estático) puede seguir en Vercel
# 7. Cambiar API_BASE en frontend/js/app.js a la URL de Railway
```

---

## Uso del sistema

### Flujo completo de una partida

```
Admin → /admin → Crear partida → Código UAA-XXXX generado
           ↓
Admin muestra QR con URL del lobby
           ↓
Jugadores escanean → lobby.html?code=UAA-XXXX
           ↓
Jugadores ingresan nombre → se conectan al lobby
           ↓
Admin ve jugadores listos → INICIAR COMPETENCIA
           ↓
Countdown 3-2-1 simultáneo para todos
           ↓
Competencia: 5 rondas × misiones por jugador
           ↓
Leaderboard en tiempo real durante todo el juego
           ↓
Timer llega a 0 → Pantalla de resultados
           ↓
Jugadores elegibles → /rewards → CANJEAR PREMIO
           ↓
Staff verifica código de canje → entrega premio físico
```

---

## Panel de administrador

Accede en `/admin.html`

**Contraseña por defecto**: `uaa2026admin` (cambiar en `.env`)

### Funciones disponibles

| Función | Descripción |
|---|---|
| Crear partida | Nombre, dificultad, jugadores, duración, rondas |
| Iniciar partida | Dispara countdown para todos |
| Pausar/Reanudar | Pausa el timer global |
| Agregar tiempo | +30s, +60s al timer actual |
| Misión especial | Activa misión secreta para todos |
| Evento global | Speed x2, Flash mission, Double points |
| Expulsar jugador | Kick inmediato con notificación |
| Ver jugadores sospechosos | Flag ⚠️ en tabla |
| Gestionar premios | Stock real, entregados |
| Crear códigos | Temporales, con usos y expiración |
| Analytics | Estadísticas de todas las partidas |

---

## Sistema de misiones

### 10 tipos de misiones

| # | Tipo | Descripción | Puntos base |
|---|---|---|---|
| 1 | Detective | Detectar vendedor/tienda sospechosa | 80 |
| 2 | Encuentra el error | Encontrar error matemático en checkout | 90 |
| 3 | Carrito perfecto | Construir carrito con condiciones exactas | 100 |
| 4 | Decisión | Elegir mejor combinación de productos | 70 |
| 5 | Velocidad | Encontrar producto en N segundos | 100 |
| 6 | Memoria | Recordar info mostrada por 5s | 80 |
| 7 | Ordenar | Ordenar etapas del proceso de compra | 70 |
| 8 | Código | Introducir código (QR/físico/digital) | 120 |
| 9 | Social | Misión Instagram con código temporal | 150 |
| 10 | Especial | Misión secreta (~30% de partidas) | 200 |

### Fórmula de puntuación

```
Puntos = base × dificultad × precisión × velocidad × racha - penalizaciones

Dificultad: Fácil×0.8, Normal×1.0, Difícil×1.3, Feria×1.5
Velocidad:  < 30% del tiempo → +50pts | < 60% → +25pts
Precisión:  Sin errores → +30pts | 1 error → +10pts
Racha:      ≥4 seguidas → ×2.0 | 3 → ×1.5 | 2 → ×1.25
Penalización: Respuesta incorrecta -20 | Tiempo excedido -40 | Sospechoso -50
```

### Misiones por ronda

| Ronda | Tipo | Enfoque |
|---|---|---|
| 1 | Detective / Encuentra error | Exploración y análisis |
| 2 | Carrito / Decisión | Toma de decisiones |
| 3 | Velocidad / Memoria | Habilidades de velocidad |
| 4 | Ordenar / Código | Estrategia y conocimiento |
| 5 | Especial (30%) / Aleatoria | Sorpresa final |

---

## Sistema de premios

### Configuración de premios

Los premios se configuran al crear la partida. Defaults:

| Premio | Stock | Puntos mín. | Rank mín. |
|---|---|---|---|
| 🏆 Premio Especial | 2 | 500 | Top 3 |
| ☕ Taza UAA | 3 | 300 | — |
| 📒 Libreta EC | 5 | 200 | — |
| 🖊️ Pluma UAA | 10 | 100 | — |
| 🎟️ Sticker | 20 | 50 | — |

### Operación atómica de canje

El backend usa `UPDATE rewards SET stock = stock - 1 WHERE stock > 0` de forma atómica. Si dos jugadores intentan el último premio simultáneamente, **exactamente uno** lo obtiene (el que llegó primero al servidor).

---

## Estructura del proyecto

```
TIENDA UAA/
├── frontend/
│   ├── index.html          # Landing + modales de unirse/crear
│   ├── lobby.html          # Sala de espera
│   ├── game.html           # Pantalla de competencia
│   ├── results.html        # Resultados finales
│   ├── rewards.html        # Canje de premios
│   ├── admin.html          # Panel administrador
│   ├── css/
│   │   ├── variables.css
│   │   ├── base.css
│   │   ├── components.css
│   │   ├── lobby.css
│   │   ├── game.css
│   │   ├── leaderboard.css
│   │   └── responsive.css
│   └── js/
│       ├── app.js          # Config global, Api, Session
│       ├── websocket.js    # Ably wrapper + polling fallback
│       ├── ui.js           # Toast, modal, sonido, confetti
│       ├── timer.js        # Timers global y por misión
│       ├── scoring.js      # Display de puntuación
│       ├── leaderboard.js  # Leaderboard en tiempo real
│       ├── missions.js     # 10 tipos de misiones
│       ├── lobby.js        # Controlador lobby
│       ├── game.js         # Controlador principal juego
│       ├── rewards.js      # Sistema de premios
│       └── admin.js        # Dashboard admin
├── backend/
│   ├── app.py              # FastAPI main
│   ├── game_server.py      # WS nativo (modo local)
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── game_state.py
│   │   ├── matchmaking.py
│   │   ├── anti_cheat.py
│   │   └── security.py
│   ├── models/
│   │   ├── game.py
│   │   └── rewards.py
│   └── api/
│       ├── games.py
│       ├── players.py
│       ├── missions.py
│       ├── scoring.py
│       ├── rewards.py
│       ├── codes.py
│       ├── events.py
│       └── admin.py
├── requirements.txt
├── package.json
├── vercel.json
├── .env.example
└── README.md
```

---

## Seguridad

- ✅ Puntuación calculada **exclusivamente en servidor**
- ✅ Stock de premios con operación **atómica** (no se puede duplicar)
- ✅ Códigos secretos **nunca** en JavaScript del cliente
- ✅ JWT firmados por servidor para cada jugador
- ✅ Rate limiting por jugador (anti-trampa)
- ✅ Timestamps validados (misiones imposiblemente rápidas = flag)
- ✅ Registro de actividad sospechosa en `audit_logs`
- ✅ Panel admin separado con autenticación propia

---

## Créditos

Desarrollado para la **Feria Universitaria UAA 2026**  
Ingeniería en Comercio Electrónico  
Universidad Autónoma de Aguascalientes  
