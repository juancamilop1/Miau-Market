import google.generativeai as genai
from django.conf import settings
from .models import Producto
import json

# Configurar la API de Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


def get_products_from_db():
    """
    Obtiene todos los productos de la base de datos con sus detalles.
    """
    try:
        productos = Producto.objects.all().values(
            'id', 'Titulo', 'Descripcion', 'Categoria', 'Precio', 'Stock', 'Imagen'
        )
        return list(productos)
    except Exception as e:
        print(f"❌ Error obteniendo productos de BD: {str(e)}")
        return []


def get_products_by_category(category):
    """
    Obtiene productos de una categoría específica.
    """
    try:
        productos = Producto.objects.filter(
            Categoria__icontains=category
        ).values(
            'id', 'Titulo', 'Descripcion', 'Categoria', 'Precio', 'Stock', 'Imagen'
        )
        return list(productos)
    except Exception as e:
        print(f"❌ Error obteniendo productos por categoría: {str(e)}")
        return []


def format_products_for_ai(products):
    """
    Formatea los productos para presentarlos a la IA.
    """
    formatted = []
    for p in products:
        formatted.append({
            'id': p['id'],
            'nombre': p['Titulo'],
            'descripcion': p['Descripcion'],
            'categoria': p['Categoria'],
            'precio': float(p['Precio']),
            'stock': p['Stock']
        })
    return formatted

def get_product_recommendations(dog_type, age, size, health_conditions=None, budget=None, user_message=None):
    """
    Obtiene recomendaciones de productos basadas en las características del perro
    y los productos disponibles en la base de datos.
    """
    print(f"   🔍 get_product_recommendations llamado con: dog_type={dog_type}, age={age}, size={size}")
    
    # Obtener todos los productos disponibles
    all_products = get_products_from_db()
    formatted_products = format_products_for_ai(all_products)
    
    print(f"   📦 Productos disponibles en BD: {len(formatted_products)}")
    
    if not formatted_products:
        return {
            'success': False,
            'error': 'No hay productos disponibles en la tienda.',
            'status': 'Error: sin productos'
        }
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Crear lista de productos formateada para el prompt
    products_text = "PRODUCTOS DISPONIBLES EN LA TIENDA:\n"
    for p in formatted_products:
        products_text += f"- {p['nombre']} (ID: {p['id']}, Categoría: {p['categoria']}, Precio: ${p['precio']}, Stock: {p['stock']})\n"
        if p['descripcion']:
            products_text += f"  Descripción: {p['descripcion'][:100]}...\n"
    
    # Inteligencia del prompt para recomendaciones
    prompt = f"""Eres un experto en productos para gatos de MiauMarket. 
    
    INFORMACIÓN DEL GATO:
    - Raza/Tipo: {dog_type}
    - Edad: {age} años
    - Tamaño: {size}
    - Condiciones especiales: {health_conditions if health_conditions else 'Ninguna'}
    - Rango de presupuesto: {user_message if user_message else (budget if budget else 'No especificado')}
    
    {products_text}
    
    Basándote SOLO en los productos disponibles listados arriba:
    1. Recomienda 3-5 productos específicos de la tienda que sean adecuados para este gato
    2. Explica por qué cada producto es apropiado
    3. Menciona el nombre exacto del producto y su categoría
    4. Proporciona consejos de cuidado específicos para esta raza y edad
    5. Si el cliente mencionó un presupuesto, respeta ese rango
    
    Sé específico y refiérete a los productos reales disponibles."""
    
    try:
        print(f"   ⏳ Llamando API de Gemini...")
        # Configuración de generación
        generation_config = {
            'temperature': 0.7,
            'max_output_tokens': 1000,
            'top_p': 0.8,
            'top_k': 40
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        print(f"   ✅ Respuesta recibida de Gemini")
        
        # Obtener el texto de la respuesta
        if hasattr(response, 'text') and response.text:
            text = response.text.strip()
            print(f"   📝 Texto: {text[:100]}...")
            if text:
                return {
                    'success': True,
                    'recommendations': text,
                    'products_available': len(formatted_products),
                    'status': 'Recomendaciones generadas exitosamente'
                }
        
        # Si no hay texto, intentar obtener del contenido
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                full_text = ''.join(text_parts).strip()
                if full_text:
                    print(f"   📝 Texto (de parts): {full_text[:100]}...")
                    return {
                        'success': True,
                        'recommendations': full_text,
                        'products_available': len(formatted_products),
                        'status': 'Recomendaciones generadas exitosamente'
                    }
        
        print(f"   ⚠️ Respuesta vacía")
        return {
            'success': False,
            'error': 'La API de Gemini no pudo generar recomendaciones. Intenta de nuevo.',
            'status': 'Error: respuesta vacía'
        }
    except Exception as e:
        print(f"   ❌ ERROR en get_product_recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'status': 'Error al generar recomendaciones'
        }


def chatbot_response(message, context=None):
    """
    Genera una respuesta conversacional del chatbot sobre cuidado de gatos y productos.
    Consulta la BD de productos para recomendaciones personalizadas.
    """
    print(f"   🔍 chatbot_response llamado con message='{message[:50]}...'")
    
    # Obtener productos disponibles
    all_products = get_products_from_db()
    formatted_products = format_products_for_ai(all_products)
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Construir contexto
    context_text = ""
    if context:
        context_text = f"""
CONTEXTO DEL GATO DEL USUARIO:
- Raza/Tipo: {context.get('dog_type', 'No especificada')}
- Edad: {context.get('age', 'No especificada')} años
- Tamaño: {context.get('size', 'No especificado')}
"""
    
    # Crear lista de productos disponibles para la IA
    products_info = "PRODUCTOS DISPONIBLES EN MIAUMARKET:\n"
    if formatted_products:
        for p in formatted_products[:15]:  # Limitar a 15 productos para el prompt
            products_info += f"- {p['nombre']} ({p['categoria']}) - ${p['precio']}\n"
    else:
        products_info = "No hay productos disponibles en este momento.\n"
    
    prompt = f"""Eres un experto amigable en cuidado de gatos y asesor de productos de MiauMarket.
    
    {context_text}
    
    {products_info}
    
    PREGUNTA DEL CLIENTE: {message}
    
    Responde de forma amigable y útil. Si el cliente pregunta sobre productos:
    1. Recomienda opciones reales de nuestra tienda
    2. Explica por qué son adecuadas
    3. Sé conversacional y empático
    4. Si no tenemos un producto específico, sugiere alternativas disponibles
    
    Respuesta:"""
    
    try:
        print(f"   ⏳ Llamando API de Gemini para respuesta conversacional...")
        # Configuración de generación para chatbot
        generation_config = {
            'temperature': 0.7,
            'max_output_tokens': 1000,
            'top_p': 0.9,
            'top_k': 40
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        print(f"   ✅ Respuesta recibida de Gemini")
        
        # Obtener el texto de la respuesta
        if hasattr(response, 'text') and response.text:
            text = response.text.strip()
            print(f"   📝 Texto: {text[:100]}...")
            if text:
                return {
                    'success': True,
                    'response': text,
                    'status': 'Respuesta generada exitosamente'
                }
        
        # Si no hay texto, intentar obtener del contenido
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                full_text = ''.join(text_parts).strip()
                if full_text:
                    print(f"   📝 Texto (de parts): {full_text[:100]}...")
                    return {
                        'success': True,
                        'response': full_text,
                        'status': 'Respuesta generada exitosamente'
                    }
        
        print(f"   ⚠️ Respuesta vacía")
        return {
            'success': False,
            'error': 'La API de Gemini no pudo generar una respuesta. Intenta de nuevo.',
            'status': 'Error: respuesta vacía'
        }
    except Exception as e:
        print(f"   ❌ ERROR en chatbot_response: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f'Error: {str(e)}',
            'status': 'Error al generar respuesta'
        }


def generate_product_description(product_name, product_type, dog_size):
    """
    Genera descripciones de productos usando IA.
    """
    print(f"   🔍 generate_product_description llamado")
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""Eres un copywriter especializado en productos para mascotas. 
    Crea una descripción atractiva y clara para el siguiente producto:
    
    - Nombre: {product_name}
    - Tipo: {product_type}
    - Tamaño objetivo: {dog_size}
    
    La descripción debe ser:
    - Concisa (máximo 3 párrafos)
    - Enfocada en beneficios
    - Incluir características principales
    - Apropiada para un sitio de compras online
    """
    
    try:
        print(f"   ⏳ Llamando API de Gemini...")
        # Configuración para descripciones de productos
        generation_config = {
            'temperature': 0.6,
            'max_output_tokens': 300,
            'top_p': 0.8,
            'top_k': 30
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        print(f"   ✅ Descripción generada")
        return {
            'success': True,
            'description': response.text,
            'status': 'Descripción generada exitosamente'
        }
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'status': 'Error al generar descripción'
        }
