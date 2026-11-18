import requests # Importa la librería 'requests' para hacer peticiones HTTP a la API del router
import json # Importa la librería 'json' para dar formato y guardar el archivo de inventario
from requests.auth import HTTPBasicAuth # Importa 'HTTPBasicAuth' para enviar el usuario y contraseña

# Desactiva los avisos en consola por usar certificados SSL de prueba (autofirmados)
requests.packages.urllib3.disable_warnings()

# 1. Datos de conexión (Sandbox de Cisco del PDF)
# Dirección URL del recurso YANG estándar que contiene las interfaces del router
url = "https://sandbox-iosxe-latest-1.cisco.com/restconf/data/ietf-interfaces:interfaces"
# url = "https://192.168.1.1/restconf/data/ietf-interfaces:interfaces"

# Cabeceras HTTP para pedir que el router nos responda en formato JSON
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# Credenciales de acceso al router de laboratorio
auth = HTTPBasicAuth("developer", "C1sco12345")

try:
    # 2. Petición GET al router (ignora validación SSL y espera máximo 10 segundos)
    response = requests.get(url, headers=headers, auth=auth, verify=False, timeout=10)

    # Verifica que el router haya respondido correctamente (código 200 OK)
    if response.status_code == 200:
        # Convierte la respuesta JSON a un diccionario de Python
        data = response.json()
        # Extrae la lista completa de interfaces del router
        interfaces = data["ietf-interfaces:interfaces"]["interface"]
        
        # Lista vacía donde guardaremos solo las interfaces que sí estén activas y tengan IP
        activas = []

        # 3. Revisar interfaz por interfaz
        for iface in interfaces:
            # Busca si la interfaz tiene direcciones IPv4 asignadas (si no tiene, devuelve lista vacía)
            ips = iface.get("ietf-ip:ipv4", {}).get("address", [])
            
            # Si la interfaz está encendida (True) Y tiene al menos una IP, la guarda
            if iface.get("enabled") == True and len(ips) > 0:
                # Agrega un diccionario con el nombre real, su primera IP y su máscara
                activas.append({
                    "nombre": iface["name"],
                    "ip": ips[0]["ip"],
                    "mascara": ips[0]["netmask"]
                })

        # 4. Crear el archivo inventario_interfaces.json y guardar la lista ordenada
        with open("inventario_interfaces.json", "w") as archivo:
            json.dump(activas, archivo, indent=4)

        # Imprime mensaje de confirmación en la consola
        print("Archivo inventario_interfaces.json generado.")
    else:
        # Muestra el código de error si el router rechazó la petición
        print("Error:", response.status_code)

# Captura cualquier fallo de conexión o falta de respuesta del dispositivo
except requests.exceptions.RequestException as e:
    print("Errorrrrr:", e)