#!/usr/bin/env python
"""
Script para probar el endpoint del chatbot
"""
import requests
import json

print("=" * 60)
print("PRUEBA DE ENDPOINT CHATBOT")
print("=" * 60)

API_URL = "http://localhost:8000/api/usuarios/chatbot/"

# Prueba 1: Mensaje simple
test_data = {
    "message": "Hola"
}

print(f"\n📤 Enviando mensaje simple a: {API_URL}")
print(f"   Mensaje: '{test_data['message']}'")

try:
    response = requests.post(API_URL, json=test_data)
    
    print(f"\n📥 Respuesta del servidor:")
    print(f"   - Status Code: {response.status_code}")
    
    try:
        json_response = response.json()
        print(f"\n📦 Contenido:")
        print(json.dumps(json_response, indent=2, ensure_ascii=False))
    except:
        print(f"   Texto plano: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ CHATBOT FUNCIONANDO")
    else:
        print(f"\n❌ ERROR: Status code {response.status_code}")
        
except Exception as e:
    print(f"\n❌ ERROR DE CONEXIÓN: {e}")

print("\n" + "=" * 60)

# Prueba 2: Mensaje con contexto
print("\n\nPRUEBA 2: Con información del perro")
print("=" * 60)

test_data2 = {
    "message": "Recomiéndame productos",
    "dog_type": "Golden Retriever",
    "age": "3",
    "size": "grande"
}

print(f"\n📤 Enviando mensaje con contexto")
print(f"   Mensaje: '{test_data2['message']}'")
print(f"   Perro: {test_data2['dog_type']}, {test_data2['age']} años, {test_data2['size']}")

try:
    response = requests.post(API_URL, json=test_data2, timeout=30)
    
    print(f"\n📥 Respuesta del servidor:")
    print(f"   - Status Code: {response.status_code}")
    
    try:
        json_response = response.json()
        print(f"\n📦 Contenido:")
        print(json.dumps(json_response, indent=2, ensure_ascii=False))
    except:
        print(f"   Texto plano: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ RECOMENDACIONES GENERADAS")
    else:
        print(f"\n❌ ERROR: Status code {response.status_code}")
        
except requests.exceptions.Timeout:
    print("\n⏱️ TIMEOUT: La API tardó más de 30 segundos")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "=" * 60)
