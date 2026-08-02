# Gab - Fotógrafo & Director

Portafolio web inspirado en [weareapostrophe.com/photographers](https://weareapostrophe.com/photographers/).

Diseño editorial, minimalista y centrado en la fotografía. Fondo blanco, grid
limpio de proyectos, navegación sencilla y filtros por categoría.

## Características

- Diseño claro y tipo agencia creativa
- Tipografía serif elegante (Cormorant Garamond) + sans-serif limpia (Inter)
- Grid de proyectos con hover suave
- Filtros por categoría: All, Photography, Direction, Commercial, Editorial
- Páginas: Photographers, About, Contact y proyecto individual
- 100% gratuito, ideal para GitHub Pages
- Totalmente responsive

## Estructura

```text
Gabweb/
├── index.html       # Home con grid de proyectos y filtros
├── about.html       # Página About
├── contact.html     # Página Contact
├── project.html     # Plantilla de proyecto individual
├── css/style.css    # Estilos del portafolio
├── js/main.js       # Interacciones del portafolio
├── app.py           # Servidor del explorador local de Copilot
├── static/          # Interfaz del explorador de conversaciones
└── tests/           # Pruebas del servidor y su API
```

## Cómo usar el portafolio

1. Reemplaza las imágenes de `https://images.unsplash.com/...` por tus propias fotos.
2. Edita títulos, categorías y textos en cada HTML.
3. Actualiza el email, teléfono y redes sociales.
4. Activa GitHub Pages desde Settings > Pages > Source: Deploy from a branch.

## Conversaciones locales de GitHub Copilot

El repositorio también incluye una aplicación web local para consultar las
sesiones guardadas por GitHub Copilot CLI. Requiere Python 3.10 o posterior, no
usa dependencias externas y abre `~/.copilot/session-store.db` en modo de solo
lectura.

```bash
python3 app.py
```

Abre <http://127.0.0.1:8000>. Puedes indicar otra base o puerto:

```bash
python3 app.py --db /ruta/session-store.db --port 8080
```

Ejecuta las pruebas con:

```bash
python3 -m unittest discover -s tests -v
```

## Próximos pasos

- Crear una pagina por cada proyecto real.
- Agregar videos para los proyectos de dirección.
- Conectar el formulario con [Formspree](https://formspree.io/) (gratis).
- Agregar un logo o favicon.

## Licencia

Uso personal para el titular del repositorio.
