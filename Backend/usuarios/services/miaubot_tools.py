"""
Herramientas (tools) y cache TTL de MiauBot.
Desacopla el LLM de la base de datos: Gemini invoca estas funciones solo cuando
necesita consultar catalogo, categorias, conocimiento o mascotas del usuario.
"""

from __future__ import annotations

from datetime import date
import re
import time
import unicodedata

from django.db.models import Q

from ..models import MascotaUsuario, Producto
from .miaubot_aprendizaje import buscar_aprendizaje_aprobado
from .miaubot_knowledge import buscar_conocimiento
from .ratings_service import obtener_ratings_dict

_CATALOGO_TTL = 60
_catalogo_cache: dict = {'ts': 0.0, 'productos': [], 'ratings': {}}

_STOPWORDS_BUSQUEDA = {
    'para', 'como', 'que', 'con', 'por', 'los', 'las', 'del', 'una', 'uno',
    'unos', 'unas', 'algo', 'quiero', 'busco', 'necesito', 'tienen', 'dame',
    'recomienda', 'recomiendame', 'producto', 'productos', 'mascota', 'mascotas',
}

_SINONIMOS_BUSQUEDA = {
    'comida': ('comida', 'alimento', 'croqueta', 'concentrado', 'snack', 'humedo'),
    'juguete': ('juguete', 'jugar', 'pelota', 'raton', 'rascador'),
    'higiene': ('higiene', 'arena', 'arenera', 'shampoo', 'champu', 'bano'),
    'accesorio': ('accesorio', 'collar', 'cama', 'bebedero', 'transportador', 'guacal'),
    'farmacia': ('farmacia', 'antipulgas', 'pipeta', 'vitamina', 'vitaminas', 'pulga'),
    'servicio': ('servicio', 'peluqueria', 'veterinario', 'chequeo', 'bano'),
}


def normalizar_texto(texto: str) -> str:
    sin_tildes = unicodedata.normalize('NFKD', (texto or '').lower())
    return ''.join(c for c in sin_tildes if not unicodedata.combining(c))


def resolver_imagen(raw_img: str | None) -> str | None:
    if not raw_img:
        return None
    raw = str(raw_img).strip()
    if not raw:
        return None
    if raw.startswith(('/productos/', '/media/', 'http://', 'https://')):
        return raw
    return f'/media/{raw.lstrip("/")}'


def invalidar_cache_catalogo() -> None:
    _catalogo_cache['ts'] = 0.0


def obtener_catalogo_cacheado() -> tuple[list[dict], dict]:
    """Devuelve (productos_activos, ratings) usando cache en memoria con TTL."""
    now = time.time()
    if now - _catalogo_cache['ts'] < _CATALOGO_TTL and _catalogo_cache['ts'] > 0:
        return _catalogo_cache['productos'], _catalogo_cache['ratings']

    ratings = obtener_ratings_dict()
    hoy = date.today()
    productos = []
    qs = (
        Producto.objects.filter(Stock__gt=0)
        .filter(Q(Fecha_Caducidad__isnull=True) | Q(Fecha_Caducidad__gte=hoy))
        .values(
            'id',
            'Titulo',
            'Descripcion',
            'categoria__nombre',
            'categoria__codigo',
            'categoria__animal',
            'Precio',
            'Stock',
            'Imagen',
        )
    )
    for p in qs:
        productos.append({
            'id': p['id'],
            'nombre': p['Titulo'],
            'descripcion': p['Descripcion'] or '',
            'categoria': p['categoria__nombre'] or 'General',
            'categoria_codigo': (p['categoria__codigo'] or '').upper(),
            'categoria_animal': (p['categoria__animal'] or 'general').lower(),
            'precio': int(p['Precio']),
            'stock': int(p['Stock']),
            'imagen': resolver_imagen(p.get('Imagen')),
        })

    _catalogo_cache['productos'] = productos
    _catalogo_cache['ratings'] = ratings
    _catalogo_cache['ts'] = now
    return productos, ratings


def serializar_productos_card(productos: list[dict], ratings: dict) -> list[dict]:
    cards = []
    vistos = set()
    for p in productos:
        if p['id'] in vistos:
            continue
        vistos.add(p['id'])
        r = ratings.get(p['id'], {})
        prom = float(r.get('promedio', 0) or 0)
        cards.append({
            'id': p['id'],
            'titulo': p['nombre'],
            'categoria': p['categoria'],
            'precio': int(p['precio']),
            'stock': int(p['stock']),
            'imagen': p.get('imagen'),
            'rating': round(prom, 1) if prom > 0 else None,
            'total_reviews': int(r.get('total', 0) or 0),
        })
    return cards


def productos_mencionados_en_texto(
    texto: str,
    candidatos: list[dict] | None = None,
    limite: int = 4,
) -> list[dict]:
    """Encuentra productos mencionados en texto, ordenados por aparicion."""
    if not texto:
        return []
    base = candidatos if candidatos is not None else obtener_catalogo_cacheado()[0]
    norm_texto = normalizar_texto(texto)
    encontrados: list[tuple[int, dict]] = []
    vistos = set()
    for p in base:
        if p['id'] in vistos:
            continue
        norm_nombre = normalizar_texto(p['nombre']).strip()
        if len(norm_nombre) < 3:
            continue
        pos = norm_texto.find(norm_nombre)
        if pos != -1:
            vistos.add(p['id'])
            encontrados.append((pos, p))
    encontrados.sort(key=lambda item: item[0])
    return [p for _, p in encontrados[:limite]]


def _coincide_animal(producto: dict, animal: str) -> bool:
    if animal not in ('gato', 'perro'):
        return True
    otro = 'perro' if animal == 'gato' else 'gato'
    cat_animal = producto.get('categoria_animal', 'general')
    if cat_animal == otro:
        return False
    blob = normalizar_texto(f"{producto['nombre']} {producto['descripcion']} {producto['categoria']}")
    if otro in blob and animal not in blob:
        return False
    return True


def buscar_productos_catalogo(
    consulta: str = '',
    animal: str = '',
    categoria: str = '',
    precio_max: int = 0,
    limite: int = 4,
) -> tuple[list[dict], dict]:
    """Busqueda eficiente en memoria sobre el catalogo cacheado."""
    productos, ratings = obtener_catalogo_cacheado()
    if not productos:
        return [], ratings

    animal_norm = normalizar_texto(animal).strip()
    if animal_norm not in ('gato', 'perro'):
        animal_norm = ''

    cat_norm = normalizar_texto(categoria).strip()
    max_p = max(0, int(precio_max or 0))
    lim = max(1, min(int(limite or 4), 8))

    pool = [p for p in productos if _coincide_animal(p, animal_norm)] if animal_norm else list(productos)

    if cat_norm:
        por_cat = [
            p for p in pool
            if cat_norm in normalizar_texto(p['categoria'])
            or cat_norm in normalizar_texto(p['categoria_codigo'])
        ]
        if por_cat:
            pool = por_cat

    if max_p > 0:
        en_presupuesto = [p for p in pool if p['precio'] <= max_p]
        if en_presupuesto:
            pool = en_presupuesto

    q_norm = normalizar_texto(consulta)
    tokens = [
        w for w in re.findall(r'[a-z0-9]+', q_norm)
        if len(w) > 2 and w not in _STOPWORDS_BUSQUEDA
    ]
    expandidos = list(tokens)
    for keys in _SINONIMOS_BUSQUEDA.values():
        if any(k in q_norm for k in keys):
            expandidos.extend(keys)
    terminos = list(dict.fromkeys(expandidos))

    if 'barato' in q_norm or 'econom' in q_norm:
        pool.sort(key=lambda p: p['precio'])
        return pool[:lim], ratings

    if terminos:
        scored = []
        for p in pool:
            cat_l = normalizar_texto(p['categoria'])
            tit_l = normalizar_texto(p['nombre'])
            desc_l = normalizar_texto(p['descripcion'])
            score = 0
            for t in terminos:
                if t in tit_l:
                    score += 3
                elif t in cat_l:
                    score += 2
                elif t in desc_l:
                    score += 1
            if score > 0:
                scored.append((score, ratings.get(p['id'], {}).get('promedio', 0), p))
        if scored:
            scored.sort(key=lambda x: (-x[0], -x[1], -x[2]['stock']))
            return [p for _, _, p in scored[:lim]], ratings

    pool.sort(key=lambda p: (-ratings.get(p['id'], {}).get('promedio', 0), -p['stock']))
    return pool[:lim], ratings


def _compacto_para_llm(p: dict, ratings: dict, incluir_desc_completa: bool = False) -> dict:
    r = ratings.get(p['id'], {})
    desc = p['descripcion'] if incluir_desc_completa else p['descripcion'][:100]
    item = {
        'id': p['id'],
        'titulo': p['nombre'],
        'categoria': p['categoria'],
        'precio_cop': p['precio'],
        'stock': p['stock'],
        'descripcion': desc,
    }
    if r.get('promedio', 0) > 0:
        item['rating'] = round(float(r['promedio']), 1)
        item['resenas'] = int(r.get('total', 0))
    return item


def construir_herramientas_bot(usuario_id: int | None = None, memoria: dict | None = None):
    """
    Crea el conjunto de tools invocables por Gemini para un turno de conversacion.
    Captura los productos reales consultados para construir tarjetas sin re-consultar BD.
    """
    productos_recuperados: list[dict] = []
    tools_usadas: list[str] = []

    def buscar_productos(
        consulta: str = '',
        animal: str = '',
        categoria: str = '',
        precio_max: int = 0,
        limite: int = 4,
    ) -> dict:
        """Busca productos disponibles en MiauMarket por texto, animal (gato/perro), categoria o precio maximo en COP."""
        tools_usadas.append('buscar_productos')
        encontrados, ratings = buscar_productos_catalogo(
            consulta=consulta,
            animal=animal,
            categoria=categoria,
            precio_max=int(precio_max or 0),
            limite=int(limite or 4),
        )
        productos_recuperados.extend(encontrados)
        return {
            'total': len(encontrados),
            'productos': [_compacto_para_llm(p, ratings) for p in encontrados],
        }

    def obtener_detalle_producto(producto_id: int) -> dict:
        """Obtiene la ficha completa de un producto especifico por su ID."""
        tools_usadas.append('obtener_detalle_producto')
        pid = int(producto_id or 0)
        productos, ratings = obtener_catalogo_cacheado()
        for p in productos:
            if p['id'] == pid:
                productos_recuperados.append(p)
                return _compacto_para_llm(p, ratings, incluir_desc_completa=True)
        return {'error': 'Producto no disponible o sin stock'}

    def listar_categorias() -> dict:
        """Lista las categorias activas de la tienda con cantidad de productos y rango de precios."""
        tools_usadas.append('listar_categorias')
        productos, _ = obtener_catalogo_cacheado()
        resumen: dict[str, dict] = {}
        for p in productos:
            cat = p['categoria']
            entry = resumen.setdefault(cat, {'categoria': cat, 'cantidad': 0, 'precio_min': p['precio'], 'precio_max': p['precio']})
            entry['cantidad'] += 1
            entry['precio_min'] = min(entry['precio_min'], p['precio'])
            entry['precio_max'] = max(entry['precio_max'], p['precio'])
        return {'categorias': list(resumen.values())}

    def consultar_conocimiento(tema: str, animal: str = 'general') -> dict:
        """Consulta guias de cuidado de mascotas, proceso de compra y respuestas aprobadas de MiauMarket."""
        tools_usadas.append('consultar_conocimiento')
        animal_ok = animal if animal in ('gato', 'perro', 'general') else 'general'
        guia = buscar_conocimiento(tema, animal_ok)
        aprendidos = buscar_aprendizaje_aprobado(tema, animal_ok, limite=2)
        return {
            'guia': guia.respuesta if guia else None,
            'referencias': [{'pregunta': a.pregunta, 'respuesta': a.respuesta} for a in aprendidos],
        }

    def obtener_mascotas_cliente() -> dict:
        """Obtiene las mascotas registradas y preferencias recordadas del cliente autenticado."""
        tools_usadas.append('obtener_mascotas_cliente')
        mascotas_perfil = []
        if usuario_id:
            for m in MascotaUsuario.objects.filter(usuario_id=usuario_id, activo=True)[:6]:
                mascotas_perfil.append({
                    'nombre': m.nombre,
                    'especie': m.especie,
                    'edad_anios': m.edad_anios,
                    'notas': (m.notas or '')[:120],
                })
        return {
            'mascotas_registradas': mascotas_perfil,
            'memoria': (memoria or {}).get('mascotas', [])[:4],
        }

    tools = [
        buscar_productos,
        obtener_detalle_producto,
        listar_categorias,
        consultar_conocimiento,
        obtener_mascotas_cliente,
    ]
    dispatcher = {fn.__name__: fn for fn in tools}
    return tools, dispatcher, productos_recuperados, tools_usadas
