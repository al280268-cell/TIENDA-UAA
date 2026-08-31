"""
Módulo de misiones tipo quiz para el Modo Competencia.

Cada MISIÓN pertenece a un área de la carrera de Comercio Electrónico y tiene
MÍNIMO 3 preguntas. Las opciones se mezclan aleatoriamente en cada partida para
que no se aprendan patrones (la respuesta correcta no queda siempre en A/B/C).

Puntuación por pregunta:
  - base según dificultad: media=100, dificil=150, avanzada=200
  - bono por velocidad: hasta +50 según lo rápido que respondas
  - bono por racha: +25 por cada acierto consecutivo a partir del 3.º
  - respuesta incorrecta: -50
"""
import time
import uuid
import random
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.database import get_db
from backend.core.game_state import get_game, update_score

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

DIFFICULTY_POINTS = {"media": 100, "dificil": 150, "avanzada": 200}
WRONG_PENALTY = 50
SPEED_MAX_BONUS = 50
SPEED_WINDOW_MS = 15000   # responder en <15s da bono proporcional

# ─────────────────────────────────────────────────────────────────────────────
# BANCO DE MISIONES (áreas de la carrera). Cada opción es texto; "correct" es el
# índice de la opción correcta ANTES de mezclar.
# ─────────────────────────────────────────────────────────────────────────────
MISSIONS = [
    {
        "id": "m1", "area": "Negocios Digitales", "emoji": "💼",
        "questions": [
            {"id": "q6", "difficulty": "media",
             "text": "Una empresa vende productos directamente a consumidores mediante su página web. ¿Qué modelo representa mejor esta operación?",
             "options": ["B2B", "B2C", "C2C"], "correct": 1,
             "explanation": "B2C (Business to Consumer): la empresa vende directamente al consumidor final."},
            {"id": "q7", "difficulty": "dificil",
             "text": "Una empresa que fabrica uniformes vende grandes cantidades directamente a otras empresas mediante una plataforma digital. ¿Qué modelo corresponde?",
             "options": ["B2C", "C2C", "B2B"], "correct": 2,
             "explanation": "B2B (Business to Business): una empresa le vende a otra empresa, típicamente en volumen."},
            {"id": "q16", "difficulty": "media",
             "text": "Una empresa vende sus productos a través de una plataforma donde también venden cientos de otros negocios. ¿Qué tipo de plataforma usa?",
             "options": ["Marketplace", "ERP", "CRM"], "correct": 0,
             "explanation": "Un marketplace reúne a muchos vendedores en una sola plataforma (Amazon, Mercado Libre)."},
            {"id": "q15", "difficulty": "avanzada",
             "text": "Alguien tiene una idea para vender productos personalizados por internet, pero no sabe si hay demanda. ¿Qué debería hacer antes de invertir mucho dinero?",
             "options": ["Comprar miles de productos de inmediato", "Investigar el mercado y validar la idea con clientes potenciales", "Crear el logotipo y dar por terminado el proyecto"], "correct": 1,
             "explanation": "Validar la demanda antes de invertir fuerte reduce el riesgo: investigación de mercado y prueba con clientes reales."},
        ],
    },
    {
        "id": "m2", "area": "Marketing Digital", "emoji": "📱",
        "questions": [
            {"id": "q1", "difficulty": "media",
             "text": "Una tienda recibe muchas visitas desde Instagram, pero muy pocas personas compran. ¿Qué debería analizar primero?",
             "options": ["El color del logotipo", "El comportamiento de los usuarios en el sitio y el proceso de conversión", "La cantidad de seguidores de la cuenta"], "correct": 1,
             "explanation": "Muchas visitas y pocas compras = problema de conversión: hay que analizar qué hacen los usuarios dentro del sitio."},
            {"id": "q9", "difficulty": "dificil",
             "text": "Una tienda quiere aparecer entre los primeros resultados cuando alguien busca en Google un producto que vende. ¿Qué estrategia debe conocer?",
             "options": ["SEO", "CRM", "ERP"], "correct": 0,
             "explanation": "SEO (Search Engine Optimization) mejora el posicionamiento orgánico en buscadores."},
            {"id": "q10", "difficulty": "media",
             "text": "Una empresa quiere registrar las compras anteriores de sus clientes para ofrecerles productos relacionados después. ¿Qué sistema le ayuda?",
             "options": ["CRM", "Editor de imágenes", "Sistema operativo"], "correct": 0,
             "explanation": "El CRM (gestión de relación con clientes) guarda el historial para personalizar ofertas y fidelizar."},
        ],
    },
    {
        "id": "m3", "area": "Tecnología y Desarrollo", "emoji": "💻",
        "questions": [
            {"id": "q4", "difficulty": "media",
             "text": "Una tienda tiene miles de clientes y necesita almacenar nombres, correos, pedidos y productos comprados para consultarlos después. ¿Qué conocimiento es clave?",
             "options": ["Bases de datos", "Fotografía comercial", "Diseño de empaques"], "correct": 0,
             "explanation": "Las bases de datos permiten almacenar y consultar de forma estructurada grandes volúmenes de información."},
            {"id": "q5", "difficulty": "dificil",
             "text": "Una empresa quiere que el carrito actualice automáticamente el precio cuando el cliente cambia la cantidad. ¿Qué área se encarga principalmente?",
             "options": ["Programación y desarrollo web", "Mercadotecnia tradicional", "Logística de almacén"], "correct": 0,
             "explanation": "Esa lógica interactiva la implementa el desarrollo web (front y back)."},
            {"id": "q19", "difficulty": "avanzada",
             "text": "Una tienda quiere conectar su web con el sistema de inventario y con una paquetería para que los pedidos se transfieran automáticamente. ¿Qué conocimiento es especialmente útil?",
             "options": ["Integración de sistemas y APIs", "Fotografía de productos únicamente", "Diseño de logotipos"], "correct": 0,
             "explanation": "Las APIs permiten que distintos sistemas se comuniquen e intercambien datos automáticamente."},
            {"id": "q18", "difficulty": "dificil",
             "text": "Una tienda quiere que, al confirmarse una compra, el sistema envíe automáticamente un correo al cliente y actualice el inventario. ¿Qué concepto aplica?",
             "options": ["Automatización de procesos", "Publicidad impresa", "Diseño editorial"], "correct": 0,
             "explanation": "La automatización ejecuta tareas repetitivas (correos, inventario) sin intervención manual."},
        ],
    },
    {
        "id": "m4", "area": "Logística y Operaciones", "emoji": "🚚",
        "questions": [
            {"id": "q8", "difficulty": "media",
             "text": "Un producto debe salir del almacén, prepararse, empaquetarse y entregarse. ¿Qué área coordina principalmente este proceso?",
             "options": ["Logística y cadena de suministro", "Diseño UX", "Publicidad en redes sociales"], "correct": 0,
             "explanation": "La logística y la cadena de suministro coordinan almacenamiento, preparación y entrega."},
            {"id": "q17", "difficulty": "avanzada",
             "text": "Una empresa mexicana quiere vender a clientes de otros países. ¿Qué debe considerar además de crear una página web?",
             "options": ["Logística internacional, métodos de pago, impuestos, regulaciones y diferencias de mercado", "Únicamente cambiar el idioma del botón de compra", "Solamente subir el precio de los productos"], "correct": 0,
             "explanation": "El comercio internacional implica aduanas, impuestos, pagos, regulaciones y adaptación cultural, no solo traducir."},
            {"id": "q_last_mile", "difficulty": "dificil",
             "text": "Los clientes se quejan de entregas lentas y sin seguimiento. ¿Qué mejora operativa tendría mayor impacto en la satisfacción?",
             "options": ["Optimizar la última milla y ofrecer rastreo del pedido en tiempo real", "Quitar la opción de envío a domicilio", "Aumentar el costo de envío"], "correct": 0,
             "explanation": "La 'última milla' (la entrega final) y el rastreo en tiempo real son clave para la satisfacción y reducen dudas del cliente."},
            {"id": "q_stock", "difficulty": "dificil",
             "text": "Una tienda vendió un producto que ya no tenía en existencia porque su inventario en línea no coincidía con el real. ¿Qué necesita?",
             "options": ["Sincronización de inventario en tiempo real entre canales", "Vender solo un producto a la vez", "Eliminar el catálogo en línea"], "correct": 0,
             "explanation": "La sincronización de inventario evita sobreventa cuando se vende por varios canales al mismo tiempo."},
        ],
    },
    {
        "id": "m5", "area": "Datos y Analítica", "emoji": "📊",
        "questions": [
            {"id": "q3", "difficulty": "media",
             "text": "Una empresa quiere saber qué productos venden más, cuáles tienen mayor demanda y cuándo compran sus clientes. ¿Qué área es más útil?",
             "options": ["Analítica de datos", "Diseño gráfico exclusivamente", "Atención telefónica"], "correct": 0,
             "explanation": "La analítica de datos convierte la información de ventas y comportamiento en decisiones."},
            {"id": "q14", "difficulty": "dificil",
             "text": "Una tienda recibe 10,000 visitantes pero solo 100 compran. ¿Qué indicador debería analizar para entender por qué?",
             "options": ["Tasa de conversión", "Cantidad de empleados", "Tamaño del almacén"], "correct": 0,
             "explanation": "La tasa de conversión (compras ÷ visitas) mide qué tan bien el tráfico se convierte en ventas."},
            {"id": "q12", "difficulty": "avanzada",
             "text": "Una tienda descubre que la mayoría de sus compradores tiene 18-25 años y usa el celular para comprar. ¿Qué decisión es más lógica?",
             "options": ["Ignorar los datos porque todos compran igual", "Optimizar la experiencia móvil y adaptar la estrategia a ese segmento", "Eliminar la web y vender solo físicamente"], "correct": 1,
             "explanation": "Los datos guían la estrategia: si el segmento es joven y móvil, se prioriza la experiencia móvil."},
        ],
    },
    {
        "id": "m6", "area": "Experiencia y Seguridad", "emoji": "🛒",
        "questions": [
            {"id": "q2", "difficulty": "media",
             "text": "Una tienda tiene buenos productos y precios, pero los clientes abandonan porque no encuentran el botón de comprar. ¿Con qué área se relaciona directamente?",
             "options": ["UX (Experiencia de Usuario)", "Contabilidad fiscal", "Administración de inventarios"], "correct": 0,
             "explanation": "La UX se ocupa de que el usuario logre su objetivo (comprar) de forma fácil e intuitiva."},
            {"id": "q13", "difficulty": "media",
             "text": "Un diseñador trabaja en la distribución de botones, colores, tipografías e imágenes de una tienda. ¿Con qué concepto se relaciona principalmente?",
             "options": ["UI (Interfaz de Usuario)", "Logística inversa", "Comercio exterior"], "correct": 0,
             "explanation": "La UI es la interfaz visual: botones, colores, tipografía e imágenes con las que interactúa el usuario."},
            {"id": "q11", "difficulty": "dificil",
             "text": "Una tienda almacena datos de clientes y procesa pagos por internet. ¿Por qué es importante la ciberseguridad?",
             "options": ["Porque protege la información y reduce el riesgo de accesos o transacciones no autorizadas", "Porque hace más baratos los productos", "Porque aumenta automáticamente las ventas"], "correct": 0,
             "explanation": "La ciberseguridad protege datos sensibles y pagos, evitando fraudes y accesos no autorizados."},
            {"id": "q20", "difficulty": "avanzada",
             "text": "Una empresa busca a alguien que diseñe su tienda, analice ventas, proponga estrategias, entienda al cliente y coordine ventas y logística. ¿Qué perfil se acerca más a Comercio Electrónico?",
             "options": ["Alguien enfocado solo en publicaciones para redes sociales", "Alguien que combina negocios, tecnología, marketing, datos y operación digital", "Alguien dedicado solo a reparar computadoras"], "correct": 1,
             "explanation": "El profesional de Comercio Electrónico es un perfil híbrido: negocios + tecnología + marketing + datos + operación."},
        ],
    },
]

MISSIONS_BY_ID = {m["id"]: m for m in MISSIONS}


def _shuffle_options(q: dict) -> dict:
    """Devuelve una copia de la pregunta con las opciones mezcladas y el nuevo
    índice correcto. No expone cuál es la correcta al frontend."""
    idx = list(range(len(q["options"])))
    random.shuffle(idx)
    new_options = [q["options"][i] for i in idx]
    new_correct = idx.index(q["correct"])
    return {
        "id": q["id"],
        "difficulty": q["difficulty"],
        "points": DIFFICULTY_POINTS[q["difficulty"]],
        "text": q["text"],
        "options": new_options,
        "_correct": new_correct,           # se guarda en BD, no se manda al front
        "explanation": q["explanation"],
    }


# ── Listado de misiones con su estado para un jugador ─────────────────────────
@router.get("/missions/{game_code}/{player_id}")
async def list_missions(game_code: str, player_id: str):
    async with get_db() as db:
        cur = await db.execute(
            "SELECT mission_id, status FROM quiz_progress WHERE game_code=? AND player_id=?",
            (game_code, player_id),
        )
        rows = await cur.fetchall()
    status_by_id = {r["mission_id"]: r["status"] for r in rows}
    out = []
    for m in MISSIONS:
        out.append({
            "mission_id": m["id"],
            "area": m["area"],
            "emoji": m["emoji"],
            "num_questions": len(m["questions"]),
            "status": status_by_id.get(m["id"], "available"),
        })
    all_complete = all(o["status"] == "completed" for o in out)
    return {"missions": out, "all_complete": all_complete}


class StartReq(BaseModel):
    player_id: str
    game_code: str
    mission_id: str


# ── Iniciar una misión: devuelve sus preguntas con opciones mezcladas ─────────
@router.post("/start")
async def start(req: StartReq):
    mission = MISSIONS_BY_ID.get(req.mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    shuffled = [_shuffle_options(q) for q in mission["questions"]]
    # Guardamos el estado (respuestas correctas) para validar sin confiar en el front
    run_id = str(uuid.uuid4())
    payload = {
        "mission_id": mission["id"],
        "run_id": run_id,
        "questions": [{"id": q["id"], "correct": q["_correct"], "points": q["points"]} for q in shuffled],
        "answered": [],
    }
    async with get_db() as db:
        await db.execute(
            "INSERT OR REPLACE INTO quiz_progress "
            "(game_code, player_id, mission_id, status, run_data, started_at) "
            "VALUES (?, ?, ?, 'in_progress', ?, ?)",
            (req.game_code, req.player_id, mission["id"], json.dumps(payload), time.time()),
        )
        await db.commit()

    # Lo que ve el frontend (sin la respuesta correcta)
    front_questions = [{
        "id": q["id"],
        "difficulty": q["difficulty"],
        "points": q["points"],
        "text": q["text"],
        "options": q["options"],
    } for q in shuffled]

    return {
        "mission_id": mission["id"],
        "area": mission["area"],
        "emoji": mission["emoji"],
        "run_id": run_id,
        "total_questions": len(front_questions),
        "questions": front_questions,
    }


class AnswerReq(BaseModel):
    player_id: str
    game_code: str
    mission_id: str
    question_id: str
    answer_index: int
    time_taken_ms: int = 8000
    streak: int = 0


# ── Responder UNA pregunta ────────────────────────────────────────────────────
@router.post("/answer")
async def answer(req: AnswerReq):
    async with get_db() as db:
        cur = await db.execute(
            "SELECT run_data, status FROM quiz_progress WHERE game_code=? AND player_id=? AND mission_id=?",
            (req.game_code, req.player_id, req.mission_id),
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Misión no iniciada")
        payload = json.loads(row["run_data"])

        qinfo = next((q for q in payload["questions"] if q["id"] == req.question_id), None)
        if not qinfo:
            raise HTTPException(status_code=400, detail="Pregunta no pertenece a la misión")

        already = req.question_id in payload["answered"]
        is_correct = (req.answer_index == qinfo["correct"])

        # ── Puntuación ──────────────────────────────────────────────────────
        base = qinfo["points"]
        speed_bonus = 0
        streak_bonus = 0
        if is_correct:
            frac = max(0.0, min(1.0, 1.0 - (req.time_taken_ms / SPEED_WINDOW_MS)))
            speed_bonus = int(round(SPEED_MAX_BONUS * frac))
            if req.streak >= 2:  # a partir del 3.er acierto consecutivo
                streak_bonus = 25 * (req.streak - 1)
            gained = base + speed_bonus + streak_bonus
        else:
            gained = -WRONG_PENALTY

        # No permitir re-responder para farmear puntos
        if already:
            gained = 0
            speed_bonus = streak_bonus = 0

        if not already:
            payload["answered"].append(req.question_id)

        mission_complete = len(payload["answered"]) >= len(payload["questions"])
        new_status = "completed" if mission_complete else "in_progress"

        await db.execute(
            "UPDATE quiz_progress SET run_data=?, status=? WHERE game_code=? AND player_id=? AND mission_id=?",
            (json.dumps(payload), new_status, req.game_code, req.player_id, req.mission_id),
        )
        await db.commit()

    # Actualiza el marcador global de la partida (en memoria) si existe
    total_points = None
    if gained and not already:
        try:
            update_score(req.game_code, req.player_id, gained, is_correct)
            # Send live update to the Ably channel so others see the score immediately
            from backend.app import publish_to_ably
            await publish_to_ably(f"game:{req.game_code}", "score_update", {
                "player_id": req.player_id,
                "points": gained
            })
            # Try to fetch it back for the local response
            from backend.core.game_state import get_game as get_gs_sync
            g = get_gs_sync(req.game_code)
            if g and req.player_id in g.players:
                total_points = g.players[req.player_id].points
        except Exception as e:
            print("Error updating score:", e)
            pass

    # Explicación desde el banco original
    src_q = next((q for m in MISSIONS for q in m["questions"] if q["id"] == req.question_id), {})

    return {
        "correct": is_correct,
        "already_answered": already,
        "points": base if is_correct else 0,
        "speed_bonus": speed_bonus,
        "streak_bonus": streak_bonus,
        "net": gained,
        "explanation": src_q.get("explanation", ""),
        "correct_index": qinfo["correct"],
        "mission_complete": mission_complete,
        "total_points": total_points,
    }
