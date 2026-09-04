"""Verifica que el dominio de un email de contacto realmente puede recibir
correo (tiene registro MX) — no confirma que la casilla específica exista,
pero descarta el caso más común de un email inventado/roto: dominio sin
servidor de correo configurado.
"""
import dns.resolver
import dns.exception

TIMEOUT = 5


def dominio_tiene_mx(dominio: str) -> bool | None:
    """True = tiene MX (probablemente puede recibir mail), False = no tiene,
    None = no se pudo determinar (sin red, timeout — no se asume nada)."""
    if not dominio:
        return None
    try:
        respuestas = dns.resolver.resolve(dominio, "MX", lifetime=TIMEOUT)
        return len(respuestas) > 0
    except dns.resolver.NXDOMAIN:
        return False
    except dns.resolver.NoAnswer:
        return False
    except dns.exception.DNSException:
        return None


def verificar_email(email: str) -> bool | None:
    if not email or "@" not in email:
        return False
    dominio = email.split("@", 1)[1]
    return dominio_tiene_mx(dominio)
