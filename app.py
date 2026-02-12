# app.py
import asyncio
import logging
import sys
import traceback
from typing import Optional, Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastHTTPException
from pydantic import BaseModel, Field, constr

# =========================
# LOGGING (consola + archivo)
# =========================
logging.basicConfig(
    level=logging.DEBUG,  # Cambia a INFO en producción
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app_errors.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("api")

# =========================
# IMPORTS de tus módulos
# =========================
from Source.consulta_Runt import ConsultaRunt
# Se eliminó la importación de Source.bot (SIMIT)

from Source.Variables import (
    Consulta_prenda,
    Consulta_propietarios,
    limitaciones_propiedad,
    validar_propietario,
)


# =========================
# HELPERS
# =========================
def _keys(d: Any):
    return sorted(list(d.keys())) if isinstance(d, dict) else str(type(d).__name__)


def where(exc: Exception | None = None):
    tb = exc.__traceback__ if exc and exc.__traceback__ else sys.exc_info()[2]
    if not tb:
        return ("<unknown>", -1, "<unknown>")
    while tb.tb_next:
        tb = tb.tb_next
    frame = tb.tb_frame
    code = frame.f_code
    return (code.co_filename, tb.tb_lineno, code.co_name)


# =========================
# SCHEMAS (solo lo que devuelves)
# =========================
PlacaStr = constr(pattern=r"^[A-Za-z0-9]{5,8}$")


class ConsultaInput(BaseModel):
    placa: PlacaStr = Field(..., description="Placa del vehículo (sin espacios).")
    numero_documento: Optional[str] = Field(None, description="Documento para validar propietario (opcional).")
    nombre_propietario: Optional[str] = Field(None, description="Nombre para validar propietario (opcional).")


class ConsultaResponse(BaseModel):
    placa: str
    # multas_vehiculo: bool  <-- ELIMINADO (era SIMIT)
    limitaciones_propiedad: bool
    prenda: bool
    total_propietarios: int
    propietario_valido: Optional[bool] = None
    organismoTransito: str

# =========================
# FASTAPI APP
# =========================
app = FastAPI(title="Consultas Vehiculares API", version="1.0.0")


# ---------- Handlers de errores ----------
@app.exception_handler(FastHTTPException)
async def http_exception_logger(request: Request, exc: FastHTTPException):
    f, ln, fn = where(exc)
    logger.error(
        "⚠️ HTTPException at %s:%d in %s() -> %s %s :: %s",
        f, ln, fn, request.method, request.url.path, exc.detail
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "file": f, "line": ln, "function": fn},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    f, ln, fn = where(exc)
    tb_txt = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(
        "🧨 Unhandled error at %s:%d in %s()\nURL: %s %s\nMSG: %s\nTRACE:\n%s",
        f, ln, fn, request.method, request.url.path, str(exc), tb_txt
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "file": f, "line": ln, "function": fn,
            "message": str(exc),
            "trace": tb_txt,  # quita en prod si no deseas exponerlo
        },
    )


# ---------- Health ----------
@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------- Endpoint principal ----------
@app.post("/consulta", response_model=ConsultaResponse)
async def consultar_vehiculo(payload: ConsultaInput):
    placa = payload.placa.strip().upper()
    logger.debug(
        "➡️ /consulta recibido: placa=%s, numero_documento=%s, nombre=%s",
        placa, payload.numero_documento, payload.nombre_propietario
    )

    # 1) Consulta SOLO RUNT (mantenemos to_thread para no bloquear el loop)
    try:
        runt_json = await asyncio.to_thread(ConsultaRunt, placa)

    except Exception as e:
        f, ln, fn = where(e)
        logger.error("❌ Error consultando RUNT at %s:%d in %s() placa=%s :: %s", f, ln, fn, placa, str(e))
        raise HTTPException(status_code=502, detail={
            "error": "Error consultando servicios externos (RUNT)",
            "file": f, "line": ln, "function": fn, "message": str(e)
        })

    logger.debug("🧩 RUNT tipo=%s keys=%s", type(runt_json).__name__, _keys(runt_json))

    # 2) Validación mínima de RUNT (debe ser dict)
    if not isinstance(runt_json, dict):
        f, ln, fn = where(None)
        raise HTTPException(status_code=500, detail={
            "error": "Respuesta RUNT no válida (se esperaba JSON dict).",
            "file": f, "line": ln, "function": fn
        })

    # 3) Post-proceso con tus funciones
    try:
        limitaciones = bool(limitaciones_propiedad(runt_json))
        prenda = bool(Consulta_prenda(runt_json))
        n_prop = int(Consulta_propietarios(runt_json))

        propietario_valido = None
        organismo_Transito = runt_json.get("organismoTransito")
        if payload.numero_documento and payload.nombre_propietario:
            # print(validar_propietario(...)) # Comentado para limpiar logs


            propietario_valido = bool(
                validar_propietario(
                    runt_json,
                    numero_documento=payload.numero_documento,
                    nombre=payload.nombre_propietario,
                )
            )

        # === SOLO lo que ya devuelves (sin multas_vehiculo) ===
        respuesta = ConsultaResponse(
            placa=placa,
            limitaciones_propiedad=limitaciones,
            prenda=prenda,
            total_propietarios=n_prop,
            propietario_valido=propietario_valido,
            organismoTransito = organismo_Transito
        )

        logger.debug("✅ Respuesta armada para placa=%s", placa)
        return respuesta

    except Exception as e:
        f, ln, fn = where(e)
        tb_txt = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(
            "❌ Error procesando respuesta at %s:%d in %s() para placa=%s\nPayload=%s\nMSG: %s\nTRACE:\n%s",
            f, ln, fn, placa, payload.model_dump(), str(e), tb_txt
        )
        raise HTTPException(status_code=500, detail={
            "error": "Error procesando la respuesta",
            "file": f, "line": ln, "function": fn, "message": str(e)
        })