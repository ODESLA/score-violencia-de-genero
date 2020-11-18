# Script de bajada de PDF (procesar_pdf)

Foobar is a Python library for dealing with word pluralization.

## Requerimientos
En el ambiente ```conda```, asegurarse que de tener instalados las siguientes librerias:

```
black==v19.10b0
flake8>=3.7.9, <4.0
fuzzysearch>=0.7.3
ipython>=7.0.0, <8.0
isort>=4.3.21, <5.0
jupyter>=1.0.0, <2.0
```

Se puede utilizar el siguiente comando, clonando el repo:

```bash
pip install -r ~/d2-violencia-de-genero/src/requirements.txt
```

## Modo de uso

Para procesar todos los archivos en una carpeta, usar el parámetro `-a`, como se muestra debajo:

```bash
python procesar_pdf.py -a
```

Para procesar un archivo puntual en la carpeta donde se ejecuta el programa, usar el parámetro `-f`, como se muestra debajo:

```bash
python procesar_pdf.py -f nombre_de_archivo
```

## Lógica de desarrollo
El código se resuelve con los siguientes pasos:
1. Se evalúan los parámetros de llamada (`-f` o `-a`) y se responde con un mensaje en caso de error
2. Se llama a la función `extract_information` que se encarga de:
   1. Extraer el texto del PDF (a través de la función `extract_text_from_pdf`)
   2. Busca la cantidad de páginas del PDF
   3. Evalua si tiene que escribir en el archivo la página leída, y lo hace en caso de ser necesario en el directorio de ejecución


## Licencia
Autor: Leonardo Millán
