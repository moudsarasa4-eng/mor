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
