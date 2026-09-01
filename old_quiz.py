"""
M├│dulo de misiones tipo quiz para el Modo Competencia.

Cada MISI├ôN pertenece a un ├írea de la carrera de Comercio Electr├│nico y tiene
M├ìNIMO 3 preguntas. Las opciones se mezclan aleatoriamente en cada partida para
que no se aprendan patrones (la respuesta correcta no queda siempre en A/B/C).

Puntuaci├│n por pregunta:
  - base seg├║n dificultad: media=100, dificil=150, avanzada=200
  - bono por velocidad: hasta +50 seg├║n lo r├ípido que respondas
  - bono por racha: +25 por cada acierto consecutivo a partir del 3.┬║
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

# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# BANCO DE MISIONES (├íreas de la carrera). Cada opci├│n es texto; "correct" es el
# ├¡ndice de la opci├│n correcta ANTES de mezclar.
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
MISSIONS = [
    {
        "id": "m1", "area": "Negocios Digitales", "emoji": "­ƒÆ╝",
        "questions": [
            {"id": "q6", "difficulty": "media",
             "text": "Una empresa vende productos directamente a consumidores mediante su p├ígina web. ┬┐Qu├® modelo representa mejor esta operaci├│n?",
             "options": ["B2B", "B2C", "C2C"], "correct": 1,
             "explanation": "B2C (Business to Consumer): la empresa vende directamente al consumidor final."},
            {"id": "q7", "difficulty": "dificil",
             "text": "Una empresa que fabrica uniformes vende grandes cantidades directamente a otras empresas mediante una plataforma digital. ┬┐Qu├® modelo corresponde?",
             "options": ["B2C", "C2C", "B2B"], "correct": 2,
             "explanation": "B2B (Business to Business): una empresa le vende a otra empresa, t├¡picamente en volumen."},
            {"id": "q16", "difficulty": "media",
             "text": "Una empresa vende sus productos a trav├®s de una plataforma donde tambi├®n venden cientos de otros negocios. ┬┐Qu├® tipo de plataforma usa?",
             "options": ["Marketplace", "ERP", "CRM"], "correct": 0,
             "explanation": "Un marketplace re├║ne a muchos vendedores en una sola plataforma (Amazon, Mercado Libre)."},
            {"id": "q15", "difficulty": "avanzada",
             "text": "Alguien tiene una idea para vender productos personalizados por internet, pero no sabe si hay demanda. ┬┐Qu├® deber├¡a hacer antes de invertir mucho dinero?",
             "options": ["Comprar miles de productos de inmediato", "Investigar el mercado y validar la idea con clientes potenciales", "Crear el logotipo y dar por terminado el proyecto"], "correct": 1,
             "explanation": "Validar la demanda antes de invertir fuerte reduce el riesgo: investigaci├│n de mercado y prueba con clientes reales."},
        ],
    },
    {
        "id": "m2", "area": "Marketing Digital", "emoji": "­ƒô▒",
        "questions": [
            {"id": "q1", "difficulty": "media",
             "text": "Una tienda recibe muchas visitas desde Instagram, pero muy pocas personas compran. ┬┐Qu├® deber├¡a analizar primero?",
             "options": ["El color del logotipo", "El comportamiento de los usuarios en el sitio y el proceso de conversi├│n", "La cantidad de seguidores de la cuenta"], "correct": 1,
             "explanation": "Muchas visitas y pocas compras = problema de conversi├│n: hay que analizar qu├® hacen los usuarios dentro del sitio."},
            {"id": "q9", "difficulty": "dificil",
             "text": "Una tienda quiere aparecer entre los primeros resultados cuando alguien busca en Google un producto que vende. ┬┐Qu├® estrategia debe conocer?",
             "options": ["SEO", "CRM", "ERP"], "correct": 0,
             "explanation": "SEO (Search Engine Optimization) mejora el posicionamiento org├ínico en buscadores."},
            {"id": "q10", "difficulty": "media",
             "text": "Una empresa quiere registrar las compras anteriores de sus clientes para ofrecerles productos relacionados despu├®s. ┬┐Qu├® sistema le ayuda?",
             "options": ["CRM", "Editor de im├ígenes", "Sistema operativo"], "correct": 0,
             "explanation": "El CRM (gesti├│n de relaci├│n con clientes) guarda el historial para personalizar ofertas y fidelizar."},
        ],
    },
    {
        "id": "m3", "area": "Tecnolog├¡a y Desarrollo", "emoji": "­ƒÆ╗",
        "questions": [
            {"id": "q4", "difficulty": "media",
             "text": "Una tienda tiene miles de clientes y necesita almacenar nombres, correos, pedidos y productos comprados para consultarlos despu├®s. ┬┐Qu├® conocimiento es clave?",
             "options": ["Bases de datos", "Fotograf├¡a comercial", "Dise├▒o de empaques"], "correct": 0,
             "explanation": "Las bases de datos permiten almacenar y consultar de forma estructurada grandes vol├║menes de informaci├│n."},
            {"id": "q5", "difficulty": "dificil",
             "text": "Una empresa quiere que el carrito actualice autom├íticamente el precio cuando el cliente cambia la cantidad. ┬┐Qu├® ├írea se encarga principalmente?",
             "options": ["Programaci├│n y desarrollo web", "Mercadotecnia tradicional", "Log├¡stica de almac├®n"], "correct": 0,
             "explanation": "Esa l├│gica interactiva la implementa el desarrollo web (front y back)."},
            {"id": "q19", "difficulty": "avanzada",
             "text": "Una tienda quiere conectar su web con el sistema de inventario y con una paqueter├¡a para que los pedidos se transfieran autom├íticamente. ┬┐Qu├® conocimiento es especialmente ├║til?",
             "options": ["Integraci├│n de sistemas y APIs", "Fotograf├¡a de productos ├║nicamente", "Dise├▒o de logotipos"], "correct": 0,
             "explanation": "Las APIs permiten que distintos sistemas se comuniquen e intercambien datos autom├íticamente."},
            {"id": "q18", "difficulty": "dificil",
             "text": "Una tienda quiere que, al confirmarse una compra, el sistema env├¡e autom├íticamente un correo al cliente y actualice el inventario. ┬┐Qu├® concepto aplica?",
             "options": ["Automatizaci├│n de procesos", "Publicidad impresa", "Dise├▒o editorial"], "correct": 0,
             "explanation": "La automatizaci├│n ejecuta tareas repetitivas (correos, inventario) sin intervenci├│n manual."},
        ],
    },
    {
        "id": "m4", "area": "Log├¡stica y Operaciones", "emoji": "­ƒÜÜ",
        "questions": [
            {"id": "q8", "difficulty": "media",
             "text": "Un producto debe salir del almac├®n, prepararse, empaquetarse y entregarse. ┬┐Qu├® ├írea coordina principalmente este proceso?",
             "options": ["Log├¡stica y cadena de suministro", "Dise├▒o UX", "Publicidad en redes sociales"], "correct": 0,
             "explanation": "La log├¡stica y la cadena de suministro coordinan almacenamiento, preparaci├│n y entrega."},
            {"id": "q17", "difficulty": "avanzada",
             "text": "Una empresa mexicana quiere vender a clientes de otros pa├¡ses. ┬┐Qu├® debe considerar adem├ís de crear una p├ígina web?",
             "options": ["Log├¡stica internacional, m├®todos de pago, impuestos, regulaciones y diferencias de mercado", "├Ünicamente cambiar el idioma del bot├│n de compra", "Solamente subir el precio de los productos"], "correct": 0,
             "explanation": "El comercio internacional implica aduanas, impuestos, pagos, regulaciones y adaptaci├│n cultural, no solo traducir."},
            {"id": "q_last_mile", "difficulty": "dificil",
             "text": "Los clientes se quejan de entregas lentas y sin seguimiento. ┬┐Qu├® mejora operativa tendr├¡a mayor impacto en la satisfacci├│n?",
             "options": ["Optimizar la ├║ltima milla y ofrecer rastreo del pedido en tiempo real", "Quitar la opci├│n de env├¡o a domicilio", "Aumentar el costo de env├¡o"], "correct": 0,
             "explanation": "La '├║ltima milla' (la entrega final) y el rastreo en tiempo real son clave para la satisfacci├│n y reducen dudas del cliente."},
            {"id": "q_stock", "difficulty": "dificil",
             "text": "Una tienda vendi├│ un producto que ya no ten├¡a en existencia porque su inventario en l├¡nea no coincid├¡a con el real. ┬┐Qu├® necesita?",
             "options": ["Sincronizaci├│n de inventario en tiempo real entre canales", "Vender solo un producto a la vez", "Eliminar el cat├ílogo en l├¡nea"], "correct": 0,
             "explanation": "La sincronizaci├│n de inventario evita sobreventa cuando se vende por varios canales al mismo tiempo."},
        ],
    },
    {
        "id": "m5", "area": "Datos y Anal├¡tica", "emoji": "­ƒôè",
        "questions": [
            {"id": "q3", "difficulty": "media",
             "text": "Una empresa quiere saber qu├® productos venden m├ís, cu├íles tienen mayor demanda y cu├índo compran sus clientes. ┬┐Qu├® ├írea es m├ís ├║til?",
             "options": ["Anal├¡tica de datos", "Dise├▒o gr├ífico exclusivamente", "Atenci├│n telef├│nica"], "correct": 0,
             "explanation": "La anal├¡tica de datos convierte la informaci├│n de ventas y comportamiento en decisiones."},
            {"id": "q14", "difficulty": "dificil",
             "text": "Una tienda recibe 10,000 visitantes pero solo 100 compran. ┬┐Qu├® indicador deber├¡a analizar para entender por qu├®?",
             "options": ["Tasa de conversi├│n", "Cantidad de empleados", "Tama├▒o del almac├®n"], "correct": 0,
             "explanation": "La tasa de conversi├│n (compras ├À visitas) mide qu├® tan bien el tr├ífico se convierte en ventas."},
            {"id": "q12", "difficulty": "avanzada",
             "text": "Una tienda descubre que la mayor├¡a de sus compradores tiene 18-25 a├▒os y usa el celular para comprar. ┬┐Qu├® decisi├│n es m├ís l├│gica?",
             "options": ["Ignorar los datos porque todos compran igual", "Optimizar la experiencia m├│vil y adaptar la estrategia a ese segmento", "Eliminar la web y vender solo f├¡sicamente"], "correct": 1,
             "explanation": "Los datos gu├¡an la estrategia: si el segmento es joven y m├│vil, se prioriza la experiencia m├│vil."},
        ],
    },
    {
        "id": "m6", "area": "Experiencia y Seguridad", "emoji": "­ƒøÆ",
        "questions": [
            {"id": "q2", "difficulty": "media",
             "text": "Una tienda tiene buenos productos y precios, pero los clientes abandonan porque no encuentran el bot├│n de comprar. ┬┐Con qu├® ├írea se relaciona directamente?",
             "options": ["UX (Experiencia de Usuario)", "Contabilidad fiscal", "Administraci├│n de inventarios"], "correct": 0,
             "explanation": "La UX se ocupa de que el usuario logre su objetivo (comprar) de forma f├ícil e intuitiva."},
            {"id": "q13", "difficulty": "media",
             "text": "Un dise├▒ador trabaja en la distribuci├│n de botones, colores, tipograf├¡as e im├ígenes de una tienda. ┬┐Con qu├® concepto se relaciona principalmente?",
             "options": ["UI (Interfaz de Usuario)", "Log├¡stica inversa", "Comercio exterior"], "correct": 0,
             "explanation": "La UI es la interfaz visual: botones, colores, tipograf├¡a e im├ígenes con las que interact├║a el usuario."},
            {"id": "q11", "difficulty": "dificil",
             "text": "Una tienda almacena datos de clientes y procesa pagos por internet. ┬┐Por qu├® es importante la ciberseguridad?",
             "options": ["Porque protege la informaci├│n y reduce el riesgo de accesos o transacciones no autorizadas", "Porque hace m├ís baratos los productos", "Porque aumenta autom├íticamente las ventas"], "correct": 0,
             "explanation": "La ciberseguridad protege datos sensibles y pagos, evitando fraudes y accesos no autorizados."},
            {"id": "q20", "difficulty": "avanzada",
             "text": "Una empresa busca a alguien que dise├▒e su tienda, analice ventas, proponga estrategias, entienda al cliente y coordine ventas y log├¡stica. ┬┐Qu├® perfil se acerca m├ís a Comercio Electr├│nico?",
             "options": ["Alguien enfocado solo en publicaciones para redes sociales", "Alguien que combina negocios, tecnolog├¡a, marketing, datos y operaci├│n digital", "Alguien dedicado solo a reparar computadoras"], "correct": 1,
             "explanation": "El profesional de Comercio Electr├│nico es un perfil h├¡brido: negocios + tecnolog├¡a + marketing + datos + operaci├│n."},
        ],
    },
]

MISSIONS_BY_ID = {m["id"]: m for m in MISSIONS}


def _shuffle_options(q: dict) -> dict:
    """Devuelve una copia de la pregunta con las opciones mezcladas y el nuevo
    ├¡ndice correcto. No expone cu├íl es la correcta al frontend."""
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


# ÔöÇÔöÇ Listado de misiones con su estado para un jugador ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
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


# ÔöÇÔöÇ Iniciar una misi├│n: devuelve sus preguntas con opciones mezcladas ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
@router.post("/start")
async def start(req: StartReq):
    mission = MISSIONS_BY_ID.get(req.mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Misi├│n no encontrada")

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


# ÔöÇÔöÇ Responder UNA pregunta ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
@router.post("/answer")
async def answer(req: AnswerReq):
    async with get_db() as db:
        cur = await db.execute(
            "SELECT run_data, status FROM quiz_progress WHERE game_code=? AND player_id=? AND mission_id=?",
            (req.game_code, req.player_id, req.mission_id),
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Misi├│n no iniciada")
        payload = json.loads(row["run_data"])

        qinfo = next((q for q in payload["questions"] if q["id"] == req.question_id), None)
        if not qinfo:
            raise HTTPException(status_code=400, detail="Pregunta no pertenece a la misi├│n")

        already = req.question_id in payload["answered"]
        is_correct = (req.answer_index == qinfo["correct"])

        # ÔöÇÔöÇ Puntuaci├│n ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
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

    # Explicaci├│n desde el banco original
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
