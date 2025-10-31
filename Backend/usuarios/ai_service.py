import google.generativeai as genai
from django.conf import settings

# Configurar la API de Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_product_recommendations(dog_type, age, size, health_conditions=None, budget=None):
    """
    Obtiene recomendaciones de productos basadas en las características del perro.
    
    Args:
        dog_type (str): Raza o tipo de perro
        age (int): Edad del perro en años
        size (str): Tamaño del perro (pequeño, mediano, grande, extra grande)
        health_conditions (str): Condiciones de salud especiales (opcional)
        budget (str): Rango de presupuesto (bajo, medio, alto) (opcional)
    
    Returns:
        dict: Recomendaciones y explicaciones
    """
    
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
        # Configuración de generación
        generation_config = {
            'temperature': 0.7,           # Creatividad (0.0 - 1.0)
            'max_output_tokens': 150,     # Respuestas MÁS CORTAS
            'top_p': 0.8,                 # Control de diversidad
            'top_k': 40                   # Límite de opciones
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Validar que la respuesta sea válida
        if response.candidates and response.candidates[0].content.parts:
            return {
                'success': True,
                'recommendations': response.text,
                'status': 'Recomendaciones generadas exitosamente'
            }
        else:
            return {
                'success': False,
                'error': 'La respuesta fue cortada por límites de tokens',
                'status': 'Error: respuesta incompleta'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'status': 'Error al generar recomendaciones'
        }


def chatbot_response(message, context=None):
    """
    Genera una respuesta conversacional del chatbot sobre cuidado de perros y productos.
    
    Args:
        message (str): Pregunta o mensaje del usuario
        context (dict): Contexto opcional con información del perro
            - dog_type (str): Raza del perro
            - age (int): Edad del perro
            - size (str): Tamaño del perro
    
    Returns:
        dict: Respuesta conversacional
    """
    
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
    
    prompt = f"""Eres un experto en cuidado de perros. Responde de forma BREVE y útil.
    
    {context_text}
    
    PREGUNTA: {message}
    
    Respuesta (máximo 3 oraciones):"""
    
    try:
        # Configuración de generación para chatbot
        generation_config = {
            'temperature': 0.8,           # Más creativo para conversación
            'max_output_tokens': 400,     # Aumentar tokens para evitar cortes
            'top_p': 0.9,
            'top_k': 40
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Validar que la respuesta sea válida
        if response.candidates and response.candidates[0].content.parts:
            return {
                'success': True,
                'response': response.text,
                'status': 'Respuesta generada exitosamente'
            }
        else:
            return {
                'success': False,
                'error': 'La respuesta fue demasiado corta o cortada por límites de tokens',
                'status': 'Error: respuesta incompleta'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'status': 'Error al generar respuesta'
        }


def generate_product_description(product_name, product_type, dog_size):
    """
    Genera descripciones de productos usando IA.
    
    Args:
        product_name (str): Nombre del producto
        product_type (str): Tipo de producto
        dog_size (str): Tamaño de perro al que va dirigido
    
    Returns:
        dict: Descripción generada
    """
    
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
        # Configuración para descripciones de productos
        generation_config = {
            'temperature': 0.6,           # Menos creativo, más preciso
            'max_output_tokens': 500,     # Descripciones breves
            'top_p': 0.8,
            'top_k': 30
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return {
            'success': True,
            'description': response.text,
            'status': 'Descripción generada exitosamente'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'status': 'Error al generar descripción'
        }
