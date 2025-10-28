# Documentación UML del Sistema SADAT

Este directorio contiene toda la documentación UML (Unified Modeling Language) del Sistema de Apoyo al Desarrollo de Artesanos Textiles (SADAT).

## 📋 Contenido

### Metodología y Guías
- **METODOLOGIA_CREACION_UML.md**: Guía completa de 6 fases para crear diagramas UML
- **EJEMPLOS_DETALLADOS.md**: 4 ejemplos detallados basados en el proyecto de referencia

### Diagramas UML

#### 1️⃣ Diagramas de Casos de Uso (Use Cases)
Muestran las funcionalidades del sistema y los actores que interactúan con ellas.

- `01_casos_uso_autenticacion.puml` - Autenticación y gestión de usuarios (13 casos de uso)
- `02_casos_uso_productos.puml` - Gestión de productos y catálogo (18 casos de uso)
- `03_casos_uso_pedidos.puml` - Carrito, pedidos y pagos (24 casos de uso)

**Total**: 55 casos de uso documentados

#### 2️⃣ Diagramas de Secuencia (Sequence)
Muestran la interacción temporal entre objetos en procesos específicos.

- `04_secuencia_login.puml` - Proceso de inicio de sesión (22 pasos detallados)
- `05_secuencia_registro.puml` - Proceso de registro por tipo de usuario (33 pasos)

**Características**:
- Numeración secuencial de cada paso
- División en fases lógicas del proceso
- Notas explicativas de validaciones y reglas de negocio
- Manejo de flujos alternativos (éxito/error)

#### 3️⃣ Diagramas de Actividad (Activity)
Muestran el flujo de trabajo completo de procesos de negocio.

- `06_actividad_proceso_pedido.puml` - Flujo completo desde selección hasta entrega
- `07_actividad_gestion_productos.puml` - Gestión CRUD de productos por empresa

**Características**:
- Separación por swim lanes (actores)
- Decisiones y flujos condicionales
- Notas con reglas de negocio
- Manejo de excepciones

#### 4️⃣ Diagramas de Clases (Class)
Muestran la estructura de datos y relaciones entre modelos.

- `08_clases_core.puml` - Módulo Core (Usuario, Configuración, Forms)
- `09_clases_empresas.puml` - Módulo Empresas (Productos, Servicios, Maquinaria)
- `10_clases_pedidos.puml` - Módulo Pedidos (Carrito, Pedidos, Solicitudes)
- `11_clases_pagos.puml` - Módulo Pagos (Transacciones, Stripe, Webhooks)

**Características**:
- Atributos con tipos de datos Django
- Métodos principales de cada clase
- Relaciones (OneToOne, ForeignKey, ManyToMany)
- Enums para estados y opciones
- Notas explicativas de lógica de negocio
- Restricciones y validaciones

## 🎯 Propósito

Esta documentación tiene como objetivo:

1. **Facilitar el entendimiento** del sistema para nuevos desarrolladores
2. **Documentar los flujos** críticos del negocio
3. **Servir como referencia** para mantenimiento y nuevas funcionalidades
4. **Estandarizar** el proceso de creación de diagramas UML
5. **Visualizar la arquitectura** del sistema completo

## 🔧 Cómo Visualizar los Diagramas

### Opción 1: Visual Studio Code (Recomendado)
1. Instalar la extensión "PlantUML" de jebbs
2. Instalar Java (requerido por PlantUML):
   ```bash
   # Windows (con Chocolatey)
   choco install openjdk

   # macOS
   brew install openjdk

   # Linux
   sudo apt-get install default-jre
   ```
3. Abrir cualquier archivo `.puml`
4. Presionar `Alt+D` para ver la vista previa en tiempo real

### Opción 2: PlantUML Web Server
1. Ir a http://www.plantuml.com/plantuml/uml/
2. Copiar el contenido del archivo `.puml`
3. Pegar en el editor web
4. Ver renderizado instantáneo

### Opción 3: Línea de Comandos
```bash
# Instalar PlantUML
sudo apt-get install plantuml  # Linux
brew install plantuml          # macOS
choco install plantuml         # Windows

# Generar imagen PNG
plantuml archivo.puml

# Generar SVG (escalable, recomendado)
plantuml -tsvg archivo.puml

# Generar todos los diagramas
plantuml *.puml

# Generar con directorio de salida
plantuml -o ./output *.puml
```

### Opción 4: Extensiones de Navegador
- **Chrome/Edge**: PlantUML Viewer
- **Firefox**: PlantUML Viewer

## 📖 Guía de Lectura

### Para Nuevos Desarrolladores
1. **Inicio**: Leer `METODOLOGIA_CREACION_UML.md` para entender el proceso de creación
2. **Ejemplos**: Revisar `EJEMPLOS_DETALLADOS.md` para ver patrones aplicados
3. **Casos de Uso**: Estudiar los 3 diagramas de casos de uso para conocer todas las funcionalidades
4. **Secuencia**: Revisar diagramas de secuencia de Login y Registro (flujos críticos)
5. **Actividad**: Entender el flujo completo de un pedido
6. **Clases**: Estudiar la estructura de datos de cada módulo

### Para Añadir Nuevas Funcionalidades
1. Consultar `METODOLOGIA_CREACION_UML.md` - Fase 1 (Análisis)
2. Actualizar o crear nuevos casos de uso en el diagrama correspondiente
3. Crear diagrama de secuencia del nuevo flujo
4. Actualizar diagramas de clases si hay nuevos modelos o relaciones
5. Crear diagrama de actividad si el proceso es complejo

### Para Mantenimiento y Debugging
1. Revisar diagramas de secuencia para entender el flujo exacto
2. Consultar diagramas de clases para ver relaciones entre modelos
3. Verificar en diagramas de actividad las validaciones y reglas de negocio

## 🏗️ Estructura del Sistema SADAT

### Módulos Principales

```
SADAT/
├── core/               → Usuario, Autenticación, Configuración
├── empresas/           → Empresas Integrales/Satélites, Productos, Servicios
├── pedidos/            → Carrito, Pedidos, Solicitudes de Confección
├── pagos/              → Transacciones, Integración con Stripe
├── notificaciones/     → Sistema de notificaciones
└── reportes/           → Estadísticas y reportes
```

### Tipos de Usuario

- **Cliente**: Compra productos, solicita servicios
- **Microempresa Integral**: Fabrica y vende productos terminados
- **Microempresa Satélite**: Ofrece servicios de confección y arrienda maquinaria
- **Super Usuario**: Administrador del sistema, acceso total

### Flujos Principales Documentados

1. **Autenticación**: Login, Registro, Recuperación de contraseña
2. **Productos**: CRUD de productos, gestión de stock, catálogo público
3. **Pedidos**: Carrito → Checkout → Pago → Envío → Entrega
4. **Pagos**: Integración completa con Stripe (PaymentIntents, Webhooks)
5. **Servicios**: Solicitudes de confección a empresas satélites

## 📝 Convenciones Utilizadas

### En Diagramas de Casos de Uso
- **Actores**: Representados con stickman, etiquetados claramente
- **Paquetes**: Agrupan casos de uso relacionados
- **Include**: Funcionalidad obligatoria (línea punteada con flecha)
- **Extend**: Funcionalidad opcional (línea punteada con flecha)
- **Notas**: Explican validaciones, reglas, detalles técnicos
- **Numeración**: UC01, UC02... para identificar casos de uso

### En Diagramas de Secuencia
- **Numeración de pasos**: 1, 2, 3... para seguir el flujo cronológico
- **Fases**: Separadores `== Fase N: Descripción ==`
- **Activación**: Barras verticales muestran cuando un objeto está activo
- **Alt/Loop**: Bloques para flujos condicionales y repetitivos
- **Notas**: Detalles de validaciones, formatos, seguridad

### En Diagramas de Actividad
- **Swim Lanes**: Columnas verticales por actor (Cliente, Sistema, Empresa)
- **Decisiones**: Rombos con condiciones
- **Particiones**: Agrupan actividades relacionadas
- **Notas**: Reglas de negocio, cálculos, validaciones
- **Puntos de inicio/fin**: start/stop

### En Diagramas de Clases
- **Visibilidad**: `+` público, `-` privado, `#` protegido
- **Tipos de datos**: Django field types (CharField, ForeignKey, etc.)
- **Relaciones**: Cardinalidad claramente marcada (1, 0..1, 0..*, 1..*)
- **Enums**: Separados como clases especiales
- **Paquetes**: Agrupan clases del mismo módulo Django
- **<<external>>**: Marca clases de otros módulos

## 🔄 Mantenimiento

### Los diagramas DEBEN actualizarse cuando:
- ✅ Se añaden nuevos modelos al sistema
- ✅ Cambian flujos de negocio existentes
- ✅ Se agregan nuevas funcionalidades
- ✅ Se modifican relaciones entre entidades
- ✅ Cambian estados de pedidos/transacciones
- ✅ Se integran nuevos servicios externos

### Proceso de Actualización:
1. Identificar el tipo de cambio
2. Localizar el/los diagrama(s) afectado(s)
3. Actualizar el archivo `.puml` correspondiente
4. Verificar que el diagrama renderiza correctamente
5. Actualizar fecha en este README
6. Commit con mensaje descriptivo: `docs(uml): actualizar [nombre_diagrama] - [motivo]`

## 📊 Estadísticas de Documentación

| Tipo de Diagrama | Cantidad | Pasos/Elementos | Última Actualización |
|------------------|----------|-----------------|----------------------|
| Casos de Uso     | 3        | 55 casos        | 2024-01-15          |
| Secuencia        | 2        | 55 pasos        | 2024-01-15          |
| Actividad        | 2        | 2 procesos      | 2024-01-15          |
| Clases           | 4        | 20+ clases      | 2024-01-15          |
| **TOTAL**        | **11**   | **130+ elementos** | **2024-01-15**   |

## 🛠️ Herramientas Recomendadas

- **Editor**: Visual Studio Code con extensión PlantUML
- **Versión de Control**: Git (los archivos .puml son texto plano)
- **Visualización**: PlantUML Server (http://www.plantuml.com/)
- **Exportación**: SVG para documentación, PNG para presentaciones
- **Validación**: PlantUML CLI para verificar sintaxis

## 📚 Recursos Adicionales

- [PlantUML Official Documentation](https://plantuml.com/)
- [PlantUML Cheat Sheet](https://ogom.github.io/draw_uml/plantuml/)
- [UML Best Practices](https://www.uml-diagrams.org/)
- [Django Model Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)

## 🤝 Contribuciones

Al añadir o modificar diagramas, por favor:
1. Seguir las convenciones establecidas en `METODOLOGIA_CREACION_UML.md`
2. Usar nombres descriptivos y consistentes
3. Incluir notas explicativas para lógica compleja
4. Numerar pasos en diagramas de secuencia
5. Documentar todas las relaciones en diagramas de clases
6. Actualizar este README con cambios significativos

---

**Última actualización**: Enero 2024  
**Herramienta**: PlantUML 1.2024.x  
**Formato**: .puml (texto plano)  
**Mantenedor**: Equipo de Desarrollo SADAT  
**Licencia**: Documentación del proyecto SADAT
