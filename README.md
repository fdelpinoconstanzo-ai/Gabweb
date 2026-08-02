# Gab - Fotografo & Director

Portafolio web inspirado en [weareapostrophe.com/photographers](https://weareapostrophe.com/photographers/).

Diseno editorial, minimalista y centrado en la fotografia. Fondo blanco, grid
limpio de proyectos, navegacion sencilla y filtros por categoria.

## Caracteristicas

- Diseno claro y tipo agencia creativa
- Tipografia serif elegante (Cormorant Garamond) + sans-serif limpia (Inter)
- Grid de proyectos con hover suave
- Filtros por categoria: All, Photography, Direction, Commercial, Editorial
- Paginas: Photographers, About, Contact y proyecto individual
- 100% gratuito, ideal para GitHub Pages
- Totalmente responsive

## Estructura

```text
Gabweb/
├── index.html       # Home con grid de proyectos y filtros
├── about.html       # Pagina About
├── contact.html     # Pagina Contact
├── project.html     # Plantilla de proyecto individual
├── css/style.css    # Estilos del portafolio
├── js/main.js       # Interacciones del portafolio
├── app.py           # Servidor del explorador local de Copilot
├── static/          # Interfaz del explorador de conversaciones
└── tests/           # Pruebas del servidor y su API
```

## Como usar el portafolio

1. Reemplaza las imagenes de `https://images.unsplash.com/...` por tus propias fotos.
2. Edita titulos, categorias y textos en cada HTML.
3. Actualiza el email, telefono y redes sociales.
4. Activa GitHub Pages desde Settings > Pages > Source: Deploy from a branch.

## Conversaciones locales de GitHub Copilot

El repositorio tambien incluye una aplicacion web local para consultar las
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

## Proximos pasos

- Crear una pagina por cada proyecto real.
- Agregar videos para los proyectos de direccion.
- Conectar el formulario con [Formspree](https://formspree.io/) (gratis).
- Agregar un logo o favicon.

## Licencia

Uso personal para el titular del repositorio.
