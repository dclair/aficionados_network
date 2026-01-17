# InstaDclair
## 📝 Descripción
InstaDclair es una aplicación web inspirada en Instagram, desarrollada con Django, que permite a los usuarios compartir imágenes, seguir a otros usuarios, comentar, crear posts y dar me gusta a las publicaciones. 
Este proyecto forma parte del portafolio de proyectos del Máster Full Stack de Conquer Blocks.
## 🚀 Características principales
- Autenticación de usuarios (registro, inicio de sesión, recuperación de contraseña)
- Subida de imágenes con descripción
- Sistema de seguidores/seguidos
- Feed de publicaciones personalizado
- Perfiles de usuario personalizables
- Sistema de notificaciones
## 🛠️ Tecnologías utilizadas
- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Base de datos**: SQLite (desarrollo)
- **Autenticación**: Sistema de autenticación de Django
- **Almacenamiento**: Sistema de archivos local (desarrollo)
## 🧪 Pruebas
El proyecto incluye un conjunto completo de pruebas unitarias y de integración:
### Modelos
- [UserProfile] Pruebas para el modelo de perfil de usuario
- [Follow] Pruebas para el sistema de seguidores
### Vistas
- Autenticación (login, registro, logout)
- Gestión de perfiles
- Publicaciones
- Sistema de seguimiento
Para ejecutar las pruebas:
```bash
python manage.py test
🚀 Instalación
Clona el repositorio:
bash
git clone git@github.com:dclair/instadclair.git
cd instadclair
Crea y activa un entorno virtual:
bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
Instala las dependencias:
bash
pip install -r requirements.txt
Aplica las migraciones:
bash
python manage.py migrate
Crea un superusuario:
bash
python manage.py createsuperuser
Inicia el servidor de desarrollo:
bash
python manage.py runserver
📝 Licencia
Este proyecto es libre de licencia, puedes usarlo, copiarlo, modificarlo, distribuirlo... libremente.
Cualquier comentario o sugerencia de mejora es bienvenida.

👨‍💻 Autor
Nombre: [Dclair]
GitHub: @dclair
LinkedIn: Sin perfil
Portafolio: Sin sitio web personal
📚 Sobre Conquer Blocks
Este proyecto fue desarrollado como parte del Máster Full Stack de Conquer Blocks, un programa de formación en desarrollo web full stack que combina teoría y práctica para formar desarrolladores profesionales.

✨ Desarrollado con pasión por el código limpio y las buenas prácticas de desarrollo.