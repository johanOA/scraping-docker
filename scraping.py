import requests
import json
import os
import hashlib
import csv
from jsonpath_ng import parse

def buscarColsubsidio(searchWord):
    archivos_guardados = []
    generarHashCarpeta("/scraping/processed", archivos_guardados)
    
    #Cabecera de la peticiones HTTP
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }
    #URL 
    url = f"https://www.drogueriascolsubsidio.com/api/catalog_system/pub/products/search?ft={searchWord}&_from=0&_to=20&sm=0&O=OrderByReleaseDateDESC"
    
    res = requests.get(url, headers=headers, timeout=10)

    data = res.json()
    
    # Escribe el archivo json de la solicitud (Para pruebas se comenta la solicitud a la API para evitar bloqueos)
    with open('/scraping/unprocessed/response.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    # Leer el archivo JSON
    with open('/scraping/unprocessed/response.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    #Inicializar la lista de salida
    products = []

    #Busqueda avanzada para evitar for anidados
    jsonpath_expr = parse("$[*].items[*].sellers[*].commertialOffer.Installments[0].Value")
    resultados = [match.value for match in jsonpath_expr.find(data)]

    #Se recorre los datos de los productos en conjunto con los resultados de los precios 
    for item, precio in zip(data, resultados):
        product_name = item.get("productName", "N/A")
        product_id = item.get("productReferenceCode", "N/A")

        data = {
            "producto": product_name,
            "referencia": product_id,
            "precio": precio
        }
        products.append(data)
    

    # Guarda el csv que usa para verificar si ya existe
    with open("/scraping/unprocessed/unchecked.csv", 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["producto", "referencia", "precio"])
        writer.writeheader()
        writer.writerows(products)

    # Abrir el archivo en modo lectura
    with open(f'/scraping/hash.txt', "r") as archivo:
        # Leer todas las líneas, eliminar saltos de línea y almacenarlas en la lista
        hashes_guardados = [linea.strip() for linea in archivo]
    
    #Genera el hash de la busqueda actual
    hashUnchecked = calcular_hash_archivo("/scraping/unprocessed/unchecked.csv")

    #En caso de que no haya cambios en la busqueda(Se verifica con el hash) entonces no se va a guardar 
    if hashUnchecked not in hashes_guardados:
        # Guarda los csv en base al nombre de la busqueda
        print("Archivo con cambios, se actualiza el .csv")

        #Guarda en .CSV
        with open(f'/scraping/processed/{searchWord}.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["producto", "referencia", "precio"])
            writer.writeheader()
            writer.writerows(products)

        # Se escribe el nuevo hash que se agrego cuando se encuentran cambios
        with open('/scraping/hash.txt', 'a') as archivo_hash:
            archivo_hash.write(hashUnchecked + '\n')

    return products

#Genera un hash.txt para una carpeta, cada hash representa un archivo
def generarHashCarpeta(rutaCarpeta, archivos_guardados):    
    
    for archivo in os.listdir(rutaCarpeta):
        ruta_archivo = os.path.join(rutaCarpeta, archivo)
        
        if os.path.isfile(ruta_archivo):
            hash_archivo = calcular_hash_archivo(ruta_archivo)
            archivos_guardados.append(hash_archivo)

    with open(f'hash.txt', 'w' ) as file:
        for item in archivos_guardados:
            file.write(item + "\n")


# Función para calcular el hash de un archivo
def calcular_hash_archivo(ruta_archivo):
    sha256 = hashlib.sha256()
    with open(ruta_archivo, 'rb') as archivo:
        while chunk := archivo.read(8192):  # Leer el archivo en bloques de 8 KB
            sha256.update(chunk)
    return sha256.hexdigest()

if __name__ == '__main__':
    # Abrir el archivo en modo lectura
    with open(f'/scraping/busquedas.txt', "r") as archivo:
        # Leer todas las líneas, eliminar saltos de línea y almacenarlas en la lista
        busquedas = [linea.strip() for linea in archivo]
    
    for busqueda in busquedas:
        products = buscarColsubsidio(busqueda)
        print(products)