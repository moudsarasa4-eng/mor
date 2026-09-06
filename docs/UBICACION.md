# Ubicación — reglas geográficas del Motor de Jackpots

Documento único de referencia para todo lo relacionado a zona/distancia/transporte,
para no tener que buscarlo repartido en `config.yaml`, `app/geography.py` y
`app/exclusions.py`.

## Punto de partida

- **Candidato:** Marco Ammazzalorso
- **Dirección base:** Rosas Castillo 1698, Hurlingham, Provincia de Buenos Aires, Argentina
- Usada por `app/geocoding.py` (Nominatim/OpenStreetMap) como origen para calcular
  distancia en línea recta a cada empresa candidata.

## Reglas duras (nunca se negocian)

1. **CABA (Capital Federal) está completamente prohibida.** Ninguna empresa ubicada
   en Capital Federal se promueve como candidata, sin excepción. Verificado por
   `app/exclusions.py::es_zona_prohibida()`.
2. **Máximo 50 minutos netos de viaje** en colectivo/tren. No es un límite de
   distancia en km, es de tiempo de viaje real.
3. **Homónimos de otra provincia/país descartan automáticamente** (ej. "Caseros,
   Salta" no es "Caseros, Buenos Aires"; "Trujillo" en Perú no es una zona
   argentina). Ver `PATRONES_NO_EMPRESA` en `app/discovery.py` y las exclusiones
   de query en `app/keywords.py::EXCLUSIONES_QUERY`.

## Zonas de búsqueda (orden de prioridad, `config.yaml`)

| Anillo | Localidades |
|---|---|
| Cercana | Hurlingham, Morón, El Palomar, Caseros, Martín Coronado, Villa Tesei |
| Media | Haedo, Ramos Mejía, William Morris, Santos Lugares, Bella Vista, San Miguel, Muñiz |
| Extendida | José C. Paz, Moreno, Ciudadela, Tres de Febrero |

El motor busca en este orden: agota (satura) el anillo cercano antes de pasar
al siguiente. Una zona se considera "saturada" tras 5 búsquedas seguidas sin
encontrar empresas nuevas (`saturation_rounds` en `config.yaml`).

## Caza industrial (CLAE) — partidos habilitados

`config.yaml::caza_industrial.partidos`: Morón, Hurlingham, Merlo, Ituzaingó.

## Transporte de referencia

**Línea San Martín** (columna vertebral geográfica, `app/geography.py`), de
Retiro hacia el oeste — Hurlingham es la estación de referencia (índice 0):

```
Retiro → Palermo → Villa Crespo → La Paternal → Villa del Parque → Devoto →
Sáenz Peña → Santos Lugares → Caseros → El Palomar → HURLINGHAM →
William Morris → Bella Vista → Muñiz → San Miguel → José C. Paz →
Sol y Verde → Derqui → Villa Astolfi → Pilar → Manzanares → Dr. Cabred
```

Nota: aunque Retiro está en la lista (es la cabecera de la línea), las
estaciones dentro de CABA quedan excluidas igual por la regla dura de zona
prohibida — la lista existe para calcular distancia entre estaciones, no
para habilitar búsqueda ahí.

**Colectivos prioritarios** (orden de investigación, no ranking de calidad —
el motor puede reordenar esto con datos reales de qué línea da mejores
resultados):

1. Tren Línea San Martín
2. Colectivo 182
3. Colectivo 320
4. Colectivo 237
5. Colectivo 463

## Cómo se calcula la distancia real

1. `app/geocoding.py` geocodifica la dirección de la empresa vía Nominatim
   (OpenStreetMap, gratis, 1 req/seg) → lat/lon.
2. `distancia_haversine_metros()` calcula distancia en línea recta desde
   Rosas Castillo 1698.
3. `app/geography.py::estacion_mas_cercana()` calcula la estación de la Línea
   San Martín más cercana a esa empresa y estima minutos de caminata (a 5
   km/h). **No calcula ruta real de colectivo/tren** (necesitaría Google
   Directions pago o GTFS+OpenTripPlanner) — es una aproximación en línea
   recta, pensada para descartar candidatas obviamente inaccesibles, no para
   reemplazar el criterio del usuario sobre el viaje real.

## Dónde se usa esto en el código

- `config.yaml` — fuente de verdad de zonas/dirección/partidos.
- `app/exclusions.py::es_zona_prohibida()` — bloqueo duro de CABA.
- `app/geocoding.py` — geocodificación + distancia en línea recta.
- `app/geography.py` — Línea San Martín, estación más cercana, accesibilidad.
- `app/discovery.py` — filtra homónimos de otras provincias/países por nombre.
- `app/ronda_presencial.py` — ordena candidatas por `distancia_km` real para
  armar la ronda de visita a pie/colectivo.
