from decimal import Decimal

from django.db import transaction
from django.db.models import Prefetch

from ..models import DetallePedido, Notificacion, Pedido, Producto, Usuario


def _serializar_detalle(detalle: DetallePedido) -> dict:
    return {
        'Id_Products': detalle.producto_id,
        'Cantidad': detalle.Cantidad,
        'Precio_Unitario': detalle.Precio_Unitario,
        'Subtotal': detalle.Subtotal,
        'Titulo': detalle.producto.Titulo,
        'Imagen': detalle.producto.Imagen.name if detalle.producto.Imagen else None,
    }


def listar_pedidos_admin() -> list[dict]:
    pedidos = Pedido.objects.select_related('usuario').prefetch_related(
        Prefetch(
            'detalles',
            queryset=DetallePedido.objects.select_related('producto'),
        )
    ).order_by('-Fecha')

    return [
        {
            'Id_Factura': pedido.id,
            'Id_User': pedido.usuario_id,
            'Fecha': pedido.Fecha,
            'Total': pedido.Total,
            'Metodo_Pago': pedido.Metodo_Pago,
            'Estado': pedido.Estado,
            'Direccion_Envio': pedido.Direccion_Envio,
            'Telefono_Envio': pedido.Telefono_Envio,
            'usuario_nombre': f'{pedido.usuario.Nombre} {pedido.usuario.Apellido}',
            'usuario_email': pedido.usuario.Email,
            'productos': [_serializar_detalle(d) for d in pedido.detalles.all()],
        }
        for pedido in pedidos
    ]


def listar_pedidos_usuario(usuario_id: int) -> list[dict]:
    pedidos = Pedido.objects.filter(usuario_id=usuario_id).prefetch_related(
        Prefetch(
            'detalles',
            queryset=DetallePedido.objects.select_related('producto'),
        )
    ).order_by('-Fecha')

    return [
        {
            'Id_Factura': pedido.id,
            'Total': pedido.Total,
            'Fecha_Compra': pedido.Fecha,
            'Estado': pedido.Estado,
            'Direccion_Envio': pedido.Direccion_Envio,
            'Telefono_Envio': pedido.Telefono_Envio,
            'productos': [_serializar_detalle(d) for d in pedido.detalles.all()],
        }
        for pedido in pedidos
    ]


def _limpiar_notificaciones(usuario_id: int, limite: int) -> None:
    ids = list(
        Notificacion.objects.filter(usuario_id=usuario_id)
        .order_by('-Fecha_Creacion')
        .values_list('id', flat=True)[:limite]
    )
    Notificacion.objects.filter(usuario_id=usuario_id).exclude(id__in=ids).delete()


def _notificar_admins(pedido: Pedido) -> None:
    for admin in Usuario.objects.filter(is_staff=True):
        Notificacion.objects.create(
            usuario=admin,
            Titulo='Nuevo Pedido Recibido',
            Mensaje=f'Se ha confirmado un nuevo pedido #{pedido.id} por COP {pedido.Total}',
            Tipo='nuevo_pedido',
            pedido=pedido,
        )
        _limpiar_notificaciones(admin.id, 10)


@transaction.atomic
def crear_pedido(usuario: Usuario, data: dict) -> Pedido:
    productos_validados = []
    total = Decimal('0')

    for item in data['productos']:
        producto = Producto.objects.filter(id=item['Id_Products']).first()
        if not producto:
            raise ValueError(f'Producto con ID {item["Id_Products"]} no encontrado')
        if producto.Stock < item['Cantidad']:
            raise ValueError(
                f'Stock insuficiente para "{producto.Titulo}". '
                f'Disponible: {producto.Stock}, Solicitado: {item["Cantidad"]}'
            )

        precio = Decimal(producto.Precio)
        subtotal = precio * item['Cantidad']
        total += subtotal
        productos_validados.append((producto, item['Cantidad'], precio, subtotal))

    pedido = Pedido.objects.create(
        usuario=usuario,
        Total=total,
        Metodo_Pago=data['Metodo_Pago'],
        Estado='Pendiente',
        Direccion_Envio=data['direccion_envio'],
        Telefono_Envio=data['telefono_envio'],
    )

    for producto, cantidad, precio, subtotal in productos_validados:
        DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            Cantidad=cantidad,
            Precio_Unitario=precio,
            Subtotal=subtotal,
        )
        producto.Stock -= cantidad
        producto.save(update_fields=['Stock'])

    _notificar_admins(pedido)
    return pedido


def actualizar_estado_pedido(pedido_id: int, nuevo_estado: str) -> Pedido:
    pedido = Pedido.objects.select_related('usuario').filter(id=pedido_id).first()
    if not pedido:
        raise ValueError('Pedido no encontrado')

    pedido.Estado = nuevo_estado
    pedido.save(update_fields=['Estado'])

    mensajes = {
        'Pendiente': f'Tu pedido #{pedido.id} esta pendiente de procesamiento.',
        'Enviado': f'Tu pedido #{pedido.id} ha sido enviado. Pronto llegara a tu direccion.',
        'Entregado': f'Tu pedido #{pedido.id} ha sido entregado. Gracias por tu compra!',
        'Devuelto': f'Tu pedido #{pedido.id} ha sido devuelto.',
    }

    Notificacion.objects.create(
        usuario=pedido.usuario,
        Titulo=f'Pedido {nuevo_estado}',
        Mensaje=mensajes[nuevo_estado],
        Tipo=nuevo_estado.lower(),
        pedido=pedido,
    )
    _limpiar_notificaciones(pedido.usuario_id, 7)
    return pedido
