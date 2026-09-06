# Palabras envolventes — método de descubrimiento indirecto

## El método, explicado

No se busca "trabajo de logística" ni "empleo administrativo" — eso es lo que
hacen los portales de empleo, que están excluidos por regla del proyecto. Se
busca **quién provee/fabrica/distribuye/transporta un producto o servicio
concreto en la zona** (ej. "proveedor de ladrillos Hurlingham"). Esa empresa
casi nunca publica una vacante, pero es una empresa real, con depósito,
administración, atención a clientes/compras y logística — exactamente los 4
rubros del CV de Marco — sin competir con nadie que busque por portal.

Es la misma lógica que ya se usa para "quién le fabrica a Carrefour" (ver
`app/supplier_discovery.py`) y para el "entramado" de keywords (`limpieza de
trenes` → lleva a otras tercerizadas). Este documento generaliza esa idea a
una lista amplia y reutilizable de:

```
{ROL COMERCIAL} + {PRODUCTO/MATERIAL/SERVICIO} + {ZONA}
```

Cuantas más combinaciones de columna 1 × columna 2, más cobertura real sin
depender de que la empresa haya publicado nada.

## Columna 1 — roles comerciales (el verbo de la búsqueda)

| Rol | Por qué funciona |
|---|---|
| proveedor de | quien abastece necesita depósito/logística/compras |
| distribuidor de | intermediario con flota, depósito, administración |
| fabricante de | planta con producción, necesita todo el back office |
| mayorista de | venta al por mayor, necesita atención a clientes B2B |
| importador de | trámites + depósito + administración |
| representante de | oficina comercial, ventas, atención al cliente |
| depósito de | logística pura |
| service técnico de | taller + atención al cliente + repuestos (compras) |
| alquiler de | necesita mantenimiento, logística de entrega/retiro |
| transportista de / flete de | logística directa |
| mantenimiento de | service técnico, requiere administración y compras |
| insumos para | proveedor de insumos a otro rubro (ej. "insumos para gastronomía") |
| repuestos de | depósito + atención al cliente |
| venta de | comercio con necesidad de administración/atención |

## Columna 2 — productos/materiales/servicios (por rubro relacionado)

**300 categorías en total** (`app/supplier_discovery.py::CATEGORIAS_PRODUCTO`),
agrupadas en 16 rubros. Además de las 9 familias de abajo, se sumaron:
textil/indumentaria, papelería/oficina/informática, farmacia/salud/estética,
energía/climatización, transporte/logística de insumos, y una categoría
"otros servicios B2B" (lavaderos, tintorerías, imprentas, carpinterías,
vidrierías, herrerías, gastronomía, hotelería, call centers, entre otros).

### Construcción / ferretería (mucho depósito y logística)
ladrillos, cemento, arena, hierro para construcción, maderas, chapas,
caños, cables, pinturas, cerámicos, revestimientos, aberturas (puertas y
ventanas), herramientas, tornillería, sanitarios, membranas, áridos,
premoldeados, andamios, materiales eléctricos

### Industria / metalúrgica / autopartes
autopartes, repuestos automotor, neumáticos, baterías, lubricantes,
maquinaria industrial, herramientas industriales, insumos metalúrgicos,
chapa y pintura, matricería, fundición

### Alimentos y bebidas (mucha logística de reparto)
alimentos al por mayor, bebidas, gaseosas, aguas envasadas, panificados,
lácteos, fiambres y embutidos, productos congelados, insumos gastronómicos,
envases para alimentos, packaging alimenticio

### Limpieza e higiene (directamente el rubro de Marco)
productos de limpieza, insumos de limpieza industrial, artículos de
librería e higiene, detergentes industriales, indumentaria de trabajo,
elementos de protección personal (EPP), uniformes, textiles para el hogar

### Papel, cartón, embalaje (logística intensiva)
envases, embalajes, cartón corrugado, papel, film stretch, pallets,
cajas de cartón, etiquetas, packaging en general

### Plástico / químico
envases plásticos, productos plásticos para el hogar, químicos
industriales, agroquímicos, pinturas industriales, adhesivos, resinas

### Textil / indumentaria
telas, indumentaria de trabajo, uniformes corporativos, textiles para el
hogar, calzado de seguridad

### Muebles / equipamiento de oficina y comercio
muebles de oficina, mobiliario comercial, estanterías industriales,
equipamiento para gastronomía, refrigeración comercial, cámaras
frigoríficas, góndolas y exhibidores

### Agro (zona oeste GBA tiene actividad rural residual)
forrajes, semillas, insumos agropecuarios, maquinaria agrícola,
fertilizantes

### Servicios técnicos / mantenimiento (talleres con necesidad de todo)
aire acondicionado, ascensores, matafuegos, portones automáticos,
sistemas de seguridad/CCTV, plomería industrial, electricidad industrial,
service de electrodomésticos, service de informática

## Cómo se arma la query final

```
"{rol} {producto}" {zona} -Peru -Trujillo -Lima -México -Chile -Colombia -España -Zonaprop -Argenprop -pasajes
```

Ejemplos reales:
- `"proveedor de ladrillos" Hurlingham`
- `"fabricante de envases plásticos" Morón`
- `"distribuidor de productos de limpieza" El Palomar`
- `"service técnico de aire acondicionado" Ituzaingó`

## Entramado: de cada hallazgo salen nuevas keywords

Cuando una candidata aparece por una de estas búsquedas, su descripción se
pasa por `app/discovery.py::extraer_keywords_de_texto()`, que ya busca
frases tipo "servicio de X" / "fabricación de X" en el texto y las registra
como keyword nueva (tabla `keywords`, origen='discovered') — así una
búsqueda de "ladrillos" puede terminar registrando "servicio de logística de
áridos" como keyword nueva, sin que nadie la haya tipeado a mano. Este
documento es la semilla inicial; el entramado sigue creciendo solo.

## Dónde vive esto en el código

- `app/supplier_discovery.py::CATEGORIAS_PRODUCTO` — ampliado con estas
  categorías (antes solo tenía productos de supermercado, pensado para
  "quién le fabrica a Carrefour").
- `app/supplier_discovery.py::_queries_por_categoria()` — ya arma la query
  con los roles "quién fabrica", "proveedor de", "fabricante" (columna 1 de
  este documento aplicada parcialmente); se puede ampliar con más roles de
  la tabla de arriba si se quiere más cobertura por corrida.
- `app/discovery.py::extraer_keywords_de_texto()` — el mecanismo de
  entramado que sigue expandiendo la lista solo, a partir de lo que cada
  candidata dice de sí misma.
