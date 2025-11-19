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


def get_product_ratings():
    """
    Obtiene los ratings promedio de los productos desde la tabla Product_Ratings.
    Retorna un diccionario con product_id como clave y rating_promedio como valor.
    """
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Id_Products, Rating_Promedio, Total_Reviews 
                FROM Product_Ratings
            """)
            ratings = {}
            for row in cursor.fetchall():
                product_id, rating_avg, total_reviews = row
                ratings[product_id] = {
                    'promedio': float(rating_avg) if rating_avg else 0,
                    'total': int(total_reviews) if total_reviews else 0
                }
        return ratings
    except Exception as e:
        print(f"⚠️ Error obteniendo ratings: {str(e)}")
        return {}


def format_products_for_ai(products):
    """
    Formatea los productos para presentarlos a la IA, incluyendo ratings.
    """
    ratings = get_product_ratings()
    formatted = []
    for p in products:
        product_rating = ratings.get(p['id'], {'promedio': 0, 'total': 0})
        formatted.append({
            'id': p['id'],
            'nombre': p['Titulo'],
            'descripcion': p['Descripcion'],
            'categoria': p['Categoria'],
            'precio': float(p['Precio']),
            'stock': p['Stock'],
            'rating_promedio': product_rating['promedio'],
            'total_reviews': product_rating['total']
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
        
        # Agregar rating si existe
        if p['rating_promedio'] > 0:
            stars = "⭐" * int(p['rating_promedio'])
            products_text += f"   Calificación: {stars} ({p['rating_promedio']:.1f}/5) - {p['total_reviews']} reseñas\n"
        
        if p['descripcion']:
            products_text += f"   Descripción completa: {p['descripcion']}\n"
        products_text += "-" * 80 + "\n"
    
    # Inteligencia del prompt para recomendaciones
    prompt = f"""Eres un vendedor experto de MiauMarket. Tu trabajo es dar recomendaciones CORTAS, directas y convincentes.

INFORMACIÓN DEL CLIENTE Y SU GATO:
- Raza/Tipo: {dog_type}
- Edad: {age} años
- Tamaño: {size}
- Condiciones especiales: {health_conditions if health_conditions else 'Ninguna'}
- Solicitud: {user_message if user_message else (budget if budget else 'No especificado')}

{products_text}

INSTRUCCIONES:
1. SOLO usa productos que TIENEN STOCK (stock > 0)
2. Respeta presupuesto si lo mencionó
3. Recomienda 2-3 productos máximo (sé selectivo)
4. FORMATO POR CADA PRODUCTO:
   - Nombre del producto en negrita
   - Símbolo ✓ con beneficios clave (2-3 máximo)
   - Stock y precio en la misma línea
   - Pregunta directa para vender (ej: "¿Lo agregamos?")

ESTILO REQUERIDO:
- CORTO y directo (sin párrafos largos)
- Natural y humano, sin exageración
- Enfocado en VENDER
- Tono amable pero profesional
- Usa símbolos (✓, 🐾) con moderación
- NUNCA uses asteriscos (*) para énfasis
- NUNCA hagas listas con viñetas
- Integra todo de forma natural

EJEMPLO CORRECTO:
Gatsy – Alimento para Gato Adulto
✓ Pollo y pescado (proteína de calidad)
✓ Contiene taurina para ojos sanos
✓ Pelaje brillante
15 unidades | $100.000
¿Lo agregamos al carrito?

IMPORTANTE: Basa recomendaciones SOLO en productos reales listados. No inventes."""
    
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
        
        # Detectar error de cuota excedida
        error_str = str(e).lower()
        if "quota" in error_str or "429" in error_str or "exceeded" in error_str:
            print(f"   ⚠️ Cuota de API excedida")
            return {
                'success': True,
                'recommendations': "Estoy procesando muchas solicitudes. Por favor intenta en unos segundos. 😊",
                'status': 'Cuota temporal excedida'
            }
        
        return {
            'success': False,
            'error': str(e)[:100],
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
    
    # Construir historial de conversación
    history_text = ""
    conversation_history = context.get('conversation_history', []) if context else []
    if conversation_history and len(conversation_history) > 0:
        history_text = "HISTORIAL DE CONVERSACIÓN RECIENTE:\n"
        # Mostrar los últimos 6 mensajes para mantener contexto sin saturar
        for msg in conversation_history[-6:]:
            role = "Cliente" if msg.get('role') == 'user' else "Asesor"
            content = msg.get('content', '')
            # Limitar línea si es muy larga
            if len(content) > 120:
                content = content[:120] + "..."
            history_text += f"{role}: {content}\n"
        history_text += "\n"
    
    # Crear lista DETALLADA de productos disponibles
    products_info = "PRODUCTOS DISPONIBLES EN MIAUMARKET (Revisa cada detalle):\n"
    if formatted_products:
        for i, p in enumerate(formatted_products[:20], 1):  # Limitar a 20 productos
            products_info += f"\n{i}. {p['nombre']}\n"
            products_info += f"   Categoría: {p['categoria']} | Precio: ${p['precio']} | Stock: {p['stock']} unidades\n"
            
            # Agregar rating si existe
            if p['rating_promedio'] > 0:
                stars = "⭐" * int(p['rating_promedio'])
                products_info += f"   Calificación: {stars} ({p['rating_promedio']:.1f}/5) - {p['total_reviews']} reseñas\n"
            
            if p['descripcion']:
                products_info += f"   Descripción: {p['descripcion']}\n"
    else:
        products_info = "No hay productos disponibles en este momento.\n"
    
    prompt = f"""Eres un asesor de servicio al cliente de MiauMarket, especialista en productos para gatos.

Tu rol es SIMPLE Y CLARO:
- Responder preguntas sobre productos para gatos
- Dar recomendaciones basadas en necesidades del cliente
- Ofrecer información sobre stock, precio, beneficios
- Continuar la conversación de forma natural

{context_text}

{history_text}

{products_info}

PREGUNTA DEL CLIENTE: {message}

RESPONDE ASÍ:
1. Lee la pregunta del cliente cuidadosamente
2. Si pregunta sobre PRODUCTOS: recomienda 1-2 opciones con nombre, precio y 1-2 beneficios
3. Si pregunta sobre CANTIDAD/DISPONIBILIDAD: confirma el stock disponible
4. Si pregunta sobre OTROS TEMAS (juguetes, accesorios, etc): Busca en los productos listados y recomienda lo más relevante
5. Siempre responde en español, natural y breve (máximo 4 líneas)
6. Nunca uses formatos como listas con *, encabezados con ##, o explicaciones técnicas
7. Usa emojis solo ocasionalmente (máximo 1-2)
8. Mantén el tono como amigo experto en gatos, no como robot

IMPORTANTE:
- Recuerda el historial: No repitas saludos que ya diste
- Si el cliente dice números solos (ej: "1", "5"), asume que es respuesta a una pregunta anterior
- Sé conversacional: Si pregunta sobre juguetes, responde sobre juguetes. Si pregunta sobre comida, responde sobre comida.
- Evita respuestas genéricas: Siempre conecta con lo que el cliente ya mencionó

RESTRICCIÓN CRÍTICA:
- Tu respuesta SIEMPRE debe ser sobre PRODUCTOS PARA GATOS
- No hagas advertencias de seguridad ni explicaciones sobre políticas
- Solo responde de forma natural y útil

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
        
        # Verificar si la respuesta fue bloqueada por filtros de seguridad
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            finish_reason = candidate.finish_reason
            
            # Finish reason 2 = SAFETY (bloqueado por seguridad)
            if finish_reason == 2:
                print(f"   ⚠️ Respuesta bloqueada por filtros de seguridad - Intentando prompt simplificado...")
                
                # Intentar con un prompt mucho más simple
                simple_prompt = f"""Eres un vendedor de productos para gatos en MiauMarket. Responde la pregunta del cliente de forma breve y natural.

Cliente pregunta: {message}

Productos disponibles que puedes recomendar:
{products_info}

Responde en una sola línea o dos, como lo haría un vendedor real. Solo habla de productos para gatos."""
                
                try:
                    simple_response = model.generate_content(
                        simple_prompt,
                        generation_config=generation_config
                    )
                    
                    if hasattr(simple_response, 'text') and simple_response.text:
                        text = simple_response.text.strip()
                        print(f"   📝 Respuesta recuperada con prompt simplificado: {text[:80]}...")
                        return {
                            'success': True,
                            'response': text,
                            'status': 'Respuesta (prompt simplificado)'
                        }
                except Exception as e:
                    print(f"   ⚠️ Segundo intento también falló: {str(e)[:100]}")
                
                # Si todo falla, usar fallback contextual
                lower_message = message.lower()
                
                # Fallback inteligente basado en el tipo de pregunta
                if "jugete" in lower_message or "juguete" in lower_message:
                    fallback_msg = "¡Claro! Tenemos juguetes para gatos como ratones, pelotas y más. ¿Cuál te llama la atención? 🐾"
                elif "stock" in lower_message or "cantidad" in lower_message:
                    fallback_msg = "Tenemos muy buena disponibilidad. ¿Cuántos necesitas? 🛒"
                elif message.strip().isdigit():
                    fallback_msg = "Perfecto, anotado. ¿Hay algo más que necesites? 😸"
                else:
                    fallback_msg = "¿Hay algo específico que te interese? Estoy aquí para ayudarte 🐱"
                
                print(f"   💬 Fallback contextual: {fallback_msg[:60]}...")
                return {
                    'success': True,
                    'response': fallback_msg,
                    'status': 'Respuesta alternativa (filtro de seguridad)'
                }
        
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
            'success': True,
            'response': "Lo siento, no pude generar una respuesta adecuada. ¿Podrías hacer tu pregunta de otra forma? 🤔",
            'status': 'Respuesta vacía'
        }
    except Exception as e:
        print(f"   ❌ ERROR en chatbot_response: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Detectar error de cuota excedida
        error_str = str(e).lower()
        if "quota" in error_str or "429" in error_str or "exceeded" in error_str:
            print(f"   ⚠️ Cuota de API excedida - devolviendo respuesta local")
            return {
                'success': True,
                'response': "Estoy procesando muchas solicitudes en este momento. Por favor, intenta de nuevo en unos segundos. 😊",
                'status': 'Cuota de API temporal excedida'
            }
        
        # Para otros errores
        return {
            'success': True,
            'response': "Lo siento, hubo un problema al procesar tu solicitud. Intenta de nuevo más tarde. 🙏",
            'status': f'Error: {str(e)[:50]}'
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
