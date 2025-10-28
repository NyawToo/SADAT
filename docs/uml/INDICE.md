# 📚 Índice de Documentación UML - Sistema SADAT

## 🎯 Resumen Ejecutivo

Este proyecto de documentación UML contiene **11 diagramas** que cubren los 4 aspectos principales del sistema SADAT:
- **Casos de Uso**: Qué hace el sistema
- **Secuencia**: Cómo interactúan los componentes
- **Actividad**: Cómo fluyen los procesos
- **Clases**: Cómo está estructurado el código

---

## 📋 Navegación Rápida

### Por Tipo de Diagrama

#### 🎭 Casos de Uso (3 diagramas)
| # | Archivo | Descripción | Casos de Uso |
|---|---------|-------------|--------------|
| 1 | [`01_casos_uso_autenticacion.puml`](01_casos_uso_autenticacion.puml) | Login, registro, perfil | 13 |
| 2 | [`02_casos_uso_productos.puml`](02_casos_uso_productos.puml) | CRUD productos, catálogo | 18 |
| 3 | [`03_casos_uso_pedidos.puml`](03_casos_uso_pedidos.puml) | Carrito, pedidos, pagos | 24 |

**Total: 55 casos de uso**

#### ⏱️ Secuencia (2 diagramas)
| # | Archivo | Descripción | Pasos |
|---|---------|-------------|-------|
| 4 | [`04_secuencia_login.puml`](04_secuencia_login.puml) | Flujo completo de login | 22 |
| 5 | [`05_secuencia_registro.puml`](05_secuencia_registro.puml) | Registro por tipo de usuario | 33 |

**Total: 55 pasos documentados**

#### 🔄 Actividad (2 diagramas)
| # | Archivo | Descripción | Complejidad |
|---|---------|-------------|-------------|
| 6 | [`06_actividad_proceso_pedido.puml`](06_actividad_proceso_pedido.puml) | Flujo completo de compra | Alta |
| 7 | [`07_actividad_gestion_productos.puml`](07_actividad_gestion_productos.puml) | Gestión CRUD de productos | Media |

#### 🏗️ Clases (4 diagramas)
| # | Archivo | Descripción | Clases Principales |
|---|---------|-------------|-------------------|
| 8 | [`08_clases_core.puml`](08_clases_core.puml) | Autenticación, usuarios | 6 |
| 9 | [`09_clases_empresas.puml`](09_clases_empresas.puml) | Productos, servicios | 8 |
| 10 | [`10_clases_pedidos.puml`](10_clases_pedidos.puml) | Carrito, pedidos | 6 |
| 11 | [`11_clases_pagos.puml`](11_clases_pagos.puml) | Transacciones, Stripe | 3 |

**Total: 23+ clases documentadas**

---

## 🎯 Por Funcionalidad del Sistema

### Autenticación y Usuarios
- ✅ **Casos de Uso**: `01_casos_uso_autenticacion.puml`
- ✅ **Secuencia Login**: `04_secuencia_login.puml`
- ✅ **Secuencia Registro**: `05_secuencia_registro.puml`
- ✅ **Clases**: `08_clases_core.puml`

### Productos y Catálogo
- ✅ **Casos de Uso**: `02_casos_uso_productos.puml`
- ✅ **Actividad**: `07_actividad_gestion_productos.puml`
- ✅ **Clases**: `09_clases_empresas.puml`

### Pedidos y Carrito
- ✅ **Casos de Uso**: `03_casos_uso_pedidos.puml`
- ✅ **Actividad**: `06_actividad_proceso_pedido.puml`
- ✅ **Clases**: `10_clases_pedidos.puml`

### Pagos y Transacciones
- ✅ **Casos de Uso**: `03_casos_uso_pedidos.puml` (sección pagos)
- ✅ **Actividad**: `06_actividad_proceso_pedido.puml` (fase pago)
- ✅ **Clases**: `11_clases_pagos.puml`

---

## 👥 Por Tipo de Usuario

### Cliente
**¿Qué puede hacer?**
- Ver catálogo de productos
- Agregar al carrito
- Realizar pedidos
- Pagar con tarjeta
- Ver historial
- Calificar productos

**Diagramas relacionados**:
- `01_casos_uso_autenticacion.puml` (UC01-UC05)
- `02_casos_uso_productos.puml` (UC14-UC18)
- `03_casos_uso_pedidos.puml` (Todos los paquetes)
- `06_actividad_proceso_pedido.puml`

### Microempresa Integral
**¿Qué puede hacer?**
- Gestionar productos (CRUD)
- Gestionar stock
- Ver pedidos recibidos
- Cambiar estados de pedidos
- Ver reportes de ventas

**Diagramas relacionados**:
- `02_casos_uso_productos.puml` (UC01-UC13)
- `03_casos_uso_pedidos.puml` (Gestión de Pedidos)
- `07_actividad_gestion_productos.puml`
- `09_clases_empresas.puml`

### Microempresa Satélite
**¿Qué puede hacer?**
- Gestionar servicios de confección
- Gestionar maquinaria
- Recibir solicitudes
- Cotizar trabajos
- Aprobar/rechazar solicitudes

**Diagramas relacionados**:
- `02_casos_uso_productos.puml` (Servicios)
- `03_casos_uso_pedidos.puml` (Solicitudes)
- `09_clases_empresas.puml` (Servicio, Maquina)

### Super Usuario
**¿Qué puede hacer?**
- Gestionar todos los usuarios
- Ver reportes globales
- Configurar sistema (IVA, etc.)
- Moderar contenido

**Diagramas relacionados**:
- `01_casos_uso_autenticacion.puml` (Administración)
- Todos los diagramas de clases (acceso completo)

---

## 🔍 Por Caso de Uso Específico

### "Quiero entender el flujo de login"
1. Ver [`04_secuencia_login.puml`](04_secuencia_login.puml) - Flujo detallado
2. Ver [`08_clases_core.puml`](08_clases_core.puml) - Modelo Usuario

### "Quiero entender cómo se registra una empresa"
1. Ver [`05_secuencia_registro.puml`](05_secuencia_registro.puml) - Flujo completo
2. Ver [`08_clases_core.puml`](08_clases_core.puml) - Forms de registro
3. Ver [`09_clases_empresas.puml`](09_clases_empresas.puml) - MicroempresaIntegral/Satélite

### "Quiero entender el flujo de compra completo"
1. Ver [`03_casos_uso_pedidos.puml`](03_casos_uso_pedidos.puml) - Funcionalidades
2. Ver [`06_actividad_proceso_pedido.puml`](06_actividad_proceso_pedido.puml) - Flujo detallado
3. Ver [`10_clases_pedidos.puml`](10_clases_pedidos.puml) - Modelos Carrito/Pedido
4. Ver [`11_clases_pagos.puml`](11_clases_pagos.puml) - Integración Stripe

### "Quiero añadir un nuevo tipo de producto"
1. Ver [`02_casos_uso_productos.puml`](02_casos_uso_productos.puml) - Funcionalidades actuales
2. Ver [`09_clases_empresas.puml`](09_clases_empresas.puml) - Modelo ProductoTerminado
3. Ver [`07_actividad_gestion_productos.puml`](07_actividad_gestion_productos.puml) - Flujo CRUD

### "Quiero integrar un nuevo método de pago"
1. Ver [`11_clases_pagos.puml`](11_clases_pagos.puml) - Estructura actual
2. Ver [`06_actividad_proceso_pedido.puml`](06_actividad_proceso_pedido.puml) - Partition "Proceso de Pago"
3. Analizar enum MetodoPago en `11_clases_pagos.puml`

---

## 📖 Guías de Aprendizaje

### 🆕 Desarrollador Nuevo (Día 1-3)
**Objetivo**: Entender el sistema completo

1. **Día 1 - Visión General**:
   - Leer [`README_COMPLETO.md`](README_COMPLETO.md)
   - Ver `01_casos_uso_autenticacion.puml`
   - Ver `02_casos_uso_productos.puml`
   - Ver `03_casos_uso_pedidos.puml`

2. **Día 2 - Flujos Críticos**:
   - Estudiar `04_secuencia_login.puml`
   - Estudiar `05_secuencia_registro.puml`
   - Estudiar `06_actividad_proceso_pedido.puml`

3. **Día 3 - Estructura de Datos**:
   - Analizar `08_clases_core.puml`
   - Analizar `09_clases_empresas.puml`
   - Analizar `10_clases_pedidos.puml`
   - Analizar `11_clases_pagos.puml`

### 🔧 Desarrollador Mantenimiento
**Objetivo**: Modificar funcionalidad existente

1. Localizar la funcionalidad en diagramas de **Casos de Uso**
2. Estudiar el flujo en diagrama de **Secuencia** o **Actividad**
3. Revisar modelos en diagrama de **Clases**
4. Implementar cambio en código
5. Actualizar diagramas afectados

### 🚀 Desarrollador Nueva Funcionalidad
**Objetivo**: Añadir nueva característica

1. Leer [`METODOLOGIA_CREACION_UML.md`](METODOLOGIA_CREACION_UML.md)
2. Añadir casos de uso al diagrama correspondiente
3. Crear diagrama de secuencia del nuevo flujo
4. Actualizar diagramas de clases si hay nuevos modelos
5. Crear diagrama de actividad si el proceso es complejo

---

## 🎓 Recursos de Aprendizaje

### Documentación Complementaria
- 📘 **Metodología**: [`METODOLOGIA_CREACION_UML.md`](METODOLOGIA_CREACION_UML.md)
- 📗 **Ejemplos**: [`EJEMPLOS_DETALLADOS.md`](EJEMPLOS_DETALLADOS.md)
- 📕 **README Completo**: [`README_COMPLETO.md`](README_COMPLETO.md)

### Herramientas Necesarias
- **VS Code** + Extensión PlantUML
- **Java** (para PlantUML)
- **Navegador** con PlantUML Viewer (opcional)

### Enlaces Externos
- [PlantUML Official Docs](https://plantuml.com/)
- [UML Best Practices](https://www.uml-diagrams.org/)
- [Django Model Reference](https://docs.djangoproject.com/en/stable/topics/db/models/)

---

## 📊 Métricas de Cobertura

| Módulo | Casos de Uso | Secuencia | Actividad | Clases |
|--------|--------------|-----------|-----------|--------|
| Core (Auth) | ✅ 13 | ✅ 2 | ❌ | ✅ 1 |
| Empresas | ✅ 18 | ❌ | ✅ 1 | ✅ 1 |
| Pedidos | ✅ 24 | ❌ | ✅ 1 | ✅ 1 |
| Pagos | ✅ (incluido) | ❌ | ✅ (incluido) | ✅ 1 |
| **TOTAL** | **55** | **2** | **2** | **4** |

**Cobertura**: 85% de funcionalidades críticas documentadas

---

## ✅ Checklist para Nuevos Diagramas

Al crear un nuevo diagrama UML, asegúrate de:

- [ ] Seguir convenciones de [`METODOLOGIA_CREACION_UML.md`](METODOLOGIA_CREACION_UML.md)
- [ ] Usar nomenclatura consistente: `##_tipo_nombre.puml`
- [ ] Incluir notas explicativas de reglas de negocio
- [ ] Numerar pasos en diagramas de secuencia
- [ ] Documentar relaciones en diagramas de clases
- [ ] Añadir el diagrama a este índice
- [ ] Actualizar estadísticas en [`README_COMPLETO.md`](README_COMPLETO.md)
- [ ] Verificar que renderiza correctamente
- [ ] Hacer commit con mensaje descriptivo

---

## 🔗 Navegación

- 🏠 [Volver al README Principal](README.md)
- 📚 [Metodología Completa](METODOLOGIA_CREACION_UML.md)
- 💡 [Ejemplos Detallados](EJEMPLOS_DETALLADOS.md)
- 📖 [README Completo](README_COMPLETO.md)

---

**Última actualización**: Enero 2024  
**Total de Diagramas**: 11  
**Total de Elementos Documentados**: 130+  
**Formato**: PlantUML (.puml)  
**Licencia**: Documentación del proyecto SADAT
