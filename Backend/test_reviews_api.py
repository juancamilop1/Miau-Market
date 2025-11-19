"""
Script de prueba para los endpoints de reseñas de productos
Ejecutar: python test_reviews_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_product_reviews():
    print("=== PRUEBA DE ENDPOINTS DE RESEÑAS ===\n")
    
    # 1. Login para obtener token
    print("1. Iniciando sesión...")
    login_data = {
        "Email": "admin@miau.com",  # Cambia esto por un usuario real
        "Password": "admin123"
    }
    
    login_response = requests.post(f"{BASE_URL}/usuarios/login/", json=login_data)
    if login_response.status_code == 200:
        token = login_response.json()["token"]
        user_id = login_response.json()["id"]
        print(f"✅ Login exitoso. User ID: {user_id}")
        headers = {"Authorization": f"Token {token}"}
    else:
        print(f"❌ Error en login: {login_response.text}")
        return
    
    # 2. Obtener lista de productos
    print("\n2. Obteniendo productos...")
    productos_response = requests.get(f"{BASE_URL}/usuarios/productos/")
    if productos_response.status_code == 200:
        productos = productos_response.json()
        if productos:
            product_id = productos[0]["Id_Products"]
            print(f"✅ Productos obtenidos. Usando producto ID: {product_id}")
        else:
            print("❌ No hay productos disponibles")
            return
    else:
        print(f"❌ Error al obtener productos: {productos_response.text}")
        return
    
    # 3. Ver reseñas del producto
    print(f"\n3. Obteniendo reseñas del producto {product_id}...")
    reviews_response = requests.get(f"{BASE_URL}/usuarios/productos/{product_id}/reviews/")
    if reviews_response.status_code == 200:
        reviews_data = reviews_response.json()
        print(f"✅ Reseñas obtenidas: {reviews_data['total']} reseñas")
        if reviews_data['reviews']:
            print(f"   Primera reseña: {reviews_data['reviews'][0]}")
    else:
        print(f"❌ Error al obtener reseñas: {reviews_response.text}")
    
    # 4. Ver rating agregado del producto
    print(f"\n4. Obteniendo rating del producto {product_id}...")
    rating_response = requests.get(f"{BASE_URL}/usuarios/productos/{product_id}/rating/")
    if rating_response.status_code == 200:
        rating_data = rating_response.json()
        print(f"✅ Rating obtenido:")
        if rating_data['rating']:
            print(f"   Promedio: {rating_data['rating']['Rating_Promedio']}")
            print(f"   Total reseñas: {rating_data['rating']['Total_Reviews']}")
    else:
        print(f"❌ Error al obtener rating: {rating_response.text}")
    
    # 5. Ver mi reseña (si existe)
    print(f"\n5. Verificando mi reseña para el producto {product_id}...")
    my_review_response = requests.get(
        f"{BASE_URL}/usuarios/productos/{product_id}/my-review/", 
        headers=headers
    )
    if my_review_response.status_code == 200:
        my_review = my_review_response.json()['review']
        if my_review:
            print(f"✅ Ya tengo una reseña para este producto")
            print(f"   Rating: {my_review['Rating']}")
            print(f"   Comentario: {my_review['Comentario']}")
            
            # 6. Actualizar mi reseña
            print(f"\n6. Actualizando mi reseña...")
            update_data = {
                "Rating": 5,
                "Comentario": "Producto actualizado - ¡Excelente! (Prueba API)"
            }
            update_response = requests.put(
                f"{BASE_URL}/usuarios/productos/{product_id}/my-review/",
                json=update_data,
                headers=headers
            )
            if update_response.status_code == 200:
                print(f"✅ Reseña actualizada exitosamente")
            else:
                print(f"❌ Error al actualizar: {update_response.text}")
        else:
            # 7. Crear nueva reseña
            print(f"✅ No tengo reseña para este producto")
            print(f"\n7. Creando nueva reseña...")
            new_review_data = {
                "Rating": 5,
                "Comentario": "¡Producto excelente! Me encantó. (Prueba API)"
            }
            create_response = requests.post(
                f"{BASE_URL}/usuarios/productos/{product_id}/reviews/",
                json=new_review_data,
                headers=headers
            )
            if create_response.status_code == 201:
                print(f"✅ Reseña creada exitosamente")
            else:
                print(f"❌ Error al crear reseña: {create_response.text}")
    else:
        print(f"❌ Error al verificar mi reseña: {my_review_response.text}")
    
    # 8. Ver todos los ratings
    print(f"\n8. Obteniendo ratings de todos los productos...")
    all_ratings_response = requests.get(f"{BASE_URL}/usuarios/ratings/")
    if all_ratings_response.status_code == 200:
        all_ratings = all_ratings_response.json()['ratings']
        print(f"✅ Ratings obtenidos: {len(all_ratings)} productos con ratings")
        if all_ratings:
            # Mostrar top 3 productos mejor calificados
            sorted_ratings = sorted(
                all_ratings, 
                key=lambda x: x['Rating_Promedio'], 
                reverse=True
            )[:3]
            print(f"\n   Top 3 productos mejor calificados:")
            for i, rating in enumerate(sorted_ratings, 1):
                print(f"   {i}. {rating['Titulo']}: {rating['Rating_Promedio']:.1f} ★ ({rating['Total_Reviews']} reseñas)")
    else:
        print(f"❌ Error al obtener ratings: {all_ratings_response.text}")
    
    print("\n=== PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    try:
        test_product_reviews()
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
