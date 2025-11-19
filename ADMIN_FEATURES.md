# 🎯 Guía de Funcionalidades del Panel de Administración

## ✨ Nuevas Características Implementadas

### 1. 📋 Vistas Intercambiables

#### Vista de Tabla
- **Activación**: Botón "📋 Vista Tabla" en el header
- **Características**:
  - Tabla tradicional con todas las columnas
  - Checkbox para selección múltiple
  - Ordenamiento por defecto: Fecha de registro (más recientes primero)
  - Acciones individuales por usuario

#### Vista de Tarjetas
- **Activación**: Botón "🎴 Vista Tarjetas" en el header
- **Características**:
  - Diseño visual tipo card
  - Avatar con iniciales del usuario
  - Información organizada en grid (Teléfono, Pedidos, Total Gastado, Fecha)
  - Checkbox integrado en cada tarjeta
  - Efecto hover con animación
  - Borde naranja cuando está seleccionado

---

### 2. ⚡ Acciones Masivas

#### Selección de Usuarios
1. **Selección Individual**: Click en checkbox de cada usuario
2. **Seleccionar Todos**: Checkbox en el header de la tabla (solo selecciona la página actual)
3. **Contador en Tiempo Real**: El botón muestra cuántos usuarios tienes seleccionados

#### Acciones Disponibles

##### 🗑️ Eliminar Usuarios Masivamente
- **Requisito**: Tener al menos 1 usuario seleccionado
- **Restricciones**:
  - No puedes eliminarte a ti mismo
  - Staff NO puede eliminar superusuarios (solo superusuarios pueden)
- **Confirmación**: Ventana de confirmación antes de ejecutar
- **Proceso**:
  1. Selecciona usuarios con checkboxes
  2. Click en "⚡ Acciones Masivas"
  3. Click en "🗑️ Eliminar Usuarios"
  4. Confirma la acción

##### 👑 Hacer Administradores Masivamente
- **Requisito**: Ser Superusuario
- **Restricciones**:
  - Solo superusuarios tienen acceso
  - No puede aplicarse a otros superusuarios
  - No puedes modificar tus propios permisos
- **Confirmación**: Ventana de confirmación antes de ejecutar
- **Proceso**:
  1. Selecciona usuarios normales
  2. Click en "⚡ Acciones Masivas"
  3. Click en "👑 Hacer Administradores"
  4. Confirma la acción

---

### 3. 📥 Exportación de Datos (CSV)

#### Dropdown de Exportación
Click en el botón "📥 Exportar" para ver 3 opciones:

##### 👥 Lista de Usuarios
- **Archivo**: `usuarios.csv`
- **Contenido**:
  - ID, Nombre, Apellido, Email, Teléfono
  - Dirección, Ciudad, Rol
  - Total de Pedidos, Total Gastado
  - Fecha de Registro
- **Filtros**: Exporta usuarios filtrados por búsqueda actual
- **Codificación**: UTF-8 con BOM (compatible con Excel)

##### 🛒 Lista de Pedidos
- **Archivo**: `pedidos.csv`
- **Contenido**:
  - ID Pedido, Cliente, Email
  - Fecha, Total, Estado
  - Método de Pago, Dirección, Teléfono
- **Filtros**: Exporta todos los pedidos cargados

##### 📊 Reporte de Ventas
- **Archivo**: `reporte_ventas.csv`
- **Contenido**:
  - Resumen General: Total Ventas, Total Pedidos, Promedio por Pedido
  - Pedidos por Estado: Desglose de Pendiente, Enviado, Entregado, Devuelto
  - Pedidos por Método de Pago: PSE, Tarjeta Crédito, Efectivo, etc.
- **Formato**: Organizado por secciones para análisis

---

### 4. 🔍 Búsqueda y Filtros

#### Barra de Búsqueda
- **Búsqueda en Tiempo Real**: Actualiza resultados mientras escribes
- **Campos Buscables**:
  - Nombre
  - Apellido
  - Email
  - Nombre completo (Nombre + Apellido)
- **Contador**: Muestra cantidad de resultados encontrados
- **Paginación Automática**: Vuelve a página 1 al buscar

#### Paginación
- **Selector de Items por Página**: 10, 20, 50, 100
- **Navegación**:
  - Botones Anterior/Siguiente
  - Números de página clickeables
  - Elipsis (...) para grandes rangos
  - Muestra rango actual (ej: "Mostrando 1-10 de 50 usuarios")

---

### 5. ⚠️ Modal de Confirmación de Eliminación

#### Características del Modal
- **Diseño Seguro**: Requiere confirmación explícita
- **Input de Verificación**: Debes escribir el nombre completo del usuario
- **Información Detallada**: Muestra datos del usuario a eliminar
- **Animaciones**: Efecto pulse en ícono de advertencia
- **Responsive**: Se adapta a móviles

#### Proceso de Eliminación
1. Click en botón "Eliminar" de un usuario
2. Modal muestra información del usuario
3. Escribe el nombre completo exacto (insensible a mayúsculas)
4. Si el nombre coincide, se activa el botón "Eliminar Usuario"
5. Click en "Eliminar Usuario" para confirmar
6. El usuario es eliminado permanentemente

#### Validaciones
- ❌ Nombre incorrecto → Muestra error
- ❌ Campo vacío → Botón deshabilitado
- ✅ Nombre correcto → Botón activado
- ⌨️ Enter → Intenta confirmar (si el nombre es correcto)
- 🖱️ Click fuera del modal → Cancela

---

### 6. 🎨 Mejoras Visuales

#### Badges y Etiquetas
- **"Tú"**: Badge verde que identifica tu cuenta
- **Roles**:
  - 🔴 Superusuario: Rojo intenso
  - 🟡 Administrador: Naranja
  - 🔵 Usuario: Azul

#### Animaciones
- **Cards**: Elevación al hacer hover
- **Botones**: Efecto lift al pasar el mouse
- **Modal**: Slide up con bounce
- **Transiciones**: Todas las interacciones tienen animaciones suaves

#### Dark Mode
- ✅ Completamente compatible
- ✅ Colores adaptativos con CSS variables
- ✅ Contraste optimizado para legibilidad

---

## 🔐 Permisos y Restricciones

### Roles del Sistema

#### 👤 Usuario Normal
- ❌ No tiene acceso al panel de administración

#### 👨‍💼 Administrador (is_staff)
- ✅ Ver todos los usuarios
- ✅ Eliminar usuarios normales
- ✅ Gestionar productos y pedidos
- ❌ Eliminar superusuarios
- ❌ Crear administradores
- ❌ Eliminar otros administradores

#### 👑 Superusuario (is_superuser)
- ✅ Acceso completo
- ✅ Eliminar cualquier usuario (excepto a sí mismo)
- ✅ Crear/quitar administradores
- ✅ Todas las funcionalidades de admin

---

## 📱 Responsive Design

### Móviles (< 768px)
- Vista de tarjetas en 1 columna
- Botones de acción en columna vertical
- Modal a pantalla completa
- Dropdown de exportación expandido
- Grid de información en 1 columna

### Tablets (768px - 1024px)
- Vista de tarjetas en 2 columnas
- Tabla horizontal scrollable

### Desktop (> 1024px)
- Vista de tarjetas en 3+ columnas
- Tabla completa visible
- Todos los controles en horizontal

---

## 🚀 Backend - Nuevos Endpoints

### Acciones Masivas

#### Eliminar Múltiples Usuarios
```
POST /usuarios/gestion/usuarios/bulk-delete/
```
**Body**:
```json
{
  "user_ids": [1, 2, 3, 4]
}
```
**Respuesta**:
```json
{
  "success": true,
  "message": "4 usuarios eliminados exitosamente"
}
```

#### Convertir en Administradores
```
POST /usuarios/gestion/usuarios/bulk-make-admin/
```
**Body**:
```json
{
  "user_ids": [5, 6, 7]
}
```
**Respuesta**:
```json
{
  "success": true,
  "message": "3 usuarios convertidos en administradores exitosamente"
}
```

---

## 🐛 Solución de Problemas

### La exportación no funciona
- ✅ Verifica que tengas datos cargados
- ✅ Revisa la consola del navegador para errores
- ✅ Algunos navegadores bloquean descargas automáticas

### No puedo seleccionar usuarios
- ✅ Asegúrate de estar en la pestaña de Usuarios
- ✅ Recarga la página si los checkboxes no responden

### Modal de confirmación no valida
- ✅ Escribe el nombre exacto como aparece (sin espacios extra)
- ✅ No importan mayúsculas/minúsculas
- ✅ Debe coincidir: "Juan Pérez" = "juan pérez" ✅

### Acciones masivas no aparecen
- ✅ Selecciona al menos 1 usuario
- ✅ Para "Hacer Administradores", debes ser Superusuario

---

## 📋 Cambios en el Backend

### Modelos
- ✅ Campo `Address` ahora NO es único (múltiples usuarios pueden tener la misma dirección)

### Validaciones Eliminadas
- ❌ Validación de dirección única en `RegistroSerializer`

---

## 💡 Tips y Trucos

1. **Selección Rápida**: Usa el checkbox del header para seleccionar toda la página
2. **Exportación Inteligente**: La lista de usuarios exporta solo los filtrados por búsqueda
3. **Vista Recomendada**: Usa tarjetas en móvil, tabla en desktop
4. **Búsqueda Efectiva**: Puedes buscar por nombre completo o solo apellido
5. **Paginación**: Cambia a 100 items para ver más usuarios a la vez
6. **Atajos de Teclado**: Enter en el modal de confirmación para eliminar rápido

---

## 🎯 Roadmap Futuro (Sugerencias)

- [ ] Filtros avanzados (por rol, por fecha de registro, por gastos)
- [ ] Ordenamiento personalizado en tabla
- [ ] Envío de correos masivos
- [ ] Exportación en formato Excel (.xlsx)
- [ ] Importación masiva de usuarios
- [ ] Historial de cambios (audit log)
- [ ] Gráficos de usuarios activos
- [ ] Búsqueda avanzada con operadores

---

**Versión**: 2.0  
**Última Actualización**: Noviembre 2025  
**Desarrollado para**: Miau Market 🐱
