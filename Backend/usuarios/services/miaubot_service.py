"""
MiauBot — motor hibrido: IA en la nube (Gemini con tools) + fallback local.
"""

import re
import random
from dataclasses import dataclass, field

from ..models import CatCategoria
from .miaubot_knowledge import (
    buscar_conocimiento,
    frase_aleatoria,
    obtener_config,
)
from .miaubot_tools import (
    buscar_productos_catalogo,
    normalizar_texto,
    obtener_catalogo_cacheado,
    productos_mencionados_en_texto,
    serializar_productos_card,
)


_OTROS_ANIMALES = (
    'alce', 'conejo', 'conejos', 'hamster', 'pez', 'peces', 'loro', 'loros',
    'pajaro', 'pajaros', 'ave', 'aves', 'tortuga', 'tortugas', 'iguana',
    'caballo', 'caballos', 'vaca', 'vacas', 'cerdo', 'cerdos', 'huron',
    'cobaya', 'cuy', 'serpiente', 'tarantula', 'erizo', 'chinchilla',
    'oveja', 'cabra', 'pato', 'gallina', 'leon', 'tigre', 'oso', 'elefante',
)


@dataclass
class PerfilMascota:
    animal: str | None = None
    otro_animal: str | None = None
    nombre: str | None = None
    raza: str | None = None
    edad: str | None = None
    tamano: str | None = None
    temas: set = field(default_factory=set)


def _cargar_productos():
    return obtener_catalogo_cacheado()


def _format_price(precio) -> str:
    try:
        return f'${int(precio):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return str(precio)


def _detectar_especie_en_texto(texto_norm: str) -> tuple[str | None, str | None]:
    """Devuelve (animal_soportado, otro_animal) con coincidencia por palabra completa."""
    for otro in _OTROS_ANIMALES:
        if re.search(rf'\b{re.escape(otro)}\b', texto_norm):
            return None, otro
    if re.search(r'\b(perro|perra|perrito|perrita|cachorro|cachorros|canino|perruno|dog\s+chow|dogourmet)\b', texto_norm):
        return 'perro', None
    if re.search(r'\b(gato|gata|gatito|gatita|felino|michi|cat\s+chow)\b', texto_norm):
        return 'gato', None
    return None, None


def _extraer_perfil(textos: list[str]) -> PerfilMascota:
    perfil = PerfilMascota()
    msg_actual_norm = normalizar_texto(textos[0]) if textos else ''
    blob = normalizar_texto(' '.join(textos))

    # Priorizar la especie mencionada en el mensaje actual
    animal_actual, otro_actual = _detectar_especie_en_texto(msg_actual_norm)
    if otro_actual:
        perfil.otro_animal = otro_actual
    elif animal_actual:
        perfil.animal = animal_actual
    else:
        animal_hist, _ = _detectar_especie_en_texto(blob)
        if animal_hist:
            perfil.animal = animal_hist

    razas_perro = [
        'pitbull', 'pit bull', 'labrador', 'golden', 'bulldog', 'pastor', 'husky',
        'chihuahua', 'poodle', 'caniche', 'beagle', 'rottweiler', 'doberman',
        'boxer', 'dachshund', 'salchicha', 'pug', 'shih tzu', 'cocker',
    ]
    razas_gato = ['persa', 'siames', 'siamese', 'maine coon', 'bengala', 'ragdoll', 'sphynx']

    if not perfil.otro_animal:
        for raza in razas_perro:
            if re.search(rf'\b{re.escape(raza)}\b', blob):
                if not perfil.animal:
                    perfil.animal = 'perro'
                perfil.raza = raza
                if raza in ('chihuahua', 'pug', 'salchicha', 'dachshund', 'caniche', 'poodle', 'toy'):
                    perfil.tamano = 'pequeño'
                elif raza in ('pitbull', 'pit bull', 'labrador', 'golden', 'rottweiler', 'doberman', 'husky', 'pastor'):
                    perfil.tamano = 'grande'
                break

        for raza in razas_gato:
            if re.search(rf'\b{re.escape(raza)}\b', blob):
                if not perfil.animal:
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

    texto_original = ' '.join(textos)
    m_nombre = re.search(
        r'(?:se llama|llama|nombre es)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ]{2,20})', texto_original, re.IGNORECASE
    )
    if not m_nombre:
        m_nombre = re.search(
            r'mi (?:gato|gata|perro|perra|mascota)\s+'
            r'(?!(?:se|es|tiene|esta|está|no|ya|come|quiere|necesita)\b)([A-ZÁÉÍÓÚÑa-záéíóúñ]{2,20})',
            texto_original,
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
    if not temas:
        return []
    categorias = CatCategoria.objects.filter(activo=True, tema__in=temas)
    if perfil.animal in ('gato', 'perro'):
        categorias = categorias.filter(animal__in=(perfil.animal, 'general'))
    return list(categorias.values_list('nombre', flat=True))


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
    if perfil.otro_animal:
        _, ratings = obtener_catalogo_cacheado()
        return [], ratings
    return buscar_productos_catalogo(
        consulta=texto,
        animal=perfil.animal or '',
        limite=limite,
    )


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
    msg_limpio = re.sub(r'[¡!¿?.,;:]+', '', msg_l).strip()
    if msg_limpio in {'hola', 'hello', 'hi', 'hey', 'buenas', 'saludos', 'que tal', 'qué tal', 'buenos dias', 'buenas tardes', 'buenas noches'}:
        return 'saludo'
    if any(k in msg_limpio for k in ['adios', 'adiós', 'chao', 'hasta luego', 'nos vemos', 'bye']):
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
    if msg_limpio.isdigit() or msg_limpio in {'si', 'sí', 'ok', 'dale', 'va', 'listo'}:
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
    animal_txt = perfil.animal or 'mascota'
    texto = texto.replace('{nombre}', nombre).replace('{mascota}', _ref_mascota(perfil))
    texto = texto.replace('{animal}', animal_txt)
    if nombre and '{nombre}' not in texto and random.random() < 0.35:
        texto = f"{nombre}, {texto[0].lower()}{texto[1:]}" if texto else texto
    return texto


def _respuesta_saludo(contexto: dict, perfil: PerfilMascota) -> str:
    config = obtener_config()
    if config:
        tpl = config.mensaje_bienvenida_retorno if contexto.get('user_name') else config.mensaje_bienvenida
        if tpl:
            return _personalizar(tpl, contexto, perfil)

    intro = frase_aleatoria('saludo', perfil.animal or 'general') or 'Hola!'
    return _personalizar(
        f"{intro} Soy MiauBot de MiauMarket. Cuéntame de tu {_tono_animal(perfil.animal or 'general')} "
        f"y te recomiendo productos reales de nuestra tienda.",
        contexto,
        perfil,
    )


def _respuesta_productos(msg: str, perfil: PerfilMascota, contexto: dict) -> str:
    if perfil.otro_animal:
        return _personalizar(
            f"En MiauMarket nos especializamos en perros y gatos, por lo que no manejamos productos para {perfil.otro_animal}. "
            f"Si buscas algo para un perro o un gato, cuéntame y te ayudo.",
            contexto, perfil,
        )

    productos, ratings = _buscar_productos(msg, perfil)
    ref = _ref_mascota(perfil)

    if not productos:
        return _personalizar(
            f'No encontré coincidencias exactas para "{msg.strip()}" en nuestro catálogo actual. '
            f'En MiauMarket manejamos comida, juguetes, accesorios, higiene, farmacia y servicios para perros y gatos. '
            f'¿Quieres que te muestre opciones de alguna de estas categorías?',
            contexto, perfil,
        )

    intro = frase_aleatoria('intro_producto', perfil.animal or 'general') or f"Para {ref} te sugiero:"
    if perfil.edad:
        intro = f"Con {perfil.edad}, {intro[0].lower()}{intro[1:]}" if intro else intro

    lineas = [_describir_producto(p, ratings, perfil) for p in productos]
    cierre = frase_aleatoria('cierre_producto', perfil.animal or 'general') or 'Agregalos al carrito desde Tienda.'

    return _personalizar(
        f"{intro}\n\n" + '\n'.join(lineas) + f"\n{cierre}",
        contexto,
        perfil,
    )


def _respuesta_cuidado(msg: str, perfil: PerfilMascota, contexto: dict) -> str:
    animal_key = perfil.animal or 'general'
    conocimiento = buscar_conocimiento(msg, animal_key)
    ref = _ref_mascota(perfil)

    if conocimiento:
        cuerpo = conocimiento.respuesta
    else:
        cuerpo = (
            f"Cada {_tono_animal(animal_key)} es unico. Lo basico para {ref}: "
            f"alimentacion balanceada, agua fresca, espacio limpio y revision veterinaria periodica."
        )

    productos, ratings = _buscar_productos(msg, perfil, limite=2)
    extra = ''
    if productos:
        empatia = frase_aleatoria('empatia', animal_key) or 'En la tienda tengo esto que te puede servir:'
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

    # Prioridad: Gemini con Function Calling sobre tools cacheadas
    from .miaubot_llm import generar_respuesta_ia

    intencion = _detectar_intencion(message)
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
    animal_key = perfil.animal or 'general'
    handlers = {
        'saludo': lambda: _respuesta_saludo(context, perfil),
        'despedida': lambda: _personalizar(
            frase_aleatoria('despedida', animal_key) or 'Hasta pronto! Cuida bien a tu mascota.',
            context, perfil,
        ),
        'compra': lambda: _respuesta_compra(context, perfil),
        'producto': lambda: _respuesta_productos(message, perfil, context),
        'cuidado': lambda: _respuesta_cuidado(message, perfil, context),
        'seguimiento': lambda: _respuesta_seguimiento(history, perfil, context),
    }

    if perfil.otro_animal:
        respuesta = _respuesta_productos(message, perfil, context)
    elif intencion in handlers:
        respuesta = handlers[intencion]()
    else:
        conocimiento = buscar_conocimiento(message, animal_key)
        if conocimiento:
            respuesta = _personalizar(conocimiento.respuesta, context, perfil)
        elif _buscar_productos(message, perfil)[0]:
            respuesta = _respuesta_productos(message, perfil, context)
        else:
            respuesta = _personalizar(
                f"Cuéntame qué necesitas para {_ref_mascota(perfil)} (comida, juguetes, accesorios, higiene, farmacia o servicios) "
                f"o pregunta por una marca o producto en particular.",
                context,
                perfil,
            )

    _, ratings = obtener_catalogo_cacheado()
    cards_src = (
        []
        if intencion in ('saludo', 'despedida', 'compra') or perfil.otro_animal
        else productos_mencionados_en_texto(respuesta, limite=4)
    )
    result = {
        'success': True,
        'response': respuesta,
        'products': serializar_productos_card(cards_src, ratings),
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
        animal=perfil.animal or 'general',
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
