🚀 Hubs&Clicks - Red Social de Aficionados
Hubs&Clicks es una plataforma web diseñada para conectar a personas a través de sus aficiones, permitiéndoles organizar eventos, unirse a quedadas y gestionar su comunidad de forma ágil y moderna.

🛠️ Características Principales (Features)
1. Gestión de Eventos 360º
Creación y Edición: Los usuarios pueden proponer planes detallando lugar, fecha, hobby y límite de asistentes.

Sistema de Duplicado: Función inteligente para clonar eventos pasados y ahorrar tiempo al organizador.

Control de Asistencia: Sistema de "Me apunto/Desapuntarme" con validación de plazas en tiempo real.

Gestión de Estados: Soporte para eventos activos, finalizados y cancelaciones con aviso a los asistentes.

2. Dashboard de Usuario (Perfiles Vitaminados)
Identidad Social: Perfiles personalizados con biografía, ubicación, sitio web y selección de aficiones con niveles (Principiante a Experto).

Estadísticas en Tiempo Real: Contadores dinámicos de publicaciones, seguidores, siguiendo, eventos organizados y participaciones.

Accesos Directos: Las medallas del perfil actúan como enlaces rápidos a las secciones de gestión personal.

Agenda Personal: Visualización de las próximas 3 citas confirmadas directamente en el perfil.

3. UX/UI "Mobile-First" & Pro
Diseño Responsivo: Interfaz optimizada para Smartphone (menú hamburguesa), Tablet y PC (menú sticky).

Navegación Fluida: Header siempre visible al hacer scroll y botón flotante "Back to Top" para facilitar la lectura de hilos largos.

Tablas Inteligentes: Gestión de planes mediante menús desplegables (three-dots dropdown) con posicionamiento fijo para evitar cortes visuales en móviles.

4. Motor de Búsqueda y Filtrado
Multifiltro: Buscador avanzado que permite combinar texto libre, ubicación (ciudad) y categorías de aficiones.

Paginación Persistente: Sistema que mantiene los filtros activos al navegar entre las distintas páginas de resultados.

5. Comunicación e Identidad
Emails HTML: Notificaciones de sistema con diseño corporativo, logotipos y botones de acción integrados.

Sistema de Seguidores: Lógica social completa para seguir/dejar de seguir a otros aficionados con notificaciones internas.

💻 Stack Tecnológico
Backend: Django 6.0 + Python 3.12.

Frontend: HTML5, CSS3, Bootstrap 5.3.

Interactividad: HTMX (para notificaciones y actualizaciones parciales).

Iconografía: Bootstrap Icons.

Base de Datos: SQLite (Desarrollo) / MySQL (Producción).

🏗️ Estructura del Proyecto
Bash
aficionados_network/
├── posts/            # Gestión de Eventos y Publicaciones
├── profiles/         # Usuarios, Hobbies, Seguidores y Estadísticas
├── notifications/    # Sistema de avisos internos
├── aficionados_network/ # Configuración principal y Formularios
└── templates/        # Componentes UI globales (Header, Layout, etc.)
📈 Próximamente (Roadmap)
[ ] Sistema de Valoraciones (Reviews): Puntuación por estrellas tras finalizar un evento.

[ ] Filtro de "Mis Aficiones": Acceso rápido a eventos que coinciden con los hobbies del perfil del usuario.

[ ] Chat en tiempo real: Para coordinar los detalles de cada quedada.

Hubs&Clicks - "Descubre, Comparte, Disfruta"