# Documentación UML - Sistema SADAT

Este directorio contiene los diagramas UML del Sistema SADAT (Sistema de Apoyo al Desarrollo de Artesanos Textiles).

## 📋 Índice de Diagramas

### 1. Diagramas de Secuencia
- **01_diagrama_secuencia_login.puml** - Proceso de autenticación de usuarios
- **04_diagrama_secuencia_registro.puml** - Proceso de registro de nuevos usuarios
- **11_diagrama_secuencia_pago.puml** - Proceso de pago con integración Stripe

### 2. Diagramas de Clases
- **02_diagrama_clases_core.puml** - Módulo principal (usuarios y configuración)
- **03_diagrama_clases_empresas.puml** - Módulo de empresas, productos y servicios
- **09_diagrama_clases_pedidos.puml** - Módulo de pedidos y carrito de compras
- **10_diagrama_clases_pagos.puml** - Módulo de pagos y transacciones

### 3. Diagramas de Casos de Uso
- **05_diagrama_casos_uso.puml** - Funcionalidades del sistema por tipo de usuario

### 4. Diagramas de Actividades
- **06_diagrama_actividades_pedido.puml** - Flujo del proceso de realizar un pedido

### 5. Diagramas de Estados
- **12_diagrama_estados_pedido.puml** - Ciclo de vida de un pedido estándar
- **13_diagrama_estados_pedido_personalizado.puml** - Ciclo de vida de un pedido personalizado
- **14_diagrama_estados_transaccion.puml** - Ciclo de vida de una transacción de pago

### 6. Diagramas de Arquitectura
- **07_diagrama_componentes.puml** - Arquitectura de componentes del sistema
- **08_diagrama_despliegue.puml** - Infraestructura de despliegue

### 7. Modelo de Datos
- **15_modelo_entidad_relacion.puml** - Modelo Entidad-Relación completo de la base de datos

## 🚀 Cómo Visualizar los Diagramas

### Opción 1: PlantUML en VS Code
1. Instala la extensión "PlantUML" en VS Code
2. Abre cualquier archivo `.puml`
3. Presiona `Alt + D` para ver la vista previa

### Opción 2: PlantUML Online
1. Visita [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
2. Copia y pega el contenido del archivo `.puml`
3. Visualiza el diagrama generado

### Opción 3: Instalación Local de PlantUML
```bash
# Instalar Java (requerido)
# Descargar plantuml.jar

# Generar imagen PNG
java -jar plantuml.jar diagrama.puml

# Generar imagen SVG
java -jar plantuml.jar -tsvg diagrama.puml
```

## 📊 Descripción de los Diagramas

### Diagrama de Secuencia - Login
Muestra el flujo de interacción entre el usuario, la vista, el controlador, el modelo y la base de datos durante el proceso de inicio de sesión. Incluye validación de credenciales y redirección según el tipo de usuario.

### Diagrama de Secuencia - Registro
Detalla el proceso de registro de usuarios, incluyendo validación de formularios, creación de usuarios y, en caso de empresas, la creación del perfil empresarial asociado.

### Diagrama de Clases - Core
Representa las clases principales del sistema: Usuario y ConfiguracionSistema, incluyendo sus atributos, métodos y relaciones.

### Diagrama de Clases - Empresas
Muestra la estructura de clases para microempresas (integral y satélite), productos, servicios, maquinaria y sus relaciones.

### Diagrama de Casos de Uso
Ilustra las funcionalidades disponibles para cada tipo de actor del sistema:
- Cliente
- Microempresa Integral
- Microempresa Satélite
- Super Usuario

### Diagrama de Actividades - Pedido
Representa el flujo completo del proceso de realizar un pedido, desde la selección de productos hasta la confirmación del pago.

### Diagrama de Clases - Pedidos
Representa el módulo de gestión de pedidos, incluyendo carrito de compras, pedidos estándar, pedidos personalizados y solicitudes de confección.

### Diagrama de Clases - Pagos
Muestra el sistema de transacciones y la integración con Stripe para procesamiento de pagos.

### Diagrama de Secuencia - Pago
Detalla el flujo completo de procesamiento de pagos con Stripe, incluyendo la creación de Payment Intent, confirmación de pago y actualización de estados.

### Diagrama de Estados - Pedido
Representa el ciclo de vida completo de un pedido estándar desde su creación hasta su entrega o cancelación.

### Diagrama de Estados - Pedido Personalizado
Muestra los estados por los que pasa un pedido personalizado, incluyendo cotización y aceptación.

### Diagrama de Estados - Transacción
Ilustra los diferentes estados de una transacción de pago y sus transiciones.

### Modelo Entidad-Relación
Diagrama completo de la base de datos mostrando todas las entidades, atributos y relaciones del sistema SADAT.

## 🎯 Tipos de Usuarios del Sistema

1. **Cliente** - Usuario final que compra productos
2. **Microempresa Integral** - Produce y vende productos terminados
3. **Microempresa Satélite** - Ofrece servicios de confección
4. **Super Usuario** - Administrador del sistema

## 🔧 Módulos Principales

- **Core** - Autenticación y gestión de usuarios
- **Empresas** - Gestión de microempresas, productos y servicios
- **Pedidos** - Carrito de compras y gestión de pedidos
- **Pagos** - Procesamiento de pagos con Stripe
- **Reportes** - Generación y exportación de reportes
- **Notificaciones** - Sistema de notificaciones

## 📝 Notas

- Todos los diagramas están en formato PlantUML (.puml)
- Los diagramas se pueden exportar a PNG, SVG o PDF
- Se recomienda mantener los diagramas actualizados cuando se realicen cambios en el sistema

## 🔄 Actualización de Diagramas

Al modificar la estructura del sistema:
1. Actualiza los archivos `.puml` correspondientes
2. Regenera las imágenes si es necesario
3. Actualiza este README si se agregan nuevos diagramas

---

**Sistema SADAT** - Documentación UML  
*Última actualización: Octubre 2025*
