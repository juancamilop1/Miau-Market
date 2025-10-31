import google.generativeai as genai
from django.conf import settings

# Configurar la API de Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_product_recommendations(dog_type, age, size, health_conditions=None, budget=None):
    """
    Obtiene recomendaciones de productos basadas en las características del perro.
    """
    print(f"   🔍 get_product_recommendations llamado con: dog_type={dog_type}, age={age}, size={size}")
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Inteligencia del prompt para recomendaciones
    prompt = f"""Eres un experto en productos para perros. Basándote en la siguiente información del perro, 
    proporciona recomendaciones específicas de productos de una tienda de mascotas.

    INFORMACIÓN DEL PERRO:
    - Raza/Tipo: {dog_type}
    - Edad: {age} años
    - Tamaño: {size}
    - Condiciones de salud especiales: {health_conditions if health_conditions else 'Ninguna'}
    - Rango de presupuesto: {budget if budget else 'No especificado'}

    Por favor, proporciona:
    1. 3-5 productos recomendados (alimento, juguetes, accesorios, etc.)
    2. Para cada producto, explica por qué es apropiado para este perro
    3. Incluye categorías como: alimento, juguetes, cuidado, accesorios
    4. Proporciona consejos de cuidado específicos para esta raza y edad

    Formatea la respuesta de manera clara y estructurada."""
    
    try:
        print(f"   ⏳ Llamando API de Gemini...")
        # Configuración de generación
        generation_config = {
            'temperature': 0.7,
            'max_output_tokens': 1000,  # Aumentado para evitar truncamiento
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
            if text:  # Si hay contenido, devolverlo
                return {
                    'success': True,
                    'recommendations': text,
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
    Genera una respuesta conversacional del chatbot sobre cuidado de perros y productos.
    """
    print(f"   🔍 chatbot_response llamado con message='{message[:50]}...'")
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Construir contexto
    context_text = ""
    if context:
        context_text = f"""
CONTEXTO DEL PERRO DEL USUARIO:
- Raza/Tipo: {context.get('dog_type', 'No especificada')}
- Edad: {context.get('age', 'No especificada')} años
- Tamaño: {context.get('size', 'No especificado')}
"""
    
    prompt = f"""Eres un experto en cuidado de perros. Responde de forma útil y amigable.
    
    {context_text}
    
    PREGUNTA: {message}
    
    Respuesta:"""
    
    try:
        print(f"   ⏳ Llamando API de Gemini para respuesta conversacional...")
        # Configuración de generación para chatbot
        generation_config = {
            'temperature': 0.7,
            'max_output_tokens': 1000,  # Aumentado para evitar truncamiento
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
            if text:  # Si hay contenido, devolverlo
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
