"""
MiauBot — cliente LLM sobre Gemini REST API v1beta con Function Calling.
Sin dependencia de google-generativeai/protobuf (compatible con Python 3.14+),
sin acceso directo a BD ni prompts largos quemados. Incluye rotacion automatica
de modelos ante 429/404/503 para evitar caidas por cuota del tier gratuito.
"""

from __future__ import annotations

import inspect
import json
import logging
import time
import urllib.error
import urllib.request

from django.conf import settings

from .miaubot_knowledge import obtener_config
from .miaubot_service import PerfilMascota, _extraer_perfil
from .miaubot_tools import (
    construir_herramientas_bot,
    obtener_catalogo_cacheado,
    productos_mencionados_en_texto,
    serializar_productos_card,
)

logger = logging.getLogger(__name__)

_MAX_TOOL_ROUNDS = 3
_HTTP_TIMEOUT_SEGUNDOS = 20
_COOLDOWN_429_SEGUNDOS = 300
_MODELOS_RETIRADOS = {
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-2.5-flash-lite',
}
_MODELOS_FALLBACK = (
    'gemini-3.5-flash-lite',
    'gemini-3.1-flash-lite',
    'gemini-2.5-flash',
    'gemini-3.5-flash',
)
_GEMINI_REST_URL = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'

_REGLA_TOOLS = (
    'Antes de confirmar o negar stock, marcas, productos o precios de MiauMarket, '
    'llama siempre a buscar_productos y responde solo con lo que devuelva. '
    'Para preguntas generales de mascotas o charla libre, responde directo.'
)

_modelo_en_pausa: dict[str, float] = {}


class _GeminiHTTPError(RuntimeError):
    def __init__(self, status_code: int, body: str):
        super().__init__(f'Gemini HTTP {status_code}: {body}')
        self.status_code = status_code
        self.body = body


def _construir_system_instruction(context: dict, perfil: PerfilMascota) -> str:
    """Usa prompt_sistema de MiauBotConfig (BD cacheada) + regla de tools + contexto minimo."""
    config = obtener_config()
    base = (
        config.prompt_sistema.strip()
        if config and config.prompt_sistema
        else 'Eres MiauBot, asistente de MiauMarket.'
    )

    datos_sesion = []
    if context.get('user_name'):
        datos_sesion.append(f"Cliente: {context['user_name']}")
    if getattr(perfil, 'otro_animal', None):
        datos_sesion.append(
            f"Consulta sobre: {perfil.otro_animal} (MiauMarket solo vende productos para perros y gatos)"
        )
    else:
        if perfil.nombre:
            especie = f" ({perfil.animal})" if perfil.animal else ''
            datos_sesion.append(f"Mascota: {perfil.nombre}{especie}")
        elif perfil.animal:
            datos_sesion.append(f"Animal: {perfil.animal}")
        if perfil.edad:
            datos_sesion.append(f"Edad: {perfil.edad}")
        if getattr(perfil, 'raza', None):
            datos_sesion.append(f"Raza: {perfil.raza}")

    linea_sesion = f"\nContexto: {' | '.join(datos_sesion)}." if datos_sesion else ''
    return f"{base}\n{_REGLA_TOOLS}{linea_sesion}"


def _historial_gemini(conversation_history: list) -> list[dict]:
    historial = []
    for msg in conversation_history[-10:]:
        role = msg.get('role')
        content = (msg.get('content') or '').strip()
        if not content:
            continue
        if role == 'user':
            historial.append({'role': 'user', 'parts': [{'text': content}]})
        elif role == 'assistant':
            historial.append({'role': 'model', 'parts': [{'text': content}]})
    return historial


def _llamar_gemini_rest(api_key: str, model_name: str, payload: dict) -> dict:
    url = _GEMINI_REST_URL.format(model=model_name)
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'x-goog-api-key': api_key.strip(),
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT_SEGUNDOS) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        body = ''
        try:
            body = exc.read().decode('utf-8', 'ignore')[:300]
        except Exception:
            pass
        raise _GeminiHTTPError(exc.code, body) from exc


def _partes_respuesta(response_data: dict) -> list[dict]:
    candidates = response_data.get('candidates') or []
    if not candidates:
        return []
    content = candidates[0].get('content') or {}
    parts = content.get('parts') or []
    return [p for p in parts if isinstance(p, dict)]


def _extraer_texto(parts: list[dict]) -> str:
    texto = ''.join(p.get('text', '') for p in parts if p.get('text')).strip()
    return texto.replace('**', '').strip()


def _extraer_function_calls(parts: list[dict]) -> list[dict]:
    return [
        p['functionCall']
        for p in parts
        if isinstance(p.get('functionCall'), dict) and p['functionCall'].get('name')
    ]


def _modelos_candidatos() -> list[str]:
    configurado = (getattr(settings, 'GEMINI_MODEL', '') or '').strip()
    orden = []
    if configurado and configurado not in _MODELOS_RETIRADOS:
        orden.append(configurado)
    for m in _MODELOS_FALLBACK:
        if m not in orden:
            orden.append(m)

    ahora = time.monotonic()
    activos = [m for m in orden if _modelo_en_pausa.get(m, 0) <= ahora]
    return activos or orden[:2]


def _ejecutar_conversacion_modelo(
    api_key: str,
    model_name: str,
    system_text: str,
    base_contents: list[dict],
    tool_declarations: list[dict],
    dispatcher: dict,
) -> list[dict]:
    contents = list(base_contents)
    generation_config: dict = {
        'temperature': 0.7,
        'maxOutputTokens': 1000,
        'topP': 0.9,
    }
    if '2.5' in model_name:
        generation_config['thinkingConfig'] = {'thinkingBudget': 0}

    parts: list[dict] = []
    for ronda in range(_MAX_TOOL_ROUNDS + 1):
        payload = {
            'systemInstruction': {'parts': [{'text': system_text}]},
            'contents': contents,
            'tools': [{'functionDeclarations': tool_declarations}],
            'generationConfig': generation_config,
        }
        response_data = _llamar_gemini_rest(api_key, model_name, payload)
        parts = _partes_respuesta(response_data)
        calls = _extraer_function_calls(parts)
        if not calls or ronda >= _MAX_TOOL_ROUNDS:
            break

        contents.append({'role': 'model', 'parts': parts})
        tool_response_parts = []
        for call in calls:
            name = call['name']
            fn = dispatcher.get(name)
            if not fn:
                result_payload = {'error': f'Herramienta desconocida: {name}'}
            else:
                try:
                    raw_args = call.get('args') or {}
                    valid_params = inspect.signature(fn).parameters
                    args = {k: v for k, v in raw_args.items() if k in valid_params}
                    result_payload = fn(**args)
                except Exception as tool_exc:
                    logger.warning('Error en tool %s: %s', name, tool_exc)
                    result_payload = {'error': 'No se pudo completar la consulta'}
            fn_response: dict = {'name': name, 'response': result_payload}
            if call.get('id'):
                fn_response['id'] = call['id']
            tool_response_parts.append({'functionResponse': fn_response})
        contents.append({'role': 'user', 'parts': tool_response_parts})

    return parts


def generar_respuesta_ia(
    message: str,
    conversation_history: list | None = None,
    context: dict | None = None,
    perfil: PerfilMascota | None = None,
) -> dict | None:
    """
    Ejecuta Gemini con Function Calling via REST v1beta (max 3 rondas de herramientas).
    Rota automaticamente a modelos alternos ante HTTP 429/404/503; retorna None si
    todos fallan para activar el fallback local.
    """
    api_key = (getattr(settings, 'GEMINI_API_KEY', '') or '').strip()
    if not api_key:
        return None

    context = context or {}
    history = conversation_history or []

    if perfil is None:
        textos = [message] + [m.get('content', '') for m in history if m.get('role') == 'user']
        perfil = _extraer_perfil(textos)

    system_text = _construir_system_instruction(context, perfil)
    base_contents = _historial_gemini(history)
    base_contents.append({'role': 'user', 'parts': [{'text': message}]})

    parts: list[dict] = []
    productos_recuperados: list[dict] = []
    tools_usadas: list[str] = []
    modelo_usado = ''

    for model_name in _modelos_candidatos():
        tool_declarations, dispatcher, prod_run, used_run = construir_herramientas_bot(
            usuario_id=context.get('user_id'),
            memoria=context.get('memoria'),
        )
        try:
            parts = _ejecutar_conversacion_modelo(
                api_key=api_key,
                model_name=model_name,
                system_text=system_text,
                base_contents=base_contents,
                tool_declarations=tool_declarations,
                dispatcher=dispatcher,
            )
            productos_recuperados = prod_run
            tools_usadas = used_run
            modelo_usado = model_name
            break
        except _GeminiHTTPError as exc:
            logger.warning('Gemini (%s) fallo: %s', model_name, exc)
            if exc.status_code in (404, 429):
                _modelo_en_pausa[model_name] = time.monotonic() + _COOLDOWN_429_SEGUNDOS
            if exc.status_code in (404, 429, 500, 503):
                continue
            return None
        except Exception as exc:
            logger.warning('Gemini (%s) error: %s', model_name, exc)
            return None

    texto = _extraer_texto(parts)
    if not texto:
        return None

    cards = []
    if productos_recuperados:
        _, ratings = obtener_catalogo_cacheado()
        seleccionados = productos_mencionados_en_texto(
            texto, candidatos=productos_recuperados, limite=4
        )
        if not seleccionados:
            seleccionados = productos_recuperados[:4]
        cards = serializar_productos_card(seleccionados, ratings)

    return {
        'success': True,
        'response': texto,
        'products': cards,
        'status': 'ia',
        'model': modelo_usado,
        'tools_used': list(dict.fromkeys(tools_usadas)),
        'perfil': {
            'animal': perfil.animal,
            'nombre': perfil.nombre,
            'edad': perfil.edad,
        },
    }
