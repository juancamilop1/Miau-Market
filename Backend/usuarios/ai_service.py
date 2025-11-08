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
    Revisa stock, precio, nombre y descripción de cada producto.
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
    
    # Crear lista detallada de productos formateada para el prompt
    products_text = "PRODUCTOS DISPONIBLES EN LA TIENDA (Revisa cada detalle):\n"
    products_text += "=" * 80 + "\n"
    for i, p in enumerate(formatted_products, 1):
        products_text += f"\n{i}. PRODUCTO: {p['nombre']}\n"
        products_text += f"   ID: {p['id']}\n"
        products_text += f"   Categoría: {p['categoria']}\n"
        products_text += f"   Precio: ${p['precio']}\n"
        products_text += f"   Stock disponible: {p['stock']} unidades\n"
        products_text += f"   Disponibilidad: {'✅ Disponible' if p['stock'] > 0 else '❌ Agotado'}\n"
        if p['descripcion']:
            products_text += f"   Descripción completa: {p['descripcion']}\n"
        products_text += "-" * 80 + "\n"
    
    # Inteligencia del prompt para recomendaciones
    prompt = f"""Eres un experto en productos para gatos de MiauMarket. Tu objetivo es dar EXCELENTES recomendaciones personalizadas.

INFORMACIÓN DEL CLIENTE Y SU GATO:
- Raza/Tipo: {dog_type}
- Edad: {age} años
- Tamaño: {size}
- Condiciones especiales de salud: {health_conditions if health_conditions else 'Ninguna'}
- Comentario/Solicitud del cliente: {user_message if user_message else (budget if budget else 'No especificado')}

{products_text}

INSTRUCCIONES CRÍTICAS:
1. REVISA DETALLADAMENTE: El stock, precio, nombre exacto y descripción de CADA producto
2. Solo recomienda productos que TIENEN STOCK DISPONIBLE (stock > 0)
3. Respeta el presupuesto del cliente si lo mencionó
4. Recomienda 3-5 productos que sean realmente adecuados para este gato específico
5. Para cada recomendación:
   - Menciona el nombre exacto del producto
   - Explica específicamente por qué es adecuado BASÁNDOTE en la descripción real del producto
   - Menciona el precio
   - Menciona la disponibilidad de stock
6. Proporciona consejos de cuidado específicos para esta raza y edad
7. Sé conversacional, amigable y utiliza emojis ocasionalmente
8. Si no hay productos adecuados disponibles, sé honesto pero sugiere alternativas

IMPORTANTE SOBRE EL FORMATO:
- NO uses asteriscos (*) para títulos o énfasis
- Usa un formato natural y conversacional
- Presenta la información de forma fluida, no como listas robóticas
- Ejemplo: "Te recomiendo el producto 'Nombre del Producto' porque..." 
- NO escribas "Descripción corta:" ni cosas similares
- Integra la descripción naturalmente en tu explicación

IMPORTANTE: Basa tus recomendaciones ÚNICAMENTE en los productos reales listados arriba. No inventes productos."""
    
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
    Revisa detalladamente stock, precio, nombre y descripción de productos.
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
    
    # Crear lista DETALLADA de productos disponibles
    products_info = "PRODUCTOS DISPONIBLES EN MIAUMARKET (Revisa cada detalle):\n"
    if formatted_products:
        for i, p in enumerate(formatted_products[:20], 1):  # Limitar a 20 productos
            products_info += f"\n{i}. {p['nombre']}\n"
            products_info += f"   Categoría: {p['categoria']} | Precio: ${p['precio']} | Stock: {p['stock']} unidades\n"
            if p['descripcion']:
                products_info += f"   Descripción: {p['descripcion']}\n"
    else:
        products_info = "No hay productos disponibles en este momento.\n"
    
    prompt = f"""Eres un experto amigable en cuidado de gatos y asesor de productos de MiauMarket.
    
{context_text}

{products_info}

PREGUNTA DEL CLIENTE: {message}

INSTRUCCIONES:
1. REVISA DETALLADAMENTE el nombre exacto, descripción, precio y stock de cada producto
2. Si recomiendas productos:
   - Menciona el nombre exacto del producto de forma natural en la conversación
   - Explica específicamente POR QUÉ es adecuado basándote en su descripción real
   - Menciona el precio y disponibilidad de forma conversacional
   - Solo recomienda productos con stock disponible
3. Sé conversacional, empático y utiliza emojis ocasionalmente
4. Si el cliente pregunta por algo que no tenemos, sugiere alternativas reales disponibles
5. Proporciona consejos de cuidado específicos para gatos
6. NO uses formato robótico con asteriscos o puntos innecesarios
7. Escribe como si estuvieras teniendo una conversación natural con un cliente
8. Integra la información de productos de forma fluida y natural

Respuesta:"""
    
    try:
        print(f"   ⏳ Llamando API de Gemini para respuesta conversacional...")
        # Configuración de generación para chatbot
        generation_config = {
            'temperature': 0.7,
            'max_output_tokens': 1200,
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
