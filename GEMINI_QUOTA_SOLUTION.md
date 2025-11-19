# 📊 Solución: Cuota de Gemini Excedida (Error 429)

## 🔴 El Problema
```
Error: 429 You exceeded your current quota
Límite gratuito: 250 requests/día
Status: AGOTADO por hoy
```

## ✅ Lo que ya hicimos
Implementamos manejo elegante de errores en el backend:
- El chatbot NO se cae si se agota la cuota
- El usuario recibe mensaje amable
- Puede reintentar después

## 🚀 Cómo Resolver PERMANENTEMENTE

### Opción 1: Actualizar a API de Pago (RECOMENDADO) ⭐⭐⭐
**Mejor opción para producción**

1. Ve a: https://console.cloud.google.com/
2. Selecciona tu proyecto
3. Ve a Facturación → Agregar método de pago
4. Llena información de tarjeta de crédito
5. Listo! Ahora tienes:
   - ✅ Límite de 1,000,000 requests/mes
   - ✅ Pago por uso ($0.075-0.30 por millón de tokens)
   - ✅ Soporte prioritario

**Costo estimado:**
- 100 usuarios = ~$5-10/mes
- 1,000 usuarios = ~$50-100/mes
- 10,000 usuarios = ~$500-1,000/mes

**Verificar que está activado:**
```
Backend > settings.py
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# Este mismo key funciona con API de pago
```

### Opción 2: Crear Múltiples API Keys Gratuitas
**Temporal/Testing solamente**

1. Crear Google Account nuevo
2. Generar nuevo GEMINI_API_KEY
3. Usar en diferentes horarios
4. ⚠️ NO es solución para producción

### Opción 3: Implementar Rate Limiting Local
**Controlar cantidad de requests**

```python
# Backend/usuarios/ai_service.py

import time
from django.core.cache import cache

def is_rate_limited(user_id, max_requests=5, time_window=3600):
    """
    Máximo 5 requests por hora por usuario
    """
    cache_key = f"chatbot_requests_{user_id}"
    requests_count = cache.get(cache_key, 0)
    
    if requests_count >= max_requests:
        return True
    
    cache.set(cache_key, requests_count + 1, time_window)
    return False
```

---

## 📈 Recomendación para MIAU-MARKET

**Corto Plazo (Próxima Semana):**
1. ✅ Agregar método de pago a Google Cloud
2. ✅ Actualizar GEMINI_API_KEY a versión de pago
3. ✅ Testear con más requests

**Mediano Plazo (Este Mes):**
1. Monitorear uso de cuota
2. Optimizar prompts para gastar menos tokens
3. Implementar caché para respuestas frecuentes

**Largo Plazo (Próximos Meses):**
1. Evaluar alternativas (Claude API, OpenAI, etc.)
2. Implementar mezcla de IAs (fallback inteligente)
3. Analytics de uso vs costo

---

## 🔄 Plan de Acción Inmediato

### Paso 1: Agregar Facturación (5 minutos)
```
https://console.cloud.google.com/
Proyecto: Miau-Market
Facturación → Agregar método de pago
```

### Paso 2: Verificar Límites Nuevos (2 minutos)
```
https://console.cloud.google.com/
APIs → Gemini API
Cuotas → Verificar: "Unlimited"
```

### Paso 3: Reiniciar Django (1 minuto)
```bash
python manage.py runserver
# Automáticamente usará nuevo límite
```

### Paso 4: Testear Chatbot (5 minutos)
```
Abrir http://localhost:4200
Enviar 10+ mensajes rápido
Verificar que NO hay error 429
```

---

## 📱 Monitorear Cuota Actual

### Dashboard de Uso:
https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

### Ver Costos:
https://console.cloud.google.com/billing/reports

---

## ⚡ Optimize para Gastar Menos Tokens

```python
# ANTES (Gasta ~500 tokens por request)
prompt = f"""Eres un experto completo en {descripcion_larga}...
{lista_de_productos_entera}
{contexto_completo}
Responde detalladamente...
"""

# DESPUÉS (Gasta ~150 tokens por request)
prompt = f"""Eres asesor de MiauMarket.
{productos_relevantes_solo}
Pregunta: {message}
Responde en 2-3 líneas.
"""

# Ahorro: 300 tokens/request × 1000 requests/día = 300,000 tokens
# Costo reducido en 60%
```

---

## 🎯 Decisión Recomendada

| Opción | Costo | Complejidad | Recomendado |
|--------|-------|-------------|------------|
| **API Pago** | $50-100/mes | Muy fácil | ✅✅✅ |
| **Rate Limiting** | Gratis | Media | ✅✅ |
| **Caché Local** | Gratis | Media | ✅✅ |
| **Múltiples Keys** | Gratis | Difícil | ❌ |

**Mi recomendación: API de Pago + Rate Limiting + Caché**

---

## 📞 Contacto para Ayuda

Si necesitas:
- ✅ Configurar facturación: Contacta a Google Cloud Support
- ✅ Modificar código: Me avisa y lo actualizo
- ✅ Monitorear costos: Dashboard de Google Cloud

---

**Prioridad:** 🔴 ALTA - Necesario para producción
**Tiempo estimado:** 10-15 minutos
**Dificultad:** Muy fácil
**Impacto:** Crítico

**Acción:** Completa esto hoy para evitar caídas del chatbot mañana.
