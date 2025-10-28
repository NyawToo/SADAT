# Ejemplos Prácticos Detallados - Creación de Diagramas UML

## 📌 Basado en Proyecto de Referencia (.vpd files)

Este documento muestra **ejemplos completos paso a paso** de cómo crear cada tipo de diagrama UML, siguiendo la metodología del proyecto de referencia.

---

## 🎯 EJEMPLO 1: Diagrama de Casos de Uso - Registro y Login

### Análisis del Archivo de Referencia: "Caso de uso registro y login.vpd"

#### Paso 1: Identificar Actores

```
Actor Principal: Usuario No Registrado
Actor Secundario: Usuario Registrado
Actor del Sistema: Sistema de Email
```

#### Paso 2: Identificar Casos de Uso

**Funcionalidades de Registro:**
- UC01: Registrarse como Cliente
- UC02: Registrarse como Empresa Integral
- UC03: Registrarse como Empresa Satélite
- UC04: Validar Datos de Registro
- UC05: Enviar Email de Confirmación

**Funcionalidades de Login:**
- UC06: Iniciar Sesión
- UC07: Validar Credenciales
- UC08: Crear Sesión
- UC09: Cerrar Sesión
- UC10: Recuperar Contraseña

#### Paso 3: Definir Relaciones

```
Usuario No Registrado --> UC01 (Asociación)
Usuario No Registrado --> UC02 (Asociación)
Usuario No Registrado --> UC03 (Asociación)

UC01 ..> UC04 <<include>> (Todos requieren validación)
UC02 ..> UC04 <<include>>
UC03 ..> UC04 <<include>>

UC01 ..> UC05 <<include>> (Enviar confirmación)
UC02 ..> UC05 <<include>>
UC03 ..> UC05 <<include>>

Usuario Registrado --> UC06 (Asociación)
UC06 ..> UC07 <<include>> (Login requiere validación)
UC07 ..> UC08 <<include>> (Validación crea sesión)

Usuario Registrado --> UC09 (Asociación)
Usuario Registrado --> UC10 (Asociación)
```

#### Paso 4: Código PlantUML Completo

```plantuml
@startuml Caso de Uso - Registro y Login
title Sistema SADAT - Registro y Autenticación

left to right direction
skinparam packageStyle rectangle

actor "Usuario\nNo Registrado" as NoReg
actor "Usuario\nRegistrado" as Reg
actor "Sistema\nEmail" as Email

rectangle "Sistema SADAT" {
  
  package "Módulo de Registro" {
    usecase "Registrarse\ncomo Cliente" as UC01
    usecase "Registrarse como\nEmpresa Integral" as UC02
    usecase "Registrarse como\nEmpresa Satélite" as UC03
    usecase "Validar Datos\nde Registro" as UC04
    usecase "Enviar Email\nde Confirmación" as UC05
  }
  
  package "Módulo de Autenticación" {
    usecase "Iniciar Sesión" as UC06
    usecase "Validar\nCredenciales" as UC07
    usecase "Crear Sesión\nde Usuario" as UC08
    usecase "Cerrar Sesión" as UC09
    usecase "Recuperar\nContraseña" as UC10
  }
}

' Relaciones de Registro
NoReg --> UC01
NoReg --> UC02
NoReg --> UC03

UC01 ..> UC04 : <<include>>
UC02 ..> UC04 : <<include>>
UC03 ..> UC04 : <<include>>

UC01 ..> UC05 : <<include>>
UC02 ..> UC05 : <<include>>
UC03 ..> UC05 : <<include>>

UC05 --> Email : envía

' Relaciones de Login
Reg --> UC06
Reg --> UC09
Reg --> UC10

UC06 ..> UC07 : <<include>>
UC07 ..> UC08 : <<include>>

note right of UC04
  Valida:
  - Email único
  - Username único
  - RUT válido (empresas)
  - Contraseña segura
end note

note right of UC08
  Crea sesión Django
  y determina redirección
  según tipo de usuario
end note

@enduml
```

---

## 🔄 EJEMPLO 2: Diagrama de Secuencia - Proceso de Login

### Análisis del Archivo de Referencia: "Caso de uso login.vpd"

Este es el diagrama que coincide con la imagen de referencia proporcionada.

#### Paso 1: Listar Participantes (en orden de aparición)

```
1. Usuario (Actor)
2. Vista Login (Boundary)
3. Controlador login_view (Control)
4. Modelo Usuario (Entity)
5. Base de Datos (Database)
```

#### Paso 2: Definir Flujo Principal

**Secuencia de Mensajes:**

```
1.  Usuario → Vista: Solicitar Login
2.  Vista → Usuario: Mostrar Formulario Login
3.  Usuario → Vista: Llenar Formulario (username, password)
4.  Vista → Controlador: Solicitar Validar Datos
5.  Controlador → Controlador: Verificar campos no vacíos
6.  Controlador → Modelo: authenticate(username, password)
7.  Modelo → Base de Datos: Consultar Datos De Acceso
8.  Base de Datos → Modelo: Datos De Acceso
9.  Modelo → Modelo: Verificar hash de contraseña
10. Modelo → Controlador: Usuario autenticado o None
```

#### Paso 3: Definir Flujos Alternativos

**Alt: Datos Válidos**
```
11. Controlador → Modelo: login(request, user)
12. Modelo → Base de Datos: Crear sesión
13. Base de Datos → Modelo: Sesión creada
14. Modelo → Controlador: Usuario logueado
15. Controlador → Controlador: Determinar página según rol
16. Controlador → Vista: Redirigir a Página Principal
17. Vista → Usuario: Mostrar Página Principal
```

**Alt: Datos Inválidos**
```
11. Controlador → Vista: Datos Incorrectos (mensaje error)
12. Vista → Usuario: Mostrar Formulario Login con error
```

#### Paso 4: Código PlantUML Completo

```plantuml
@startuml Diagrama de Secuencia - Login
title Sistema SADAT - Proceso de Login (Detallado)

actor Usuario
participant "Vista\nLogin" as Vista
participant "Controlador\n(login_view)" as Controlador
participant "Modelo\nUsuario" as Modelo
database "Base de\nDatos" as BD

' === FASE 1: Solicitar Formulario ===
Usuario -> Vista: 1. Solicitar Login
activate Vista
Vista --> Usuario: 2. Mostrar Formulario\nLogin
deactivate Vista

note over Usuario, Vista
  Usuario accede a /login/
  Vista renderiza template login.html
end note

' === FASE 2: Enviar Credenciales ===
Usuario -> Vista: 6. Llenar Formulario\nLogin (username, password)
activate Vista

Vista -> Controlador: 7. Solicitar Validar Datos\n(username, password)
activate Controlador

note over Controlador
  POST request con:
  - username
  - password
end note

Controlador -> Controlador: Verificar campos\nno vacíos

' === FASE 3: Autenticación ===
Controlador -> Modelo: 8. authenticate(\nusername, password)
activate Modelo

Modelo -> BD: 9. Consultar Datos\nDe Acceso\nSELECT * FROM core_usuario\nWHERE username = ?
activate BD

BD --> Modelo: 10. Datos De Acceso
deactivate BD

Modelo -> Modelo: Verificar hash\nde contraseña

Modelo --> Controlador: 11. Usuario autenticado\no None
deactivate Modelo

' === FASE 4: Decisión ===
alt Datos Válidos
    
    note over Controlador
      Usuario encontrado
      y password correcto
    end note
    
    Controlador -> Modelo: 12. login(request, user)
    activate Modelo
    
    Modelo -> BD: Crear sesión\nINSERT INTO django_session
    activate BD
    BD --> Modelo: Sesión creada
    deactivate BD
    
    Modelo --> Controlador: Usuario logueado
    deactivate Modelo
    
    Controlador -> Controlador: Determinar página\nsegún user.tipo
    
    note over Controlador
      Redirección según tipo:
      - integral → gestionar_productos
      - satelite → gestionar_solicitudes
      - cliente → catalogo_empresas
      - superusuario → reporte_global
    end note
    
    Controlador --> Vista: 13. Redirigir a Página\nPrincipal (redirect)
    deactivate Controlador
    
    Vista --> Usuario: 14. Mostrar Página\nPrincipal (dashboard)
    deactivate Vista
    
else Datos Inválidos
    
    note over Controlador
      Usuario no encontrado
      o password incorrecto
    end note
    
    Controlador --> Vista: 12. Datos Incorrectos\n(mensaje de error)
    deactivate Controlador
    
    Vista --> Usuario: 14. Mostrar Formulario\nLogin con error
    deactivate Vista
    
end

note over Usuario, BD
  El proceso completo incluye:
  1. Solicitud de formulario
  2. Validación de datos
  3. Autenticación con BD
  4. Creación de sesión
  5. Redirección según rol
end note

@enduml
```

---

## 📊 EJEMPLO 3: Diagrama de Casos de Uso - Gestión de Productos

### Análisis del Archivo de Referencia: "Caso de uso Gestio de productos.vpd"

#### Paso 1: Identificar Actores

```
Actor Principal: Microempresa Integral
Actor Secundario: Cliente (para visualización)
Actor del Sistema: Sistema de Notificaciones
```

#### Paso 2: Identificar Casos de Uso

**CRUD de Productos:**
- UC01: Crear Producto
- UC02: Editar Producto
- UC03: Eliminar Producto
- UC04: Listar Productos
- UC05: Ver Detalle Producto

**Gestión de Stock:**
- UC06: Actualizar Stock
- UC07: Verificar Stock Disponible
- UC08: Alertar Stock Bajo

**Gestión de Categorías:**
- UC09: Crear Categoría
- UC10: Asignar Categoría a Producto

**Gestión de Imágenes:**
- UC11: Subir Imagen Producto
- UC12: Actualizar Imagen Producto

#### Paso 3: Código PlantUML Completo

```plantuml
@startuml Caso de Uso - Gestión de Productos
title Sistema SADAT - Gestión de Productos

left to right direction

actor "Microempresa\nIntegral" as Empresa
actor "Cliente" as Cliente
actor "Sistema\nNotificaciones" as Sistema

rectangle "Sistema SADAT - Módulo Productos" {
  
  package "CRUD Productos" {
    usecase "Crear\nProducto" as UC01
    usecase "Editar\nProducto" as UC02
    usecase "Eliminar\nProducto" as UC03
    usecase "Listar Mis\nProductos" as UC04
    usecase "Ver Detalle\nProducto" as UC05
  }
  
  package "Gestión de Stock" {
    usecase "Actualizar\nStock" as UC06
    usecase "Verificar Stock\nDisponible" as UC07
    usecase "Alertar\nStock Bajo" as UC08
  }
  
  package "Gestión de Categorías" {
    usecase "Crear\nCategoría" as UC09
    usecase "Asignar Categoría\na Producto" as UC10
  }
  
  package "Gestión de Imágenes" {
    usecase "Subir Imagen\nProducto" as UC11
    usecase "Actualizar Imagen\nProducto" as UC12
  }
  
  usecase "Validar Datos\nProducto" as UC13
  usecase "Guardar en\nBase de Datos" as UC14
}

' Relaciones Empresa
Empresa --> UC01
Empresa --> UC02
Empresa --> UC03
Empresa --> UC04
Empresa --> UC06
Empresa --> UC09

' Relaciones Cliente
Cliente --> UC05

' Relaciones Include
UC01 ..> UC13 : <<include>>
UC02 ..> UC13 : <<include>>

UC01 ..> UC10 : <<include>>
UC01 ..> UC11 : <<include>>
UC01 ..> UC14 : <<include>>

UC02 ..> UC12 : <<extend>>
UC02 ..> UC14 : <<include>>

UC03 ..> UC14 : <<include>>

UC06 ..> UC07 : <<include>>
UC07 ..> UC08 : <<extend>>

' Relaciones con Sistema
UC08 --> Sistema : notifica

note right of UC13
  Validaciones:
  - Nombre no vacío
  - Precio > 0
  - Stock >= 0
  - Descripción válida
  - Imagen en formato correcto
end note

note right of UC08
  Alerta cuando:
  stock < 10 unidades
end note

note left of UC01
  Campos requeridos:
  - Nombre
  - Descripción
  - Precio
  - Stock inicial
  - Categoría
  - Imagen (opcional)
end note

@enduml
```

---

## 📈 EJEMPLO 4: Diagrama de Casos de Uso - Informe Estadístico General

### Análisis del Archivo de Referencia: "Caso de uso Informe estadistico general.vpd"

#### Paso 1: Identificar Actores

```
Actor Principal: Super Usuario
Actor Secundario: Microempresa Integral
Actor Secundario: Microempresa Satélite
```

#### Paso 2: Identificar Casos de Uso

**Visualización de Reportes:**
- UC01: Ver Reporte Global del Sistema
- UC02: Ver Reporte de Ventas (Empresas)
- UC03: Filtrar por Período
- UC04: Filtrar por Categoría
- UC05: Filtrar por Empresa

**Exportación:**
- UC06: Exportar a PDF
- UC07: Exportar a Excel
- UC08: Exportar a CSV

**Análisis:**
- UC09: Ver Gráficos Estadísticos
- UC10: Calcular Indicadores
- UC11: Comparar Períodos

#### Paso 3: Código PlantUML Completo

```plantuml
@startuml Caso de Uso - Reportes Estadísticos
title Sistema SADAT - Informes Estadísticos

left to right direction

actor "Super\nUsuario" as Admin
actor "Microempresa\nIntegral" as Integral
actor "Microempresa\nSatélite" as Satelite

rectangle "Sistema SADAT - Módulo Reportes" {
  
  package "Visualización de Reportes" {
    usecase "Ver Reporte\nGlobal del Sistema" as UC01
    usecase "Ver Reporte\nde Ventas" as UC02
    usecase "Filtrar por\nPeríodo" as UC03
    usecase "Filtrar por\nCategoría" as UC04
    usecase "Filtrar por\nEmpresa" as UC05
  }
  
  package "Exportación de Datos" {
    usecase "Exportar\na PDF" as UC06
    usecase "Exportar\na Excel" as UC07
    usecase "Exportar\na CSV" as UC08
  }
  
  package "Análisis Estadístico" {
    usecase "Ver Gráficos\nEstadísticos" as UC09
    usecase "Calcular\nIndicadores" as UC10
    usecase "Comparar\nPeríodos" as UC11
  }
  
  usecase "Consultar Base\nde Datos" as UC12
  usecase "Generar\nDocumento" as UC13
}

' Relaciones Super Usuario
Admin --> UC01
Admin --> UC05

' Relaciones Empresas
Integral --> UC02
Satelite --> UC02

' Relaciones Comunes
Admin --> UC09
Integral --> UC09
Satelite --> UC09

' Relaciones Include
UC01 ..> UC03 : <<extend>>
UC01 ..> UC04 : <<extend>>
UC02 ..> UC03 : <<extend>>

UC01 ..> UC09 : <<include>>
UC02 ..> UC09 : <<include>>

UC01 ..> UC10 : <<include>>
UC02 ..> UC10 : <<include>>

UC09 ..> UC12 : <<include>>
UC10 ..> UC12 : <<include>>

' Relaciones Exportación
Admin --> UC06
Admin --> UC07
Admin --> UC08
Integral --> UC06
Integral --> UC07
Satelite --> UC06
Satelite --> UC07

UC06 ..> UC13 : <<include>>
UC07 ..> UC13 : <<include>>
UC08 ..> UC13 : <<include>>

' Comparación
Admin --> UC11
Integral --> UC11
Satelite --> UC11

note right of UC01
  Muestra estadísticas de:
  - Total de usuarios
  - Total de empresas
  - Total de productos
  - Total de ventas
  - Ingresos totales
  - Productos más vendidos
end note

note right of UC02
  Muestra estadísticas de:
  - Ventas del período
  - Productos vendidos
  - Ingresos generados
  - Pedidos pendientes
  - Clientes activos
end note

note right of UC10
  Indicadores:
  - Promedio de ventas
  - Tasa de conversión
  - Ticket promedio
  - Productos más vendidos
  - Categorías más demandadas
end note

note left of UC13
  Genera documento
  con los datos
  filtrados y gráficos
end note

@enduml
```

---

## 🎓 LECCIONES APRENDIDAS DEL PROYECTO DE REFERENCIA

### 1. Organización de Diagramas

**Del proyecto .vpd aprendemos:**
- Separar diagramas por módulo funcional
- Un archivo por proceso principal
- Nomenclatura descriptiva de archivos

### 2. Nivel de Detalle

**Casos de Uso:**
- No incluir detalles técnicos
- Enfocarse en la funcionalidad del usuario
- Usar lenguaje del dominio del negocio

**Diagramas de Secuencia:**
- Incluir todos los pasos importantes
- Numerar mensajes secuencialmente
- Mostrar alternativas con "alt"

### 3. Uso de Relaciones

**Include vs Extend:**
- **Include**: Funcionalidad siempre requerida
  - Ejemplo: Login → Validar Credenciales
- **Extend**: Funcionalidad opcional
  - Ejemplo: Ver Producto → Agregar Comentario

### 4. Notas Explicativas

**Siempre incluir notas para:**
- Validaciones de datos
- Reglas de negocio importantes
- Decisiones de diseño
- Restricciones del sistema

---

## 📋 PLANTILLAS REUTILIZABLES

### Plantilla: Caso de Uso Básico

```plantuml
@startuml
left to right direction

actor "Actor Principal" as Actor1
actor "Actor Secundario" as Actor2

rectangle "Sistema [Nombre]" {
  usecase "Caso de Uso 1" as UC1
  usecase "Caso de Uso 2" as UC2
  usecase "Validación" as UC3
}

Actor1 --> UC1
Actor1 --> UC2
UC1 ..> UC3 : <<include>>
UC2 ..> UC3 : <<include>>

note right of UC1
  Descripción del caso de uso
end note

@enduml
```

### Plantilla: Secuencia Básica

```plantuml
@startuml
actor Usuario
participant Vista
participant Controlador
participant Modelo
database BD

Usuario -> Vista: Acción
activate Vista
Vista -> Controlador: Procesar
activate Controlador
Controlador -> Modelo: Operación
activate Modelo
Modelo -> BD: Query
activate BD
BD --> Modelo: Resultado
deactivate BD
Modelo --> Controlador: Datos
deactivate Modelo
Controlador --> Vista: Respuesta
deactivate Controlador
Vista --> Usuario: Mostrar
deactivate Vista

@enduml
```

---

**Última actualización**: Octubre 2025  
**Basado en**: Proyecto de Referencia Visual Paradigm (.vpd files)
