from django.contrib import admin

from .models import (
    DetallePedido, MiauBotAprendizaje, MiauBotConfig, MiauBotConocimiento, MiauBotFrase,
    Notificacion, Pedido, Producto, ResenaProducto, Usuario,
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'Username', 'Email', 'Nombre', 'Apellido', 'is_staff', 'is_active')
    search_fields = ('Username', 'Email', 'Nombre', 'Apellido')
    list_filter = ('is_staff', 'is_active')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'Titulo', 'Categoria', 'Precio', 'Stock', 'Fecha_Caducidad')
    search_fields = ('Titulo', 'Categoria')
    list_filter = ('Categoria',)


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'Cantidad', 'Precio_Unitario', 'Subtotal')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'Total', 'Estado', 'Fecha')
    list_filter = ('Estado',)
    search_fields = ('usuario__Email', 'usuario__Nombre')
    inlines = [DetallePedidoInline]


@admin.register(ResenaProducto)
class ResenaProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'usuario', 'Rating', 'Fecha')
    list_filter = ('Rating',)


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'Titulo', 'Tipo', 'Leida', 'Fecha_Creacion')
    list_filter = ('Tipo', 'Leida')


@admin.register(MiauBotConfig)
class MiauBotConfigAdmin(admin.ModelAdmin):
    list_display = ('nombre_bot', 'activo', 'updated_at')


@admin.register(MiauBotConocimiento)
class MiauBotConocimientoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'tema', 'prioridad', 'activo')
    list_filter = ('animal', 'activo')
    search_fields = ('tema', 'palabras_clave', 'respuesta')


@admin.register(MiauBotFrase)
class MiauBotFraseAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'animal', 'texto', 'activo')
    list_filter = ('tipo', 'animal', 'activo')


@admin.register(MiauBotAprendizaje)
class MiauBotAprendizajeAdmin(admin.ModelAdmin):
    list_display = ('pregunta_corta', 'animal', 'estado', 'veces_usada', 'Fecha_Creacion')
    list_filter = ('estado', 'animal')
    search_fields = ('pregunta', 'respuesta', 'palabras_clave')
    readonly_fields = ('palabras_clave', 'veces_usada', 'Fecha_Creacion')
    actions = ['aprobar_aprendizajes', 'rechazar_aprendizajes']

    @admin.display(description='Pregunta')
    def pregunta_corta(self, obj):
        return obj.pregunta[:80]

    @admin.action(description='Aprobar y agregar a conocimiento')
    def aprobar_aprendizajes(self, request, queryset):
        from .services.miaubot_aprendizaje import aprobar_aprendizaje
        for item in queryset.filter(estado='pendiente'):
            aprobar_aprendizaje(item)
        self.message_user(request, f'{queryset.count()} aprendizajes aprobados.')

    @admin.action(description='Rechazar')
    def rechazar_aprendizajes(self, request, queryset):
        queryset.update(estado='rechazado')
        self.message_user(request, f'{queryset.count()} aprendizajes rechazados.')
