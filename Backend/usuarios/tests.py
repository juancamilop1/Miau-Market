from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import CatCategoria, CatEstadoPedido, CatMetodoPago, Pedido, Producto
from .services import pedidos_service

Usuario = get_user_model()


class SeguridadYPedidosTests(TestCase):
    def setUp(self):
        CatCategoria.objects.get_or_create(
            codigo='juguetes', defaults={'nombre': 'Juguetes', 'activo': True, 'orden': 1}
        )
        CatMetodoPago.objects.get_or_create(
            codigo='contra_entrega',
            defaults={'nombre': 'Contra Entrega', 'activo': True, 'orden': 1},
        )
        for codigo, nombre, restaura in (
            ('pendiente', 'Pendiente', False),
            ('devuelto', 'Devuelto', True),
            ('cancelado', 'Cancelado', True),
        ):
            CatEstadoPedido.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'activo': True, 'restaura_stock': restaura, 'orden': 1},
            )

        self.admin = Usuario.objects.create_user(
            Email='admin@test.com',
            Username='admin',
            password='ClaveSegura1!',
            Nombre='Admin',
            Apellido='Test',
            Telefono='3001111111',
            Address='Calle 1',
            City='Bogota',
            BirthDate=date(1990, 1, 1),
            is_staff=True,
            is_superuser=True,
        )
        self.user = Usuario.objects.create_user(
            Email='user@test.com',
            Username='user1',
            password='ClaveSegura1!',
            Nombre='User',
            Apellido='Test',
            Telefono='3002222222',
            Address='Calle 2',
            City='Bogota',
            BirthDate=date(1995, 1, 1),
        )
        self.other = Usuario.objects.create_user(
            Email='other@test.com',
            Username='other1',
            password='ClaveSegura1!',
            Nombre='Other',
            Apellido='Test',
            Telefono='3003333333',
            Address='Calle 3',
            City='Bogota',
            BirthDate=date(1992, 1, 1),
        )
        cat = CatCategoria.objects.get(codigo='juguetes')
        self.producto = Producto.objects.create(
            Titulo='Raton de juguete',
            Descripcion='Para gatos',
            Categoria=cat.nombre,
            categoria=cat,
            Precio=10000,
            Stock=5,
            Fecha_Caducidad=date.today() + timedelta(days=365),
        )
        self.client = APIClient()

    def test_usuario_list_solo_admin(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get('/api/usuarios/')
        self.assertEqual(res.status_code, 403)

    def test_usuario_detail_idor(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get(f'/api/usuarios/{self.other.id}/')
        self.assertEqual(res.status_code, 403)

    def test_crear_pedido_descuenta_stock(self):
        pedido = pedidos_service.crear_pedido(
            self.user,
            {
                'Metodo_Pago': 'contra_entrega',
                'direccion_envio': 'Calle 10',
                'telefono_envio': '3009999999',
                'productos': [
                    {'Id_Products': self.producto.id, 'Cantidad': 2, 'Precio_Unitario': Decimal('10000')}
                ],
            },
        )
        self.producto.refresh_from_db()
        self.assertEqual(pedido.Estado, 'Pendiente')
        self.assertEqual(self.producto.Stock, 3)

    def test_devolver_restaura_stock(self):
        pedido = pedidos_service.crear_pedido(
            self.user,
            {
                'Metodo_Pago': 'Contra Entrega',
                'direccion_envio': 'Calle 10',
                'telefono_envio': '3009999999',
                'productos': [
                    {'Id_Products': self.producto.id, 'Cantidad': 2, 'Precio_Unitario': Decimal('10000')}
                ],
            },
        )
        pedidos_service.actualizar_estado_pedido(pedido.id, 'devuelto')
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.Stock, 5)
        pedido.refresh_from_db()
        self.assertEqual(pedido.Estado, 'Devuelto')

    def test_cancelar_pedido_usuario(self):
        pedido = pedidos_service.crear_pedido(
            self.user,
            {
                'Metodo_Pago': 'contra_entrega',
                'direccion_envio': 'Calle 10',
                'telefono_envio': '3009999999',
                'productos': [
                    {'Id_Products': self.producto.id, 'Cantidad': 1, 'Precio_Unitario': Decimal('10000')}
                ],
            },
        )
        pedidos_service.cancelar_pedido_usuario(pedido.id, self.user.id)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.Stock, 5)
        self.assertEqual(Pedido.objects.get(pk=pedido.id).Estado, 'Cancelado')

    def test_catalogos_publico(self):
        res = self.client.get('/api/usuarios/catalogos/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('categorias', res.data)
        self.assertIn('metodos_pago', res.data)
