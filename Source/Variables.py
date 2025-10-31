import json
def limitaciones_propiedad(json):
    limitaciones = json.get("igvLimitacionesPropiedad")
    print(limitaciones)
    if isinstance(limitaciones, str) and limitaciones.strip().lower() == "no":
        return False
    elif limitaciones is None:
        return False
    else:
        return True

def Consulta_prenda(json):
    prenda = json.get('igvPrendas')
    if isinstance(prenda, str) and prenda.strip().lower() == "no":
        prenda_vehiculo = False
    else:
        prenda_vehiculo = True
    return prenda_vehiculo

def Consulta_propietarios(json_data):
    propietarios = json_data.get('propietariosActuales')

    if isinstance(propietarios, list):
        cantidad = len(propietarios)
    else:
        cantidad = 0  # Si es None o no es lista, devuelve 0

    return cantidad

def validar_propietario(data, numero_documento: str, nombre: str) -> bool:
    """
    Verifica si existe un propietario que coincida por número de documento
    y por nombre completo o por coincidencia con nombres/apellidos individuales.

    - Ignora mayúsculas/minúsculas y espacios adicionales.
    - Retorna True si encuentra coincidencia, False en caso contrario.
    """

    propietarios = data.get("propietariosActuales")

    if not isinstance(propietarios, list):
        return False  # No hay lista válida

    nombre_normalizado = nombre.strip().lower()

    for p in propietarios:
        doc = p.get("numeroDocumento")
        if not doc or str(doc).strip() != str(numero_documento).strip():
            continue  # Documento no coincide, pasa al siguiente

        # Obtener todas las posibles combinaciones de nombres
        completo = p.get("nombreCompleto", "")
        primer_nombre = p.get("primerNombre", "")
        segundo_nombre = p.get("segundoNombre", "")
        primer_apellido = p.get("primerApellido", "")
        segundo_apellido = p.get("segundoApellido", "")

        # Unir nombres individuales
        nombre_compuesto = " ".join(
            part for part in [primer_nombre, segundo_nombre, primer_apellido, segundo_apellido] if part
        ).strip().lower()

        # Normalizar
        completo = completo.strip().lower()

        # Comparar con el nombre proporcionado
        if nombre_normalizado in [completo, nombre_compuesto]:
            return True

    return False


jsonD = '''{
    "clienteBolivar": true,
    "igPatVeh": "USA691",
    "igPais": "90",
    "igPaisDesc": "COLOMBIA",
    "igNroLicenciaTransito": "10029194337",
    "igEstadoVehiculo": "",
    "igEstadoVehiculoDesc": "",
    "igTipoServicio": "2",
    "igTipoServicioDesc": "PÚBLICO",
    "igClaseVehiculo": "4",
    "igClaseVehiculoDesc": "CAMION",
    "igvMarca": "1",
    "igvMarcaDesc": "CHEVROLET",
    "igvLinea": "257",
    "igvLineaDesc": "NPR",
    "igvModelo": 2006,
    "igvColor": "AZUL CORCEGA",
    "idColor": "AZUL CORCEGA",
    "igvNumeroSerie": "9GDNPR7156B005984",
    "igvNumeroMotor": "344807",
    "igvNumeroChasis": "9GDNPR7156B005984",
    "igvNumeroVin": null,
    "divipola": 66682000,
    "igvCilindraje": 4570,
    "igvNroLlantas": null,
    "igvAlto": null,
    "igvAncho": null,
    "igvLargo": null,
    "igvTipoCarroceria": "1 - ESTACAS",
    "idTipoCarroceria": 1,
    "igvLimitacionesPropiedad": null,
    "igvPrendas": "NO",
    "igvRepotenciado": "NO",
    "igvClasificacion": "AUTOMOVIL",
    "igvEsRegrabadoMotor": "NO",
    "igvNumeroRegrabacionMotor": null,
    "igvEsRegrabadoChasis": "NO",
    "igvNumeroRegrabacionChasis": null,
    "igvEsRegrabadoSerie": "NO",
    "igvNumeroRegrabacionSerie": null,
    "igvEsRegrabadoVin": "NO",
    "igvNumeroRegrabacionVin": null,
    "dtCapacidadCarga": 4410,
    "dtNumeroEjes": 2,
    "soatNumeroPoliza": "1508005709460000",
    "soatFechaExpedicion": "2024-06-05-00:00",
    "soatFechaVigencia": null,
    "soatFechaVencimiento": "2026-06-09-00:00",
    "soatEntidadExpide": "LA PREVISORA S.A.COMPAÑIA DE SEGUROS",
    "soatVigente": "VIGENTE",
    "crTipoRevision": "REVISION TECNICO-MECANICO",
    "crFechaExpedicion": "2024-06-20-00:00",
    "crFechaVigencia": "2025-06-20-00:00",
    "crCdaExpide": "CENTRO DE DIAGNOSTICO AUTOMOTOR DE RISARALDA S.A.",
    "ibBlindado": "NO",
    "ibNivelBlindaje": null,
    "ibFechaBlindaje": null,
    "ibFechaDesblindaje": null,
    "riNumeroCertificado": null,
    "riFechaExpedicion": null,
    "riEstadoCertificado": null,
    "riPlacasReposicion": null,
    "dtNumeroPasajeros": 2,
    "igvFechaMatricula": "2006-05-24-00:00",
    "idTipoImportacion": null,
    "numRegistro": null,
    "organismoTransito": "STRIA TTO y GOB MCPAL SANTA ROSA CABAL",
    "tipoCombustible": 3,
    "propietariosActuales": [
        {
            "idTipoDocumento": "CC",
            "tipoDocumento": null,
            "numeroDocumento": "9861475",
            "nombreCompleto": "ADOLFO ENRIQUE OSPINO TREJOS",
            "primerNombre": "ADOLFO",
            "segundoNombre": "ENRIQUE",
            "primerApellido": "OSPINO",
            "segundoApellido": "TREJOS",
            "tipoPropiedad": null,
            "detallePropiedad": null,
            "direcciones": null,
            "locatarios": null
        }
    ]
}
 '''
data = json.loads(jsonD)

primetarios = validar_propietario(data,"9861475","ADOLFO ENRIQUE OSPINO TREJOS")

print(primetarios)