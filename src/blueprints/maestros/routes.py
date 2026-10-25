from flask import Blueprint, jsonify, request
from database import mysql

maestros_bp = Blueprint(
    'maestros',
    __name__,
    url_prefix='/api/maestros'
)

def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.descripcion]
    return dict(zip(columnas, fila))

# GET: Listar todos los maestros
@maestros_bp.route("/", methods=['GET'])
def listar_maestros():
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM maestros")
        datos = cursor.fetchall()
        maestros = [
            fila_a_diccionario(cursor, fila)
            for fila in datos
        ]
        return jsonify({
            'maestros': maestros,
            'mensaje': 'Lista de maestros',
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({
            'mensaje': 'Error al consultar los maestros: {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

# GET: Leer un maestro por ID
@maestros_bp.route("/<int:idmaestro>", methods=['GET'])
def leer_maestro(idmaestro):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT * FROM maestros WHERE idmaestro = %s
        """, (idmaestro,))
        fila = cursor.fetchone()
        
        if fila is None:
            return jsonify({
                'mensaje': 'Maestro no encontrado',
                'exito': False
            }), 404
            
        maestro = fila_a_diccionario(cursor, fila)
        return jsonify({
            'maestro': maestro,
            'exito': True
        }), 200
        
    except Exception as ex:
        return jsonify({
            'mensaje': 'Error al consultar el maestro: {}'.format(ex),
            'exito': False
        }), 500
        
    finally:
        if cursor is not None:
            cursor.close()

# POST: Registrar un maestro
@maestros_bp.route('/', methods=['POST'])
def registrar_maestro():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            'mensaje': 'Se requiere un objeto JSON',
            'exito': False
        }), 400

    # Nota: idmaestro se incluye si se envía manualmente o si la BD lo maneja, 
    # ajusta según si el ID es autoincrementable o provisto.
    campos = [
        'idmaestro', 'nombre', 'apaterno',
        'amaterno', 'correo'
    ]

    if any(
        campo not in datos
        or (isinstance(datos[campo], str) and not datos[campo].strip())
        for campo in campos
    ):
        return jsonify({
            'mensaje': 'Faltan campos obligatorios o son inválidos',
            'exito': False
        }), 400

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        # Comprobar si el idmaestro ya existe
        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro = %s",
            (datos['idmaestro'],)
        )

        if cursor.fetchone() is not None:
            return jsonify({
                'mensaje': 'El ID del maestro ya existe',
                'exito': False
            }), 409

        # Insertar el registro con parámetros SQL
        cursor.execute("""
            INSERT INTO maestros
                (idmaestro, nombre, apaterno, amaterno, correo)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datos['idmaestro'],
            datos['nombre'].strip() if isinstance(datos['nombre'], str) else datos['nombre'],
            datos['apaterno'].strip() if isinstance(datos['apaterno'], str) else datos['apaterno'],
            datos['amaterno'].strip() if isinstance(datos['amaterno'], str) else datos['amaterno'],
            datos['correo'].strip() if isinstance(datos['correo'], str) else datos['correo']
        ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Maestro registrado correctamente',
            'exito': True
        }), 201

    except Exception as ex:
        mysql.connection.rollback()
        return jsonify({
            'mensaje': 'Error al registrar el maestro: {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

# PUT: Modificar un maestro
@maestros_bp.route("/<int:idmaestro>", methods=['PUT'])
def modificar_maestro(idmaestro):
    datos = request.get_json()
    if not datos:
        return jsonify({
            "mensaje": "No se recibieron datos para modificar",
            "exito": False
        }), 400

    nombre = datos.get('nombre')
    apaterno = datos.get('apaterno')
    amaterno = datos.get('amaterno')
    correo = datos.get('correo')

    if not nombre or not apaterno or not correo:
        return jsonify({
            "mensaje": "Nombre, apellido paterno y correo son obligatorios",
            "exito": False
        }), 400

    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )
        maestro = cursor.fetchone()
        
        if not maestro:
            return jsonify({
                "mensaje": "No existe un maestro con ese ID",
                "exito": False
            }), 404

        sql = """
            UPDATE maestros
            SET nombre = %s,
                apaterno = %s,
                amaterno = %s,
                correo = %s
            WHERE idmaestro = %s
        """
        cursor.execute(sql, (
            nombre,
            apaterno,
            amaterno,
            correo,
            idmaestro
        ))
        
        mysql.connection.commit()
        
        return jsonify({
            "mensaje": "Maestro modificado correctamente",
            "idmaestro": idmaestro,
            "exito": True
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            "mensaje": "Error al modificar el maestro",
            "error": str(e),
            "exito": False
        }), 500

    finally:
        if cursor:
            cursor.close()

# DELETE: Eliminar un maestro
@maestros_bp.route("/<int:idmaestro>", methods=['DELETE'])
def eliminar_maestro(idmaestro):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )
        maestro = cursor.fetchone()
        
        if not maestro:
            return jsonify({
                "mensaje": "No existe un maestro con ese ID",
                "exito": False
            }), 404
            
        cursor.execute(
            "DELETE FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )
        
        mysql.connection.commit()
        
        return jsonify({
            "mensaje": "Maestro eliminado correctamente",
            "idmaestro": idmaestro,
            "exito": True
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            "mensaje": "Error al eliminar el maestro",
            "error": str(e),
            "exito": False
        }), 500

    finally:
        if cursor:
            cursor.close()