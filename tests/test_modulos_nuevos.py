"""Tests unitarios de los módulos agregados después del pipeline principal:
exclusiones, salarios de referencia, backup, y las funciones puras de
geocoding/site_check que no requieren red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_exclusion_cadena_detecta_variantes():
    from app.exclusions import es_cadena_excluida
    assert es_cadena_excluida("Carrefour Argentina SA") == "Carrefour"
    assert es_cadena_excluida("Supermercados DIA Argentina") == "Dia"
    assert es_cadena_excluida("Distribuidora El Roble SRL") is None


def test_es_agencia_rrhh_por_patron_generico():
    """No es una lista fija de marcas: detecta cualquier agencia de RRHH/
    staffing (chica, mediana o grande) por patrón en el nombre/descripción."""
    from app.exclusions import es_agencia_rrhh
    assert es_agencia_rrhh("Consultora XYZ de Recursos Humanos") is True
    assert es_agencia_rrhh("Personal Temporario del Oeste SRL") is True
    assert es_agencia_rrhh("Bolsa de Trabajo Zona Oeste") is True
    assert es_agencia_rrhh("Distribuidora Real del Oeste SRL") is False
    assert es_agencia_rrhh("") is False


def test_exclusion_zona_prohibida_caba():
    from app.exclusions import es_zona_prohibida
    assert es_zona_prohibida("CABA") == "CABA"
    assert es_zona_prohibida("Ciudad Autónoma de Buenos Aires") is not None
    assert es_zona_prohibida("Hurlingham") is None
    assert es_zona_prohibida("") is None
    assert es_zona_prohibida(None) is None


def test_salarios_referencia_devuelve_los_4_rubros():
    from app.salarios_referencia import estimar_sueldo
    for rubro in ["logistica", "administrativo", "atencion_cliente", "limpieza"]:
        r = estimar_sueldo(rubro)
        assert r is not None, f"falta referencia para {rubro}"
        assert r["min"] < r["max"]
        assert r["confianza"] in ("alta", "media", "baja")
        assert r["fuente"]  # nunca vacío: toda cifra debe tener fuente citada

    assert estimar_sueldo("rubro_inexistente") is None


def test_haversine_distancia_conocida():
    from app.geocoding import distancia_haversine_metros
    # Hurlingham vs Retiro (CABA), distancia real conocida ~24-25 km
    d_km = distancia_haversine_metros(-34.6167, -58.6372, -34.5924, -58.3742) / 1000
    assert 22 < d_km < 27


def test_contact_verify_mx():
    from app.contact_verify import dominio_tiene_mx, verificar_email
    assert dominio_tiene_mx("") is None
    assert verificar_email("no-es-un-email") is False
    assert verificar_email("") is False


def test_search_providers_registro():
    from app.search_providers import get_provider, PROVEEDORES
    assert "serper" in PROVEEDORES
    p = get_provider("serper")
    assert p.nombre == "serper"
    try:
        get_provider("inexistente")
        assert False, "debería haber lanzado ValueError"
    except ValueError:
        pass


def test_estacion_mas_cercana(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_estaciones.sqlite")
    db_module.init_db()

    import app.geocoding as geo

    coords_reales = {
        "Hurlingham": (-34.6167, -58.6372),
        "El Palomar": (-34.6122, -58.6161),
    }

    def mock_geocodificar(direccion):
        for nombre, (lat, lon) in coords_reales.items():
            if nombre in direccion:
                return geo.Coordenadas(lat=lat, lon=lon, direccion_encontrada=direccion)
        return None

    monkeypatch.setattr(geo, "geocodificar", mock_geocodificar)

    from app.geography import estacion_mas_cercana
    r = estacion_mas_cercana(-34.6180, -58.6380)  # muy cerca de Hurlingham
    assert r is not None
    assert r["estacion"] == "Hurlingham"
    assert r["distancia_metros"] < 500


def test_filtra_basura_real_encontrada_en_produccion():
    """Regresión: estos 17 casos exactos aparecieron en una corrida real del
    usuario y pasaban el filtro viejo — diccionarios, listicles, spam
    educativo en inglés, un aviso de empleo colado, un homónimo de otra
    provincia (Caseros = calle en Salta), perfil de Instagram, directorios."""
    from app.discovery import extraer_candidatas
    casos_basura = [
        ("Concesionaria en Caseros en Cylex", "https://www.cylex.com.ar/x"),
        ("Shouer (@shouer.arg) • Instagram photos and videos", "https://www.instagram.com/shouer.arg/"),
        ("principales - Definición - WordReference.com", "https://www.wordreference.com/x"),
        ("principales - Wiktionary, the free dictionary", "https://en.wiktionary.org/wiki/principales"),
        ("PRINCIPALES Definition & Meaning - Merriam-Webster", "https://www.merriam-webster.com/x"),
        ("LOS40: noticias musicales y radio online con todos los éxitos", "https://los40.com/"),
        ("Definición - principal | Diccionario de la lengua española", "https://dle.rae.es/principal"),
        ("52 Cosas Rentables para Fabricar y Vender desde Casa en 2026", "https://blog.com/negocios"),
        ("Las 32 mejores ideas de negocios pequeños rentables en 2026", "https://blog.com/ideas"),
        ("20 ideas de negocios caseros y de bajo costo - ENTER.CO", "https://enter.co/x"),
        ("Vendedor tecnico de Mostrador - Zona Caseros", "https://algunportal.com.ar/aviso/123"),
        ("Hotel Caseros Salta | Alojamiento con encanto en el centro", "https://hotelcaserossalta.com.ar/"),
        ("10 tipos de servicio al cliente que debes conocer - Zendesk", "https://www.zendesk.com/blog/x"),
        ("Empresas", "https://algunsitio.com.ar/"),
        ("Contacto para empresas", "https://algunsitio.com.ar/contacto"),
        ("Best Affordable Online Nursing Programs of 2026 - BestColleges", "https://www.bestcolleges.com/x"),
        ("Abogados y Estudios Jurídicos en Caseros - CercanoOeste.com", "https://www.cercanooeste.com/x"),
    ]
    mock = {"organic": [{"title": t, "link": u, "snippet": ""} for t, u in casos_basura]}
    r = extraer_candidatas(mock, "Caseros")
    assert len(r) == 0, f"basura que no se filtró: {[c['nombre_crudo'] for c in r]}"

    casos_reales = [
        ("Metalúrgica Tesei S.A.", "https://www.metalurgicatesei.com.ar/"),
        ("Distribuidora Real del Oeste SRL", "https://distrealoeste.com.ar/"),
        ("Empresa X SA", "https://empresax.com.ar/"),
    ]
    mock2 = {"organic": [{"title": t, "link": u, "snippet": ""} for t, u in casos_reales]}
    r2 = extraer_candidatas(mock2, "Caseros")
    assert len(r2) == 3, "no debería filtrar empresas reales por error"


def test_dominio_excluido_no_hace_falsos_positivos():
    """Regresión: 'x.com' (Twitter/X) como substring bloqueaba cualquier
    dominio que terminara en 'x.com...', como 'empresax.com.ar'."""
    from app.discovery import _es_dominio_excluido
    assert _es_dominio_excluido("https://empresax.com.ar/") is False
    assert _es_dominio_excluido("https://twitter.com/algo") is True
    assert _es_dominio_excluido("https://x.com/algo") is True
    assert _es_dominio_excluido("https://ar.bumeran.com/x") is True
    assert _es_dominio_excluido("https://facebook.com/photo/x") is True
    assert _es_dominio_excluido("https://facebook.com/empresareal") is False


def test_extraer_keywords_de_texto_sin_stopwords_sueltas():
    from app.discovery import extraer_keywords_de_texto
    r = extraer_keywords_de_texto("brindamos servicio de limpieza de trenes y flota vehicular")
    assert r  # encontró algo
    for frase in r:
        assert not frase.endswith(" de"), f"frase mal cortada: {frase!r}"
        assert "de de" not in frase


def test_site_check_extraer_dominio():
    from app.site_check import extraer_dominio
    assert extraer_dominio("https://www.empresa.com.ar/pagina") == "empresa.com.ar"
    assert extraer_dominio("https://otra.com.ar") == "otra.com.ar"
    assert extraer_dominio("") == ""
    assert extraer_dominio(None) == ""


def test_backup_crea_y_limpia_viejos(tmp_path, monkeypatch):
    """Bug real encontrado en esta auditoría: backup.py fijaba DB_PATH/
    BACKUPS_DIR una sola vez al importar el módulo (from app.db import
    DB_PATH), así que monkeypatchear app.db.DB_PATH en un test no lo movía —
    hacer_backup() seguía usando la base REAL del repo. De hecho quedó un
    backup huérfano real en data/backups/ de una corrida de tests anterior,
    confirmando que pasaba de verdad. Ahora backup.py resuelve db.DB_PATH en
    cada llamada, así que alcanza con monkeypatchear app.db.DB_PATH, sin
    tocar nada dentro de app.backup."""
    import app.db as db_module
    db_path = tmp_path / "database.sqlite"
    monkeypatch.setattr(db_module, "DB_PATH", db_path)
    db_module.init_db()

    import app.backup as backup_module
    monkeypatch.setattr(backup_module, "MAX_BACKUPS", 3)

    import time
    archivos = []
    for _ in range(5):
        archivos.append(backup_module.hacer_backup())
        time.sleep(1.1)  # el nombre del backup usa resolución de segundos

    restantes = list((tmp_path / "backups").glob("database_*.sqlite"))
    assert len(restantes) == 3, "debería quedarse solo con los últimos MAX_BACKUPS"
    for a in archivos:
        assert str(tmp_path) in a  # confirma que escribió en la base de TEST, no en la real

    restaurado = backup_module.restaurar_ultimo_backup()
    assert restaurado is not None


def test_promote_no_reprocesa_excluidas_en_corridas_futuras(tmp_path, monkeypatch):
    """Regresión: las candidatas excluidas por cadena/zona quedaban con
    company_id NULL para siempre, así que se re-evaluaban en cada llamada a
    promover_candidatas — cada vez más lento a medida que se acumulan."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_no_reproceso.sqlite")
    db_module.init_db()

    import app.search_client as sc
    import app.site_check as scheck

    def mock_buscar(query, **kwargs):
        return {"organic": [{"title": "Carrefour Argentina", "link": "https://carrefour.com.ar/", "snippet": "super"}]}
    monkeypatch.setattr(sc, "buscar", mock_buscar)
    monkeypatch.setattr(scheck, "sitio_activo", lambda url: True)

    from app.discovery import ejecutar_query
    from app.promote import promover_candidatas

    ejecutar_query("empresas deposito Hurlingham", "Hurlingham", "TYPE_A", "depósito")
    r1 = promover_candidatas(zona="Hurlingham")
    assert r1["excluidas_cadena"] == 1

    r2 = promover_candidatas(zona="Hurlingham")  # sin descubrir nada nuevo
    assert r2["candidatas_evaluadas"] == 0, "no debería re-evaluar la misma excluida de nuevo"


def test_contact_finder_no_reintenta_empresa_sin_contacto(tmp_path, monkeypatch):
    """Regresión: si no se encuentra contacto, la empresa se re-consultaba en
    cada corrida futura, gastando presupuesto sin avanzar."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_no_reintento.sqlite")
    db_module.init_db()

    from app.company import upsert_company

    cid = upsert_company("Empresa Sin Contacto SA", "logistica", "Hurlingham")

    import app.search_client as sc
    llamadas = {"n": 0}

    def mock_buscar(query, **kwargs):
        llamadas["n"] += 1
        return {"organic": [{"title": "sin info util", "link": "https://x-random.com.ar/", "snippet": "nada de contacto acá"}]}
    monkeypatch.setattr(sc, "buscar", mock_buscar)

    from app.contact_finder import correr_lote

    r1 = correr_lote(zona="Hurlingham")
    assert r1["procesadas"] == 1
    assert r1["contactos_encontrados"] == 0
    assert llamadas["n"] == 1

    r2 = correr_lote(zona="Hurlingham")  # segunda corrida: no debería re-intentar
    assert r2["procesadas"] == 0, "no debería volver a elegir la misma empresa sin contacto"
    assert llamadas["n"] == 1, "no debería haber gastado una query más"


def test_loop_investigacion_no_se_queda_idle_si_geo_saturada(tmp_path, monkeypatch):
    """Regresión: si TODAS las zonas geográficas están saturadas, el motor
    antes cortaba el ciclo entero sin llegar a correr industrial/supplier/
    contacto, aunque esas fuentes sí tuvieran trabajo pendiente. Reportado
    por el usuario en producción (237 descubiertas, 0 nuevas apareciendo)."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_saturacion.sqlite")
    db_module.init_db()

    import app.runner as runner_module
    from app.db import get_conn, now

    # saturar TODAS las zonas geográficas configuradas
    conn = get_conn()
    for z in runner_module.orden_zonas():
        for _ in range(runner_module.CONFIG["discovery"]["saturation_rounds"]):
            conn.execute(
                "INSERT INTO queries_log (query, zona, keyword, tipo, resultados, empresas_nuevas, "
                "duplicados, yield, creado_en) VALUES ('x', ?, '', 'TYPE_A', 5, 0, 5, 0, ?)",
                (z, now()),
            )
    conn.commit()
    conn.close()

    assert runner_module.siguiente_zona_no_saturada() is None  # confirma el escenario

    import app.search_client as sc
    import app.site_check as scheck
    contador = {"n": 0}

    def mock_buscar(query, **kwargs):
        contador["n"] += 1
        return {"organic": [{"title": f"Empresa Nueva {contador['n']} SA",
                              "link": f"https://empresanueva{contador['n']}.com.ar/", "snippet": "fabrica"}]}
    monkeypatch.setattr(sc, "buscar", mock_buscar)
    monkeypatch.setattr(scheck, "sitio_activo", lambda url: True)

    runner_module.loop_investigacion(max_ciclos=8)

    conn = get_conn()
    total_companies = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    conn.close()
    assert total_companies > 0, "con geo saturada, industrial/supplier/contacto deben seguir corriendo"


def test_promote_excluye_cadena_y_zona_prohibida(tmp_path, monkeypatch):
    """Test de integración chico: confirma que promote.py realmente usa
    exclusions.py, no solo que exclusions.py funciona aislado."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.search_client as sc
    import app.site_check as scheck

    def mock_buscar(query, **kwargs):
        return {"organic": [
            {"title": "Carrefour Argentina", "link": "https://carrefour.com.ar/", "snippet": "super"},
            {"title": "Distribuidora Real SRL", "link": "https://distreal.com.ar/", "snippet": "distribuidora"},
        ]}
    monkeypatch.setattr(sc, "buscar", mock_buscar)
    monkeypatch.setattr(scheck, "sitio_activo", lambda url: True)

    from app.discovery import ejecutar_query
    from app.promote import promover_candidatas

    ejecutar_query("empresas deposito Hurlingham", "Hurlingham", "TYPE_A", "depósito")
    r = promover_candidatas(zona="Hurlingham")

    assert r["excluidas_cadena"] == 1
    assert r["promovidas"] == 1

    conn = db_module.get_conn()
    nombres = [row["nombre"] for row in conn.execute("SELECT nombre FROM companies")]
    conn.close()
    assert "Distribuidora Real SRL" in nombres
    assert not any("Carrefour" in n for n in nombres)


def test_marcar_jackpot_simplificado(tmp_path, monkeypatch):
    """El comando main.py score requiere ~15 parámetros que nadie llena a
    mano — por eso 'jackpots' quedaba siempre en 0. marcar_jackpot() es el
    camino simplificado real: se usa después de revisar el .txt exportado."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.company import upsert_company, marcar_jackpot
    cid = upsert_company("Metalúrgica Tesei SRL", "logistica", "Hurlingham")

    marcar_jackpot(cid, puesto="Ayudante de depósito", chances_estimadas=70,
                    motivo="Sitio propio activo, email de administración con MX OK, sin señales negativas",
                    sueldo_min=900000, sueldo_max=1200000, sueldo_fuente="salarios_referencia.py")

    conn = db_module.get_conn()
    row = conn.execute("SELECT estado FROM companies WHERE id=?", (cid,)).fetchone()
    score = conn.execute("SELECT chances_estimadas, puesto_objetivo FROM scores WHERE company_id=?", (cid,)).fetchone()
    conn.close()
    assert row["estado"] == "jackpot"
    assert score["chances_estimadas"] == 70
    assert score["puesto_objetivo"] == "Ayudante de depósito"


def test_ultima_tanda_inicio_se_registra_y_filtra(tmp_path, monkeypatch):
    """runner.loop_investigacion debe marcar el inicio de cada tanda en
    run_state para que el dashboard pueda mostrar 'solo lo de esta corrida'."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    conn = db_module.get_conn()
    antes = conn.execute("SELECT ultima_tanda_inicio FROM run_state WHERE id=1").fetchone()
    assert antes["ultima_tanda_inicio"] is None
    conn.close()

    import app.runner as runner
    runner.loop_investigacion(max_ciclos=0)  # 0 ciclos: solo debe marcar inicio y salir

    conn = db_module.get_conn()
    despues = conn.execute("SELECT ultima_tanda_inicio FROM run_state WHERE id=1").fetchone()
    conn.close()
    assert despues["ultima_tanda_inicio"] is not None


def test_export_manual_no_se_bloquea_por_auto_export_previo(tmp_path, monkeypatch):
    """Bug real: el botón manual de exportar usaba solo_nuevas=True, así que
    si el ciclo automático ya había exportado (y marcado exportada_txt=1),
    el botón devolvía 'nada para exportar' aunque hubiera candidatas
    pendientes de revisión sin outreach todavía."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.company import upsert_company
    cid = upsert_company("Distribuidora Real del Oeste SRL", "logistica", "Hurlingham")
    conn = db_module.get_conn()
    conn.execute("UPDATE companies SET estado='candidata', exportada_txt=1 WHERE id=?", (cid,))
    conn.commit()
    conn.close()

    from app.export_txt import exportar_candidatas_txt
    import app.export_txt as et
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    monkeypatch.setattr(et, "_carpeta_descargas", lambda: downloads)

    sin_filtro = exportar_candidatas_txt(solo_nuevas=True)
    assert sin_filtro is None  # reproduce el bug: ya estaba marcada como exportada

    con_fix = exportar_candidatas_txt(solo_nuevas=False)
    assert con_fix is not None
    assert "Distribuidora Real del Oeste" in Path(con_fix).read_text(encoding="utf-8")


def test_origen_contacto_presencial_se_prioriza_en_export(tmp_path, monkeypatch):
    """Históricamente el canal de mayor conversión para estos rubros es
    referido/presencial, no un hallazgo web frío — el export debe listar
    primero las marcadas como 'presencial'."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.company import upsert_company
    upsert_company("Encontrada Por Web SRL", "logistica", "Hurlingham", origen_contacto="web")
    conn = db_module.get_conn()
    conn.execute("UPDATE companies SET estado='candidata' WHERE nombre='Encontrada Por Web SRL'")
    conn.commit()
    conn.close()

    upsert_company("Grupo OL", "administrativo", "Hurlingham", origen_contacto="presencial")
    conn = db_module.get_conn()
    conn.execute("UPDATE companies SET estado='candidata' WHERE nombre='Grupo OL'")
    conn.commit()
    conn.close()

    from app.export_txt import exportar_candidatas_txt
    import app.export_txt as et
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    monkeypatch.setattr(et, "_carpeta_descargas", lambda: downloads)

    ruta = exportar_candidatas_txt(solo_nuevas=False)
    contenido = Path(ruta).read_text(encoding="utf-8")
    assert contenido.index("Grupo OL") < contenido.index("Encontrada Por Web SRL")
    assert "[REFERIDO/PRESENCIAL]" in contenido


def test_ronda_presencial_ordena_por_distancia(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.company import upsert_company
    for nombre, dist in [("Lejos SRL", 8.0), ("Cerca SRL", 1.5)]:
        cid = upsert_company(nombre, "logistica", "Hurlingham")
        conn = db_module.get_conn()
        conn.execute(
            "UPDATE companies SET estado='candidata', direccion=?, distancia_km=?, "
            "contacto_intentado_sin_resultado=1 WHERE id=?",
            (f"Calle Falsa {dist}", dist, cid),
        )
        conn.commit()
        conn.close()

    from app.ronda_presencial import generar_ronda
    ronda = generar_ronda()
    assert [r["nombre"] for r in ronda] == ["Cerca SRL", "Lejos SRL"]


def test_overpass_descubre_y_filtra(tmp_path, monkeypatch):
    """Overpass es una fuente independiente de Serper (no gasta presupuesto,
    no depende de texto de búsqueda) — busca por categoría/radio real."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.geocoding as geocoding
    from app.geocoding import Coordenadas
    monkeypatch.setattr(geocoding, "geocodificar", lambda direccion: Coordenadas(lat=-34.59, lon=-58.63, direccion_encontrada=direccion))

    import app.overpass_discovery as ovp

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"elements": [
                {"tags": {"name": "Metalúrgica Tesei SRL", "office": "yes", "addr:street": "Calle Falsa", "addr:housenumber": "123"}},
                {"tags": {"name": "Carrefour Argentina", "shop": "supermarket"}},  # cadena excluida
                {"tags": {"name": "Definición de trabajo", "office": "yes"}},  # no parece empresa
                {"tags": {}},  # sin nombre, se ignora
            ]}

    monkeypatch.setattr(ovp.requests, "post", lambda *a, **kw: FakeResp())

    r = ovp.buscar_por_zona("Hurlingham")
    assert r["nuevas"] == 1
    assert r["descartadas"] == 2

    conn = db_module.get_conn()
    nombres = [row["nombre_crudo"] for row in conn.execute("SELECT nombre_crudo FROM discovered_companies_raw")]
    conn.close()
    assert nombres == ["Metalúrgica Tesei SRL"]


def test_overpass_respeta_zona_prohibida(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.overpass_discovery as ovp
    r = ovp.buscar_por_zona("Capital Federal")
    assert r["nuevas"] == 0
    assert "prohibida" in r["error"]


def test_loop_investigacion_corre_overpass_y_no_lo_repite(tmp_path, monkeypatch):
    """Overpass está enganchado como 5ta fuente del ciclo automático: debe
    correr una zona por ciclo (no gasta presupuesto de Serper) y no
    repetirla en el siguiente ciclo, gracias a overpass_progress."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.runner as runner_module
    import app.geocoding as geocoding
    from app.geocoding import Coordenadas
    import app.overpass_discovery as ovp

    monkeypatch.setattr(geocoding, "geocodificar", lambda direccion: Coordenadas(lat=-34.59, lon=-58.63, direccion_encontrada=direccion))

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"elements": [{"tags": {"name": "Depósito Overpass SRL", "industrial": "yes"}}]}

    monkeypatch.setattr(ovp.requests, "post", lambda *a, **kw: FakeResp())

    import app.search_client as sc
    monkeypatch.setattr(sc, "buscar", lambda query, **kw: {"organic": []})  # sin resultados de Serper, para aislar overpass

    import app.directorio_dir_ar as dda
    monkeypatch.setattr(dda, "_fetch", lambda url: None)  # aislar: no queremos que compita por presupuesto de ciclos en este test

    # las fuentes gratis ahora también cuentan contra el límite de ciclos de
    # la corrida (para que el loop no recorra TODAS las zonas de una sola
    # llamada) — con max_ciclos=1 alcanza justo para 1 acción gratis.
    runner_module.loop_investigacion(max_ciclos=1)

    conn = db_module.get_conn()
    nombres = [r["nombre"] for r in conn.execute("SELECT nombre FROM companies")]
    zonas_corridas = [r["zona"] for r in conn.execute("SELECT zona FROM overpass_progress")]
    conn.close()
    assert "Depósito Overpass SRL" in nombres
    assert len(zonas_corridas) == 1  # una sola zona por ciclo, no todas de una


def test_loop_investigacion_no_corre_dos_veces_en_paralelo(tmp_path, monkeypatch):
    """Bug real: el modo automático (scheduler.py) y el botón manual
    (iniciar_en_background) llamaban a loop_investigacion desde threads
    distintos sin ningún lock compartido — podían pisarse sobre el mismo
    SQLite. Ahora un segundo llamado mientras el primero sigue activo debe
    ser un no-op inmediato."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.runner as runner_module
    runner_module._loop_activo.acquire()  # simula que ya hay una tanda corriendo
    try:
        runner_module.loop_investigacion(max_ciclos=5)  # no debería tocar nada
    finally:
        runner_module._loop_activo.release()

    from app.run_state import get_state
    assert get_state()["ultima_tanda_inicio"] is None  # ni siquiera llegó a marcar el inicio


def test_contact_finder_marca_intentado_si_falla_la_busqueda(tmp_path, monkeypatch):
    """Bug real: si search_client.buscar fallaba (SearchClientError), la
    empresa quedaba elegible para reintento en TODAS las corridas futuras
    para siempre, sin gastar presupuesto ni marcarse como intentada."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.company import upsert_company
    cid = upsert_company("Empresa Sin Contacto SA", "logistica", "Hurlingham")

    import app.contact_finder as cf
    import app.search_client as sc

    def falla(query, **kw):
        raise sc.SearchClientError("timeout simulado")
    monkeypatch.setattr(sc, "buscar", falla)

    resultado = cf.buscar_contacto(cid, "Empresa Sin Contacto SA", "Hurlingham")
    assert resultado is None

    conn = db_module.get_conn()
    row = conn.execute("SELECT contacto_intentado_sin_resultado FROM companies WHERE id=?", (cid,)).fetchone()
    queries = conn.execute("SELECT COUNT(*) c FROM queries_log").fetchone()["c"]
    conn.close()
    assert row["contacto_intentado_sin_resultado"] == 1
    assert queries == 1  # la falla debe contar contra el presupuesto igual que un éxito


def test_correr_lote_no_duplica_descuento_de_pendientes_restantes(tmp_path, monkeypatch):
    """Bug real (industrial_discovery y supplier_discovery, mismo patrón):
    pendientes_restantes restaba len(resultados) de un pendientes() que YA
    excluía lo recién procesado, subestimando (o directamente diciendo mal)
    cuánto queda."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.supplier_discovery as sd
    monkeypatch.setattr(sd, "CATEGORIAS_PRODUCTO", ["a", "b", "c", "d", "e"])

    def mock_ejecutar_query(query, zona, tipo, keyword):
        conn = db_module.get_conn()
        conn.execute(
            "INSERT INTO queries_log (query, zona, keyword, tipo, resultados, empresas_nuevas, duplicados, yield, creado_en) "
            "VALUES (?, ?, ?, ?, 0, 0, 0, 0, ?)",
            (query, zona, keyword, tipo, db_module.now()),
        )
        conn.commit()
        conn.close()
        return {"empresas_nuevas": 0}
    monkeypatch.setattr(sd, "ejecutar_query", mock_ejecutar_query)
    monkeypatch.setattr(sd, "promover_candidatas", lambda zona: None)

    r = sd.correr_lote("Hurlingham", max_categorias=2)
    assert r["procesadas"] == 2
    assert r["pendientes_restantes"] == 3  # 5 totales - 2 procesadas, no 5-2-2=1


def test_site_crawler_extrae_mailto_y_ldjson():
    """El crawler debe preferir datos schema.org (publicados explícitamente
    por la empresa) y si no hay, el primer mailto: real del HTML — nunca
    inventa ni adivina un email por patrón (ej. info@dominio.com)."""
    import app.site_crawler as sitecrawler

    html_con_ldjson = '''
    <html><body>
    <script type="application/ld+json">{"@type": "Organization", "email": "administracion@fabrica.com.ar", "telephone": "+54 11 4444-5555"}</script>
    <a href="mailto:otro@fabrica.com.ar">Escribinos</a>
    </body></html>
    '''
    monkeypatched = sitecrawler._fetch
    sitecrawler._fetch = lambda url: html_con_ldjson if url == "https://fabrica.com.ar" else None
    try:
        r = sitecrawler.extraer_contacto_de_sitio("fabrica.com.ar")
    finally:
        sitecrawler._fetch = monkeypatched

    assert r["email"] == "administracion@fabrica.com.ar"  # ld+json gana sobre el mailto:
    assert r["telefono"] == "+54 11 4444-5555"


def test_site_crawler_prueba_rutas_de_contacto_si_home_no_tiene_nada(monkeypatch):
    import app.site_crawler as sitecrawler

    def fake_fetch(url):
        if url == "https://taller.com.ar/contacto":
            return '<html><a href="mailto:info@taller.com.ar">mail</a></html>'
        return "<html>sin nada de contacto</html>"
    monkeypatch.setattr(sitecrawler, "_fetch", fake_fetch)

    r = sitecrawler.extraer_contacto_de_sitio("taller.com.ar")
    assert r["email"] == "info@taller.com.ar"
    assert r["fuente_url"] == "https://taller.com.ar/contacto"


def test_site_crawler_no_inventa_nada_si_no_hay_publicado(monkeypatch):
    import app.site_crawler as sitecrawler
    monkeypatch.setattr(sitecrawler, "_fetch", lambda url: "<html>nada de contacto acá</html>")
    assert sitecrawler.extraer_contacto_de_sitio("empresa-sin-contacto.com.ar") is None


def test_contact_finder_usa_sitio_propio_antes_que_buscar_por_snippet(tmp_path, monkeypatch):
    """El crawl al sitio propio debe intentarse primero (más preciso, gratis,
    sin gastar presupuesto de Serper) — solo cae a la búsqueda por snippet si
    no hay dominio conocido o el sitio no publica nada."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.company import upsert_company
    cid = upsert_company("Metalúrgica Tesei SRL", "logistica", "Hurlingham")

    import app.contact_finder as cf
    monkeypatch.setattr(cf, "extraer_contacto_de_sitio", lambda dominio: {
        "email": "administracion@tesei.com.ar", "telefono": None, "fuente_url": "https://tesei.com.ar/contacto",
    })

    import app.search_client as sc
    llamo_serper = {"n": 0}

    def no_deberia_llamarse(query, **kw):
        llamo_serper["n"] += 1
        return {"organic": []}
    monkeypatch.setattr(sc, "buscar", no_deberia_llamarse)

    r = cf.buscar_contacto(cid, "Metalúrgica Tesei SRL", "Hurlingham", dominio="tesei.com.ar")
    assert r["valor"] == "administracion@tesei.com.ar"
    assert r["prioridad"] == "sitio propio"
    assert llamo_serper["n"] == 0  # no debió gastar presupuesto de Serper


def test_no_repite_queries_ya_ejecutadas_en_la_misma_zona(tmp_path, monkeypatch):
    """Bug real: la lista de queries generada para una zona sale siempre en
    el mismo orden (keywords por prioridad), y cada corrida solo toma las
    primeras N (max_queries_per_zone) — sin filtrar lo ya ejecutado, el motor
    volvía a preguntar EXACTAMENTE lo mismo en cada corrida futura mientras
    la zona no llegara a saturarse, gastando presupuesto por resultados ya
    vistos."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.runner as runner_module
    from app.db import get_conn, now

    zona = "Hurlingham"
    lote_completo = runner_module._generar_lote_queries(zona)
    assert len(lote_completo) > 5

    # simular que ya se ejecutaron las primeras 3 queries de la lista
    conn = get_conn()
    for q in lote_completo[:3]:
        conn.execute(
            "INSERT INTO queries_log (query, zona, keyword, tipo, resultados, empresas_nuevas, duplicados, yield, creado_en) "
            "VALUES (?, ?, '', 'TYPE_A', 1, 0, 0, 0, ?)",
            (q["query"], zona, now()),
        )
    conn.commit()
    conn.close()

    lote_filtrado = runner_module._generar_lote_queries(zona)
    queries_filtradas = {q["query"] for q in lote_filtrado}
    for q in lote_completo[:3]:
        assert q["query"] not in queries_filtradas, "no debería repetir una query ya ejecutada para esta zona"
    assert len(lote_filtrado) == len(lote_completo) - 3


def test_categorias_producto_son_300_y_todas_unicas():
    """A pedido del usuario: la lista del método envolvente debe tener 300
    categorías reales, sin duplicados (un duplicado sería presupuesto
    gastado dos veces en la misma pregunta)."""
    import app.supplier_discovery as sd
    assert len(sd.CATEGORIAS_PRODUCTO) == 300
    assert len(set(sd.CATEGORIAS_PRODUCTO)) == 300


def test_overpass_marca_procesada_aunque_falle_geocodificar(tmp_path, monkeypatch):
    """Bug real: si geocodificar la zona fallaba, buscar_por_zona no la
    marcaba en overpass_progress — esa zona quedaba primera en
    zonas_pendientes() para siempre, y el ciclo automático la reintentaba
    cada hora sin avanzar NUNCA a las zonas siguientes."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.geocoding as geocoding
    monkeypatch.setattr(geocoding, "geocodificar", lambda direccion: None)  # simula fallo de red

    import app.overpass_discovery as ovp
    r = ovp.buscar_por_zona("Hurlingham")
    assert r["error"]

    conn = db_module.get_conn()
    marcada = conn.execute("SELECT 1 FROM overpass_progress WHERE zona=?", ("Hurlingham",)).fetchone()
    conn.close()
    assert marcada is not None, "debe marcarse como procesada aunque haya fallado, para no bloquear el resto de las zonas"

    assert "Hurlingham" not in ovp.zonas_pendientes(["Hurlingham", "Moron"])


def test_site_crawler_cae_a_http_si_https_no_carga(monkeypatch):
    """Muchos sitios chicos/viejos no tienen SSL — si https ni siquiera carga
    la home, hay que probar http antes de descartar el sitio entero."""
    import app.site_crawler as sitecrawler

    def fake_fetch(url):
        if url.startswith("https://"):
            return None  # simula que https no responde (sin SSL)
        if url == "http://tallerviejo.com.ar":
            return '<html><a href="mailto:contacto@tallerviejo.com.ar">mail</a></html>'
        return None
    monkeypatch.setattr(sitecrawler, "_fetch", fake_fetch)

    r = sitecrawler.extraer_contacto_de_sitio("tallerviejo.com.ar")
    assert r["email"] == "contacto@tallerviejo.com.ar"
    assert r["fuente_url"].startswith("http://")


def test_dashboard_fmt_sueldo_marca_estimado():
    """Bug real: la variable 'prefijo' en _fmt_sueldo nunca se usaba (era ''
    en los dos casos), así que un sueldo estimado se mostraba igual que uno
    verificado — sin la aclaración '(estimado)' que sí tiene detalle()."""
    import app.dashboard as dashboard

    fila_estimado = {"sueldo_min": 900000, "sueldo_max": 1200000, "sueldo_es_estimado": 1}
    fila_verificado = {"sueldo_min": 900000, "sueldo_max": 1200000, "sueldo_es_estimado": 0}

    assert "(estimado)" in dashboard._fmt_sueldo(fila_estimado)
    assert "(estimado)" not in dashboard._fmt_sueldo(fila_verificado)


def test_dedupe_ignora_diferencia_de_acentos():
    """Bug real encontrado en producción: 'Logística Caseros srl' (con tilde)
    e 'Logistica Caseros SRL' (sin tilde) se promovían como 2 empresas
    separadas — la misma real, solo escrita distinto en cada fuente."""
    from app.discovery import _normalizar_para_dedupe
    assert _normalizar_para_dedupe("Logística Caseros srl") == _normalizar_para_dedupe("Logistica Caseros SRL")

    from app.promote import _nucleo_nombre
    assert _nucleo_nombre("Logística Caseros srl (@logisticacaseros)") == _nucleo_nombre("Logistica Caseros SRL")


def test_promote_no_duplica_variantes_con_y_sin_acento(tmp_path, monkeypatch):
    """Test de integración del bug real de arriba: promover ambas variantes
    en la misma zona debe terminar en UNA sola empresa, no dos."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.search_client as sc
    import app.site_check as scheck

    def mock_buscar(query, **kwargs):
        return {"organic": [
            {"title": "Logística Caseros srl", "link": "https://instagram.com/logisticacaseros/", "snippet": "transporte"},
        ]}
    monkeypatch.setattr(sc, "buscar", mock_buscar)
    monkeypatch.setattr(scheck, "sitio_activo", lambda url: True)

    from app.discovery import ejecutar_query
    from app.promote import promover_candidatas

    ejecutar_query("logistica Caseros", "Caseros", "TYPE_A", "logística")
    promover_candidatas(zona="Caseros")

    def mock_buscar_2(query, **kwargs):
        return {"organic": [
            {"title": "Logistica Caseros SRL", "link": "https://logistica.dir.ar/empresa/logistica-caseros-srl.html", "snippet": "transporte"},
        ]}
    monkeypatch.setattr(sc, "buscar", mock_buscar_2)
    ejecutar_query("logistica Caseros distribucion", "Caseros", "TYPE_A", "distribución")
    promover_candidatas(zona="Caseros")

    conn = db_module.get_conn()
    total = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    conn.close()
    assert total == 1, "las dos variantes (con y sin tilde) son la misma empresa real"


def test_nuevos_dominios_de_directorios_y_saas_excluidos():
    """Reproduce dominios reales encontrados en la corrida de producción del
    2026-09-06 que se colaban: portales de empleo, registros de empresas
    extranjeros, SaaS de facturación, inmobiliarias, blogs genéricos."""
    from app.discovery import _es_dominio_excluido
    casos = [
        "https://www.opcionempleo.com.ar/trabajo-operador-logistica/Caseros",
        "https://www.emis.com/php/company-profile/AR/x.html",
        "https://datok.com.ar/empresa/30540806728",
        "https://www.dunsguide.com/es/companies/x",
        "https://www.arempresas.com/location/Caseros",
        "https://www.starofservice.com.ar/dir/x",
        "https://es.cybo.com/AR/caseros/industria/",
        "https://caseros.licuo.com.ar/empresas-en_caseros.htm",
        "https://www.argentino.com.ar/caseros-buenos-aires/x",
        "https://openhousebsas.org/catalogo/x",
        "https://www.buscainmueble.com/oficina-en-venta-x",
        "https://facturasimple.com/",
        "https://www.csfacturacion.com/",
        "https://cnpj.biz/empresas",
        "https://www.rues.org.co/",
        "https://www.universidadperu.com/empresas/x.php",
        "https://latinbiz.substack.com/p/x",
        "https://contadormype.pe/",
        "https://www.oerproject.com/OER-Materials/x",
        "https://archive.epa.gov/water/archive/x",
        "https://mapcarta.com/W321490578",
    ]
    for url in casos:
        assert _es_dominio_excluido(url), f"debería excluirse: {url}"


def test_pais_extranjero_como_palabra_suelta_sin_en():
    """Reproduce 'Bos Perú', 'Contador Mype' (contadormype.pe): el país
    aparece sin el prefijo 'en' que exigía el patrón anterior."""
    from app.discovery import _parece_empresa
    assert not _parece_empresa("Bos Perú – Back Office Solutions", "Caseros")


def test_bella_vista_homonimos_de_varios_paises():
    """Bella Vista es homónimo de ciudades en EEUU (Arkansas/Missouri),
    México (Chiapas), Guatemala — encontrado en una corrida real con más de
    10 negocios legítimos pero ubicados en el país equivocado. El título solo
    ('FedEx Bella Vista') no lo dice, pero el snippet/URL sí — por eso
    _parece_empresa ahora también revisa texto_extra (snippet + URL)."""
    from app.discovery import _parece_empresa
    assert not _parece_empresa(
        "2025 ofertas de Black Friday en teléfonos en Bella Vista, AR", "Bella Vista",
        texto_extra="Ofertas de AT&T en Arkansas https://www.att.com/es-us/stores/arkansas/bella-vista/x",
    )
    assert not _parece_empresa(
        "Hotel Bella Vista", "Bella Vista",
        texto_extra="Hotel de 3 Estrellas en Catarina, Guatemala https://www.hotelsone.com/catarina-hotels-gt/x",
    )


def test_dominios_foraneos_por_tld():
    """Bloqueo genérico por ccTLD — mucho más robusto que enumerar sitios
    extranjeros uno por uno, para zonas con homónimos en varios países."""
    from app.discovery import _es_dominio_excluido
    assert _es_dominio_excluido("https://limpiezaparaalfombras.cl/x")
    assert _es_dominio_excluido("https://aliservicios.pe/x")
    assert not _es_dominio_excluido("https://www.empresareal.com.ar/")


def test_overpass_no_trae_comercios_irrelevantes():
    """Bug real: usar tags 'shop'/'office' SIN valor traía cualquier
    comercio (joyería, zapatería, peluquería, remisería) sin relación con
    los 4 rubros del CV. Ahora solo tags específicos y relevantes."""
    from app.overpass_discovery import TAGS_RELEVANTES
    claves_valores = set(TAGS_RELEVANTES)
    assert ("shop", None) not in claves_valores
    assert ("office", None) not in claves_valores
    assert ("shop", "supermarket") in claves_valores


def test_agencia_rrhh_con_conector_en_medio_de_la_frase():
    """Bug real: 'Servicios de Personal y Eventual de alta calidad' no
    matcheaba 'personal eventual' como frase fija — la 'y' en el medio
    rompe el substring."""
    from app.exclusions import es_agencia_rrhh
    assert es_agencia_rrhh("Servicios de Personal y Eventual de alta calidad para la Industria y el Comercio")


def test_provincia_chaco_y_ruc_peruano_detectados():
    """Bug real: 'Distribuidora Moron' resultó ser una empresa real en
    Resistencia, Chaco (no Morón, Buenos Aires) — y un RUC (identificador
    tributario peruano, Argentina usa CUIT) se coló sin marca de país."""
    from app.discovery import _parece_empresa
    assert not _parece_empresa("Distribuidora Moron ubicada en Resistencia, Chaco", "Moron")
    assert not _parece_empresa("Empresa con RUC: 20525979947", "Martin Coronado")


def test_inferir_rubro_de_candidatas_overpass_por_tag_osm():
    """Bug real encontrado auditando: las candidatas de Overpass no tienen
    keyword (query_id=NULL), así que _inferir_rubro(None) les asignaba
    'logistica' a TODAS por defecto sin importar el tag real de OSM."""
    from app.promote import _inferir_rubro
    assert _inferir_rubro(None, "OpenStreetMap (supermarket)") == "atencion_cliente"
    assert _inferir_rubro(None, "OpenStreetMap (laundry)") == "limpieza"
    assert _inferir_rubro(None, "OpenStreetMap (cleaning)") == "limpieza"
    assert _inferir_rubro(None, "OpenStreetMap (industrial)") == "logistica"
    assert _inferir_rubro(None, "") == "logistica"  # sin snippet, default conservador


def test_export_aclara_origen_overpass_cuando_no_hay_fuente_web(tmp_path, monkeypatch):
    """Las candidatas de Overpass no tienen fila en `sources` (promote.py no
    inserta una si f['url'] es None) — antes el .txt simplemente omitía
    cualquier mención de 'Fuente', dejando ambiguo si el dato no se buscó
    o si vino de otro lado. Ahora aclara que viene de OpenStreetMap."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.company import upsert_company
    cid = upsert_company("Almacén Don José", "atencion_cliente", "Bella Vista",
                          actividad="OpenStreetMap (convenience) — Avenida Senador Morón")
    conn = db_module.get_conn()
    conn.execute("UPDATE companies SET estado='candidata' WHERE id=?", (cid,))
    conn.commit()
    conn.close()

    from app.export_txt import exportar_candidatas_txt
    import app.export_txt as et
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    monkeypatch.setattr(et, "_carpeta_descargas", lambda: downloads)

    ruta = exportar_candidatas_txt(solo_nuevas=False)
    contenido = Path(ruta).read_text(encoding="utf-8")
    assert "Fuente: None" not in contenido
    assert "OpenStreetMap" in contenido


def test_dominios_gobierno_y_agregadores_turismo_excluidos():
    """Del análisis del archivo real de 1787 candidatas: agregadores de
    turismo/reseñas (hoteles, alquileres temporarios) y dominios .gob.ar/.gov
    se colaban como candidatas."""
    from app.discovery import _es_dominio_excluido
    casos = [
        "https://www.trip.com/hotels/x",
        "https://www.glassdoor.com.ar/x",
        "https://www.airbnb.com/rooms/x",
        "https://www.argentina.gob.ar/x",
        "https://archive.epa.gov/x",  # ya cubierto por dominio específico, pero también por .gov
    ]
    for url in casos:
        assert _es_dominio_excluido(url), f"debería excluirse: {url}"


def test_detecta_negocio_unipersonal_sin_confundir_empresas_reales():
    """Feedback real del usuario: el filtro dejaba pasar mezclado un estudio
    de un solo abogado o un mecánico solo junto con empresas medianas reales
    ('encuentra comercios bajos'). Se agrega detección de negocio
    unipersonal — sin excluir (podría igual interesar), pero sin
    confundirlo con una candidata seria."""
    from app.discovery import _parece_negocio_unipersonal
    assert _parece_negocio_unipersonal("Juan Pérez", "Juan Pérez, Abogado en Caseros, consultas por WhatsApp")
    assert _parece_negocio_unipersonal("Maria Lopez", "Contador Público matriculado, atiendo en mi estudio")
    # NO debe confundir una empresa real de 2 palabras con un nombre de persona
    assert not _parece_negocio_unipersonal("Carrefour Argentina", "supermercado")
    assert not _parece_negocio_unipersonal("Estudio Jurídico D&S Abogados", "Estudio Jurídico D&S Abogados, teléfono")
    assert not _parece_negocio_unipersonal("Logistica Caseros", "empresa con flota y depósito propio")


def test_promote_marca_tamano_chica_para_unipersonales(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.search_client as sc
    import app.site_check as scheck

    def mock_buscar(query, **kwargs):
        return {"organic": [
            {"title": "Roberto Diaz", "link": "https://robertodiaz.com.ar/", "snippet": "Roberto Diaz, Abogado en Caseros, atención con turno previo"},
        ]}
    monkeypatch.setattr(sc, "buscar", mock_buscar)
    monkeypatch.setattr(scheck, "sitio_activo", lambda url: True)

    from app.discovery import ejecutar_query
    from app.promote import promover_candidatas
    ejecutar_query("abogado Caseros", "Caseros", "TYPE_A", "administrativo")
    promover_candidatas(zona="Caseros")

    conn = db_module.get_conn()
    row = conn.execute("SELECT tamano_estimado FROM companies WHERE nombre='Roberto Diaz'").fetchone()
    conn.close()
    assert row["tamano_estimado"] == "chica"


def test_cadena_dia_no_confunde_con_apellido_diaz():
    """Bug real encontrado auditando: 'Dia' (la cadena Día) matcheaba como
    substring contra 'Diaz'/'Díaz' — cualquier empresa con ese apellido (muy
    común en Argentina) se excluía por error, pensando que era el
    supermercado. Detectado al debuggear por qué 'Roberto Diaz' no se
    promovía en un test de negocio unipersonal."""
    from app.exclusions import es_cadena_excluida
    assert es_cadena_excluida("Roberto Diaz") is None
    assert es_cadena_excluida("Distribuidora Díaz Hermanos SRL") is None
    assert es_cadena_excluida("Supermercados DIA Argentina") == "Dia"  # el caso real sigue andando


def test_directorio_dir_ar_extrae_cards_sin_conocer_categorias(tmp_path, monkeypatch):
    """El parser generalizado ancla solo en la línea de rating (universal en
    toda la red dir.ar) — no necesita conocer las categorías reales de cada
    rubro (a diferencia del parser original de solo-logística), porque
    varios slugs (gimnasios, tiendasderopa, etc.) tienen categorías propias
    que no se pudieron verificar contra el sitio real."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    html = """
    <div class="card"><span class="rubro">Gimnasio boxeo y funcional</span>
    <h3>Power Gym Hurlingham</h3>
    <p>Av. Vergara 1200</p>
    <span>★ 4.6 (80)</span></div>
    <div class="card"><span class="rubro">Indumentaria deportiva</span>
    <h3>Sportline Hurlingham</h3>
    <p>Roca 500</p>
    <span>★ 4.2 (15)</span></div>
    """

    import app.directorio_dir_ar as dda
    monkeypatch.setattr(dda, "_fetch", lambda url: html)

    r = dda.buscar_por_zona_y_dominio("Hurlingham", "gimnasios.dir.ar")
    assert r["total_cards"] == 2
    assert r["nuevas"] == 2

    conn = db_module.get_conn()
    nombres = {row["nombre_crudo"] for row in conn.execute("SELECT nombre_crudo FROM discovered_companies_raw")}
    conn.close()
    assert "Power Gym Hurlingham" in nombres
    assert "Sportline Hurlingham" in nombres


def test_directorio_dir_ar_no_rompe_si_falla_la_descarga(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.directorio_dir_ar as dda
    monkeypatch.setattr(dda, "_fetch", lambda url: None)
    r = dda.buscar_por_zona_y_dominio("Hurlingham", "logistica.dir.ar")
    assert r["nuevas"] == 0
    assert r["error"]


def test_directorio_dir_ar_no_repite_combinacion_ya_procesada(tmp_path, monkeypatch):
    """Igual que overpass_progress: el contenido de un directorio no cambia
    tan rápido como para justificar re-leer la misma página cada hora para
    siempre."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.directorio_dir_ar as dda
    monkeypatch.setattr(dda, "_fetch", lambda url: None)
    dda.buscar_por_zona_y_dominio("Hurlingham", "logistica.dir.ar")

    pendientes = dda.combinaciones_pendientes(["Hurlingham"])
    assert ("Hurlingham", "logistica.dir.ar") not in pendientes
    assert ("Hurlingham", "catering.dir.ar") in pendientes


def test_inferir_rubro_de_candidatas_dir_ar_desde_snippet():
    """directorio_dir_ar.py guarda el rubro real directo en el snippet
    (ej. 'gimnasios.dir.ar (atencion_cliente) — ...') — no hace falta
    traducir un tag como con Overpass, solo extraerlo."""
    from app.promote import _inferir_rubro
    assert _inferir_rubro(None, "gimnasios.dir.ar (atencion_cliente) — Roca 500 — 4.6★ (80 reseñas)") == "atencion_cliente"
    assert _inferir_rubro(None, "limpieza.dir.ar (limpieza) — x") == "limpieza"


def test_auditoria_directorios_marca_sospechoso_con_5_intentos_y_0_resultados(tmp_path, monkeypatch):
    """Varios slugs de la red dir.ar se adivinaron sin poder verificar contra
    el sitio real (WebFetch a dir.ar bloqueado en este entorno) — este
    reporte detecta un slug probablemente equivocado por su rendimiento
    real en directorio_dir_ar_progress, no por revisar el texto."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.auditoria_directorios import reporte_dominios

    conn = db_module.get_conn()
    for i in range(5):
        conn.execute(
            "INSERT INTO directorio_dir_ar_progress (zona, dominio, empresas_nuevas, procesado_en) VALUES (?, ?, 0, ?)",
            (f"Zona{i}", "tiendasderopa.dir.ar", db_module.now()),
        )
    conn.commit()
    conn.close()

    filas = {f["dominio"]: f for f in reporte_dominios()}
    assert filas["tiendasderopa.dir.ar"]["sospechoso"] is True
    assert filas["logistica.dir.ar"]["sospechoso"] is False  # sin intentos todavía, no es sospechoso


def test_loop_investigacion_corre_directorio_dir_ar_gratis(tmp_path, monkeypatch):
    """La red dir.ar está enganchada como 6ta fuente del ciclo automático,
    no gasta presupuesto de Serper (igual que Overpass)."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.runner as runner_module
    import app.directorio_dir_ar as dda

    html = """
    <h3>Estudio Contable Hurlingham</h3>
    <p>Roca 100</p>
    <span>★ 4.5 (20)</span>
    """
    monkeypatch.setattr(dda, "_fetch", lambda url: html)

    # aislar Overpass (corre primero ahora) para que no intente red real
    import app.geocoding as geocoding
    monkeypatch.setattr(geocoding, "geocodificar", lambda direccion: None)

    import app.search_client as sc
    monkeypatch.setattr(sc, "buscar", lambda query, **kw: {"organic": []})

    runner_module.loop_investigacion(max_ciclos=20)

    conn = db_module.get_conn()
    nombres = [r["nombre"] for r in conn.execute("SELECT nombre FROM companies")]
    conn.close()
    assert "Estudio Contable Hurlingham" in nombres


def test_fuentes_pagas_no_se_saltan_si_las_gratis_fallan(tmp_path, monkeypatch):
    """Bug real (2 veces en la misma sesión): 1) trabajo_gratis_hecho se
    marcaba con solo INTENTAR una fuente gratis, no con encontrar algo de
    verdad — si Overpass/dir.ar fallaban (ej. sin red), igual saltaban
    industrial/proveedores/geo para SIEMPRE, dejando el motor sin encontrar
    nada. 2) quedó una línea duplicada que marcaba trabajo_gratis_hecho=True
    sin condición, fuera del if que la ponía correctamente. Este test
    reproduce el escenario real reportado: geo saturada + fuentes gratis
    fallando (sin red) + industrial con trabajo pendiente."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.runner as runner_module
    import app.overpass_discovery as ovp
    import app.directorio_dir_ar as dda

    # fuentes gratis fallan (simula sin red / sitio caído) — deben devolver
    # nuevas=0 sin romper, y NO deben bloquear las fuentes pagas
    monkeypatch.setattr(ovp, "buscar_por_zona", lambda zona: {"zona": zona, "error": "sin red", "nuevas": 0})
    monkeypatch.setattr(dda, "buscar_por_zona_y_dominio", lambda zona, dominio: {"zona": zona, "dominio": dominio, "error": "sin red", "nuevas": 0})

    import app.search_client as sc
    import app.site_check as scheck
    monkeypatch.setattr(sc, "buscar", lambda query, **kw: {"organic": [
        {"title": "Fábrica Real SA", "link": "https://fabricareal.com.ar/", "snippet": "industria"},
    ]})
    monkeypatch.setattr(scheck, "sitio_activo", lambda url: True)

    runner_module.loop_investigacion(max_ciclos=10)

    conn = db_module.get_conn()
    total = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    conn.close()
    assert total > 0, "las fuentes pagas deben poder correr igual si las gratis no encontraron nada"


def test_descarta_por_distancia_real_geocodificada(tmp_path, monkeypatch):
    """Bug real de fondo (motivo del reclamo del usuario 'pifia mucho en la
    ubicación'): la geocodificación existía en el código pero nunca se
    llamaba automáticamente, solo por comando manual — ningún homónimo
    lejano se descartaba nunca por distancia real. Overpass y dir.ar sí
    traen dirección real en el snippet, así que ahora se verifica antes de
    promover."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    import app.promote as promote_mod
    monkeypatch.setattr(promote_mod.geocoding, "calcular_distancia_a_empresa",
                        lambda direccion: {"distancia_km": 950.0, "direccion_resuelta": direccion, "lat": 0, "lon": 0})

    import app.search_client as sc
    import app.site_check as scheck
    monkeypatch.setattr(sc, "buscar", lambda query, **kw: {"organic": [
        {"title": "Fábrica Rara SA", "link": "https://fabricarara.com.ar/",
         "snippet": "OpenStreetMap (industrial) — Calle Falsa 123"},
    ]})
    monkeypatch.setattr(scheck, "sitio_activo", lambda url: True)

    from app.discovery import ejecutar_query
    from app.promote import promover_candidatas
    ejecutar_query("fabrica Bella Vista", "Bella Vista", "TYPE_C", "")
    r = promover_candidatas(zona="Bella Vista")

    assert r["promovidas"] == 0
    conn = db_module.get_conn()
    total = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    estado = conn.execute("SELECT estado FROM discovered_companies_raw WHERE nombre_crudo='Fábrica Rara SA'").fetchone()["estado"]
    conn.close()
    assert total == 0
    assert "EXCLUIDA_UBICACION" in estado


def test_no_bloquea_si_no_hay_direccion_real_o_falla_geocoding(tmp_path, monkeypatch):
    """La verificación nunca bloquea si no puede confirmar nada (sin
    dirección real en el snippet, o Nominatim sin respuesta) — es aditiva,
    no reemplaza los demás filtros."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.promote import _ubicacion_implausible
    assert _ubicacion_implausible("Empresa X SA", "una descripción normal sin dirección", "Hurlingham") is None

    import app.promote as promote_mod
    monkeypatch.setattr(promote_mod.geocoding, "calcular_distancia_a_empresa", lambda direccion: None)
    assert _ubicacion_implausible("Empresa X SA", "OpenStreetMap (industrial) — Calle Falsa 123", "Hurlingham") is None


def test_ejecutar_query_guarda_query_id_para_inferir_rubro_correcto(tmp_path, monkeypatch):
    """Regresión real de producción: ejecutar_query() insertaba las candidatas
    en discovered_companies_raw ANTES de crear la fila en queries_log, así que
    query_id quedaba NULL para siempre en TODA candidata descubierta por
    Serper (la fuente paga principal) — no solo Overpass/dir.ar, que ya de
    por sí no tienen keyword. El LEFT JOIN de promote.py nunca encontraba el
    keyword real de la búsqueda, y _inferir_rubro(None, snippet) caía al
    rubro por defecto "logistica" para casi todo lo que no matcheaba un tag
    de OSM o de dir.ar en el snippet — reportado por el usuario como "busca
    mal los trabajos"."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_query_id.sqlite")
    db_module.init_db()

    import app.search_client as sc
    monkeypatch.setattr(sc, "buscar", lambda query, **kwargs: {
        "organic": [{"title": "Estudio Contable Gómez y Asociados", "link": "https://gomezyasoc.com.ar/", "snippet": "estudio contable"}]
    })

    from app.discovery import ejecutar_query
    from app.promote import promover_candidatas, _inferir_rubro

    r = ejecutar_query("estudio contable Hurlingham", "Hurlingham", "TYPE_A", "administrativo")
    conn = db_module.get_conn()
    fila = conn.execute("SELECT query_id, keyword FROM discovered_companies_raw d "
                         "LEFT JOIN queries_log q ON q.id = d.query_id "
                         "WHERE d.nombre_crudo LIKE 'Estudio Contable%'").fetchone()
    conn.close()
    assert fila["query_id"] == r["query_id"] is not None
    assert fila["keyword"] == "administrativo"

    promover_candidatas(zona="Hurlingham")
    conn = db_module.get_conn()
    rubro = conn.execute("SELECT rubro FROM companies WHERE nombre LIKE 'Estudio Contable%'").fetchone()["rubro"]
    conn.close()
    assert rubro == "administrativo", "no debería caer al default 'logistica' teniendo el keyword real"


def test_slug_de_zona_usa_guiones_entre_palabras():
    """Bug real: dir.ar arma el slug de ciudad CON guiones entre palabras
    ('mar-del-plata', 'concepcion-del-uruguay'), pero _slug_de_zona borraba
    el espacio directamente ('mardelplata') — daba 404 silencioso en TODO
    partido de nombre compuesto (Tres de Febrero, San Martín, San Miguel...),
    justo los más relevantes para este motor. Verificado contra URLs reales
    de logistica.dir.ar encontradas por búsqueda."""
    from app.directorio_dir_ar import _slug_de_zona
    assert _slug_de_zona("Tres de Febrero") == "tres-de-febrero"
    assert _slug_de_zona("San Martín") == "san-martin"
    assert _slug_de_zona("Hurlingham") == "hurlingham"


def test_cleanup_descarta_homonimo_extranjero_por_url(tmp_path, monkeypatch):
    """Bug real (archivo de producción de 1778 candidatas): quedaban colgadas
    empresas de 'Bella Vista' de Chile/México/Arkansas cuyo nombre no delata
    el país, pero la URL sí (.cl, .mx, 'arkansas' en la ruta). La limpieza
    retroactiva nunca miraba la fuente, así que nunca las agarraba."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    conn = db_module.get_conn()
    cur = conn.execute(
        "INSERT INTO companies (nombre, rubro, zona, estado, creado_en, actualizado_en) "
        "VALUES ('Limpieza Total', 'limpieza', 'Bella Vista', 'candidata', ?, ?)",
        (db_module.now(), db_module.now()),
    )
    cid = cur.lastrowid
    conn.execute(
        "INSERT INTO sources (company_id, url, tipo, descripcion, creado_en) VALUES (?, ?, 'directorio', '', ?)",
        (cid, "http://limpiezaparaalfombras.cl/bella-vista/", db_module.now()),
    )
    conn.commit()
    conn.close()

    from app.cleanup import limpiar_candidatas_basura
    r = limpiar_candidatas_basura()
    assert r["limpiadas"] == 1

    conn = db_module.get_conn()
    estado = conn.execute("SELECT estado FROM companies WHERE id=?", (cid,)).fetchone()["estado"]
    conn.close()
    assert estado == "descartada"


def test_recalcular_rubros_corrige_logistica_por_defecto(tmp_path, monkeypatch):
    """Bug real: 1778/1778 candidatas quedaron con rubro='logistica' por el
    query_id=NULL. recalcular_rubros_basura las revisa cruzando nombre+snippet
    contra KEYWORDS_SEED y corrige las que claramente son otro rubro."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    conn = db_module.get_conn()
    cur = conn.execute(
        "INSERT INTO companies (nombre, rubro, zona, actividad, estado, creado_en, actualizado_en) "
        "VALUES ('Maclean Tapizados', 'logistica', 'Bella Vista', 'servicio premium de limpieza de tapizados', 'candidata', ?, ?)",
        (db_module.now(), db_module.now()),
    )
    cid = cur.lastrowid
    conn.commit()
    conn.close()

    from app.cleanup import recalcular_rubros_basura
    r = recalcular_rubros_basura()
    assert r["corregidas"] == 1

    conn = db_module.get_conn()
    rubro = conn.execute("SELECT rubro FROM companies WHERE id=?", (cid,)).fetchone()["rubro"]
    conn.close()
    assert rubro == "limpieza"


def test_inferir_rubro_por_texto_sin_keyword():
    """_inferir_rubro sin keyword ni tag debe deducir del nombre+snippet
    antes de caer al default 'logistica'."""
    from app.promote import _inferir_rubro
    assert _inferir_rubro(None, "servicio de limpieza de oficinas", "Limpieza Total") == "limpieza"
    assert _inferir_rubro(None, "estudio contable y facturación", "Gómez Asociados") == "administrativo"
    # sin ninguna señal, mantiene el default conservador
    assert _inferir_rubro(None, "xyz sin pistas", "Empresa Nn") == "logistica"


def test_snippet_mining_extrae_senales_reales():
    from app.snippet_mining import extraer_senales
    s = extraer_senales("La empresa inauguró una nueva planta y busca personal para el depósito")
    assert "nueva_planta" in s
    assert "contratacion_reciente_similar" in s
    # texto sin señales no inventa ninguna
    assert extraer_senales("vendemos tornillos") == []


def test_snippet_mining_extrae_contactos_sin_inventar():
    from app.snippet_mining import extraer_contactos
    r = extraer_contactos("Escribinos a ventas@fabrica.com.ar o llamá al 4665-1605")
    assert "ventas@fabrica.com.ar" in r["emails"]
    assert any("4665" in t for t in r["telefonos"])
    # ruido de plataforma se filtra, y no inventa nada donde no hay
    r2 = extraer_contactos("contacto en soporte@wixpress.com")
    assert r2["emails"] == []


def test_snippet_mining_proxies_resenas_dir_ar():
    from app.snippet_mining import extraer_proxies_calidad
    p = extraer_proxies_calidad("logistica.dir.ar (logistica) — Av Roca 500 — 4,6★ (80 reseñas)")
    assert p["resenas"] == 80
    assert p["rating"] == "4.6"


def test_triage_puntua_sin_gastar_y_no_cambia_estado(tmp_path, monkeypatch):
    """El triage rankea con datos ya en la DB, marca auto_evaluada, pero NUNCA
    promueve a jackpot: la candidata sigue 'candidata' hasta verificación real."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    conn = db_module.get_conn()
    cur = conn.execute(
        "INSERT INTO companies (nombre, rubro, zona, actividad, sitio_activo, estado, creado_en, actualizado_en) "
        "VALUES ('Distribuidora Norte SRL', 'logistica', 'Hurlingham', "
        "'operador logístico, nuevo depósito, busca personal. Escribir a info@distnorte.com.ar', 1, "
        "'candidata', ?, ?)",
        (db_module.now(), db_module.now()),
    )
    cid = cur.lastrowid
    conn.commit()
    conn.close()

    from app.auto_triage import triage_candidatas, ranking_triage
    r = triage_candidatas()
    assert r["procesadas"] == 1

    conn = db_module.get_conn()
    row = conn.execute("SELECT estado, triage_score, auto_evaluada FROM companies WHERE id=?", (cid,)).fetchone()
    # detectó email en el texto -> lo persistió como contacto (sin verificar)
    tiene_contacto = conn.execute("SELECT 1 FROM contacts WHERE company_id=?", (cid,)).fetchone()
    # detectó señales -> las persistió con procedencia [auto/snippet]
    tiene_senal = conn.execute("SELECT descripcion FROM signals WHERE company_id=?", (cid,)).fetchone()
    conn.close()

    assert row["estado"] == "candidata", "el triage NUNCA debe promover a jackpot"
    assert row["triage_score"] is not None and 0 <= row["triage_score"] <= 100
    assert row["auto_evaluada"] == 1
    assert tiene_contacto is not None
    assert tiene_senal is not None and "[auto/snippet]" in tiene_senal["descripcion"]

    top = ranking_triage()
    assert top and top[0]["id"] == cid


def test_triage_solo_sin_triage_no_recalcula(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()
    conn = db_module.get_conn()
    conn.execute(
        "INSERT INTO companies (nombre, rubro, zona, estado, triage_score, creado_en, actualizado_en) "
        "VALUES ('Ya Triada SA', 'logistica', 'Moron', 'candidata', 77, ?, ?)",
        (db_module.now(), db_module.now()),
    )
    conn.commit()
    conn.close()
    from app.auto_triage import triage_candidatas
    r = triage_candidatas(solo_sin_triage=True)
    assert r["evaluadas"] == 0  # la que ya tenía triage no se re-procesa


def test_contacto_gratis_crawlea_sitio_sin_serper(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()
    conn = db_module.get_conn()
    cur = conn.execute(
        "INSERT INTO companies (nombre, rubro, zona, dominio, estado, creado_en, actualizado_en) "
        "VALUES ('Fabrica X SRL', 'logistica', 'Moron', 'fabricax.com.ar', 'candidata', ?, ?)",
        (db_module.now(), db_module.now()),
    )
    cid = cur.lastrowid
    conn.commit()
    conn.close()

    import app.contacto_gratis as cg
    monkeypatch.setattr(cg, "extraer_contacto_de_sitio",
                        lambda dom: {"email": "admin@fabricax.com.ar", "telefono": None, "fuente_url": f"https://{dom}/contacto"})
    monkeypatch.setattr(cg, "verificar_email", lambda e: True)

    r = cg.enriquecer_contacto_gratis()
    assert r["con_contacto_nuevo"] == 1
    conn = db_module.get_conn()
    c = conn.execute("SELECT valor, verificado FROM contacts WHERE company_id=?", (cid,)).fetchone()
    conn.close()
    assert c["valor"] == "admin@fabricax.com.ar"


def test_contacto_gratis_marca_sin_resultado_para_no_reintentar(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()
    conn = db_module.get_conn()
    cur = conn.execute(
        "INSERT INTO companies (nombre, rubro, zona, dominio, estado, creado_en, actualizado_en) "
        "VALUES ('Sin Web SRL', 'logistica', 'Moron', 'sinweb.com.ar', 'candidata', ?, ?)",
        (db_module.now(), db_module.now()),
    )
    cid = cur.lastrowid
    conn.commit()
    conn.close()

    import app.contacto_gratis as cg
    monkeypatch.setattr(cg, "extraer_contacto_de_sitio", lambda dom: None)
    cg.enriquecer_contacto_gratis()
    # segunda corrida: ya no la vuelve a intentar
    r2 = cg.enriquecer_contacto_gratis()
    assert r2["evaluadas"] == 0
    conn = db_module.get_conn()
    flag = conn.execute("SELECT contacto_intentado_sin_resultado FROM companies WHERE id=?", (cid,)).fetchone()[0]
    conn.close()
    assert flag == 1


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))


def test_es_directorio_distingue_directorio_de_sitio_propio():
    """Un directorio (dir.ar, páginas amarillas) NO es el sitio de la empresa:
    guardarlo como tal hacía que el crawl gratis levantara el contacto del
    directorio y lo guardara como si fuera el de la empresa."""
    from app.site_check import es_directorio
    assert es_directorio("https://limpieza.dir.ar/ciudad/hurlingham.html") is True
    assert es_directorio("dir.ar") is True
    assert es_directorio("www.paginasamarillas.com.ar") is True
    assert es_directorio("https://transportesdelsur.com.ar/contacto") is False
    assert es_directorio("midirectorio.com.ar") is False  # no es sufijo de dir.ar
    assert es_directorio("") is False


def test_promote_no_guarda_el_directorio_como_sitio_de_la_empresa(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_dominio_dir.sqlite")
    db_module.init_db()

    import app.search_client as sc
    import app.site_check as scheck
    monkeypatch.setattr(scheck, "sitio_activo", lambda url: True)
    monkeypatch.setattr(sc, "buscar", lambda query, **kw: {"organic": [
        {"title": "Transportes El Roble SRL", "link": "https://logistica.dir.ar/ficha/el-roble.html",
         "snippet": "Empresa de transporte y distribución en Hurlingham"},
    ]})

    from app.discovery import ejecutar_query
    from app.promote import promover_candidatas
    ejecutar_query("empresas deposito Hurlingham", "Hurlingham", "TYPE_A", "depósito")
    promover_candidatas(zona="Hurlingham")

    conn = db_module.get_conn()
    fila = conn.execute("SELECT nombre, dominio FROM companies").fetchone()
    conn.close()
    assert fila is not None
    assert not fila["dominio"], "el dominio del directorio no es el sitio propio de la empresa"


def test_limpiar_dominios_directorio_borra_contacto_del_directorio(tmp_path, monkeypatch):
    """Retroactivo: candidatas cargadas antes del fix tienen el directorio
    como dominio, y contactos crawleados de ahí que son del directorio."""
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_limpieza_dir.sqlite")
    db_module.init_db()

    from app.company import upsert_company
    from app.db import get_conn, now
    cid_malo = upsert_company("Logística del Oeste SRL", "logistica", "Hurlingham")
    cid_bueno = upsert_company("Transportes Propios SA", "logistica", "Hurlingham")
    conn = get_conn()
    conn.execute("UPDATE companies SET dominio='limpieza.dir.ar', contacto_intentado_sin_resultado=1 WHERE id=?", (cid_malo,))
    conn.execute("UPDATE companies SET dominio='transportespropios.com.ar' WHERE id=?", (cid_bueno,))
    for cid, url in ((cid_malo, "https://limpieza.dir.ar"), (cid_bueno, "https://transportespropios.com.ar")):
        cur = conn.execute(
            "INSERT INTO sources (company_id, url, tipo, descripcion, creado_en) VALUES (?, ?, 'sitio_propio', '', ?)",
            (cid, url, now()))
        conn.execute(
            "INSERT INTO contacts (company_id, tipo, valor, verificado, fuente_id, es_persona, creado_en) "
            "VALUES (?, 'email', ?, 1, ?, 0, ?)",
            (cid, f"info@{url.split('//')[1]}", cur.lastrowid, now()))
    conn.commit()
    conn.close()

    from app.cleanup import limpiar_dominios_directorio
    r = limpiar_dominios_directorio()
    assert r["limpiados"] == 1
    assert r["contactos_borrados"] == 1

    conn = get_conn()
    malo = conn.execute("SELECT dominio, contacto_intentado_sin_resultado FROM companies WHERE id=?", (cid_malo,)).fetchone()
    bueno = conn.execute("SELECT dominio FROM companies WHERE id=?", (cid_bueno,)).fetchone()
    quedan = [r["valor"] for r in conn.execute("SELECT valor FROM contacts")]
    conn.close()
    assert malo["dominio"] == ""
    assert malo["contacto_intentado_sin_resultado"] == 0, "nunca se intentó contra la empresa real"
    assert bueno["dominio"] == "transportespropios.com.ar", "el sitio propio no se toca"
    assert quedan == ["info@transportespropios.com.ar"]


def test_entrega_filtra_y_arma_markdown_con_pagina_web(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_entrega.sqlite")
    db_module.init_db()

    from app.company import upsert_company
    from app.db import get_conn, now
    con_web = upsert_company("Depósitos Ituzaingó SA", "logistica", "Ituzaingó")
    sin_nada = upsert_company("Empresa Fantasma", "limpieza", "Morón")
    conn = get_conn()
    conn.execute("UPDATE companies SET dominio='depositosituzaingo.com.ar', triage_score=78 WHERE id=?", (con_web,))
    conn.execute("UPDATE companies SET triage_score=40 WHERE id=?", (sin_nada,))
    conn.execute(
        "INSERT INTO contacts (company_id, tipo, valor, verificado, es_persona, creado_en) "
        "VALUES (?, 'email', 'rrhh@depositosituzaingo.com.ar', 1, 0, ?)", (con_web, now()))
    conn.commit()
    conn.close()

    from app.entrega import filas_entrega, render_md
    todas = filas_entrega()
    assert todas["total"] == 2

    contactables = filas_entrega(solo_contactables=True)
    assert [i["nombre"] for i in contactables["items"]] == ["Depósitos Ituzaingó SA"]

    assert filas_entrega(minimo_triage=70)["total"] == 1
    assert filas_entrega(busqueda="fantasma")["total"] == 1
    assert filas_entrega(rubro="limpieza")["total"] == 1

    md = render_md(contactables["items"], contactables["total"])
    assert "https://depositosituzaingo.com.ar" in md
    assert "rrhh@depositosituzaingo.com.ar" in md
    assert "Ituzaingó" in md
    assert "Empresa Fantasma" not in md
