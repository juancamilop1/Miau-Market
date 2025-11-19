# 🧪 Guía de Testing: Chatbot v2.2.1

**Versión**: v2.2.1  
**Fecha**: 17 de Noviembre, 2025  
**Estado**: Listo para testing  

---

## 📋 Checklist Antes de Empezar

- [ ] Backend corriendo: `python manage.py runserver` (puerto 8000)
- [ ] Frontend corriendo: `ng serve` (puerto 4200)
- [ ] Gemini API Key actualizada en settings.py
- [ ] BD sincronizada: `python manage.py migrate`
- [ ] Usuario logged in (token de autenticación válido)

---

## 🧪 Test Suite 1: Memoria de Conversación

### Test 1.1: Acumulación de Historial
```
1. Abre chat
2. Envía: "Hola"
   ✅ Bot responde con saludo

3. Abre Developer Tools → Console
4. Envía: "Recomienda comida para gatos"
   ✅ Log mostrará: "Historial: 2 mensajes anteriores"

5. Envía: "¿Qué precio tiene?"
   ✅ Log mostrará: "Historial: 4 mensajes anteriores"

6. Envía: Mensajes 4, 5, 6 más...
   ✅ Log mostrará: "Historial: 12, 14, 16... mensajes"
   
RESULTADO ESPERADO: El historial crece con cada mensaje
```

### Test 1.2: Sin Saludos Repetidos
```
1. Abre chat
2. Envía: "Hola"
   ✅ Bot: "¡Hola! 🐾 Bienvenido..."

3. Envía: "Me recomendas algo"
   ❌ FALLA si bot dice "¡Hola de nuevo!"
   ✅ ÉXITO si bot responde sin saludar

4. Envía: 5 mensajes más
   ✅ ÉXITO si NINGUNO incluye saludo

RESULTADO ESPERADO: UN saludo al inicio, luego conversación normal
```

### Test 1.3: Memoria de Producto
```
1. Envía: "¿Qué me recomiendas para mi gato?"
   ✅ Bot: "Te recomiendo Gatsy - alimento seco..."

2. Envía: "¿Es de buena calidad?"
   ✅ ÉXITO: "Sí, Gatsy es de excelente calidad..."
   ❌ FALLA: "¿Cuál producto te interesa?" (no recuerda)

3. Envía: "¿Cuál es el precio?"
   ✅ ÉXITO: "Cuesta $100.000"
   ❌ FALLA: "¿Qué producto?" (no recuerda)

RESULTADO ESPERADO: Bot mantiene el contexto del producto "Gatsy"
```

---

## 🧪 Test Suite 2: Filtro de Seguridad v2.2.1

### Test 2.1: Pregunta Sobre Juguetes
```
1. Envía: "Recomendación de comida"
   ✅ Bot: "Te recomiendo Gatsy..."

2. Envía: "¿Tienen juguetes también?"
   ❌ FALLA: "¿Cuántas unidades?" (ignore juguetes)
   ✅ ÉXITO: "¡Claro! Tenemos juguetes..." (responde sobre juguetes)

BACKEND LOG:
   ✅ Normal: "📝 Texto: ¡Claro! Tenemos juguetes..."
   ⚠️ Fallback: "💬 Fallback contextual: ¡Claro! Tenemos juguetes..."

RESULTADO ESPERADO: Bot cambia tema a juguetes sin confusión
```

### Test 2.2: Pregunta Combinada
```
1. Envía: "de comida de gato necesito 15 unidades y quiero saber si tienes juguetes"
   
   ❌ FALLA: "¿Cuántas unidades?" (ignora juguetes)
   ✅ ÉXITO: Responde sobre AMBOS - cantidad de Gatsy Y juguetes

BACKEND LOG:
   ✅ "📝 Texto: Perfecto, 15 de Gatsy. Para juguetes tenemos..."
   
RESULTADO ESPERADO: Bot responde a ambas partes de la pregunta
```

### Test 2.3: Entrada Numérica
```
1. Envía: "¿Cuántas unidades de Gatsy tienes?"
   ✅ Bot: "Tenemos 20 unidades..."

2. Envía: "1"
   ❌ FALLA: "¿Cuántas unidades?" (repite)
   ✅ ÉXITO: "Perfecto, anotado. ¿Hay algo más?"

BACKEND LOG:
   ✅ "💬 Fallback contextual: Perfecto, anotado..."

RESULTADO ESPERADO: Bot reconoce el número como cantidad
```

### Test 2.4: Clarificación de Tema
```
1. Envía: "Necesito comida para gatos"
   ✅ Bot: "Te recomiendo Gatsy..."

2. Envía: "¿pero tenían juguetes?"
   ❌ FALLA: "¿Cuántas unidades?" (ignore la pregunta)
   ✅ ÉXITO: "¡Claro! Tenemos juguetes..." (aclara sobre juguetes)

RESULTADO ESPERADO: Bot entiende que user está pidiendo aclaración sobre otro tema
```

---

## 🧪 Test Suite 3: Conversación Completa

### Test 3.1: Flujo Típico
```
User: "Hola"
Bot: "¡Hola! 🐾 Bienvenido..."
✅ Saludo inicial

User: "Recomendación para gato adulto"
Bot: "Te recomiendo Gatsy - alimento seco con pollo y pescado. $100.000"
✅ Recomendación clara

User: "¿Es fresco?"
Bot: "Sí, tenemos buena rotación. Siempre está fresquito"
✅ Responde sobre Gatsy (recuerda)

User: "¿Stock?"
Bot: "Tenemos 20 unidades de Gatsy"
✅ Continúa hablando de Gatsy

User: "Quiero 5"
Bot: "Perfecto. Listo para 5 unidades de Gatsy"
✅ Reconoce cantidad

User: "¿Tienen juguetes?"
Bot: "¡Claro! Tenemos juguetes para gatos como ratones, pelotas"
✅ Cambia tema a juguetes

RESULTADO: Conversación fluida, sin repeticiones, contextual
```

### Test 3.2: Recuperación de Errores
```
Envía la pregunta que causaba fallo antes:
"pero hablamos de juguetes o de comida de gatos"

BACKEND LOG:
   ⚠️ Respuesta bloqueada por filtros de seguridad
   ⚠️ Intentando prompt simplificado...
   📝 Respuesta recuperada con prompt simplificado: "¡Claro! Tenemos juguetes..."
   
✅ Bot no queda atrapado
✅ Responde sobre juguetes correctamente

RESULTADO: Sistema de 3 capas funciona
```

---

## 📊 Backend Logs a Revisar

### Log Normal (Capa 1 Funciona)
```
[17/Nov/2025 16:23:12] "POST /api/usuarios/chatbot/ HTTP/1.1" 200
✅ Mensaje validado: 'pregunta del usuario'
   - Historial: N mensajes anteriores
💬 Generando respuesta conversacional...
   ⏳ Llamando API de Gemini...
   ✅ Respuesta recibida de Gemini
   📝 Texto: [respuesta del bot]
✅ Respuesta generada: Respuesta generada exitosamente
```

### Log con Fallback (Capa 2 o 3)
```
[17/Nov/2025 16:23:40] "POST /api/usuarios/chatbot/ HTTP/1.1" 200
✅ Mensaje validado: 'pregunta que causa fallo'
   - Historial: N mensajes anteriores
💬 Generando respuesta conversacional...
   ⚠️ Respuesta bloqueada por filtros de seguridad
   ⚠️ Intentando prompt simplificado...
   📝 Respuesta recuperada: [respuesta simplificada]
   O
   💬 Fallback contextual: [respuesta contextual]
✅ Respuesta generada: Respuesta alternativa (filtro seguridad)
```

---

## ✅ Criterios de Éxito

### Memoria de Conversación
- [ ] Historial se acumula con cada mensaje
- [ ] Un solo saludo en toda la sesión
- [ ] Bot recuerda productos mencionados
- [ ] Bot mantiene contexto de conversación

### Manejo de Filtro de Seguridad
- [ ] Preguntas sobre juguetes se responden sobre juguetes
- [ ] Preguntas sobre cantidad se responden sobre cantidad
- [ ] Números solos se reconocen como confirmaciones
- [ ] Cambios de tema se manejan correctamente
- [ ] Bot NUNCA queda atrapado sin respuesta

### General
- [ ] No hay crashes (500 errors)
- [ ] Todas las respuestas son en español
- [ ] Bot es natural y conversacional
- [ ] Usuario experimenta diálogo fluido

---

## 🐛 Debugging: Si Algo Falla

### Problema: Bot sigue saludando
**Verificar:**
1. `hasShownGreeting` flag en `chatbot.ts`
2. Backend logs muestran "Historial: N mensajes" (debe haber histórico)
3. Gemini recibe `history_text` en el prompt

**Solución:**
```bash
# 1. Clear cache del navegador
# 2. Reiniciar servidor Django
# 3. Verificar en console que conversation_history se envía
```

### Problema: Bot responde genérico
**Verificar:**
1. Si log dice "Respuesta bloqueada por filtros"
2. Backend está usando Capa 2 o Capa 3
3. Si el fallback es contextual o genérico

**Solución:**
```python
# En ai_service.py, revisar línea 405
# Asegurar que el fallback tiene la palabra clave correcta
if "juguete" in message.lower():  # ← Verifica esto
    return "¡Claro! Tenemos juguetes..."
```

### Problema: Historial no se acumula
**Verificar:**
1. Frontend construye `conversation_history` correctamente
2. `callChatbotAPI()` en chatbot.ts incluye el historial
3. Backend serializer acepta el campo

**Solución:**
```typescript
// En chatbot.ts, línea ~50
const conversationHistory = this.messages().map(msg => ({
    role: msg.type === 'user' ? 'user' : 'assistant',
    content: msg.text
}));
console.log('History:', conversationHistory);  // Agregar log
```

---

## 📈 Métricas a Seguimiento

Durante 10 mensajes en una sesión:
- [ ] Saludos: 1 (debe ser exactamente 1)
- [ ] Respuestas contextuales: 8-10 (debe ser la mayoría)
- [ ] Respuestas genéricas: 0-2 (debe ser mínimo)
- [ ] Fallback usado: 0-1 (debe ser raro)
- [ ] Usuarios frustrados: 0 (debe ser cero)

---

## 🚀 Test Rápido (2 minutos)

```
1. Abre chat
2. Envía: "Hola"
   ✅ Bot saluda

3. Envía: "Comida para gatos"
   ✅ Bot recomienda Gatsy

4. Envía: "¿Tienen juguetes?"
   ✅ Bot habla de juguetes (NO pregunta cantidad)

5. Envía: "5 juguetes"
   ✅ Bot reconoce la cantidad

Si TODO está ✅: Sistema funciona correctamente
```

---

## 📞 Contacto para Issues

Si algo no funciona como se describe:
1. Revisar CHATBOT_SAFETY_FILTER_V2.2.1.md
2. Revisar logs en Backend/console
3. Comparar con RESUMEN_FINAL_CHATBOT_V2.2.1.md
4. Verificar archivo ai_service.py líneas 315-427

---

**Happy Testing! 🎉**
