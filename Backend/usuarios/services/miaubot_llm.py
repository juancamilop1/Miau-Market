"""
MiauBot — cliente LLM (Google Gemini con Function Calling).
Sin acceso directo a BD ni prompts largos quemados: lee prompt_sistema desde
MiauBotConfig (cacheado) y delega consultas a las tools de miaubot_tools.
"""

from __future__ import annotations

import logging

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
_MODELOS_RETIRADOS = {'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro'}


def _construir_system_instruction(context: dict, perfil: PerfilMascota) -> str:
    """Usa prompt_sistema de MiauBotConfig (BD cacheada) + contexto minimo de sesion."""
    config = obtener_config()
    base = (
        config.prompt_sistema.strip()
        if config and config.prompt_sistema
        else 'Eres MiauBot, asistente de MiauMarket.'
    )

    datos_sesion = []
    if context.get('user_name'):
        datos_sesion.append(f"Cliente: {context['user_name']}")
    if perfil.nombre:
        datos_sesion.append(f"Mascota: {perfil.nombre} ({perfil.animal})")
    elif perfil.animal:
        datos_sesion.append(f"Animal: {perfil.animal}")
    if perfil.edad:
        datos_sesion.append(f"Edad: {perfil.edad}")
    if getattr(perfil, 'raza', None):
        datos_sesion.append(f"Raza: {perfil.raza}")

    linea_sesion = f"\nContexto: {' | '.join(datos_sesion)}." if datos_sesion else ''
    return f"{base}{linea_sesion}"


def _historial_gemini(conversation_history: list) -> list[dict]:
    historial = []
    for msg in conversation_history[-10:]:
        role = msg.get('role')
        content = (msg.get('content') or '').strip()
        if not content:
            continue
        if role == 'user':
            historial.append({'role': 'user', 'parts': [content]})
        elif role == 'assistant':
            historial.append({'role': 'model', 'parts': [content]})
    return historial


def _extraer_texto(response) -> str:
    texto = ''
    try:
        if response.text:
            texto = response.text.strip()
    except ValueError:
        texto = ''
    if not texto and getattr(response, 'candidates', None):
        parts = response.candidates[0].content.parts
        texto = ''.join(getattr(p, 'text', '') for p in parts if getattr(p, 'text', '')).strip()
    return texto.replace('**', '').strip()


def _extraer_function_calls(response) -> list:
    if not getattr(response, 'candidates', None):
        return []
    parts = getattr(response.candidates[0].content, 'parts', None) or []
    return [
        p.function_call
        for p in parts
        if getattr(p, 'function_call', None) and getattr(p.function_call, 'name', '')
    ]


def generar_respuesta_ia(
    message: str,
    conversation_history: list | None = None,
    context: dict | None = None,
    perfil: PerfilMascota | None = None,
) -> dict | None:
    """
    Ejecuta Gemini con Function Calling (max 3 rondas de herramientas).
    Retorna None si no hay API key o falla para activar el fallback local.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or ''
    if not api_key.strip():
        return None

    context = context or {}
    history = conversation_history or []

    if perfil is None:
        textos = [message] + [m.get('content', '') for m in history if m.get('role') == 'user']
        perfil = _extraer_perfil(textos)

    try:
        import google.generativeai as genai
        from google.generativeai import protos

        genai.configure(api_key=api_key)
        model_name = (getattr(settings, 'GEMINI_MODEL', '') or 'gemini-2.5-flash').strip()
        if model_name in _MODELOS_RETIRADOS:
            model_name = 'gemini-2.5-flash'

        tools, dispatcher, productos_recuperados, tools_usadas = construir_herramientas_bot(
            usuario_id=context.get('user_id'),
            memoria=context.get('memoria'),
        )

        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=_construir_system_instruction(context, perfil),
            tools=tools,
        )

        generation_config = {
            'temperature': 0.7,
            'max_output_tokens': 1000,
            'top_p': 0.9,
        }

        chat = model.start_chat(history=_historial_gemini(history))
        response = chat.send_message(message, generation_config=generation_config)

        for _ in range(_MAX_TOOL_ROUNDS):
            calls = _extraer_function_calls(response)
            if not calls:
                break
            tool_parts = []
            for call in calls:
                fn = dispatcher.get(call.name)
                if not fn:
                    result_payload = {'error': f'Herramienta desconocida: {call.name}'}
                else:
                    try:
                        args = dict(call.args) if call.args else {}
                        result_payload = fn(**args)
                    except Exception as tool_exc:
                        logger.warning('Error en tool %s: %s', call.name, tool_exc)
                        result_payload = {'error': 'No se pudo completar la consulta'}
                tool_parts.append(
                    protos.Part(
                        function_response=protos.FunctionResponse(
                            name=call.name,
                            response=result_payload,
                        )
                    )
                )
            response = chat.send_message(tool_parts, generation_config=generation_config)

        texto = _extraer_texto(response)
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
            'tools_used': list(dict.fromkeys(tools_usadas)),
            'perfil': {
                'animal': perfil.animal,
                'nombre': perfil.nombre,
                'edad': perfil.edad,
            },
        }

    except Exception as exc:
        logger.warning('Gemini error: %s', exc)
        return None
