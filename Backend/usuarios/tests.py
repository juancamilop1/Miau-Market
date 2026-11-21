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
        from .services.miaubot_tools import invalidar_cache_catalogo
        invalidar_cache_catalogo()
        cat = CatCategoria.objects.filter(codigo__iexact='JUGUETES').first()
        if not cat:
            cat = CatCategoria.objects.create(
                codigo='JUGUETES', nombre='Juguetes', activo=True, orden=1
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

    def test_seed_demo_idempotente(self):
        from django.core.management import call_command

        call_command('seed_demo')
        total_primera = Producto.objects.count()
        self.assertGreaterEqual(total_primera, 25)

        # Simula producto existente sin imagen (como en BD previa) y valida backfill
        p = Producto.objects.filter(Titulo='Croquetas premium gato').first()
        self.assertIsNotNone(p)
        p.Imagen = ''
        p.save(update_fields=['Imagen'])

        call_command('seed_demo')
        self.assertEqual(Producto.objects.count(), total_primera)
        p.refresh_from_db()
        self.assertEqual(p.Imagen.name, '/productos/adulto.jpg')

        # Serializacion publica de productos debe devolver rutas /productos/... sin romper ImageField
        res = self.client.get('/api/usuarios/productos/')
        self.assertEqual(res.status_code, 200)
        items = {item['Titulo']: item for item in res.data}
        self.assertEqual(items['Croquetas premium gato']['Imagen'], '/productos/adulto.jpg')
        self.assertEqual(items['Bano y peluqueria mascotas']['Imagen'], '/productos/bano_peluqueria.svg')
        self.assertTrue(Usuario.objects.filter(Email='admin@miau.market', is_staff=True).exists())
        self.assertTrue(Usuario.objects.filter(Email='cliente@miau.market', is_staff=False).exists())

    def test_chatbot_devuelve_productos_con_imagen(self):
        from django.core.management import call_command
        from django.test import override_settings

        call_command('seed_demo')
        with override_settings(GEMINI_API_KEY=''):
            res = self.client.post(
                '/api/usuarios/chatbot/',
                {'message': 'Recomiendame comida para gato', 'conversation_history': []},
                format='json',
            )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get('success'))
        prods = res.data.get('products') or []
        self.assertGreater(len(prods), 0)
        for prod in prods:
            self.assertIn('id', prod)
            self.assertIn('titulo', prod)
            self.assertIn('precio', prod)
            self.assertTrue((prod.get('imagen') or '').startswith('/productos/'))
            self.assertNotEqual(prod['titulo'], 'galletas chunky')

    def test_miaubot_tools_y_llm_desacoplado(self):
        import inspect
        from django.core.management import call_command
        from .services import miaubot_llm, miaubot_tools
        from .services.miaubot_service import PerfilMascota

        # El modulo LLM no debe importar modelos ORM directamente ni volcar catalogo en el prompt
        src = inspect.getsource(miaubot_llm)
        self.assertNotIn('Producto.objects', src)
        self.assertNotIn('MiauBotConocimiento.objects', src)

        call_command('seed_demo')
        prompt = miaubot_llm._construir_system_instruction({'user_name': 'Maria'}, PerfilMascota(animal='gato'))
        self.assertLess(len(prompt), 600)
        self.assertNotIn('CATALOGO REAL', prompt)

        tools, dispatcher, recuperados, usadas = miaubot_tools.construir_herramientas_bot(usuario_id=self.user.id)
        self.assertEqual(len(tools), 5)

        res_busq = dispatcher['buscar_productos'](consulta='comida', animal='gato', limite=3)
        self.assertGreater(res_busq['total'], 0)
        self.assertGreater(len(recuperados), 0)
        self.assertIn('buscar_productos', usadas)

        res_cats = dispatcher['listar_categorias']()
        self.assertGreaterEqual(len(res_cats['categorias']), 5)

        res_know = dispatcher['consultar_conocimiento'](tema='comida', animal='gato')
        self.assertTrue(res_know.get('guia'))
