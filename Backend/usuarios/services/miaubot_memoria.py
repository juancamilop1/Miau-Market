"""Memoria persistente de MiauBot por usuario: mascotas y seguimiento."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from ..models import MiauBotMemoriaUsuario


TEMAS = {
    'comida': ['comida', 'alimento', 'alimentacion', 'alimentación', 'croqueta', 'snack', 'comer', 'pienso'],
    'juguete': ['juguete', 'jugar', 'pelota', 'raton', 'ratón', 'mordedor'],
    'higiene': ['higiene', 'shampoo', 'champú', 'bano', 'baño', 'cepillo', 'arena', 'arenera'],
    'salud': ['enferm', 'veterin', 'dolor', 'medic', 'salud', 'cuidado', 'vacuna', 'operacion', 'operación'],
    'accesorio': ['collar', 'correa', 'cama', 'rascador', 'transportador'],
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def cargar_memoria(usuario_id: int | None) -> dict | None:
    if not usuario_id:
        return None
    obj, _ = MiauBotMemoriaUsuario.objects.get_or_create(usuario_id=usuario_id)
    return {
        'usuario_id': usuario_id,
        'mascotas': obj.mascotas or [],
        'seguimiento': obj.seguimiento or {},
        'mascota_activa_idx': obj.mascota_activa_idx or 0,
    }


def _guardar_memoria(memoria: dict) -> None:
    if not memoria or not memoria.get('usuario_id'):
        return
    MiauBotMemoriaUsuario.objects.update_or_create(
        usuario_id=memoria['usuario_id'],
        defaults={
            'mascotas': memoria.get('mascotas', []),
            'seguimiento': memoria.get('seguimiento', {}),
            'mascota_activa_idx': memoria.get('mascota_activa_idx', 0),
        },
    )


def detectar_temas(texto: str) -> set[str]:
    texto_l = texto.lower()
    encontrados = set()
    for tema, palabras in TEMAS.items():
        if any(p in texto_l for p in palabras):
            encontrados.add(tema)
    return encontrados


def detectar_salud(texto: str) -> str | None:
    texto_l = texto.lower()
    if any(w in texto_l for w in ['enferm', 'malito', 'vomit', 'fiebre', 'dolor', 'operacion', 'operación']):
        return 'enfermo'
    if any(w in texto_l for w in ['mejor', 'recuper', 'sano', 'bien de salud', 'ya esta bien', 'ya está bien']):
        return 'sano'
    return None


def _extraer_raza(blob: str) -> str | None:
    razas = [
        'pitbull', 'pit bull', 'labrador', 'golden', 'bulldog', 'pastor', 'husky',
        'chihuahua', 'poodle', 'caniche', 'beagle', 'rottweiler', 'doberman',
        'boxer', 'dachshund', 'salchicha', 'pug', 'persa', 'siames', 'maine coon',
    ]
    for r in razas:
        if r in blob:
            return r
    m = re.search(r'\bes\s+un[a]?\s+([a-záéíóúñ]{3,20})', blob)
    if m:
        return m.group(1)
    return None


def _mascota_desde_perfil(perfil) -> dict:
    return {
        'id': str(uuid.uuid4())[:8],
        'animal': perfil.animal,
        'nombre': perfil.nombre,
        'raza': getattr(perfil, 'raza', None),
        'edad': perfil.edad,
        'tamano': perfil.tamano,
        'salud': 'sano',
        'activa': True,
    }


def _mascotas_similares(m1: dict, m2: dict) -> bool:
    if m1.get('animal') != m2.get('animal'):
        return False
    if m1.get('nombre') and m2.get('nombre'):
        return m1['nombre'].lower() == m2['nombre'].lower()
    if m1.get('raza') and m2.get('raza'):
        return m1['raza'].lower() == m2['raza'].lower()
    return m1.get('animal') == m2.get('animal') and not m1.get('raza') and not m2.get('raza')


def actualizar_memoria(memoria: dict | None, perfil, message: str, textos_historial: list[str]) -> dict | None:
    if not memoria:
        return None

    blob = ' '.join([message] + textos_historial).lower()
    temas = detectar_temas(blob)
    salud = detectar_salud(message)

    mascotas = list(memoria.get('mascotas') or [])
    nueva = _mascota_desde_perfil(perfil)
    tiene_datos = any([perfil.animal, perfil.edad, perfil.nombre, getattr(perfil, 'raza', None)])

    idx_activa = memoria.get('mascota_activa_idx', 0)
    mascota_actualizada = False

    if tiene_datos:
        match_idx = None
        for i, m in enumerate(mascotas):
            if _mascotas_similares(m, nueva):
                match_idx = i
                break

        if match_idx is not None:
            m = mascotas[match_idx]
            for campo in ('nombre', 'raza', 'edad', 'tamano', 'animal'):
                val = nueva.get(campo)
                if val:
                    m[campo] = val
            if salud:
                m['salud'] = salud
            for i, m in enumerate(mascotas):
                m['activa'] = i == match_idx
            idx_activa = match_idx
            mascota_actualizada = True
        else:
            for m in mascotas:
                m['activa'] = False
            nueva['activa'] = True
            if salud:
                nueva['salud'] = salud
            mascotas.append(nueva)
            idx_activa = len(mascotas) - 1
            mascota_actualizada = True

    seguimiento = dict(memoria.get('seguimiento') or {})
    mascota_id = mascotas[idx_activa]['id'] if mascotas and 0 <= idx_activa < len(mascotas) else None

    for tema in temas:
        seguimiento[tema] = {
            'fecha': _now_iso(),
            'mascota_id': mascota_id,
            'ultimo_mensaje': message[:200],
        }

    if salud == 'enfermo':
        seguimiento['salud'] = {
            'fecha': _now_iso(),
            'mascota_id': mascota_id,
            'estado': 'enfermo',
            'ultimo_mensaje': message[:200],
        }
        if mascotas and idx_activa < len(mascotas):
            mascotas[idx_activa]['salud'] = 'enfermo'
    elif salud == 'sano' and 'salud' in seguimiento:
        seguimiento['salud']['estado'] = 'recuperado'
        seguimiento['salud']['fecha_recuperacion'] = _now_iso()
        if mascotas and idx_activa < len(mascotas):
            mascotas[idx_activa]['salud'] = 'sano'

    memoria['mascotas'] = mascotas
    memoria['seguimiento'] = seguimiento
    memoria['mascota_activa_idx'] = idx_activa
    _guardar_memoria(memoria)
    return memoria


def aplicar_memoria_a_perfil(perfil, memoria: dict | None):
    if not memoria or not memoria.get('mascotas'):
        return perfil

    idx = memoria.get('mascota_activa_idx', 0)
    mascotas = memoria['mascotas']
    if idx >= len(mascotas):
        idx = 0
    m = mascotas[idx]

    if not perfil.edad and m.get('edad'):
        perfil.edad = m['edad']
    if not perfil.nombre and m.get('nombre'):
        perfil.nombre = m['nombre']
    if not perfil.tamano and m.get('tamano'):
        perfil.tamano = m['tamano']
    if m.get('animal'):
        perfil.animal = m['animal']
    if not getattr(perfil, 'raza', None) and m.get('raza'):
        perfil.raza = m['raza']

    seg = memoria.get('seguimiento') or {}
    for tema in seg:
        perfil.temas.add(tema)

    return perfil


def temas_conocidos(memoria: dict | None) -> set[str]:
    if not memoria:
        return set()
    return set((memoria.get('seguimiento') or {}).keys())


def mascota_activa(memoria: dict | None) -> dict | None:
    if not memoria or not memoria.get('mascotas'):
        return None
    idx = memoria.get('mascota_activa_idx', 0)
    mascotas = memoria['mascotas']
    if 0 <= idx < len(mascotas):
        return mascotas[idx]
    return mascotas[0] if mascotas else None


def texto_memoria_prompt(memoria: dict | None) -> str:
    if not memoria or not memoria.get('mascotas'):
        return ''

    lineas = ['MEMORIA DEL CLIENTE (usa esto, NO vuelvas a preguntar lo que ya sabes):']
    for i, m in enumerate(memoria['mascotas']):
        activa = ' [ACTIVA]' if m.get('activa') else ''
        desc = f"- Mascota {i + 1}{activa}: {m.get('animal', '?')}"
        if m.get('raza'):
            desc += f", raza {m['raza']}"
        if m.get('edad'):
            desc += f", {m['edad']}"
        if m.get('nombre'):
            desc += f", se llama {m['nombre']}"
        if m.get('tamano'):
            desc += f", tamano {m['tamano']}"
        if m.get('salud') and m['salud'] != 'sano':
            desc += f", salud: {m['salud']}"
        lineas.append(desc)

    seg = memoria.get('seguimiento') or {}
    if seg:
        lineas.append('Temas que el cliente ya menciono (NO repreguntar categorias):')
        for tema, info in seg.items():
            lineas.append(f"  - {tema}: mencionado el {info.get('fecha', '')[:10]}")

    return '\n'.join(lineas)


def generar_seguimiento_saludo(memoria: dict | None, user_name: str | None) -> str | None:
    if not memoria:
        return None

    m = mascota_activa(memoria)
    if not m:
        return None

    ref = m.get('nombre') or (f"tu {m.get('raza')}" if m.get('raza') else f"tu {m.get('animal', 'mascota')}")
    saludo = f"Hola {user_name}!" if user_name else 'Hola de nuevo!'
    seg = memoria.get('seguimiento') or {}
    partes = []

    if m.get('salud') == 'enfermo' or seg.get('salud', {}).get('estado') == 'enfermo':
        partes.append(f'¿Como sigue {ref}? ¿Ya se siente mejor?')
    if 'comida' in seg:
        partas_comida = f'¿Como va con la comida de {ref}?'
        partes.append(partas_comida)
    if 'juguete' in seg:
        partes.append(f'¿{ref.capitalize()} ya tiene juguetes nuevos?')
    if 'higiene' in seg:
        partes.append(f'¿Necesitas algo mas de higiene para {ref}?')

    if not partes:
        if m.get('raza') or m.get('edad'):
            desc = ref
            if m.get('edad'):
                desc += f" de {m['edad']}"
            partes.append(f'¿En que mas puedo ayudarte con {desc}?')
        else:
            return None

    return f"{saludo} {' '.join(partes)}"
