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
    import app.db as db_module
    db_path = tmp_path / "database.sqlite"
    db_module.init_db.__globals__  # no-op, solo para claridad
    monkeypatch.setattr(db_module, "DB_PATH", db_path)
    db_module.init_db()

    import app.backup as backup_module
    monkeypatch.setattr(backup_module, "DB_PATH", db_path)
    monkeypatch.setattr(backup_module, "BACKUPS_DIR", tmp_path / "backups")
    monkeypatch.setattr(backup_module, "MAX_BACKUPS", 3)

    import time
    archivos = []
    for _ in range(5):
        archivos.append(backup_module.hacer_backup())
        time.sleep(1.1)  # el nombre del backup usa resolución de segundos

    restantes = list((tmp_path / "backups").glob("database_*.sqlite"))
    assert len(restantes) == 3, "debería quedarse solo con los últimos MAX_BACKUPS"

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


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
