# Mini Proyecto Sistemas Operacionales
**Universidad Icesi**  
**Curso:** Sistemas Operativos  
**Docente:** Daniel Barragán C.  
**Tema:**  Servicios web  
**Estudiantes:** 
José Luis Osorio Quintero 12203012  
Juan David Cardona Mena 13103002  
Juan Pablo Medina Mora 11112010  

## Objetivos
* Desplegar una aplicación en un servidor que ejecuta el sistema operativo Linux
* Realizar los ajustes y depuración necesarios para desplegar una aplicación en Linux
* Realizar aplicaciones para obtener información del sistema operativo

## Descripción
Para el despliegue de una aplicación en un servidor se requiere conocer los procedimientos necesarios relacionados con la configuración de las interfaces de red, ajustes de seguridad, instalación de dependencias, usuarios y herramientas de depuración del sistema operativo.

El siguiente proyecto consiste en el despliegue de una aplicación web para obtener información del sistema operativo (Deberá emplear la aplicación desarrollada en el primer parcial). Para este propósito se debe emplear el sistema operativo CentOS7, el microframework flask y ambientes virtuales.

![][17]

## Desarrollo
En el presente apartado se explicará todo el proceso realizado para la resolución del taller, desde la instalación de la máquina virtual hasta la prueba del servicio web usando Paperman y netstat.

### Instalación del sistema operativo CentOS 7 y de interfaces de red
Para la instalación del sistema CentOS 7 se procedió a descargar una imagen del sistema operativo, en específico el centos 7 x86 64 minimal. Con esta imagen descargada se procedió a realizar la instalación de la máquina virtual en el programa VirtualBox,inicialmente se creó el usuario administrador para después configurar la memoria y demás apartados del sistema incluyendo los adaptadores de red puente y NAT. El proceso de muestra a continuación.

![][1]
![][2]
![][3]

Al iniciar sesión con las credenciales para el usuario raíz creado, se procedió a probar que la configuración de los adaptadores de red hubiese sido exitosa, esto por medio de la realización de pings y posteriormente por medio de la conexión al programa putty.

```
# ping 8.8.8.8
```

Con esto se finalizó la instalación y configuración básica del sistema operativo.

### Configuración de puertos
En la actualización a CentOS 7 uno de los cambios principales al sistema fue el reemplazo del archivo de configuración iptables, en esta versión para realizar la configuración de puertos se usa el componente FirewallD. Para realizar esta configuración se optó por desactivar el componente FirewallD, e instalar posteriormente el componente iptables, en el cual se procedió a realizar la configuración, en específico se habilito el puerto 8088.

```
# cat /etc/sysconfig/iptables
# service iptables restart
```

![][4]
![][5]
![][6]

Con lo anterior el puerto del que hace uso el servicio queda habilitado.

### Creación del usuario filesystem_user, creación de ambiente virtual e instalación de flask y sus dependencias

Con las configuraciones iniciales pertinentes terminadas el primer paso para hacer uso de los programas consistió en la creación de un nuevo usuario, para tal fin se siguió el siguiente procedimiento

```
# adduser filesystem_user
# passwd password
```

Con el nuevo usuario creado se procedió a crear el ambiente virtual que el usuario utilizaría

```
# su filesystem_user
$ cd ~/
$ mkdir envs
$ cd envs
$ virtualenv flask_env
```

Se activó el ambiente virtual creado

```
$ cd ~/envs
$ . flask_env/bin/activate
```

Después se procedió a instalar Flask en el nuevo ambiente virtual

```
$ pip install Flask
```

![][7]

### Aplicación en Python
A continuación, se presentan los contratos del servicio desplegado.

Descripción de las URIs

|   |POST   |GET   |PUT   |DELETE   |
|---|---|---|---|---|
| /files  | Crear archivo  | Obtener listado de archivos  | No aplica | Elimina todos los archivos  |
| /files/recently_created  | No aplica  | Retorna los archivos que se crearon recientemente  | No aplica | No aplica  |

Descripción de los formatos de envío de las solicitudes

|   |POST   |GET   |PUT   |DELETE   |
|---|---|---|---|---|
| /files  | JSON  | No aplica  | No aplica  | No aplica  |
| /files/recently_created  | No aplica  | No aplica  | No aplica  | No aplica  |

Descripción de los formatos de respuesta de las solicitudes

|   |POST   |GET   |PUT   |DELETE   |
|---|---|---|---|---|
| /files  | HTTP 201 CREATED | JSON | HTTP 404 NOT FOUND | HTTP 200 OK |
| /files/recently_created  | HTTP 404 NOT FOUND | JSON  | HTTP 404 NOT FOUND | HTTP 404 NOT FOUND |

Descripción del formato de intercambio de datos (JSON)  

```json
{
  "filename": "carta",
  "content": "this is the file content"
}
```

```json
{
  "files": [
    "carta",
    "listado",
    "tareas",
    "recordatorio"
  ]
}
```

A continuación, se presentan los archivos que se usaron para correr los servicios.

Archivo functions.py
```python
from subprocess import Popen, PIPE

def create_files(filename,content):
  filecreate = Popen(["touch",filename+'.txt'], stdout=PIPE, stderr=PIPE)
  writeFile = Popen(['echo',content,'>>', filename+'.txt'], stdin=filecreate.stdout, stdout=PIPE, stderr=PIPE).communicate()
  return True

def get_all_files():
  process = Popen(["ls"], stdout=PIPE, stderr=PIPE)
  process2 = Popen(["col","-b"], stdin= process.stdout, stdout=PIPE, stderr=PIPE)
  return process2.communicate()[0].split('\n')


def delete_all_files():
  vip = Popen(["rm","-r","/home/filesystem_user/flask_test/parcial/prueba/*"], stdout=PIPE, stderr=PIPE).communicate()
  return True

def get_recent_files():
  rF = Popen(["ls", "-lat"], stdout=PIPE, stderr=PIPE)
  list = Popen(["awk",'{print $9}'], stdin=rF.stdout, stdout=PIPE, stderr=PIPE).communicate()
  return filter(None,list)
```

Archivo mainScript.py
```python
from flask import Flask, abort, request
import json

from functions import create_files, get_all_files, delete_all_files, get_recent_files

app = Flask(__name__)
api_url = '/v1.0'

@app.route(api_url+'/files',methods=['POST'])
def create_file():
  content = request.get_json(silent=True)
  filename = content['filename']
  content = content['content']
  if not filename or not content:
    return "cannot create empty file", 400
  if create_files(filename,content):
    return "HTTP 201 CREATED", 201
  else:
    return "error while creating user", 400

@app.route(api_url+'/files',methods=['GET'])
def get_fileList():
  list = {}
  list["files"] = get_all_files()
  return json.dumps(list), 200

@app.route(api_url+'/files',methods=['PUT'])
def update_user():
  return "HTTP 404 NOT FOUND", 404



@app.route(api_url+'/files',methods=['DELETE'])
def delete_files():

  if delete_all_files():
    return 'HTTP 200 OK', 200
  else:
    return 'ERROR', 200


@app.route(api_url+'/files/recently_created',methods=['POST'])
def func1():
  return "HTTP 404 NOT FOUND", 404

@app.route(api_url+'/files/do_ls',methods=['GET'])
def get_rece_files():
   return get_recent_files()
   


@app.route(api_url+'/files/recently_created',methods=['PUT'])
def func2():
  return "HTTP 404 NOT FOUND", 404


@app.route(api_url+'/files/recently_created',methods=['DELETE'])
def func3():
  return "HTTP 404 NOT FOUND", 404


if __name__ == "__main__":
  app.run(host='0.0.0.0',port=8088,debug='True')
```
Con los scripts realizados se procedió a realizar pruebas con la finalidad de saber si los servicios al levantarse eran accesibles.

Primero se levanta el servicio

```
$ (flask_env) python mainScript.py
```

![][8]

Después se decidió probar por medio del navegador si se podía acceder al servicio POST.

![][9]

Y se pudo observar cómo se podía contactar con todas las funciones del servicio expuesto.

![][10]

Comprobado el servicio con el navegador se comprobó el funcionamiento de los diferentes servicios por medio del programa Postman.

**files GET**

![][11]

**files POST**

![][12]

**recently created GET**

![][13]

### Validación de la ejecución del servicio (netstat)

#### Netstat
netstat (estadísticas de red) es una herramienta de la línea de comandos para controlar las conexiones de red entrantes y salientes, así como la visualización de las tablas de enrutamiento, las estadísticas de la interfaz, etc netstat está disponible en todos los sistemas operativos de tipo Unix y también disponibles en el sistema operativo Windows. Es muy útil en términos de resolución de problemas de red y la medición del desempeño. Netstat es una de las herramientas de depuración de servicios de red más básicas, que le dice qué puertos están abiertos y si los programas escuchan en tales puertos.

Esta herramienta es muy importante y muy útil para los administradores de red de Linux, así como para los administradores de sistemas para supervisar y solucionar los problemas relacionados con la red y determinar el rendimiento del tráfico de red. Este artículo muestra los usos del comando netstat con sus ejemplos que pueden ser útiles en la operación diaria.

#### Usando netstat -putona
Con el fin de realizar la comprobación de servicios se descargó e instalo el servicio netstat y se hizo uso del comando -putona, que nos permite ver que puertos despliegan un determinado proceso.

p Muestra las conexiones para el protocolo especificado que puede ser TCP o UDP
u Lista todos los puertos UDP
t Lista todos los puertos TCP
o Muestra los timers
n Muestra el número de puerto
a Visualiza todas las conexiones activas del sistema

A continuación, se presentan los resultados obtenidos.
Iniciando con la realización del comando sin tener el servicio levantado, como puede observarse en la lista de salida no figura el puerto 8088, el encargado de correr el servicio según lo que se escribió en el script.

![][14]

En las siguientes imágenes se puede observar el resultado del comando tras levantar el servicio, puede observarse que el puerto 8088 aparece en la lista, y que el servicio que por el corre es python.

![][15]
![][16]

Con lo anterior se concluye que el servicio se encuentra en correcto funcionamiento y se da por finalizado el proyecto.


## Referencias
https://ubuntulife.wordpress.com/2014/03/11/netstat-putona-un-comando-que-no-olvidaras-para-monitorizar-las-conexiones-en-linux/


[1]: capturascentos7/0.PNG
[2]: capturascentos7/1.PNG
[3]: capturascentos7/2.PNG
[4]: capturascentos7/3.PNG
[5]: capturascentos7/4.PNG
[6]: capturascentos7/5.PNG
[7]: capturascentos7/6.PNG
[8]: capturascentos7/7.PNG
[9]: capturascentos7/8.PNG
[10]: capturascentos7/9.png
[11]: capturascentos7/10.PNG
[12]: capturascentos7/11.PNG
[13]: capturascentos7/12.PNG
[14]: capturascentos7/13.png
[15]: capturascentos7/14.png
[16]: capturascentos7/15.png
[17]: capturascentos7/16.png
