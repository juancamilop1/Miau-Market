"""
Herramientas (tools) y cache TTL de MiauBot.
Desacopla el LLM de la base de datos: Gemini invoca estas funciones solo cuando
necesita consultar catalogo, categorias, politicas internas o mascotas del usuario.
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
    'unos', 'unas', 'algo', 'quiero', 'busco', 'necesito', 'tienen', 'tiene',
    'venden', 'hay', 'dame', 'favor', 'hola', 'buenas', 'puedes', 'puede',
    'recomienda', 'recomiendame', 'recomendacion', 'mostrar', 'muestrame',
    'producto', 'productos', 'mascota', 'mascotas', 'marca', 'sobre', 'esta',
    'este', 'estos', 'estas', 'tengo', 'vende', 'ver', 'comprar',
}

# Terminos amplios de categoria/especie (no identifican una marca o producto puntual)
_GENERICAS_CATEGORIA = {
    'comida', 'alimento', 'alimentos', 'croqueta', 'croquetas', 'concentrado',
    'concentrados', 'snack', 'snacks', 'humedo', 'humeda',
    'juguete', 'juguetes', 'jugar',
    'higiene', 'aseo', 'limpieza',
    'accesorio', 'accesorios',
    'farmacia', 'medicina', 'salud',
    'servicio', 'servicios',
    'gato', 'gatos', 'gatito', 'gatitos', 'felino', 'felinos', 'michi',
    'perro', 'perros', 'perrito', 'perritos', 'canino', 'caninos',
    'cachorro', 'cachorros', 'adulto', 'adultos',
    'barato', 'baratos', 'economico', 'economicos', 'mejor', 'mejores',
    'popular', 'populares', 'recomendado', 'recomendados',
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


def _token_en_texto(token: str, texto_norm: str) -> bool:
    """Coincidencia por inicio de palabra (evita falsos positivos como 'cat' en 'categoria')."""
    if not token:
        return False
    stem = token[:-1] if len(token) > 4 and token.endswith('s') else token
    return bool(re.search(rf'\b{re.escape(stem)}', texto_norm))


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
    if _token_en_texto(otro, blob) and not _token_en_texto(animal, blob):
        return False
    return True


def buscar_productos_catalogo(
    consulta: str = '',
    animal: str = '',
    categoria: str = '',
    precio_max: int = 0,
    limite: int = 4,
) -> tuple[list[dict], dict]:
    """
    Busqueda precisa sobre el catalogo cacheado.
    - Frase exacta en titulo (ej. 'cat chow') -> devuelve solo las coincidencias exactas.
    - Terminos especificos (ej. 'alce', 'whiskas', 'rascador') -> exige coincidencia real;
      si no existe ninguno, devuelve [] en lugar de rellenar con productos ajenos.
    - Consultas genericas (ej. 'comida para gato', 'juguetes') -> busca por categoria/sinonimos.
    """
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
        pool = [
            p for p in pool
            if cat_norm in normalizar_texto(p['categoria'])
            or cat_norm in normalizar_texto(p['categoria_codigo'])
        ]
        if not pool:
            return [], ratings

    if max_p > 0:
        pool = [p for p in pool if p['precio'] <= max_p]
        if not pool:
            return [], ratings

    q_norm = normalizar_texto(consulta)
    tokens = [
        w for w in re.findall(r'[a-z0-9]+', q_norm)
        if len(w) > 2 and w not in _STOPWORDS_BUSQUEDA
    ]
    especificos = [t for t in tokens if t not in _GENERICAS_CATEGORIA]
    genericos = [t for t in tokens if t in _GENERICAS_CATEGORIA]

    # 1. Coincidencia exacta de frase especifica en el titulo (ej: "cat chow", "royal canin")
    if especificos:
        frase_esp = ' '.join(especificos)
        if len(frase_esp) >= 4:
            exactos_titulo = [
                p for p in pool
                if re.search(rf'\b{re.escape(frase_esp)}', normalizar_texto(p['nombre']))
            ]
            if exactos_titulo:
                exactos_titulo.sort(key=lambda p: (-ratings.get(p['id'], {}).get('promedio', 0), -p['stock']))
                return exactos_titulo[:lim], ratings

        # 2. Exigir coincidencia con terminos especificos (nunca rellenar si el producto no existe)
        coinciden_todos = []
        coinciden_algunos = []
        for p in pool:
            tit_l = normalizar_texto(p['nombre'])
            cat_l = normalizar_texto(p['categoria'])
            desc_l = normalizar_texto(p['descripcion'])
            hits_esp = 0
            score = 0
            for t in especificos:
                if _token_en_texto(t, tit_l):
                    hits_esp += 1
                    score += 5
                elif _token_en_texto(t, cat_l):
                    hits_esp += 1
                    score += 3
                elif _token_en_texto(t, desc_l):
                    hits_esp += 1
                    score += 2
            if hits_esp == 0:
                continue
            for g in genericos:
                if _token_en_texto(g, tit_l) or _token_en_texto(g, cat_l):
                    score += 1
            entrada = (hits_esp, score, ratings.get(p['id'], {}).get('promedio', 0), p['stock'], p)
            if hits_esp == len(especificos):
                coinciden_todos.append(entrada)
            else:
                coinciden_algunos.append(entrada)

        if coinciden_todos:
            coinciden_todos.sort(key=lambda x: (-x[0], -x[1], -x[2], -x[3]))
            return [x[4] for x in coinciden_todos[:lim]], ratings
        if coinciden_algunos and len(especificos) == 1:
            coinciden_algunos.sort(key=lambda x: (-x[0], -x[1], -x[2], -x[3]))
            return [x[4] for x in coinciden_algunos[:lim]], ratings
        # Si hay varios terminos especificos (ej. "cat chow") y solo coincide 1 parcialmente,
        # solo aceptar si coincide en el titulo con fuerza (evita "alce" o marcas inexistentes)
        if coinciden_algunos:
            fuertes = [x for x in coinciden_algunos if x[1] >= 5]
            if fuertes:
                fuertes.sort(key=lambda x: (-x[0], -x[1], -x[2], -x[3]))
                return [x[4] for x in fuertes[:lim]], ratings
        return [], ratings

    # 3. Consulta generica o navegacion por categoria / precio
    if 'barato' in q_norm or 'econom' in q_norm:
        pool.sort(key=lambda p: p['precio'])
        return pool[:lim], ratings

    expandidos = list(genericos)
    for keys in _SINONIMOS_BUSQUEDA.values():
        if any(_token_en_texto(k, q_norm) for k in keys):
            expandidos.extend(keys)
    terminos = list(dict.fromkeys(expandidos))

    if terminos:
        scored = []
        for p in pool:
            cat_l = normalizar_texto(p['categoria'])
            tit_l = normalizar_texto(p['nombre'])
            desc_l = normalizar_texto(p['descripcion'])
            score = 0
            for t in terminos:
                if _token_en_texto(t, tit_l):
                    score += 3
                elif _token_en_texto(t, cat_l):
                    score += 2
                elif _token_en_texto(t, desc_l):
                    score += 1
            if score > 0:
                scored.append((score, ratings.get(p['id'], {}).get('promedio', 0), p['stock'], p))
        if scored:
            scored.sort(key=lambda x: (-x[0], -x[1], -x[2]))
            return [x[3] for x in scored[:lim]], ratings
        return [], ratings

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


TOOL_DECLARATIONS = [
    {
        'name': 'buscar_productos',
        'description': (
            'Busca productos reales en MiauMarket (tienda de perros y gatos) por nombre, '
            'marca, animal, categoria o precio_max en COP. Si total es 0, informa con '
            'honestidad que no existe en catalogo y no inventes productos.'
        ),
        'parameters': {
            'type': 'OBJECT',
            'properties': {
                'consulta': {
                    'type': 'STRING',
                    'description': 'Nombre, marca o tipo de producto buscado (ej: cat chow, arena, collar).',
                },
                'animal': {
                    'type': 'STRING',
                    'description': 'Opcional: gato o perro.',
                },
                'categoria': {
                    'type': 'STRING',
                    'description': 'Opcional: nombre o codigo de categoria.',
                },
                'precio_max': {
                    'type': 'INTEGER',
                    'description': 'Opcional: presupuesto maximo en pesos colombianos (COP).',
                },
                'limite': {
                    'type': 'INTEGER',
                    'description': 'Cantidad maxima de resultados (1 a 6, por defecto 4).',
                },
            },
        },
    },
    {
        'name': 'obtener_detalle_producto',
        'description': 'Obtiene la ficha completa de un producto especifico de MiauMarket por su ID.',
        'parameters': {
            'type': 'OBJECT',
            'properties': {
                'producto_id': {
                    'type': 'INTEGER',
                    'description': 'ID numerico del producto en MiauMarket.',
                },
            },
            'required': ['producto_id'],
        },
    },
    {
        'name': 'listar_categorias',
        'description': 'Lista las categorias activas de MiauMarket con cantidad de productos y rango de precios.',
        'parameters': {
            'type': 'OBJECT',
            'properties': {},
        },
    },
    {
        'name': 'consultar_conocimiento',
        'description': (
            'Consulta solo politicas internas de la tienda (como comprar, envios, pagos) '
            'o respuestas aprobadas por admins. Para preguntas generales sobre mascotas '
            'o conversacion libre, responde directamente con tu conocimiento sin usar esta herramienta.'
        ),
        'parameters': {
            'type': 'OBJECT',
            'properties': {
                'tema': {
                    'type': 'STRING',
                    'description': 'Tema o pregunta sobre politicas de la tienda.',
                },
                'animal': {
                    'type': 'STRING',
                    'description': 'Opcional: gato, perro o general.',
                },
            },
            'required': ['tema'],
        },
    },
    {
        'name': 'obtener_mascotas_cliente',
        'description': 'Obtiene las mascotas registradas y preferencias recordadas del cliente autenticado.',
        'parameters': {
            'type': 'OBJECT',
            'properties': {},
        },
    },
]


def construir_herramientas_bot(usuario_id: int | None = None, memoria: dict | None = None):
    """
    Crea las declaraciones JSON y el dispatcher de tools invocables por Gemini
    para un turno de conversacion. Captura los productos reales consultados para
    construir tarjetas sin re-consultar BD.
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
        tools_usadas.append('buscar_productos')
        encontrados, ratings = buscar_productos_catalogo(
            consulta=consulta,
            animal=animal,
            categoria=categoria,
            precio_max=int(precio_max or 0),
            limite=int(limite or 4),
        )
        productos_recuperados.extend(encontrados)
        if not encontrados:
            return {
                'total': 0,
                'productos': [],
                'nota': f'No hay coincidencias en catalogo para "{consulta}". Dilo con honestidad; MiauMarket maneja productos para perros y gatos.',
            }
        return {
            'total': len(encontrados),
            'productos': [_compacto_para_llm(p, ratings) for p in encontrados],
        }

    def obtener_detalle_producto(producto_id: int) -> dict:
        tools_usadas.append('obtener_detalle_producto')
        pid = int(producto_id or 0)
        productos, ratings = obtener_catalogo_cacheado()
        for p in productos:
            if p['id'] == pid:
                productos_recuperados.append(p)
                return _compacto_para_llm(p, ratings, incluir_desc_completa=True)
        return {'error': 'Producto no disponible o sin stock'}

    def listar_categorias() -> dict:
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
        tools_usadas.append('consultar_conocimiento')
        animal_ok = animal if animal in ('gato', 'perro', 'general') else 'general'
        guia = buscar_conocimiento(tema, animal_ok)
        aprendidos = buscar_aprendizaje_aprobado(tema, animal_ok, limite=2)
        return {
            'guia': guia.respuesta if guia else None,
            'referencias': [{'pregunta': a.pregunta, 'respuesta': a.respuesta} for a in aprendidos],
        }

    def obtener_mascotas_cliente() -> dict:
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

    dispatcher = {
        'buscar_productos': buscar_productos,
        'obtener_detalle_producto': obtener_detalle_producto,
        'listar_categorias': listar_categorias,
        'consultar_conocimiento': consultar_conocimiento,
        'obtener_mascotas_cliente': obtener_mascotas_cliente,
    }
    return TOOL_DECLARATIONS, dispatcher, productos_recuperados, tools_usadas
