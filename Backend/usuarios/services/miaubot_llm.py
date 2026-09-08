"""
MiauBot — respuestas con IA en la nube (Google Gemini).
El prompt, conocimiento y catalogo vienen de la BD; la inteligencia es del LLM.
"""

import logging

from django.conf import settings

from ..models import MiauBotConocimiento, Producto
from .ratings_service import obtener_ratings_dict
from .miaubot_knowledge import obtener_config
from .miaubot_aprendizaje import aprendizaje_para_prompt
from .miaubot_memoria import texto_memoria_prompt
from .miaubot_service import PerfilMascota, _extraer_perfil, _ref_mascota

logger = logging.getLogger(__name__)


def _format_price(precio) -> str:
    try:
        return f'${int(precio):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return str(precio)


def _catalogo_texto(limite: int = 25) -> str:
    ratings = obtener_ratings_dict()
    lineas = []
    for p in Producto.objects.filter(Stock__gt=0).order_by('-Stock')[:limite]:
        r = ratings.get(p.id, {})
        extra = ''
        if r.get('promedio', 0) > 0:
            extra = f" | Rating {r['promedio']:.1f}/5 ({r['total']} resenas)"
        desc = (p.Descripcion or '')[:120]
        lineas.append(
            f"- ID {p.id} | {p.Titulo} | {p.Categoria} | "
            f"{_format_price(p.Precio)} | Stock {p.Stock}{extra}"
            + (f" | {desc}" if desc else '')
        )
    return '\n'.join(lineas) if lineas else '(Sin productos con stock)'


def _conocimiento_texto(animal: str = 'gato', limite: int = 12) -> str:
    items = MiauBotConocimiento.objects.filter(
        activo=True, animal__in=[animal, 'general']
    ).order_by('-prioridad')[:limite]
    return '\n\n'.join(f"[{i.animal}/{i.tema}] {i.respuesta}" for i in items)


def _construir_system_instruction(context: dict, perfil: PerfilMascota, mensaje: str = '') -> str:
    config = obtener_config()
    base = (
        config.prompt_sistema if config else
        'Eres MiauBot, asistente experto y amable de MiauMarket (tienda de mascotas).'
    )

    user_name = context.get('user_name') or 'invitado'
    ref = _ref_mascota(perfil)
    aprendido = aprendizaje_para_prompt(mensaje, perfil.animal) if mensaje else ''
    memoria_txt = texto_memoria_prompt(context.get('memoria'))

    bloque_aprendido = ''
    if aprendido:
        bloque_aprendido = f"""
PREGUNTAS ANTERIORES DE CLIENTES (aprendizaje aprobado — usa como referencia):
{aprendido}
"""

    bloque_memoria = ''
    if memoria_txt:
        bloque_memoria = f"""
{memoria_txt}
- NO repitas preguntas sobre datos que ya conoces (raza, edad, tipo de producto).
- Si el cliente ya dijo comida/juguetes/higiene, recomienda directamente de CATALOGO.
- Si pregunto por salud antes, pregunta como sigue la mascota.
"""

    return f"""{base}

REGLAS OBLIGATORIAS:
- Responde SIEMPRE en espanol, tono calido y natural (como un asesor humano experto).
- Personaliza segun la mascota del cliente ({perfil.animal}, ref: {ref}).
- Cliente actual: {user_name}.
- SOLO recomienda productos de la lista CATALOGO abajo. NUNCA inventes productos, precios ni stock.
- Si preguntan por algo que no esta en catalogo, dilo con honestidad y ofrece alternativas reales.
- Respuestas concisas (3-6 lineas salvo que pidan detalle). Sin markdown ni asteriscos.
- Adapta consejos al animal: gato vs perro.
- Recuerda el historial de la conversacion.

PERFIL MASCOTA DETECTADO:
- Animal: {perfil.animal}
- Nombre: {perfil.nombre or 'no indicado'}
- Raza: {getattr(perfil, 'raza', None) or 'no indicada'}
- Edad: {perfil.edad or 'no indicada'}
- Tamano: {perfil.tamano or 'no indicado'}
- Temas ya mencionados: {', '.join(perfil.temas) if perfil.temas else 'ninguno'}

CONOCIMIENTO INTERNO (usa como base, no copies textual):
{_conocimiento_texto(perfil.animal)}
{bloque_memoria}{bloque_aprendido}
CATALOGO REAL MIAUMARKET (unica fuente de productos):
{_catalogo_texto()}
"""


def _historial_gemini(conversation_history: list) -> list[dict]:
    historial = []
    for msg in conversation_history[-12:]:
        role = msg.get('role')
        content = (msg.get('content') or '').strip()
        if not content:
            continue
        if role == 'user':
            historial.append({'role': 'user', 'parts': [content]})
        elif role == 'assistant':
            historial.append({'role': 'model', 'parts': [content]})
    return historial


def generar_respuesta_ia(
    message: str,
    conversation_history: list | None = None,
    context: dict | None = None,
    perfil: PerfilMascota | None = None,
) -> dict | None:
    """
    Llama a Gemini. Retorna None si no hay API key o falla (usa fallback local).
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or ''
    if not api_key.strip():
        return None

    context = context or {}
    history = conversation_history or []

    if perfil is None:
        textos = [message] + [m.get('content', '') for m in history if m.get('role') == 'user']
        for m in history:
            if m.get('role') == 'assistant':
                textos.append(m.get('content', ''))
        perfil = _extraer_perfil(textos)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')

        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=_construir_system_instruction(context, perfil, message),
        )

        generation_config = {
            'temperature': 0.75,
            'max_output_tokens': 800,
            'top_p': 0.9,
        }

        chat_history = _historial_gemini(history)
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(message, generation_config=generation_config)

        texto = ''
        if hasattr(response, 'text') and response.text:
            texto = response.text.strip()
        elif response.candidates:
            parts = response.candidates[0].content.parts
            texto = ''.join(getattr(p, 'text', '') for p in parts).strip()

        if not texto:
            return None

        return {
            'success': True,
            'response': texto,
            'status': 'ia',
            'perfil': {
                'animal': perfil.animal,
                'nombre': perfil.nombre,
                'edad': perfil.edad,
            },
        }

    except Exception as exc:
        logger.warning('Gemini error: %s', exc)
        return None
