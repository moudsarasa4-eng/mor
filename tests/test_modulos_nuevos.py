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

    runner_module.loop_investigacion(max_ciclos=20)

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


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
