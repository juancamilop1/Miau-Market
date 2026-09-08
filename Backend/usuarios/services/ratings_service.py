from django.db.models import Avg, Count, Q

from ..models import Producto, ResenaProducto


def _rating_dict(producto: Producto) -> dict:
    return {
        'Id_Products': producto.id,
        'Titulo': producto.Titulo,
        'Total_Reviews': producto.Total_Reviews or 0,
        'Rating_Promedio': float(producto.Rating_Promedio or 0),
        'Reviews_5_Estrellas': producto.Reviews_5_Estrellas or 0,
        'Reviews_4_Estrellas': producto.Reviews_4_Estrellas or 0,
        'Reviews_3_Estrellas': producto.Reviews_3_Estrellas or 0,
        'Reviews_2_Estrellas': producto.Reviews_2_Estrellas or 0,
        'Reviews_1_Estrella': producto.Reviews_1_Estrella or 0,
    }


def _annotated_products():
    return Producto.objects.annotate(
        Total_Reviews=Count('resenas'),
        Rating_Promedio=Avg('resenas__Rating'),
        Reviews_5_Estrellas=Count('resenas', filter=Q(resenas__Rating=5)),
        Reviews_4_Estrellas=Count('resenas', filter=Q(resenas__Rating=4)),
        Reviews_3_Estrellas=Count('resenas', filter=Q(resenas__Rating=3)),
        Reviews_2_Estrellas=Count('resenas', filter=Q(resenas__Rating=2)),
        Reviews_1_Estrella=Count('resenas', filter=Q(resenas__Rating=1)),
    )


def obtener_rating_producto(product_id: int) -> dict | None:
    producto = _annotated_products().filter(id=product_id).first()
    return _rating_dict(producto) if producto else None


def obtener_ratings_todos() -> list[dict]:
    return [_rating_dict(p) for p in _annotated_products()]


def obtener_ratings_dict() -> dict[int, dict]:
    ratings = {}
    for item in obtener_ratings_todos():
        ratings[item['Id_Products']] = {
            'promedio': item['Rating_Promedio'],
            'total': item['Total_Reviews'],
        }
    return ratings


def listar_resenas_producto(product_id: int) -> list[dict]:
    resenas = (
        ResenaProducto.objects.filter(producto_id=product_id)
        .select_related('usuario')
        .order_by('-Fecha')
    )
    return [
        {
            'Id_Review': r.id,
            'Id_Products': r.producto_id,
            'Id_User': r.usuario_id,
            'Nombre': r.usuario.Nombre,
            'Apellido': r.usuario.Apellido,
            'Rating': r.Rating,
            'Comentario': r.Comentario,
            'Fecha': r.Fecha,
        }
        for r in resenas
    ]


def crear_resena(usuario_id: int, product_id: int, rating: int, comentario: str = '') -> ResenaProducto:
    if ResenaProducto.objects.filter(usuario_id=usuario_id, producto_id=product_id).exists():
        raise ValueError('Ya has dejado una resena para este producto')
    return ResenaProducto.objects.create(
        usuario_id=usuario_id,
        producto_id=product_id,
        Rating=rating,
        Comentario=comentario,
    )


def obtener_resena_usuario(usuario_id: int, product_id: int) -> dict | None:
    resena = ResenaProducto.objects.filter(usuario_id=usuario_id, producto_id=product_id).first()
    if not resena:
        return None
    return {
        'Id_Review': resena.id,
        'Id_Products': resena.producto_id,
        'Id_User': resena.usuario_id,
        'Rating': resena.Rating,
        'Comentario': resena.Comentario,
        'Fecha': resena.Fecha,
    }


def actualizar_resena(usuario_id: int, product_id: int, rating: int, comentario: str = '') -> None:
    updated = ResenaProducto.objects.filter(
        usuario_id=usuario_id, producto_id=product_id
    ).update(Rating=rating, Comentario=comentario)
    if not updated:
        raise ValueError('No se encontro la resena')


def eliminar_resena(usuario_id: int, product_id: int) -> None:
    deleted, _ = ResenaProducto.objects.filter(
        usuario_id=usuario_id, producto_id=product_id
    ).delete()
    if not deleted:
        raise ValueError('No se encontro la resena')
