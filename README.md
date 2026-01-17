# Aficionados Network
## 📝 Descripción
Aficionados Network es una red social temática desarrollada con Django que permite a los usuarios con intereses en común conectarse, compartir publicaciones, seguir a otros aficionados y descubrir contenido relevante. Este proyecto es una evolución de InstaDclair, enfocado en crear comunidades alrededor de aficiones específicas.
## 🚀 Características principales
- **Perfiles personalizables** con información detallada de intereses
- **Sistema de publicaciones** con texto e imágenes
- **Seguimiento de usuarios** para crear tu red de aficionados
- **Feed personalizado** con publicaciones de usuarios que sigues
- **Comentarios** en publicaciones
- **Sistema de notificaciones** (en desarrollo)
- **Búsqueda avanzada** por intereses y ubicación
## 🛠️ Tecnologías utilizadas
- **Backend**: Django 6.0
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Autenticación**: Sistema de autenticación de Django
- **Almacenamiento**: Sistema de archivos local (desarrollo) / AWS S3 (producción)
- **Despliegue**: Docker, Nginx, Gunicorn
## 🚀 Instalación
### Requisitos previos
- Python 3.10+
- pip
- Git
### Pasos para configuración
1. **Clona el repositorio:**
   ```bash
   git clone git@github.com:dclair/aficionados_network.git
   cd aficionados_network
Crea y activa un entorno virtual:
bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
Instala las dependencias:
bash
pip install -r requirements.txt
Configura las variables de entorno: Crea un archivo .env en la raíz del proyecto con las siguientes variables:
ini
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
Aplica las migraciones:
bash
python manage.py migrate
Crea un superusuario:
bash
python manage.py createsuperuser
Inicia el servidor de desarrollo:
bash
python manage.py runserver
Accede al sitio:
Aplicación: http://127.0.0.1:8000/
Panel de administración: http://127.0.0.1:8000/admin/
🧪 Pruebas
El proyecto incluye pruebas unitarias y de integración:

Ejecutar todas las pruebas:
bash
python manage.py test
Ejecutar pruebas específicas:
bash
# Pruebas de la aplicación profiles
python manage.py test profiles
# Pruebas de la aplicación posts
python manage.py test posts
🏗️ Estructura del proyecto
aficionados_network/
├── aficionados_network/      # Configuración principal del proyecto
├── profiles/                 # Aplicación de perfiles de usuario
├── posts/                    # Aplicación de publicaciones
├── static/                   # Archivos estáticos (CSS, JS, imágenes)
├── templates/                # Plantillas HTML
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
📄 Licencia
Este proyecto es de código abierto bajo la licencia MIT. Siéntete libre de usarlo, modificarlo y distribuirlo.

👨‍💻 Autor
Nombre: [Dclair]
GitHub: @dclair
LinkedIn: [Tu perfil de LinkedIn]
Portafolio: [Tu sitio web personal]
🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor, lee las pautas de contribución antes de enviar un pull request.

📝 Notas de la versión
v1.0.0 (2026-01-17)
Versión inicial del proyecto
Sistema de perfiles de usuario
Publicaciones y comentarios
Sistema de seguimiento entre usuarios