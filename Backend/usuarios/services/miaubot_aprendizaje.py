"""Aprendizaje de MiauBot a partir de preguntas reales de usuarios."""

import re

from ..models import MiauBotAprendizaje, MiauBotConocimiento
from .miaubot_knowledge import invalidar_cache


STOPWORDS = {
    'para', 'como', 'que', 'con', 'por', 'los', 'las', 'del', 'una', 'uno',
    'the', 'and', 'pero', 'muy', 'mas', 'más', 'tengo', 'puedo', 'hola',
}


def extraer_palabras_clave(texto: str) -> str:
    palabras = [
        w.lower() for w in re.findall(r'[a-zA-Z0-9áéíóúñ]+', texto)
        if len(w) > 2 and w.lower() not in STOPWORDS
    ]
    return ', '.join(dict.fromkeys(palabras[:15]))


def registrar_interaccion(
    pregunta: str,
    respuesta: str,
    animal: str = 'general',
    usuario_id: int | None = None,
) -> None:
    """Guarda cada conversacion para revision/aprendizaje."""
    pregunta = pregunta.strip()
    respuesta = respuesta.strip()
    if len(pregunta) < 4 or len(respuesta) < 10:
        return

    claves = extraer_palabras_clave(pregunta)

    similar = MiauBotAprendizaje.objects.filter(
        pregunta__iexact=pregunta, estado='pendiente'
    ).first()
    if similar:
        similar.respuesta = respuesta
        similar.palabras_clave = claves
        similar.save(update_fields=['respuesta', 'palabras_clave'])
        return

    MiauBotAprendizaje.objects.create(
        pregunta=pregunta,
        respuesta=respuesta,
        palabras_clave=claves,
        animal=animal,
        usuario_id=usuario_id,
        estado='pendiente',
    )


def buscar_aprendizaje_aprobado(texto: str, animal: str = 'general', limite: int = 5) -> list:
    """Busca Q&A aprobados similares a la pregunta actual."""
    texto_l = texto.lower()
    palabras = [w for w in extraer_palabras_clave(texto).split(', ') if w]

    candidatos = MiauBotAprendizaje.objects.filter(
        estado='aprobado',
        animal__in=[animal, 'general'],
    ).order_by('-veces_usada', '-Fecha_Creacion')[:50]

    scored = []
    for item in candidatos:
        keys = [k.strip() for k in item.palabras_clave.split(',') if k.strip()]
        score = sum(1 for k in keys if k in texto_l)
        if score > 0 or item.pregunta.lower() in texto_l:
            scored.append((score + item.veces_usada * 0.1, item))

    scored.sort(key=lambda x: -x[0])
    resultados = [item for _, item in scored[:limite]]

    for item in resultados:
        MiauBotAprendizaje.objects.filter(pk=item.pk).update(
            veces_usada=item.veces_usada + 1
        )

    return resultados


def aprendizaje_para_prompt(texto: str, animal: str = 'general') -> str:
    items = buscar_aprendizaje_aprobado(texto, animal)
    if not items:
        return ''
    lineas = []
    for i in items:
        lineas.append(f"P: {i.pregunta}\nR: {i.respuesta}")
    return '\n\n'.join(lineas)


def aprobar_aprendizaje(item: MiauBotAprendizaje, promover_conocimiento: bool = True) -> None:
    """Aprueba una interaccion y opcionalmente la copia a conocimiento base."""
    item.estado = 'aprobado'
    item.save(update_fields=['estado'])

    if not promover_conocimiento:
        return

    tema = (item.palabras_clave.split(',')[0] if item.palabras_clave else 'aprendido')[:50]
    existe = MiauBotConocimiento.objects.filter(
        tema=tema, respuesta=item.respuesta, animal=item.animal
    ).exists()
    if not existe:
        MiauBotConocimiento.objects.create(
            animal=item.animal if item.animal in ('gato', 'perro') else 'general',
            tema=f'aprendido_{item.id}',
            palabras_clave=item.palabras_clave or extraer_palabras_clave(item.pregunta),
            respuesta=item.respuesta,
            prioridad=3,
            activo=True,
        )
        invalidar_cache()
