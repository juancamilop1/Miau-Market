#!/usr/bin/env python
"""
Script para probar la conexión a la base de datos MySQL
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model

Usuario = get_user_model()

print("=" * 60)
print("PRUEBA DE CONEXIÓN A BASE DE DATOS")
print("=" * 60)

try:
    # Probar conexión básica
    print("\n1️⃣  Intentando conectar a la base de datos...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    print("✅ Conexión exitosa a MySQL")
    
    # Obtener información de la base de datos
    print("\n2️⃣  Información de la base de datos:")
    db_config = connection.settings_dict
    print(f"   - Engine: {db_config['ENGINE']}")
    print(f"   - Base de datos: {db_config['NAME']}")
    print(f"   - Usuario: {db_config['USER']}")
    print(f"   - Host: {db_config['HOST']}")
    print(f"   - Puerto: {db_config['PORT']}")
    
    # Probar modelos
    print("\n3️⃣  Probando modelo Usuario...")
    users_count = Usuario.objects.count()
    print(f"✅ Usuarios en la BD: {users_count}")
    
    # Listar usuarios
    if users_count > 0:
        print("\n4️⃣  Usuarios existentes:")
        for user in Usuario.objects.all():
            print(f"   - {user.Nombre} {user.Apellido} ({user.Email})")
    else:
        print("\n4️⃣  No hay usuarios creados aún")
    
    # Probar creación de usuario (sin guardarlo)
    print("\n5️⃣  Prueba de creación de usuario (sin guardar):")
    test_user = Usuario(
        Email="test@example.com",
        Nombre="Test",
        Apellido="Usuario"
    )
    print(f"   ✅ Usuario de prueba creado: {test_user.Nombre} {test_user.Apellido}")
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   Mensaje: {str(e)}")
    print("\nPosibles soluciones:")
    print("   1. Verifica que MySQL esté corriendo")
    print("   2. Verifica la contraseña en settings.py")
    print("   3. Verifica que la BD 'miau_market' exista")
    print("=" * 60)
