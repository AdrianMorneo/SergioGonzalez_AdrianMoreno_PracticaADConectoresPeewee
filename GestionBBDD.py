import peewee
import pymysql as ps
from peewee import MySQLDatabase, CharField, Model, DateField, ForeignKeyField, TextField, AutoField

import Utiles as ut
import GestionProfesores as gp
import GestionAlumnos as ga
import GestionCursos as gc
from configparser import ConfigParser

######################################################################
######################################################################
###                             BBDD                               ###
######################################################################
######################################################################

db = MySQLDatabase('adrianmoreno_sergiogonzalezPeewee', user='root', password='my-secret-pw', host='localhost',
                   port=3307)


def crearBBDD():
    """
    Crea la base de datos si no existe con conectores
    :return: No devuelve nada
    """
    configuracion = ConfigParser()
    configuracion.read("ConexionConfig.ini")

    con = ps.connect(host=configuracion.get('conexion', 'host'),
                     port=configuracion.getint('conexion', 'puerto'),
                     user=configuracion.get('conexion', 'user'),
                     password=configuracion.get('conexion', 'password'))
    cursor = con.cursor()

    try:
        cursor.execute('CREATE DATABASE IF NOT EXISTS adrianmoreno_sergiogonzalezPeewee;')
    except Exception as errorCrearBBDD:
        print("Error al crear la base de datos:", errorCrearBBDD)
    finally:
        con.commit()
        cursor.close()


def conexion():
    """
    Realiza la conexión la BBDD con los parametros que contiene el fichero de configuracion ConexionConfig.ini
    :return: No devuelve nada
    """

    try:
        # Definición del modelo
        class MiModelo(Model):
            campo_texto = CharField()

            class Meta:
                database = db

        # Conexión a la base de datos
        db.connect()

        return db

    except Exception as errorConexion:
        print("Error en la conexión:", errorConexion)

    return None, None  # Retorna None en caso de error en la conexión


class profesores(Model):
    ID = AutoField(primary_key=True)
    DNI = CharField(unique=True, max_length=9)
    Nombre = CharField(max_length=255)
    Direccion = CharField(max_length=255)
    Telefono = CharField(max_length=9)

    class Meta:
        database = db
        table_name = 'profesores'
    # Tabla para cursos


class cursos(Model):
    Codigo = AutoField(primary_key=True)
    Nombre = CharField(unique=True, max_length=255)
    Descripcion = TextField()
    ProfesorID = ForeignKeyField(profesores, backref='cursos', null=True)

    class Meta:
        database = db
        table_name = 'Cursos'
        # Tabla Alumnos


class alumnos(Model):
    NumeroExpediente = AutoField(primary_key=True)
    Nombre = CharField(max_length=255)
    Apellidos = CharField(max_length=255)
    Telefono = CharField(unique=True, max_length=9)
    Direccion = CharField(max_length=255)
    FechaNacimiento = DateField()

    class Meta:
        database = db
        table_name = 'alumnos'
    # Tabla para la relación entre alumnos y cursos (muchos a muchos)


class alumnoscursos(Model):
    AlumnoExpediente = ForeignKeyField(alumnos, field='NumeroExpediente', backref='alumnos')
    CursoCodigo = ForeignKeyField(cursos, field='Codigo', backref='cursos')

    class Meta:
        database = db
        table_name = 'alumnoscursos'


def crearTablasBBDD():
    """
    Crea las tablas principales de la BBDD si no existen
    :return: No devuelve nada.
    """

    try:
        # Tabla para profesores
        db.create_tables([profesores, cursos, alumnos, alumnoscursos])
        db.close()

    except Exception as errorCrearTablas:

        "-----Las tablas ya existen----"


######################################################################
######################################################################
###                          PROFESORES                            ###
######################################################################
######################################################################

def nuevoProfesorInsertBBDD(dni, nombre, direccion, telefono):
    """
    Introduce en la base de datos un nuevo profesor con los datos recibidos por parametro

    :param dni: Recibe DNI profesor
    :param nombre: Recibe nombre profesor
    :param direccion: Recibe direccion profesor
    :param telefono: Recibe telefono profesor
    :return: No devuelve nada
    """

    try:
        # Insertar Profesor
        nuevoProfesor = profesores.create(DNI=dni, Nombre=nombre, Direccion=direccion, Telefono=telefono)
        nuevoProfesor.save()
        print("Profesor dado de alta correcctamente")

    except Exception as errorMeterProfesor:
        print("Error al introducir profesor en la BBDD", errorMeterProfesor)
        print("No se ha realizado un nuevo alta")
    finally:
        'confirmarEjecucionCerrarCursor(con, cur)'


def eliminarProfesorBBDD():
    """
    Realiza la consulta SQL para eliminar al profesor, pide DNI y confirma
    :return: No devuelve nada
    """

    if ut.comprobarVacio("profesores"):
        dni = gp.buscarProfesor()
        if dni != "":
            if ut.confirmacion(
                    "Si el profesor imparte algún curso, el curso se quedará sin profesor\nSeguro que quieres ELIMINAR AL PROFESOR?",
                    f"Eliminacion de Profesor con {dni} realizada"):
                try:
                    profesores.delete().where(profesores.DNI == dni).execute()

                except Exception as errorEliminar:
                    print(f"Error al eliminar el profesor con DNI: {dni}: {errorEliminar}")
                finally:
                    '#confirmarEjecucionCerrarCursor(con, cur)'


def buscarProfesorBBDD(dni):
    """
    Realiza la consulta en la BBDD buscando un profesor, recibiendo el dni
    :param dni: Recibe el DNI
    :return: Devuelve el ID del profesor encontrado por el DNI
    """

    if ut.comprobarVacio("profesores"):
        try:
            profesor = profesores.select().where(profesores.DNI == dni).first()
            if profesor:
                print("Datos del profesor:")
                print("ID:", profesor.ID)
                print("DNI:", profesor.DNI)
                print("Nombre:", profesor.Nombre)
                print("Dirección:", profesor.Direccion)
                print("Teléfono:", profesor.Telefono)
                return profesor.ID
            else:
                print("No se encontró ningún profesor con el DNI especificado.")
                return 0
        except Exception as errorModificarProfesor:
            print(f"Error al buscar el profesor con DNI: {dni}: {errorModificarProfesor}")
            return 0
        finally:
            'confirmarEjecucionCerrarCursor(con, cur)'


def buscarProfesorBBDDSinPrint(dni):
    """
    Realiza la consulta en la BBDD buscando un profesor, recibiendo el dni
    :param dni: Recibe el DNI
    :return: Devuelve el ID del profesor encontrado por el DNI
    """

    try:
        profesor = profesores.select().where(profesores.DNI == dni).first()
        if profesor:
            return profesor.ID
        else:
            print("No se encontró ningún profesor con el DNI especificado.")
            return 0
    except Exception as errorBuscar:
        print(f"Todavia no hay ningun profesor con dni: {dni}")
        return 0
    finally:
        ''


# confirmarEjecucionCerrarCursor(con, cur)


def modificarProfesorBBDD():
    """
    Permite al usuario modificar un profesor seleccionando el campo a modificar.
    :return: No devuelve nada.
    """

    if ut.comprobarVacio("profesores"):
        dni = gp.buscarProfesor()
        if dni != "":
            try:
                # Consultar datos actuales del profesor

                profesor = profesores.select().where(profesores.DNI == dni).first()

                # Mostrar opciones al usuario
                print("\nSeleccione el campo a modificar:")
                print("1. DNI")
                print("2. Nombre")
                print("3. Dirección")
                print("4. Teléfono")
                print("0. Cancelar")

                finEntradaAlta = False
                fallos = 0

                opcion = input("Opción: ")

                if opcion == "1":

                    while not finEntradaAlta and fallos < 5:
                        dniNuevo = input("DNI: ").strip().upper()
                        if ut.validarDNI(dniNuevo):
                            if buscarProfesorBBDDSinPrint(dniNuevo) == 0:
                                if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                    profesores.update(DNI=dniNuevo).where(profesores.DNI == dni).execute()
                                    finEntradaAlta = True
                                    print("Profesor actualizado correctamente.")
                                else:
                                    finEntradaAlta = True
                            else:
                                fallos = ut.fallo(fallos, "DNI está ya en la BBDD")
                        else:
                            fallos = ut.fallo(fallos, "El Dni debe tener 8 numeros y una letra")

                elif opcion == "2":

                    while not finEntradaAlta and fallos < 5:

                        nombreNuevo = input("Nombre: ").strip().upper()
                        if ut.validarNombre(nombreNuevo):
                            if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                profesores.update(Nombre=nombreNuevo).where(profesores.DNI == dni).execute()
                                finEntradaAlta = True
                                print("Profesor actualizado correctamente.")
                            else:
                                finEntradaAlta = True
                        else:
                            fallos = ut.fallo(fallos, "El nombre debe contener al menos 2 caracteres.")

                elif opcion == "3":

                    while not finEntradaAlta and fallos < 5:
                        direccionNueva = input("Direccion: ").strip().upper()
                        if ut.validarDireccion(direccionNueva):
                            if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                profesores.update(Direccion=direccionNueva).where(profesores.DNI == dni).execute()
                                finEntradaAlta = True
                                print("Profesor actualizado correctamente.")
                            else:
                                finEntradaAlta = True
                        else:
                            fallos = ut.fallo(fallos, "La dirección debe de contener mínimo 4 carácteres.")

                elif opcion == "4":

                    while not finEntradaAlta and fallos < 5:
                        telefonoNuevo = input("Telefono: ").strip().upper()
                        if ut.validarTelefono(telefonoNuevo):
                            if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                profesores.update(Telefono=telefonoNuevo).where(profesores.DNI == dni).execute()
                                finEntradaAlta = True
                                print("Profesor actualizado correctamente.")
                            else:
                                finEntradaAlta = True
                        else:
                            fallos = ut.fallo(fallos, "El Telefono debe tener 9 numeros")

                elif opcion == "0":
                    print("Modificación cancelada.")
                else:
                    print("Opción no válida.")

            except Exception as errorModificarProfesor:
                print(f"Error al modificar el profesor {dni}: {errorModificarProfesor}")
            finally:
                'confirmarEjecucionCerrarCursor(con, cur)'


def mostrarProfesores():
    """
    Muestra los profesores de una manera atractiva
    :return: No devuelve nada
    """
    cont = 1
    # Seleccionar todos los alumnos

    profesor = profesores.select()

    # Recuperar todos los resultados

    if not profesores:
        print("No hay profesores registrados en la BBDD.")
    else:
        print("Lista de profesores:")
        for profesor in profesores:
            print(f"--- PROFESOR {cont}---")
            print("ID:", profesor.ID)
            print("DNI:", profesor.DNI)
            print("Nombre:", profesor.Nombre)
            print("Dirección:", profesor.Direccion)
            print("Teléfono:", profesor.Telefono + '\n')
            cont = cont + 1
    'confirmarEjecucionCerrarCursor(con, cur)'


######################################################################
######################################################################
###                           CURSOS                               ###
######################################################################
######################################################################

def nuevoCursoInsertBBDD(nombre, descripcion):
    """
    Introduce en la base de datos un nuevo profesor con los datos recibidos por parametro
    :param nombre: Recibe nombre Curso
    :param descripcion: Recibe descripcion Curso
    :return: No devuelve nada
    """
    try:
        nuevoCurso = cursos.create(Nombre=nombre, Descripcion=descripcion)
        nuevoCurso.save()
        print("Curso dado de alta correcctamente")

    except Exception as errorMeterCurso:
        print("Error al introducir Curso en la BBDD", errorMeterCurso)
        print("No se ha realizado un nuevo alta")


def eliminarCursosBBDD():
    '''
    Metodo para eliminar un curso
    :return: No devuelve nada
    '''
    if ut.comprobarVacio("Cursos"):
        nombre = gc.buscarCurso()

        if nombre != "":
            if ut.confirmacion(
                    "Si el curso tiene alumnos, estos de desmatricularan\nSeguro que quieres ELIMINAR EL CURSO?",
                    f"Eliminacion del CURSO: {nombre} realizada"):
                try:
                    cursos.delete().where(cursos.Nombre == nombre).execute()

                except Exception as errorEliminar:
                    print(f"Error al eliminar el CURSO: {nombre}: {errorEliminar}")
                finally:
                    'confirmarEjecucionCerrarCursor(con, cur)'


def buscarCursoBBDD(nombre):
    '''
    Metodo para buscar un curso concreto , tambien muestra su profesor si tiene uno
    , en caso contrario avisa de que todavia no tiene
    :param nombre: Nombre del curso que se desea buscar
    :return: Devuelve True o False en funcion de si encuentra el curso con el nombre indicado
    '''

    encontrado = False
    if ut.comprobarVacio("Cursos"):
        try:
            curso = cursos.select(cursos.Codigo, cursos.Nombre, cursos.Descripcion, cursos.ProfesorID).where(
                cursos.Nombre == nombre).first()
            if curso:
                print("Datos del Curso:")
                print("Codigo:", curso.Codigo)
                print("Nombre:", curso.Nombre)
                print("Descripcion:", curso.Descripcion)
                profe = (profesores.select(profesores.Nombre, profesores.DNI).where(
                    profesores.ID == curso.ProfesorID).first())
                if profe is not None:
                    print(f"Profesor: {profe.Nombre} , con el DNI: {profe.DNI}\n")
                else:
                    print("No tiene profesor todavia")
                encontrado = True
            else:
                print("No se encontró ningún curso con el nombre especificado.")
        except peewee.DoesNotExist:
            print(f"No se encontró ningún curso con el nombre especificado: {nombre}")
        except Exception as errorBuscarCurso:
            print(f"Error al buscar el curso con nombre: {nombre}: {errorBuscarCurso}")

    return encontrado


def modificarCursoBBDD():
    """
    Permite al usuario modificar un profesor seleccionando el campo a modificar.

    :return: No devuelve nada.
    """
    if ut.comprobarVacio("Cursos"):
        nombre = gc.buscarCurso()
        if nombre != "":
            try:
                # Consultar datos actuales del curso
                curso = cursos.select().where(cursos.Nombre == nombre).first()

                # Mostrar opciones al usuario
                print("\nSeleccione el campo a modificar:")
                print("1. Nombre")
                print("2. Descripcion")
                print("3. Aniadir/Cambiar Profesor de Curso")
                print("0. Cancelar")

                finEntradaAlta = False
                fallos = 0

                opcion = input("Opcion: ")

                if opcion == "1":

                    while not finEntradaAlta and fallos < 5:

                        nombreNuevo = input("Nuevo nombre: ").strip().upper()
                        if ut.validarNombre(nombreNuevo):
                            if devolverIddeCurso(nombreNuevo) is None:
                                if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                    cursos.update(Nombre=nombreNuevo).where(cursos.Nombre == nombre).execute()
                                    finEntradaAlta = True
                                    print("Curso actualizado correctamente.")
                                else:
                                    finEntradaAlta = True
                            else:
                                fallos = ut.fallo(fallos, "El nombre ya esta en la BBDD.")
                        else:
                            fallos = ut.fallo(fallos, "El nombre debe contener al menos 2 caracteres.")

                elif opcion == "2":

                    while not finEntradaAlta and fallos < 5:
                        descripcionNueva = input("Nueva descripcion: ").strip().upper()
                        if ut.validarDireccion(descripcionNueva):
                            if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                cursos.update(Descripcion=descripcionNueva).where(cursos.Nombre == nombre).execute()
                                finEntradaAlta = True
                                print("Curso actualizado correctamente.")
                            else:
                                finEntradaAlta = True
                        else:
                            fallos = ut.fallo(fallos, "La dirección debe de contener mínimo 4 carácteres.")

                elif opcion == "3":
                    while not finEntradaAlta and fallos < 5:
                        profesorDni = input("DNI Profesor: ").strip().upper()

                        if ut.validarDNI(profesorDni):
                            IDProfesor = buscarProfesorBBDD(profesorDni)
                            if IDProfesor != 0:
                                if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                    cursos.update(ProfesorID=IDProfesor).where(cursos.Nombre == nombre).execute()
                                    finEntradaAlta = True
                                    print("Curso actualizado correctamente.")
                                else:
                                    finEntradaAlta = True
                            else:
                                print("No hay en la BBDD ningun profesor con ese DNI")
                        else:
                            fallos = ut.fallo(fallos, "El DNI debe de tener 8 digitos y una letra")

                elif opcion == "0":
                    print("Modificación cancelada.")
                else:
                    print("Opción no válida.")

            except Exception as errorModificarProfesor:
                print(f"Error al modificar el profesor {nombre}: {errorModificarProfesor}")
            finally:
                ' confirmarEjecucionCerrarCursor(con, cur)'


def mostrarTodosCursosBBDD():
    '''
    Metodo para mostrar todos los cursos y en caso de tener un profesor asignado lo muestra tambien
    :return: No devuelve nada
    '''

    cont = 1
    # Seleccionar todos los cursos
    curso = cursos.select()
    # Recuperar todos los resultados
    if not cursos:
        print("No hay cursos registrados en la BBDD.")
    else:
        print("Lista de cursos:")
        for curso in cursos:
            print(f"--- CURSO {cont}---")
            print("Codigo:", curso.Codigo)
            print("Nombre:", curso.Nombre)
            print("Descripcion:", curso.Descripcion)
            profe = (
                profesores.select(profesores.Nombre, profesores.DNI).where(profesores.ID == curso.ProfesorID).first())
            if profe is not None:
                print(f"Profesor: {profe.Nombre} , con el DNI: {profe.DNI}\n")
            else:
                print("No tiene profesor todavia")

            cont = cont + 1


def devolverIddeCurso(nombre):
    '''
    Metodo para devolver el id del curso con el nombre pasado por parametro
    :param nombre: Nombre del curso del que se desea saber el id
    :return: Devuelve el id si encuentra el curso , de lo contrario devuelve None
    '''
    resultados = cursos.select().where(cursos.Nombre == nombre)

    if resultados:
        # El resultado no es None, lo que significa que se encontro un curso con ese nombre
        id = resultados[0]
        return id
    else:
        return None


######################################################################
######################################################################
###                           ALUMNOS                              ###
######################################################################
######################################################################
def nuevoAlumnoInsertBBDD(nombre, apellidos, telefono, direccion, fecha):
    '''
    Metodo para inertar nuevos alumnos a la bbdd el cual recibe todos los atributos necesarios
    :param nombre: Nombre del nuevo alumno
    :param apellidos: apellidos del nuevo alumno
    :param telefono: telefono del nuevo alumno
    :param direccion: direccion del nuevo alumno
    :param fecha: fecha del nuevo alumno
    :return: No devuelve nada
    '''

    try:
        nuevoAlumno = alumnos.create(Nombre=nombre, Apellidos=apellidos, Telefono=telefono, Direccion=direccion,
                                     FechaNacimiento=fecha)
        nuevoAlumno.save()
        print("Alumno dado de alta correcctamente")

    except Exception as errorMeterProfesor:
        print("Error al introducir alumno en la BBDD", errorMeterProfesor)
        print("No se ha realizado un nuevo alta")


def buscarAlumnoBBDD(nombre, apellidos):
    '''
    Metodo para buscar un alumno , tambien imprime la informacion de este en caso de encontrarlo
    :param nombre: Nombre del alumno a buscar
    :param apellidos: Apellidos del alumno a buscar
    :return: Devuelve el id o 0 en caso de no encontrar el alumno
    '''
    encontrado = False
    if ut.comprobarVacio("alumnos"):

        alumno = alumnos.select().where(alumnos.Nombre == nombre, alumnos.Apellidos == apellidos).first()
        if alumno:
            print("Datos del Alumno:")
            print("ID:", alumno.NumeroExpediente)
            print("Nombre:", alumno.Nombre)
            print("Apellidos:", alumno.Apellidos)
            print("telefono:", alumno.Telefono)
            print("Direccion:", alumno.Direccion)
            print("Fecha de nacimiento :", alumno.FechaNacimiento)
            return alumno.NumeroExpediente
        else:
            print("No se encontro ningun alumno ")
            return 0


def buscarAlumnoBBDDid(nombre, apellidos):
    '''
    Metodo para buscar un alumno
    :param nombre: Nombre del alumno a buscar
    :param apellidos: Apellidos del alumno a buscar
    :return: Devuelve el id o 0 en caso de no encontrar el alumno
    '''
    encontrado = False
    if ut.comprobarVacio("alumnos"):
        try:
            alumno = alumnos.select().where(alumnos.Nombre == nombre, alumnos.Apellidos == apellidos).first()
            if alumno:
                return alumno.NumeroExpediente
            else:
                print("No se encontro ningun alumno. ")
                return 0
        except:
            print("Error al buscar el alumno. ")
            return 0


def eliminarAlumnoBBDD():
    '''
    Metodo para eliminar un alumno de la bbdd
    :return: No devuelve nada
    '''
    if ut.comprobarVacio("alumnos"):
        alumno = ga.buscarAlumno()
        if alumno != "":
            if ut.confirmacion("Seguro que quieres eliminar el Alumno?",
                               f"Eliminacion del Alumno {alumno[0]} {alumno[1]}"):
                try:
                    alumnos.delete().where(alumnos.Nombre == alumno[0], alumnos.Apellidos == alumno[1]).execute()

                except Exception as errorEliminar:
                    print(f"Error al eliminar el Alumno: {alumno[0]}")


def modificarAlumnoBBDD():
    '''
    Permite al usuario modificar un Alumno seleccionando el campo a modificar
    :return: No devuelve nada
    '''
    if ut.comprobarVacio("alumnos"):
        nombre = ga.buscarAlumno()
        if nombre != "":
            try:
                # Consultar datos actuales del profesor
                alumnoAlumno = alumnos.select().where(alumnos.Nombre == nombre[0]).first()

                # Mostrar opciones al usuario
                print("\nSeleccione el campo a modificar:")
                print("1. Nombre")
                print("2. Apellidos")
                print("3. Telefono")
                print("4. Direccion")
                print("5. Fecha de Nacimiento")
                print("0. Cancelar")

                finEntradaAlta = False
                fallos = 0

                opcion = input("Opcion: ")

                if opcion == "1":

                    while not finEntradaAlta and fallos < 5:
                        nombreNuevo = input("Nuevo nombre: ").strip().upper()
                        if ut.validarNombre(nombreNuevo):
                            if not alumnoRepe(nombreNuevo, nombre[1]):
                                if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                    alumnos.update(Nombre=nombreNuevo).where(alumnos.Nombre == nombre[0],
                                                                             alumnos.Apellidos == nombre[1]).execute()
                                    finEntradaAlta = True
                                    print("Alumno actualizado correctamente.")
                                else:
                                    finEntradaAlta = True
                            else:
                                fallos = ut.fallo(fallos,
                                                  f"Ya existe un alumno con el nombre {nombreNuevo} y el apellido {nombre[1]}")
                        else:
                            fallos = ut.fallo(fallos, "El nombre debe tener minimo dos caracteres")

                elif opcion == "2":

                    while not finEntradaAlta and fallos < 5:

                        nuevoApellidos = input("Nuevos apellidos: ").strip().upper()
                        if ut.validarNombre(nuevoApellidos):
                            if not alumnoRepe(nombre[0], nuevoApellidos):
                                if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                    alumnos.update(Apellidos=nuevoApellidos).where(alumnos.Nombre == nombre[0],
                                                                                   alumnos.Apellidos == nombre[
                                                                                       1]).execute()
                                    finEntradaAlta = True
                                    print("Alumno actualizado correctamente.")
                                else:
                                    finEntradaAlta = True
                            else:
                                fallos = ut.fallo(fallos,
                                                  f"Ya existe un alumno con el nombre {nombre[0]} y el apellido {nuevoApellidos}")
                        else:
                            fallos = ut.fallo(fallos, "Los apellidos deben contener al menos 2 caracteres.")

                elif opcion == "4":

                    while not finEntradaAlta and fallos < 5:
                        direccionNueva = input("Nueva direccion: ").strip().upper()
                        if ut.validarDireccion(direccionNueva):
                            if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                alumnos.update(Direccion=direccionNueva).where(alumnos.Nombre == nombre[0],
                                                                               alumnos.Apellidos == nombre[1]).execute()
                                finEntradaAlta = True
                                print("Alumno actualizado correctamente.")
                            else:
                                finEntradaAlta = True
                        else:
                            fallos = ut.fallo(fallos, "La dirección debe de contener mínimo 4 carácteres.")

                elif opcion == "3":

                    while not finEntradaAlta and fallos < 5:
                        telefonoNuevo = input("Nuevo telefono: ").strip().upper()
                        if ut.validarTelefono(telefonoNuevo):
                            if not ga.tlfRepe(telefonoNuevo):
                                if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                    alumnos.update(Telefono=telefonoNuevo).where(alumnos.Nombre == nombre[0],
                                                                                 alumnos.Apellidos == nombre[
                                                                                     1]).execute()

                                    finEntradaAlta = True
                                    print("Alumno actualizado correctamente.")
                                else:
                                    finEntradaAlta = True
                            else:
                                fallos = ut.fallo(fallos, "El telefono introducido ya existe en otro alumno.")
                        else:
                            fallos = ut.fallo(fallos, "El Telefono debe tener 9 numeros")
                elif opcion == "5":

                    while not finEntradaAlta and fallos < 5:
                        fechaNueva = input("Nueva fecha de nacimiento: ").strip().upper()
                        if ut.validarFechaNacimiento(fechaNueva):
                            if ut.confirmacion("Seguro que quieres modificar?", "Solicitud"):
                                alumnos.update(FechaNacimiento=fechaNueva).where(alumnos.Nombre == nombre[0],
                                                                                 alumnos.Apellidos == nombre[
                                                                                     1]).execute()
                                finEntradaAlta = True
                                print("Alumno actualizado correctamente.")
                            else:
                                finEntradaAlta = True
                        else:
                            fallos = ut.fallo(fallos,
                                              "Fecha no valida ,deben ser numeros con el siguiente formato: yyyy-mm-dd.\n Además debe ser entre 1950 y 2020")
                elif opcion == "0":
                    print("Modificación cancelada.")
                else:
                    print("Opción no válida.")
            except Exception as errorModificarProfesor:
                print(f"Error al modificar el alumno {nombre[0]} {nombre[1]}")


def mostrarAlumnos():
    '''
    Metodo para mostrar todos los amlumnos (y su informacion) de la base de datos
    :return: No devuelve nada
    '''

    cont = 1
    # Seleccionar todos los alumnos
    alumnado = alumnos.select()
    if not alumnos:
        print("No hay alumnos registrados en la BBDD.")
    else:
        print("Lista de alumnos:")
        for alumno in alumnado:
            print(f"--- Alumno {cont}---")
            print("Numero de Expediente:", alumno.NumeroExpediente)
            print("Nombre:", alumno.Nombre)
            print("Apellidos:", alumno.Apellidos)
            print("Telefono:", alumno.Telefono)
            print("Direccion:", alumno.Direccion)
            print("Fecha de Nacimiento:", alumno.FechaNacimiento, '\n')
            cont = cont + 1


def matricularAlumno():
    '''
    Metodo para dar de alta un alumno en un curso , comprueba si el alumno ya se encuentra en el curso deseado
    :return: No devuelve nada
    '''
    encontrado = False
    fallos = 0
    if ut.comprobarVacio("alumnos"):
        if ut.comprobarVacio("cursos"):
            while not encontrado and fallos < 5:
                nombreC = input("Nombre del curso: ").strip().upper()
                idCurs = devolverIddeCurso(nombreC)
                if idCurs is not None:
                    encontrado = True
                    print("Curso encontrado")
                else:
                    fallos = ut.fallo(fallos, "Curso no encontrado")
            if fallos < 5:
                encontrado = False
                fallos = 0
                while not encontrado and fallos < 5:

                    alumnoM = ga.buscarAlumno()
                    if alumnoM != "":
                        encontrado = True
                        print("Alumno encontrado")
                    else:
                        fallos = ut.fallo(fallos, "Alumno no encontrado")
            if fallos < 5:

                op = ut.confirmacion(
                    f"Seguro que deseas dar de alta al alumno {alumnoM[0]} {alumnoM[1]} al curso {nombreC} ?",
                    "Matricula ")
                if op:
                    idAlumnoM = buscarAlumnoBBDDid(alumnoM[0], alumnoM[1])
                    alumnoEnCurso = alumnoscursos.select().where(alumnoscursos.AlumnoExpediente == idAlumnoM,
                                                                 alumnoscursos.CursoCodigo == idCurs).first()
                    if alumnoEnCurso is None:
                        nAlumnoEnCurso = alumnoscursos.create(AlumnoExpediente=idAlumnoM, CursoCodigo=idCurs)
                        nAlumnoEnCurso.save()

                        print("Alumno matriculado correctamente.")
                    else:
                        print("No se matriculo el alumno , ya pertenece a este Curso.")


def desmatricularAlumno():
    """
    Metodo para dar de baja un alumno en un curso.
    :return: No devuelve nada
    """
    encontrado = False
    fallos = 0
    if ut.comprobarVacio("alumnos"):
        if ut.comprobarVacio("cursos"):
            while not encontrado and fallos < 5:
                nombreC = input("Nombre del curso: ").strip().upper()
                idCurs = devolverIddeCurso(nombreC)
                if idCurs is not None:
                    encontrado = True
                    print("Curso encontrado")
                else:
                    fallos = ut.fallo(fallos, "Curso no encontrado")
            encontrado = False
            fallos = 0
            if fallos < 5:
                while not encontrado and fallos < 5:
                    alumnosg = alumnos.select(alumnos.NumeroExpediente, alumnos.Nombre, alumnos.Apellidos).join(
                        alumnoscursos, on=(alumnos.NumeroExpediente == alumnoscursos.AlumnoExpediente)).where(
                        alumnoscursos.CursoCodigo == idCurs)

                    print("Lista de alumnos:")
                    for alumno in alumnosg:
                        print(f"--- Alumno ---")
                        print("Numero de Expediente:", alumno.NumeroExpediente)
                        print("Nombre:", alumno.Nombre)
                        print("Apellidos:", alumno.Apellidos, '\n')

                    if alumnos:
                        encontrado = True
                        print("Alumno encontrado")
                    else:
                        fallos = ut.fallo(fallos, "Alumno no encontrado")

            if fallos < 5:
                expAlumno = input("Introduce el Numero de Expediente  del alumno a Eliminar: ")
                compAl = alumnoscursos.select().where(alumnoscursos.AlumnoExpediente == expAlumno).first()
                if compAl:
                    op = ut.confirmacion(f"Seguro que deseas dar de baja al alumno del curso {nombreC} ?",
                                         "Desmatriculacion ")
                    if op:
                        alumnoscursos.delete().where(alumnoscursos.AlumnoExpediente == expAlumno).execute()
                else:
                    print("No has introducido un expediente correcto")


def mostrarAlumnosdeCurso():
    '''
    Metodo para mostrar todos los alumnos que se encuentren dentro de un mismo curso
    :return: No devuelve nada
    '''
    encontrado = False
    fallos = 0
    if ut.comprobarVacio("cursos"):
        if ut.comprobarVacio("alumnos"):
            while not encontrado and fallos < 5:
                nombreC = input("Nombre del curso: ").strip().upper()
                idCurs = devolverIddeCurso(nombreC)
                if idCurs is not None:
                    encontrado = True
                    print("Curso encontrado")
                else:
                    fallos = ut.fallo(fallos, "Curso no encontrado")
            if fallos < 5:
                alumnos = alumnos.select(alumnos.NumeroExpediente, alumnos.Nombre, alumnos.Apellidos).join(
                    alumnoscursos, on=(alumnos.NumeroExpediente == alumnoscursos.AlumnoExpediente)).where(
                    alumnoscursos.CursoCodigo == idCurs)
                for alumno in alumnos:
                    print(
                        f"Numero de Expediente: {alumno.NumeroExpediente} , Alumno: {alumno.Nombre} {alumno.Apellidos}\n")


def alumnoRepe(nombre, apellidos):
    '''
    Para comprobar por codigo si se repite un alumno para notificar al usuario y  evitar la entrada auqnue tambien
    esta restringido en la propia tabla alumnos con UNIQUE
    :param nombre: Nombre del alumno a comprobar
    :param apellidos: Apellidos del alumno a comprobar
    :return: Devuelve True o False en funcion de si lo encuentra
    '''
    repetido = alumnos.select().where(alumnos.Nombre == nombre, alumnos.Apellidos == apellidos).first()
    if repetido:
        return True
    else:
        return False


def tlfRepe(telefono):
    '''
    Metodo para verificar que el telefono en un alumno no se repite , ya que lo logico es que cada
    persona tenga un numero de telefono unico
    :param telefono: Telefono a comprobar
    :return: Devuelve True o False en funcion de si lo encuentra
    '''
    repetido = alumnos.select().where(alumnos.Telefono == telefono).first()

    if repetido:
        return True
    else:
        return False


def buscarPorNombre(nombreAl):
    '''
    Buscar el nombre introducido para ver si existe y en caso de devolver False evitar que te pida
    seguidamente los apellidos del alumno
    :param nombreAl: Nombre a comprobar
    :return: Devuelve True o False en funcion de si lo encuentra
    '''

    repetido = alumnos.select().where(alumnos.Nombre == nombreAl).first()
    if repetido:
        return True
    else:
        return False


def buscarPorNombreyApellido(nombreAl, apellidoAl):
    '''
    Buscar usuario para comprobar si esta repetido recibiendo el nombre y los apellidos del alumno
    por parametro
    :param nombreAl: Nombre a comprobar
    :param apellidoAl: Apellidos a comprobar
    :return: Devuelve True o False en funcion de si lo encuentra
    '''
    repetido = alumnos.select().where(alumnos.Nombre == nombreAl, alumnos.Apellidos == apellidoAl).first()

    if repetido:
        return True
    else:
        return False
