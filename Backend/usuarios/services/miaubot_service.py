"""
MiauBot — motor hibrido: IA en la nube (Gemini) + fallback local.
Prompt y conocimiento en base de datos.
"""

import re
import random
from dataclasses import dataclass, field

from ..models import Producto
from .ratings_service import obtener_ratings_dict
from .miaubot_knowledge import (
    buscar_conocimiento,
    frase_aleatoria,
    obtener_config,
)


@dataclass
class PerfilMascota:
    animal: str = 'gato'
    nombre: str | None = None
    raza: str | None = None
    edad: str | None = None
    tamano: str | None = None
    temas: set = field(default_factory=set)


# Cache de productos por request (evita multiples queries)
_productos_cache: tuple[list, dict] | None = None


def _cargar_productos():
    global _productos_cache
    if _productos_cache is not None:
        return _productos_cache

    ratings = obtener_ratings_dict()
    productos = []
    for p in Producto.objects.filter(Stock__gt=0).values(
        'id', 'Titulo', 'Descripcion', 'Categoria', 'Precio', 'Stock'
    ):
        productos.append({
            'id': p['id'],
            'nombre': p['Titulo'],
            'descripcion': p['Descripcion'] or '',
            'categoria': p['Categoria'] or 'General',
            'precio': p['Precio'],
            'stock': p['Stock'],
        })
    _productos_cache = (productos, ratings)
    return _productos_cache


def _reset_productos_cache():
    global _productos_cache
    _productos_cache = None


def _format_price(precio) -> str:
    try:
        return f'${int(precio):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return str(precio)


def _extraer_perfil(textos: list[str]) -> PerfilMascota:
    perfil = PerfilMascota()
    blob = ' '.join(textos).lower()

    if any(w in blob for w in ['perro', 'perra', 'cachorro', 'canino', 'can ', 'perruno']):
        perfil.animal = 'perro'
    elif any(w in blob for w in ['gato', 'gata', 'gatito', 'felino', 'michi']):
        perfil.animal = 'gato'

    razas_perro = [
        'pitbull', 'pit bull', 'labrador', 'golden', 'bulldog', 'pastor', 'husky',
        'chihuahua', 'poodle', 'caniche', 'beagle', 'rottweiler', 'doberman',
        'boxer', 'dachshund', 'salchicha', 'pug', 'shih tzu', 'cocker',
    ]
    razas_gato = ['persa', 'siames', 'siamese', 'maine coon', 'bengala', 'ragdoll', 'sphynx']

    for raza in razas_perro:
        if raza in blob:
            perfil.animal = 'perro'
            perfil.raza = raza
            if raza in ('chihuahua', 'pug', 'salchicha', 'dachshund', 'caniche', 'poodle', 'toy'):
                perfil.tamano = 'pequeño'
            elif raza in ('pitbull', 'pit bull', 'labrador', 'golden', 'rottweiler', 'doberman', 'husky', 'pastor'):
                perfil.tamano = 'grande'
            break

    for raza in razas_gato:
        if raza in blob:
            perfil.animal = 'gato'
            perfil.raza = raza
            break

    m_edad = re.search(r'(\d+)\s*(años|ano|anos|meses|mes)', blob)
    if m_edad:
        perfil.edad = m_edad.group(0)

    m_es_un = re.search(r'\bes\s+un[a]?\s+([a-záéíóúñ]{3,20})', blob)
    if m_es_un and not perfil.tamano:
        raza = m_es_un.group(1)
        perfil.raza = raza
        if raza in ('pitbull', 'labrador', 'golden', 'rottweiler', 'husky'):
            perfil.tamano = 'grande'
            perfil.animal = 'perro'

    m_nombre = re.search(
        r'(?:se llama|llama|nombre es|mi (?:gato|gata|perro|perra|mascota))\s+([A-ZÁÉÍÓÚÑa-záéíóúñ]{2,20})',
        ' '.join(textos),
        re.IGNORECASE,
    )
    if m_nombre:
        perfil.nombre = m_nombre.group(1).capitalize()

    for tam in ['pequeño', 'pequeno', 'mediano', 'grande', 'mini', 'toy']:
        if tam in blob:
            perfil.tamano = tam
            break

    from .miaubot_memoria import detectar_temas
    perfil.temas.update(detectar_temas(blob))

    return perfil


def _ref_mascota(perfil: PerfilMascota) -> str:
    if perfil.nombre:
        return perfil.nombre
    if perfil.raza:
        return f'tu {perfil.raza}'
    return 'tu gatito' if perfil.animal == 'gato' else 'tu perrito' if perfil.animal == 'perro' else 'tu mascota'


def _categorias_por_tema(perfil: PerfilMascota, temas: set[str]) -> list[str]:
    cats = []
    animal = perfil.animal
    for tema in temas:
        if tema == 'comida':
            cats.append('Comida de Gato' if animal == 'gato' else 'Comida de Perro')
        elif tema == 'juguete':
            cats.append('Juguetes')
        elif tema in ('higiene', 'accesorio'):
            cats.extend(['Servicios', 'Juguetes'])
    return cats


def _buscar_por_categoria(perfil: PerfilMascota, categorias: list[str], limite: int = 3):
    productos, ratings = _cargar_productos()
    if not productos or not categorias:
        return [], ratings

    filtrados = []
    for p in productos:
        cat = p['categoria'].lower()
        if any(c.lower() in cat or cat in c.lower() for c in categorias):
            blob = f"{p['nombre']} {p['descripcion']}".lower()
            if perfil.animal == 'gato' and 'perro' in blob and 'gato' not in blob:
                continue
            if perfil.animal == 'perro' and 'gato' in blob and 'perro' not in blob:
                continue
            filtrados.append(p)

    if not filtrados:
        for p in productos:
            if any(c.lower() in p['categoria'].lower() for c in categorias):
                filtrados.append(p)

    filtrados.sort(key=lambda p: -ratings.get(p['id'], {}).get('promedio', 0))
    return filtrados[:limite], ratings


def _tono_animal(animal: str) -> str:
    if animal == 'perro':
        return 'perruno'
    if animal == 'gato':
        return 'felino'
    return 'mascota'


def _buscar_productos(texto: str, perfil: PerfilMascota, limite: int = 3, temas_extra: set | None = None):
    productos, ratings = _cargar_productos()
    if not productos:
        return [], ratings

    palabras = [
        w for w in re.findall(r'[a-zA-Z0-9áéíóúñ]+', texto.lower())
        if len(w) > 2 and w not in {'para', 'como', 'que', 'con', 'por', 'los', 'las', 'del', 'una', 'uno'}
    ]

    mapa_categoria = {
        'comida': ['comida', 'alimento', 'snack', 'croqueta'],
        'juguete': ['juguete', 'jugar', 'pelota', 'raton'],
        'arena': ['arena', 'arenera', 'sanitario'],
        'accesorio': ['collar', 'correa', 'cama', 'rascador'],
    }
    for cat, keys in mapa_categoria.items():
        if any(k in texto.lower() for k in keys):
            palabras.extend(keys)

    temas = set(perfil.temas)
    if temas_extra:
        temas.update(temas_extra)
    for cat, keys in mapa_categoria.items():
        if cat in temas:
            palabras.extend(keys)

    scored = []
    for p in productos:
        blob = f"{p['nombre']} {p['descripcion']} {p['categoria']}".lower()
        score = sum(2 if w in p['categoria'].lower() else 1 for w in palabras if w in blob)
        if perfil.animal == 'gato' and 'perro' in blob:
            score -= 3
        if perfil.animal == 'perro' and 'gato' in blob:
            score -= 3
        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: (-x[0], -ratings.get(x[1]['id'], {}).get('promedio', 0)))
    if scored:
        return [p for _, p in scored[:limite]], ratings

    if temas:
        cats = _categorias_por_tema(perfil, temas)
        por_cat, ratings = _buscar_por_categoria(perfil, cats, limite)
        if por_cat:
            return por_cat, ratings

    if perfil.animal in ('gato', 'perro') and not temas:
        cat_default = 'Comida de Gato' if perfil.animal == 'gato' else 'Comida de Perro'
        por_cat, ratings = _buscar_por_categoria(perfil, [cat_default], limite)
        if por_cat:
            return por_cat, ratings

    if 'barato' in texto.lower() or 'econom' in texto.lower():
        ordenados = sorted(productos, key=lambda p: p['precio'])
        return ordenados[:limite], ratings

    top = sorted(
        productos,
        key=lambda p: ratings.get(p['id'], {}).get('promedio', 0),
        reverse=True,
    )
    return top[:limite], ratings


def _describir_producto(p: dict, ratings: dict, perfil: PerfilMascota) -> str:
    ref = _ref_mascota(perfil)
    rating = ratings.get(p['id'], {})
    r_txt = ''
    if rating.get('promedio', 0) > 0:
        r_txt = f" — {rating['promedio']:.1f}/5 ({rating['total']} resenas)"

    beneficio = ''
    desc = (p['descripcion'] or '')[:80]
    if desc:
        beneficio = f"\n  {desc}{'...' if len(p['descripcion'] or '') > 80 else ''}"

    return (
        f"{p['nombre']} ({p['categoria']})\n"
        f"  {_format_price(p['precio'])} · {p['stock']} disponibles{r_txt}"
        f"{beneficio}\n"
        f"  Ideal para {ref}."
    )


def _detectar_intencion(msg: str) -> str:
    msg_l = msg.lower().strip()
    if msg_l in {'hola', 'hello', 'hi', 'hey', 'buenas', 'saludos', 'que tal', 'qué tal', 'buenos dias', 'buenas tardes'}:
        return 'saludo'
    if any(k in msg_l for k in ['adios', 'adiós', 'chao', 'hasta luego', 'nos vemos', 'bye']):
        return 'despedida'
    if any(k in msg_l for k in ['como compro', 'cómo compro', 'carrito', 'checkout', 'pagar', 'pedido']):
        return 'compra'
    if any(k in msg_l for k in [
        'recomiend', 'recomend', 'producto', 'busco', 'necesito', 'quiero', 'tienen', 'venden',
        'precio', 'catalogo', 'catálogo', 'me puedes dar', 'me puedes recomendar', 'que me das',
        'qué me das', 'que me recomiendas', 'qué me recomiendas', 'que le puedo dar',
        'qué le puedo dar', 'que comprar', 'qué comprar', 'algo para', 'me das',
    ]):
        return 'producto'
    if any(k in msg_l for k in ['consejo', 'tip', 'cuidar', 'cuidado', 'salud', 'aliment', 'duerme']):
        return 'cuidado'
    if any(k in msg_l for k in ['comida', 'juguete', 'arena', 'collar', 'correa', 'croqueta', 'snack']):
        return 'producto'
    if msg_l.isdigit() or msg_l in {'si', 'sí', 'ok', 'dale', 'va', 'listo'}:
        return 'seguimiento'
    return 'general'


def _perfil_completo(perfil: PerfilMascota) -> bool:
    return bool(perfil.edad or perfil.tamano or perfil.nombre)


def _parece_pedido_producto(msg: str) -> bool:
    msg_l = msg.lower()
    return any(k in msg_l for k in [
        'dar', 'comprar', 'recomiend', 'producto', 'algo', 'necesito', 'quiero', 'tienen',
    ])


def _personalizar(texto: str, contexto: dict, perfil: PerfilMascota) -> str:
    nombre = contexto.get('user_name') or ''
    texto = texto.replace('{nombre}', nombre).replace('{mascota}', _ref_mascota(perfil))
    texto = texto.replace('{animal}', perfil.animal)
    if nombre and '{nombre}' not in texto and random.random() < 0.35:
        texto = f"{nombre}, {texto[0].lower()}{texto[1:]}" if texto else texto
    return texto


def _respuesta_saludo(contexto: dict, perfil: PerfilMascota) -> str:
    config = obtener_config()
    if config:
        tpl = config.mensaje_bienvenida_retorno if contexto.get('user_name') else config.mensaje_bienvenida
        if tpl:
            return _personalizar(tpl, contexto, perfil)

    intro = frase_aleatoria('saludo', perfil.animal) or 'Hola!'
    return _personalizar(
        f"{intro} Soy MiauBot de MiauMarket. Cuéntame de tu {_tono_animal(perfil.animal)} "
        f"y te recomiendo productos reales de nuestra tienda.",
        contexto,
        perfil,
    )


def _respuesta_productos(msg: str, perfil: PerfilMascota, contexto: dict) -> str:
    temas_mem = contexto.get('temas_memoria') or set()
    productos, ratings = _buscar_productos(msg, perfil, temas_extra=temas_mem)
    ref = _ref_mascota(perfil)

    if not productos:
        temas = perfil.temas | temas_mem
        if 'comida' in temas or 'comida' in msg.lower():
            return _personalizar(
                f"Para {ref} busco comida de {perfil.animal}. "
                f"Revisa la seccion Comida de {'Perro' if perfil.animal == 'perro' else 'Gato'} en Tienda. "
                f"Si quieres, dime presupuesto o preferencias y te ayudo a elegir.",
                contexto, perfil,
            )
        if temas:
            tema_txt = ', '.join(sorted(temas))
            return _personalizar(
                f"Recuerdo que buscas {tema_txt} para {ref}. "
                f"Revisa la Tienda o dime mas detalles para recomendarte algo especifico.",
                contexto, perfil,
            )
        conocimiento = buscar_conocimiento(msg, perfil.animal)
        if conocimiento:
            return _personalizar(conocimiento.respuesta, contexto, perfil)
        return _personalizar(
            f"Cuéntame que necesitas para {ref} (comida, juguetes o higiene) "
            f"y te muestro lo que tenemos en tienda.",
            contexto, perfil,
        )

    intro = frase_aleatoria('intro_producto', perfil.animal) or f"Para {ref} te sugiero:"
    if perfil.edad:
        intro = f"Con {perfil.edad}, {intro[0].lower()}{intro[1:]}" if intro else intro

    lineas = [_describir_producto(p, ratings, perfil) for p in productos]
    cierre = frase_aleatoria('cierre_producto', perfil.animal) or 'Agregalos al carrito desde Tienda.'

    return _personalizar(
        f"{intro}\n\n" + '\n'.join(lineas) + f"\n{cierre}",
        contexto,
        perfil,
    )


def _respuesta_cuidado(msg: str, perfil: PerfilMascota, contexto: dict) -> str:
    conocimiento = buscar_conocimiento(msg, perfil.animal)
    ref = _ref_mascota(perfil)

    if conocimiento:
        cuerpo = conocimiento.respuesta
    else:
        cuerpo = (
            f"Cada {_tono_animal(perfil.animal)} es unico. Lo basico para {ref}: "
            f"alimentacion balanceada, agua fresca, espacio limpio y revision veterinaria periodica."
        )

    productos, ratings = _buscar_productos(msg, perfil, limite=2, temas_extra=contexto.get('temas_memoria'))
    extra = ''
    if productos:
        empatia = frase_aleatoria('empatia', perfil.animal) or 'En la tienda tengo esto que te puede servir:'
        lineas = [_describir_producto(p, ratings, perfil) for p in productos]
        extra = f"\n\n{empatia}\n" + '\n'.join(lineas)

    return _personalizar(cuerpo + extra, contexto, perfil)


def _respuesta_compra(contexto: dict, perfil: PerfilMascota) -> str:
    return _personalizar(
        'Es facil: elige productos en Tienda, agrégalos al carrito e inicia sesion. '
        'En Checkout confirmas direccion y metodo de pago. Si quieres, dime que buscas y te guio.',
        contexto,
        perfil,
    )


def _respuesta_seguimiento(history: list, perfil: PerfilMascota, contexto: dict) -> str:
    ultimo_bot = ''
    for msg in reversed(history):
        if msg.get('role') == 'assistant':
            ultimo_bot = msg.get('content', '')
            break
    if '**' in ultimo_bot:
        return _personalizar(
            'Perfecto! El producto que te mostre esta en Tienda. ¿Quieres otra recomendacion o un tip de cuidado?',
            contexto,
            perfil,
        )
    return _respuesta_productos('recomienda algo popular', perfil, contexto)


def procesar_mensaje(
    message: str,
    conversation_history: list | None = None,
    context: dict | None = None,
) -> dict:
    _reset_productos_cache()
    context = context or {}
    history = conversation_history or []
    user_id = context.get('user_id')

    from .miaubot_memoria import (
        aplicar_memoria_a_perfil,
        actualizar_memoria,
        cargar_memoria,
        temas_conocidos,
    )

    memoria = cargar_memoria(user_id)

    textos_user = [message] + [m.get('content', '') for m in history if m.get('role') == 'user']
    textos = list(textos_user)
    for m in history:
        if m.get('role') == 'assistant':
            textos.append(m.get('content', ''))
    perfil = _extraer_perfil(textos)
    perfil = aplicar_memoria_a_perfil(perfil, memoria)
    if context.get('animal'):
        perfil.animal = context['animal']

    context['memoria'] = memoria
    context['temas_memoria'] = temas_conocidos(memoria)

    # Prioridad: IA en la nube (Gemini) con prompt + catalogo desde BD
    from .miaubot_llm import generar_respuesta_ia

    ia = generar_respuesta_ia(message, history, context, perfil)
    if ia:
        actualizar_memoria(memoria, perfil, message, textos_user)
        _guardar_aprendizaje(message, ia['response'], perfil, context)
        ia['perfil'] = {
            'animal': perfil.animal,
            'nombre': perfil.nombre,
            'edad': perfil.edad,
            'raza': perfil.raza,
        }
        return ia

    # Fallback solo si no hay GEMINI_API_KEY o la API fallo
    intencion = _detectar_intencion(message)

    handlers = {
        'saludo': lambda: _respuesta_saludo(context, perfil),
        'despedida': lambda: _personalizar(
            frase_aleatoria('despedida', perfil.animal) or 'Hasta pronto! Cuida bien a tu mascota.',
            context, perfil,
        ),
        'compra': lambda: _respuesta_compra(context, perfil),
        'producto': lambda: _respuesta_productos(message, perfil, context),
        'cuidado': lambda: _respuesta_cuidado(message, perfil, context),
        'seguimiento': lambda: _respuesta_seguimiento(history, perfil, context),
    }

    if intencion in handlers:
        respuesta = handlers[intencion]()
    else:
        conocimiento = buscar_conocimiento(message, perfil.animal)
        if conocimiento:
            respuesta = _personalizar(conocimiento.respuesta, context, perfil)
        elif _buscar_productos(message, perfil, temas_extra=context.get('temas_memoria'))[0]:
            respuesta = _respuesta_productos(message, perfil, context)
        elif _perfil_completo(perfil) and _parece_pedido_producto(message):
            respuesta = _respuesta_productos(message, perfil, context)
        elif perfil.temas or context.get('temas_memoria'):
            respuesta = _respuesta_productos(message, perfil, context)
        else:
            respuesta = _personalizar(
                f"Cuéntame mas de {_ref_mascota(perfil)}: edad, tamano o que necesitas "
                f"(comida, juguetes, higiene). Asi te doy una recomendacion precisa.",
                context,
                perfil,
            )

    result = {
        'success': True,
        'response': respuesta,
        'status': f'local_{intencion}',
        'perfil': {
            'animal': perfil.animal,
            'nombre': perfil.nombre,
            'edad': perfil.edad,
            'raza': perfil.raza,
        },
    }
    actualizar_memoria(memoria, perfil, message, textos_user)
    _guardar_aprendizaje(message, respuesta, perfil, context)
    return result


def _guardar_aprendizaje(message: str, respuesta: str, perfil: PerfilMascota, context: dict) -> None:
    from .miaubot_aprendizaje import registrar_interaccion
    registrar_interaccion(
        pregunta=message,
        respuesta=respuesta,
        animal=perfil.animal,
        usuario_id=context.get('user_id'),
    )


def obtener_mensaje_bienvenida(user_name: str | None = None, user_id: int | None = None) -> str:
    from .miaubot_memoria import cargar_memoria, generar_seguimiento_saludo

    memoria = cargar_memoria(user_id)
    seguimiento = generar_seguimiento_saludo(memoria, user_name)
    if seguimiento:
        return seguimiento

    config = obtener_config()
    if not config:
        return 'Hola! Soy MiauBot. Cuéntame de tu mascota y te ayudo.'
    tpl = config.mensaje_bienvenida_retorno if user_name else config.mensaje_bienvenida
    return tpl.replace('{nombre}', user_name or '')
