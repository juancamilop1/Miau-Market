from decimal import Decimal

from django.db import transaction
from django.db.models import Prefetch

from ..models import (
    CatEstadoPedido,
    CatMetodoPago,
    DetallePedido,
    Notificacion,
    Pedido,
    Producto,
    Usuario,
)


def _serializar_detalle(detalle: DetallePedido) -> dict:
    return {
        'Id_Products': detalle.producto_id,
        'Cantidad': detalle.Cantidad,
        'Precio_Unitario': detalle.Precio_Unitario,
        'Subtotal': detalle.Subtotal,
        'Titulo': detalle.producto.Titulo,
        'Imagen': detalle.producto.Imagen.name if detalle.producto.Imagen else None,
    }


def _serializar_pedido(pedido: Pedido, *, admin: bool = False) -> dict:
    data = {
        'Id_Factura': pedido.id,
        'Total': pedido.Total,
        'Fecha_Compra': pedido.Fecha,
        'Fecha': pedido.Fecha,
        'Estado': pedido.Estado,
        'estado_codigo': pedido.estado.codigo if pedido.estado_id else None,
        'Metodo_Pago': pedido.Metodo_Pago,
        'metodo_pago_codigo': pedido.metodo_pago.codigo if pedido.metodo_pago_id else None,
        'Direccion_Envio': pedido.Direccion_Envio,
        'Telefono_Envio': pedido.Telefono_Envio,
        'productos': [_serializar_detalle(d) for d in pedido.detalles.all()],
    }
    if admin:
        data.update({
            'Id_User': pedido.usuario_id,
            'usuario_nombre': f'{pedido.usuario.Nombre} {pedido.usuario.Apellido}',
            'usuario_email': pedido.usuario.Email,
        })
    return data


def listar_pedidos_admin() -> list[dict]:
    pedidos = Pedido.objects.select_related(
        'usuario', 'estado', 'metodo_pago'
    ).prefetch_related(
        Prefetch(
            'detalles',
            queryset=DetallePedido.objects.select_related('producto'),
        )
    ).order_by('-Fecha')
    return [_serializar_pedido(p, admin=True) for p in pedidos]


def listar_pedidos_usuario(usuario_id: int) -> list[dict]:
    pedidos = Pedido.objects.filter(usuario_id=usuario_id).select_related(
        'estado', 'metodo_pago'
    ).prefetch_related(
        Prefetch(
            'detalles',
            queryset=DetallePedido.objects.select_related('producto'),
        )
    ).order_by('-Fecha')
    return [_serializar_pedido(p) for p in pedidos]


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


def _resolver_metodo_pago(raw: str) -> CatMetodoPago:
    valor = (raw or '').strip()
    metodo = CatMetodoPago.objects.filter(activo=True, codigo=valor).first()
    if not metodo:
        metodo = CatMetodoPago.objects.filter(activo=True, nombre__iexact=valor).first()
    if not metodo:
        raise ValueError('Metodo de pago invalido')
    return metodo


def _resolver_estado(raw: str) -> CatEstadoPedido:
    valor = (raw or '').strip()
    estado = CatEstadoPedido.objects.filter(activo=True, codigo=valor).first()
    if not estado:
        estado = CatEstadoPedido.objects.filter(activo=True, nombre__iexact=valor).first()
    if not estado:
        raise ValueError('Estado de pedido invalido')
    return estado


def _restaurar_stock(pedido: Pedido) -> None:
    detalles = DetallePedido.objects.select_related('producto').filter(pedido=pedido)
    for detalle in detalles:
        producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)
        producto.Stock += detalle.Cantidad
        producto.save(update_fields=['Stock'])


@transaction.atomic
def crear_pedido(usuario: Usuario, data: dict) -> Pedido:
    metodo = _resolver_metodo_pago(data['Metodo_Pago'])
    estado_inicial = CatEstadoPedido.objects.get(codigo='pendiente')

    productos_validados = []
    total = Decimal('0')
    ids = [item['Id_Products'] for item in data['productos']]
    productos = {
        p.id: p
        for p in Producto.objects.select_for_update().filter(id__in=ids)
    }

    for item in data['productos']:
        producto = productos.get(item['Id_Products'])
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
        Metodo_Pago=metodo.nombre,
        metodo_pago=metodo,
        Estado=estado_inicial.nombre,
        estado=estado_inicial,
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


@transaction.atomic
def actualizar_estado_pedido(pedido_id: int, nuevo_estado: str) -> Pedido:
    pedido = (
        Pedido.objects.select_for_update()
        .select_related('usuario', 'estado')
        .filter(id=pedido_id)
        .first()
    )
    if not pedido:
        raise ValueError('Pedido no encontrado')

    estado = _resolver_estado(nuevo_estado)
    estado_anterior = pedido.estado
    ya_restauro = bool(estado_anterior and estado_anterior.restaura_stock)

    if estado.restaura_stock and not ya_restauro:
        _restaurar_stock(pedido)

    pedido.Estado = estado.nombre
    pedido.estado = estado
    pedido.save(update_fields=['Estado', 'estado'])

    mensajes = {
        'Pendiente': f'Tu pedido #{pedido.id} esta pendiente de procesamiento.',
        'Enviado': f'Tu pedido #{pedido.id} ha sido enviado. Pronto llegara a tu direccion.',
        'Entregado': f'Tu pedido #{pedido.id} ha sido entregado. Gracias por tu compra!',
        'Devuelto': f'Tu pedido #{pedido.id} ha sido devuelto y el stock fue reintegrado.',
        'Cancelado': f'Tu pedido #{pedido.id} fue cancelado y el stock fue reintegrado.',
    }

    Notificacion.objects.create(
        usuario=pedido.usuario,
        Titulo=f'Pedido {estado.nombre}',
        Mensaje=mensajes.get(estado.nombre, f'Tu pedido #{pedido.id} cambio a {estado.nombre}.'),
        Tipo=estado.codigo,
        pedido=pedido,
    )
    _limpiar_notificaciones(pedido.usuario_id, 7)
    return pedido


@transaction.atomic
def cancelar_pedido_usuario(pedido_id: int, usuario_id: int) -> Pedido:
    pedido = (
        Pedido.objects.select_for_update()
        .select_related('estado')
        .filter(id=pedido_id, usuario_id=usuario_id)
        .first()
    )
    if not pedido:
        raise ValueError('Pedido no encontrado')

    es_pendiente = (
        (pedido.estado and pedido.estado.codigo == 'pendiente')
        or (pedido.Estado or '').strip().lower() == 'pendiente'
    )
    if not es_pendiente:
        raise ValueError('Solo puedes cancelar pedidos en estado Pendiente')

    return actualizar_estado_pedido(pedido_id, 'cancelado')
