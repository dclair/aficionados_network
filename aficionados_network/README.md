Hubs&Clicks
📝 Descripción
Hubs&Clicks es una plataforma social dinámica desarrollada con Django, diseñada para conectar a personas a través de sus pasiones. Más allá de compartir momentos, la aplicación organiza el contenido en Hobby Hubs (comunidades temáticas) donde los usuarios pueden interactuar, seguir aficiones específicas y participar en un sistema inteligente de Quedadas (Eventos) basado en niveles de habilidad.

Este proyecto forma parte del portafolio de proyectos del Máster Full Stack de Conquer Blocks.

🚀 Características principales
📸 Red Social y Clicks
Publicaciones Dinámicas: Comparte tus "Clicks" (imágenes) con descripciones y etiquetas.

Interacción Real: Sistema de "Me gusta" y comentarios en tiempo real.

Feed Personalizado: Un muro que prioriza el contenido de los usuarios a los que sigues.

Perfiles Vitaminados: Estadísticas de participación, historial de eventos organizados y valoraciones recibidas.

🤝 Hobby Hubs (Comunidades)
Espacios Temáticos: Cada afición tiene su propio "Hub" con galerías exclusivas y listas de miembros.

Sistema de Seguimiento: Únete a comunidades específicas para personalizar tu experiencia y recibir recomendaciones.

Navegación Inteligente: Sidebar dinámica con contadores de eventos activos que coinciden con tu perfil.

🎯 Sistema Inteligente de Quedadas (Eventos)
Gestión de Eventos: Creación y organización de quedadas con control de aforo, fechas y estados (activo, pasado o cancelado).

Algoritmo de Level Matching: El sistema compara automáticamente tu nivel en un hobby con el del evento:

Match: Identifica los planes perfectos para tu nivel actual (Icono de Estrella 🌟).

Mentor: Reconoce cuando tu nivel es superior, animándote a participar como guía/referente (Icono de Birrete 🎓).

Gamificación Visual: Animaciones de pulsación (glow) y badges dinámicos en la Home y Sidebar para resaltar oportunidades de participación.

Asistencia: Sistema de confirmación de asistencia con validación de plazas disponibles.

🛠️ Tecnologías utilizadas
Backend: Django 6.0

Frontend: HTML5, CSS3, Bootstrap 5, HTMX (para interactividad asíncrona sin recarga de página)

Base de datos: SQLite (desarrollo)

Iconografía: Bootstrap Icons

Autenticación: Sistema robusto de Django con validación por correo electrónico.

🧪 Pruebas
El proyecto incluye un conjunto completo de pruebas unitarias y de integración:

Modelos
[UserProfile]: Pruebas para el modelo de perfil de usuario.

[Follow]: Pruebas para el sistema de seguidores.

[UserHobby/Event]: Validación de la lógica de niveles y concurrencia en eventos.

Vistas
Autenticación (login, registro, logout).

Gestión de perfiles y Hubs.

Lógica de Match/Mentor en eventos.

Sistema de seguimiento y notificaciones.

Para ejecutar las pruebas:

Bash
python manage.py test
🚀 Instalación
Clona el repositorio:

Bash
git clone git@github.com:dclair/aficionados_network.git
cd aficionados_network
Crea y activa un entorno virtual:

Bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
Instala las dependencias:

Bash
pip install -r requirements.txt
Aplica las migraciones:

Bash
python manage.py migrate
Crea un superusuario:

Bash
python manage.py createsuperuser
Inicia el servidor de desarrollo:

Bash
python manage.py runserver
📝 Licencia
Este proyecto es libre de licencia, puedes usarlo, copiarlo, modificarlo, distribuirlo... libremente. Cualquier comentario o sugerencia de mejora es bienvenida.

👨‍💻 Autor
Nombre: [Dclair - Jose M. Declara]

GitHub: @dclair

LinkedIn: Sin perfil

Portafolio: Sin sitio web personal

📚 Sobre Conquer Blocks
Este proyecto fue desarrollado como parte del Máster Full Stack de Conquer Blocks, un programa de formación en desarrollo web full stack que combina teoría y práctica para formar desarrolladores profesionales.

✨ Desarrollado con pasión por el código limpio y las buenas prácticas de desarrollo.