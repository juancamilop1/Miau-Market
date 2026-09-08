"""Cache y acceso a configuracion/conocimiento de MiauBot desde BD."""

import random
import time

from ..models import MiauBotConfig, MiauBotConocimiento, MiauBotFrase

_CACHE_TTL = 120
_cache = {'ts': 0, 'config': None, 'conocimiento': None, 'frases': None}


def _refresh_if_needed():
    now = time.time()
    if now - _cache['ts'] < _CACHE_TTL and _cache['config'] is not None:
        return
    _cache['config'] = (
        MiauBotConfig.objects.filter(activo=True).order_by('-updated_at').first()
    )
    _cache['conocimiento'] = list(
        MiauBotConocimiento.objects.filter(activo=True).order_by('-prioridad')
    )
    _cache['frases'] = list(MiauBotFrase.objects.filter(activo=True))
    _cache['ts'] = now


def obtener_config():
    _refresh_if_needed()
    return _cache['config']


def buscar_conocimiento(texto: str, animal: str = 'gato') -> MiauBotConocimiento | None:
    _refresh_if_needed()
    texto_l = texto.lower()
    mejores = []
    for item in _cache['conocimiento'] or []:
        if item.animal not in (animal, 'general'):
            continue
        keys = [k.strip().lower() for k in item.palabras_clave.split(',') if k.strip()]
        score = sum(1 for k in keys if k in texto_l)
        if score > 0:
            mejores.append((score + item.prioridad, item))
    if not mejores:
        return None
    mejores.sort(key=lambda x: -x[0])
    return mejores[0][1]


def frase_aleatoria(tipo: str, animal: str = 'general') -> str:
    _refresh_if_needed()
    candidatas = [
        f for f in (_cache['frases'] or [])
        if f.tipo == tipo and f.animal in (animal, 'general')
    ]
    if not candidatas:
        candidatas = [f for f in (_cache['frases'] or []) if f.tipo == tipo]
    if not candidatas:
        return ''
    return random.choice(candidatas).texto


def invalidar_cache():
    _cache['ts'] = 0
