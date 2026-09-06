# Dominar la estación de Iniciador — de la pantalla a la vida real

Este documento tiene dos partes que son la misma cosa vista desde dos lados:

1. **La ficha técnica real** de la estación de Iniciador/Ensamblador, sacada
   palabra por palabra de tu Guía de Entrenamiento oficial (`GEIniciadorEnsambladorAgosto2022.pdf`,
   38 páginas, Agosto 2022).
2. **El diseño de Modo Estación**, la mecánica nueva del simulador que convierte
   esa ficha en algo que se entrena de verdad, no solo se lee.

## La idea, en una frase

> Como practicar ediciones en un mapa de Fortnite antes de entrar a una partida:
> repetís el movimiento aislado, sin presión de puntaje real, hasta que el
> cuerpo y la cabeza lo hacen solos — y cuando llega el turno de verdad, ya lo
> hiciste cien veces.

Vos ya lo sabías intuitivamente: envolver una hamburguesa con papel de McDonald's
en tu casa para practicar el pliegue es exactamente este principio aplicado a lo
físico. Modo Estación es la mitad que sí se puede simular en una pantalla: **qué
va en cada pedido y en qué orden**, para que cuando llegues al turno ya lo hayas
decidido cien veces de memoria. El pliegue del papel seguís practicándolo en tu
casa — eso ninguna pantalla te lo enseña mejor que la práctica física real.

## Por qué esto no era solo "memorizar el pedido"

Hasta ahora el simulador te ponía a prueba en UNA sola cosa: leer "2 Big Mac,
1 McPollo" y no olvidarte antes de apretar Servido. Eso es real, pero es solo
la mitad del trabajo del Iniciador según la guía: la otra mitad es **decidir
qué pan, qué salsa, cuánta cantidad y en qué orden** — y esa parte tiene
reglas exactas, con gramos y onzas, que también hay que tener automatizadas.
Modo Estación entrena esa segunda mitad.

---

## Parte 1 — Lo que dice la guía oficial

### 1.1 El disparador: la alarma del monitor

> "Cuando suene la alarma del monitor, comienza el proceso para acomodar los
> panes entre 0'' a 5''. Así podrás asegurar un tiempo de atención rápido."

Esto es literal lo que ya está en el simulador como `REACTION_STANDARD_S = 5`.
La reacción a la alarma tiene que ser en 5 segundos o menos.

### 1.2 Preparación del Iniciador (antes de que llegue el pedido)

- Almacenar pan suficiente para el horario, respetando vida útil.
- Un paño verde de limpieza, desinfectado y doblado, para la tostadora vertical
  — **nunca dejarlo sobre la línea** porque tiene calor.
- Verificar tiempos y temperaturas de los equipos.
- Verificar que el KVS (la pantalla de pedidos) funcione.
- Abrir las bolsas de pan de a una, con un corte en el frente, y mantenerlas
  cerradas entre usos para evitar desperdicio.

### 1.3 El pan — paso a paso

1. Separar la corona (parte de arriba) de la base con las dos manos, apoyar
   ambas con la cara interna sobre la placa calentadora.
2. **Big Mac es distinto**: lleva un tercer pan, el **"club"** (la capa del
   medio). Según la tostadora, el club va en el mismo compartimento que la
   base (tostadoras Antunez) o en la sección del medio (tostadoras HEBT-5V).
3. Si el pedido es especial, la comanda va en el frente del envase (caja) con
   la etiqueta "Hecho para ti"; si el producto lleva papel, la comanda va
   abajo, del mismo lado que la tostadora vertical.
4. Con cada pedido nuevo en el monitor, arrancá la tanda siguiente sin
   esperar que termine el ciclo de caramelización anterior.
5. Condimentá el sándwich apenas termina la caramelización y pasalo enseguida
   — nunca dejarlo detenido en la línea. **Tiempo de ensamblado: 35 a 50
   segundos** (esto ya está en el simulador como el "estándar oficial" que
   mide Turno Intensivo).

### 1.4 Las recetas reales (con gramos y onzas)

Estas son las que Modo Estación usa tal cual, porque la guía las da exactas.

| Producto | Pan | Pasos de armado |
|---|---|---|
| **Hamburguesa** | Regular (corona + base) | Mostaza (1/35-1/60oz) → Ketchup (1/3oz) → 3,5g cebolla rehidratada sobre el ketchup |
| **Hamburguesa c/Queso** | Regular | Igual que arriba + 1 feta de queso cheddar sobre la corona condimentada |
| **Big Mac** | Con club (3 piezas) | Salsa Big Mac (1/3oz) en la base Y en el club → 3,5g cebolla sobre ambas salsas → 14g lechuga sobre club y base → 2 rodajas de pepino sobre la lechuga del club → 1 feta de queso sobre la lechuga de la base |
| **1/4 De Libra c/Queso** | Regular | Mostaza + Ketchup (1/2oz) simultáneos, un dispensador en cada mano → 7g cebolla fresca sobre el ketchup → 1 feta de queso sobre la corona → 1 feta más sobre la base, en estrella con la primera |
| **Dbl 1/4 De Libra c/Queso** | Regular | Igual que el simple, pero la segunda feta de queso va **entre las dos carnes**, no en el pan |
| **McNífica** | Regular | Mostaza + Ketchup (1/2oz) → 7g cebolla fresca → Mayonesa (1/2oz) → 21g lechuga sobre la salsa → 2 rodajas de tomate sobre la lechuga → 1 feta de queso sobre los tomates |
| **McPollo** | Regular | Mayonesa 2/3oz (2 dispensadas de 1/3oz) en el centro de la corona → 28g lechuga cubriendo toda la superficie |

Todos los dispensadores de salsa se usan a **2,5cm de altura** sobre el pan.

### 1.5 Ensaladas

- **Side Salad**: 50g de lechuga cortada distribuida uniformemente + 2
  rodajas de tomate, cubriendo el 80% de la ensalada.
- **Ensalada Deli**: 100g lechuga + 2 dispensadas de ½oz de mayonesa (14g) +
  28g de cebolla fresca + 4 rodajas de tomate centradas.
- **Ensalada Deli con Pechuga Crispy/Grillé**: lo mismo + pechuga cortada en
  6-8 tiras de 1,5cm, sobre el lado izquierdo. Identificación en la caja:
  **2 = Crispy, 1 = Grillé**.

### 1.6 UHC (el cajón que mantiene la carne caliente)

- Pinza **roja** para pollo, pinza **verde** para carnes rojas.
- Espacio vacío en el cajón = hay que cocinar producto nuevo ahora.
- Bandeja limpia puesta **al revés** = ese espacio está desactivado a
  propósito (bajaste el nivel de producción), no es que falte cocinar.

### 1.7 Envoltorio de papel

Corona hacia abajo en el centro del papel → doblar el frente sobre la base
hasta la mitad del sándwich → girar hasta envolver por completo → plegar los
extremos hacia adentro con las dos manos → transferir a la mesa OAT.

### 1.8 Lo que la guía NO cubre (todavía)

Esta guía es de Agosto 2022 y cubre las líneas clásicas. No tiene capítulo
propio para McCrispy, McNuggets (más allá de "usá la pala correcta"), Apple
Pie, tostados/McCafé, ni las ensaladas Caesar. Antes que inventar cantidades
para esos productos, Modo Estación **no arma desafío para ellos** — los sirve
directo, igual que el modo libre. El día que aparezca una guía más nueva para
esas líneas, se suma su receta a `src/lib/recetas.js` de la misma forma.

---

## Parte 2 — Modo Estación (tecla `E`)

### Cómo funciona

Con Modo Estación prendido, al apretar Enter para servir el pedido de
adelante:

1. Si alguno de sus ítems tiene receta conocida (tabla de arriba), aparece un
   desafío: **elegí el pan correcto** y **marcá todos los pasos de
   condimentación correctos**, de memoria, antes de que se sirva de verdad.
2. Las opciones mezclan los pasos reales de ESE producto con pasos reales de
   OTROS productos — la misma lógica de interferencia y discriminación de
   `METODO-MEMORIA.md` (Método 5), pero aplicada a "qué lleva" en vez de
   "qué pedido es". Confundir la salsa de Big Mac con la de la Cuarto de
   Libra es un error real y común — el desafío te entrena justo en eso.
3. Al confirmar, ves qué acertaste, qué te faltó y qué sobra. Si hubo algún
   error, ese producto queda anotado en el mismo panel de "ítems más
   difíciles" que ya usa Modo Enfoque — así Modo Enfoque también empieza a
   darte más seguido los productos que armás mal, no solo los que olvidás.
4. Si no tenés tiempo o querés practicar solo velocidad, "Saltar" sirve el
   pedido sin desafío ni penalidad.

### Por qué se integra así y no de otra forma

- No toca la lógica de pedidos, nivel, ni Turno Intensivo — es una pausa
  entre "apretaste Enter" y "el pedido efectivamente se sirve", así que
  combina con cualquier otro modo prendido (podés tener Turno Intensivo +
  Modo Memoria + Modo Estación juntos si querés el combo más exigente).
- Usa la misma tabla de estadísticas de confusión que ya existía, en vez de
  inventar un sistema de puntaje paralelo — un solo lugar para ver "qué me
  cuesta", ya sea por olvido o por armado.

### Ajuste a Modo Memoria (de la revisión pedida)

Al analizar Modo Memoria para esta vuelta se encontró un problema: espiar
(mantener Espacio) no tenía costo real — se podía mantener la pantalla
revelada todo el tiempo spameando la tecla, lo que vacía de sentido la
recuperación activa. Se agregó un **enfriamiento de 4 segundos entre
espiadas** (`PEEK_COOLDOWN_MS`): cada chequeo cuesta un respiro real antes
del próximo, en vez de ser gratis.

### Progresión de los pedidos

También se ajustó cuántos ítems puede traer un pedido: antes, desde el nivel
1 ya podían salir pedidos de hasta 4 productos distintos, lo cual no es
realista para alguien recién empezando. Ahora el tamaño máximo crece de a
poco — 2 ítems los primeros niveles, y un ítem más cada 3 niveles, hasta
llegar al tope de siempre (5) alrededor del nivel 10.

## Practicá lo físico en casa (esto no lo reemplaza ninguna pantalla)

La guía de seguridad de tostadoras y el procedimiento de envoltorio (arriba)
son movimiento de manos, no memoria. Si en tu casa envolvés algo del tamaño
de una hamburguesa con papel de McDonald's real (o cualquier papel del mismo
tamaño) y repetís el pliegue de la sección 1.7 hasta que te sale sin pensar,
eso SÍ transfiere directo al turno — es exactamente la misma lógica de
"editar mapas" pero para las manos en vez de para la cabeza. La pantalla te
entrena qué va en cada producto; el papel en tu casa te entrena cómo se
arma con las manos. Las dos partes juntas son "dominar la estación".

## Fuente

Guía de Entrenamiento Iniciador/Ensamblador — Área de Producción, Agosto
2022 (documento interno, 38 páginas). Todas las cantidades de esta página
están citadas tal cual figuran ahí.
