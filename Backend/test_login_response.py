import requests
import json

# Hacer login y ver la respuesta completa
url = "http://127.0.0.1:8000/api/usuarios/login/"
data = {
    "Email": "betobitch@gmail.com",
    "password": "123456789juan"
}

response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("\nRespuesta completa:")
print(json.dumps(response.json(), indent=2))

# Verificar específicamente is_superuser
if response.status_code == 200:
    user_data = response.json().get('user', {})
    print("\n" + "="*50)
    print(f"is_staff: {user_data.get('is_staff')}")
    print(f"is_superuser: {user_data.get('is_superuser')}")
    print("="*50)
