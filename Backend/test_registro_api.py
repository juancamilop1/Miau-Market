#!/usr/bin/env python
"""
Script para probar el endpoint de registro via API
"""
import requests
import json

print("=" * 60)
print("PRUEBA DE ENDPOINT DE REGISTRO")
print("=" * 60)

API_URL = "http://localhost:8000/api/usuarios/registro/"

# Datos de prueba
test_data = {
    "Nombre": "Juan",
    "Apellido": "Perez",
    "Email": "juan.perez@example.com",
    "password": "TestPassword123!",
    "password2": "TestPassword123!",
    "Telefono": "1234567890",
    "Address": "Calle Principal 123",
    "City": "Bogotá",
    "BirthDate": "1990-01-15"
}

print(f"\n📤 Enviando datos a: {API_URL}")
print(f"📋 Datos:")
for key, value in test_data.items():
    if key not in ['password', 'password2']:
        print(f"   - {key}: {value}")
    else:
        print(f"   - {key}: {'*' * len(value)}")

try:
    response = requests.post(API_URL, json=test_data)
    
    print(f"\n📥 Respuesta del servidor:")
    print(f"   - Status Code: {response.status_code}")
    print(f"   - Headers: {dict(response.headers)}")
    print(f"\n📦 Contenido de la respuesta:")
    
    try:
        json_response = response.json()
        print(json.dumps(json_response, indent=2, ensure_ascii=False))
    except:
        print(f"   Texto plano: {response.text}")
    
    if response.status_code == 201:
        print("\n✅ REGISTRO EXITOSO")
    elif response.status_code == 400:
        print("\n⚠️  VALIDACIÓN FALLIDA - Revisa los errores arriba")
    else:
        print(f"\n❌ ERROR: Status code {response.status_code}")
        
except Exception as e:
    print(f"\n❌ ERROR DE CONEXIÓN: {e}")
    print("\nVerifica que:")
    print("   1. El servidor Django esté corriendo en http://localhost:8000")
    print("   2. La URL sea correcta")

print("\n" + "=" * 60)
