# Folleto (prospecto de una página)

- `folleto-whatsapp.png`: imagen de 1080 × 1350 para mandar por WhatsApp.
- `folleto.pdf`: el mismo folleto en un PDF de una página, para mandar como documento.
- `folleto.json`: tus datos.
- `folleto.html`: el diseño.
- `render-folleto.js`: arma el PNG y el PDF.

## Cambiar tus datos
Abrí `folleto.json` y reemplazá los valores de ejemplo:
- `"nombre"`: `"Tu Nombre"` → tu nombre o el nombre de la marca.
- `"instagram"`: `"@tu.usuario"` → tu usuario de Instagram.
- `"whatsapp"`: `"WhatsApp: tu número"` → por ejemplo `"WhatsApp: 11 2345-6789"`.
- `"foto"`: `"tu-foto.jpg"` → ruta a tu foto o logo (mejor si es cuadrada). Si no existe, se muestran tus iniciales.

Estos campos son opcionales:
- `"whatsapp_link"`: tu número en formato internacional, solo dígitos (ej. `5491123456789`). Con eso, en el PDF se puede tocar "Escribime" para abrir el chat.
- `"rol"`: el texto que va debajo de tu nombre.
- `"titular"`: una línea por elemento. La palabra entre `*asteriscos*` sale en verde.
- `"demos"`: las portadas de los ejemplos. La primera va a la izquierda, la segunda al centro y la tercera a la derecha.

## Volver a renderizar
```
node render-folleto.js
```
Funciona desde cualquier carpeta. En cada corrida, el script:
- usa las portadas de `/home/user/demos/*/portada.png` que ya existan. Las que falten quedan como un recuadro con la etiqueta EJEMPLO.
- te avisa si todavía quedan datos de ejemplo.
- revisa que no haya textos cortados ni contenido fuera de la hoja, y que el PDF tenga 1 página.

Los precios no van en el folleto: dice "Precio por WhatsApp". Tampoco hay testimonios ni números inventados.
