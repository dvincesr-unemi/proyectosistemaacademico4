from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
# 1. Importamos PeriodoAcademicoController junto a los demas controladores
from views import (
    EstudianteController, MateriaController, PeriodoAcademicoController, MatriculaController
)

# Se crea UN solo controlador de cada tipo.
# Inyeccion de dependencias:
# - Estudiantes, Materias y Periodos se pasan a Matriculas (flujo 1 a 1 intacto).
estudiantes = EstudianteController()
materias = MateriaController()
periodos = PeriodoAcademicoController()  # <--- NUEVO CONTROLADOR
matriculas = MatriculaController(estudiantes, materias, periodos)  # <--- RECIBE A PERIODOS


# =====================================================================
# AYUDAS DE PANTALLA
# =====================================================================

def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    """Devuelve un entero o None si el usuario escribio otra cosa."""
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    # Los controladores devuelven la TUPLA (exito, mensaje)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavia."):
    """Sirve para estudiantes, materias, periodos y matriculas: cada modelo sabe mostrarse."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    # Recorre el DICCIONARIO del objeto: clave y valor a la vez
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# =====================================================================
# MENU DE PERIODOS ACADEMICOS (NUEVO)
# =====================================================================

def crear_periodo():
    imprimir_titulo("CREAR PERIODO ACADEMICO")
    codigo = input("Codigo del ciclo (ej. 2026-1S, 2026-2S): ")
    nombre = input("Nombre descriptivo (opcional): ")
    fecha_inicio = input("Fecha de inicio [AAAA-MM-DD] (opcional): ")
    fecha_fin = input("Fecha de finalizacion [AAAA-MM-DD] (opcional): ")
    es_activo = input("¿Periodo vigente para matricula? (s/n) [Enter = si]: ").strip().lower()
    
    activo = True if es_activo in ("", "s", "si", "y", "yes") else False

    datos = {
        "codigo": codigo,
        "nombre": nombre,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "activo": activo,
    }
    mostrar_resultado(*periodos.crear(datos))
    pausa()


def listar_periodos():
    imprimir_titulo("PERIODOS ACADEMICOS")
    mostrar_lista(periodos.leer(), "Todavia no hay periodos academicos registrados.")
    pausa()


def buscar_periodo():
    imprimir_titulo("BUSCAR PERIODO ACADEMICO")
    termino = input("Codigo, nombre o fecha: ")
    encontrados = periodos.buscar(termino)
    mostrar_lista(encontrados, f"Ningun periodo coincide con '{termino}'.")
    pausa()


def ver_periodo():
    imprimir_titulo("VER PERIODO POR ID")
    periodo = periodos.obtener(pedir_entero("Id: "))
    if periodo is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(periodo)
        inscripciones = matriculas.por_periodo(periodo.id)
        print(f"\n  Matriculas inscritas en este ciclo ({len(inscripciones)}):")
        for m in inscripciones:
            est = estudiantes.obtener(m.estudiante_id)
            mat = materias.obtener(m.materia_id)
            nom_est = est.nombre_completo() if est else f"Estudiante #{m.estudiante_id}"
            nom_mat = mat.codigo if mat else f"Materia #{m.materia_id}"
            print(f"    - [{m.id}] {nom_est} -> {nom_mat} (Nota: {m.nota})")
    pausa()


def actualizar_periodo():
    imprimir_titulo("ACTUALIZAR PERIODO ACADEMICO")
    id_periodo = pedir_entero("Id: ")
    periodo = periodos.obtener(id_periodo)
    if periodo is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {periodo.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("codigo", "nombre", "fecha_inicio", "fecha_fin"):
        actual = getattr(periodo, campo)
        nuevo = input(f"{campo.replace('_', ' ').capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    cambiar_estado = input(f"¿Periodo activo? (s/n) [{ 's' if periodo.activo else 'n' }]: ").strip().lower()
    if cambiar_estado in ("s", "si"):
        cambios["activo"] = True
    elif cambiar_estado in ("n", "no"):
        cambios["activo"] = False

    mostrar_resultado(*periodos.actualizar(id_periodo, cambios))
    pausa()


def eliminar_periodo():
    imprimir_titulo("ELIMINAR PERIODO ACADEMICO")
    id_periodo = pedir_entero("Id: ")
    periodo = periodos.obtener(id_periodo)
    if periodo is None:
        imprimir_error("No encontrado")
        return pausa()

    inscritos = matriculas.por_periodo(id_periodo)
    if inscritos:
        imprimir_info(f"Aviso: Hay {len(inscritos)} matricula(s) asociadas a este periodo.")

    imprimir_info(f"Se eliminara: {periodo.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*periodos.eliminar(id_periodo))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# =====================================================================
# MENU DE ESTUDIANTES
# =====================================================================

def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet: "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(estudiantes.leer(), "Todavia no hay estudiantes registrados.")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    encontrados = estudiantes.buscar(termino)
    mostrar_lista(encontrados, f"Ningun estudiante coincide con '{termino}'.")
    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    estudiante = estudiantes.obtener(pedir_entero("Id: "))
    if estudiante is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(estudiante)
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*estudiantes.actualizar(id_estudiante, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {estudiante.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*estudiantes.eliminar(id_estudiante))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# =====================================================================
# MENU DE MATERIAS
# =====================================================================

def crear_materia():
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Codigo: "),
        "creditos": input("Creditos: "),
        "cupos": input("Cupos iniciales [Enter = 30]: "),
    }
    mostrar_resultado(*materias.crear(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(materias.leer(), "Todavia no hay materias creadas.")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o codigo: ")
    mostrar_lista(materias.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = materias.obtener(pedir_entero("Id: "))
    if materia is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(materia)
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = materias.obtener(id_materia)
    if materia is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*materias.actualizar(id_materia, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = materias.obtener(id_materia)
    if materia is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {materia.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*materias.eliminar(id_materia))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# =====================================================================
# MENU DE MATRICULAS (TRANSACCIONAL 1 A 1 CON PERIODOS)
# =====================================================================

def registrar_matricula():
    imprimir_titulo("REGISTRAR MATRICULA")
    imprimir_info("Estudiantes:")
    mostrar_lista(estudiantes.leer())
    imprimir_info("Materias:")
    mostrar_lista(materias.leer())
    
    # Mostramos los periodos activos disponibles
    imprimir_info("Periodos vigentes:")
    mostrar_lista(periodos.periodos_activos(), "No hay periodos registrados (puede escribir texto manual).")

    datos = {
        "estudiante_id": pedir_entero("\nId del estudiante: "),
        "materia_id": pedir_entero("Id de la materia: "),
        "periodo_id": pedir_entero("Id del periodo (0 o vacio si ingresa texto libre): ") or 0,
    }

    if not datos["periodo_id"]:
        datos["periodo"] = input("Periodo manual (ej. 2026-1S): ").strip()

    if None in (datos["estudiante_id"], datos["materia_id"]):
        imprimir_error("Los IDs de estudiante y materia deben ser numeros enteros")
        return pausa()

    mostrar_resultado(*matriculas.crear(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRICULAS ACTIVAS")
    mostrar_lista(matriculas.leer(), "Todavia no hay inscripciones.")
    pausa()


def asentar_calificacion():
    imprimir_titulo("ASENTAR CALIFICACION")
    id_matricula = pedir_entero("Id de la matricula: ")
    if not id_matricula:
        return pausa()
        
    nota = input("Ingrese la nota (0 a 20): ")
    mostrar_resultado(*matriculas.actualizar(id_matricula, {"nota": nota}))
    pausa()


def ver_reporte():
    imprimir_titulo("REPORTE ACADEMICO")
    texto = matriculas.reporte_academico(pedir_entero("Id del estudiante: "))
    if texto is None:
        imprimir_error("El estudiante no existe.")
    else:
        print(texto)
    pausa()


def anular_matricula():
    imprimir_titulo("ANULAR MATRICULA")
    id_matricula = pedir_entero("Id de la matricula: ")
    if id_matricula and confirmar("Se liberara el cupo. ¿Confirma?"):
        mostrar_resultado(*matriculas.eliminar(id_matricula))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


def resumen():
    imprimir_titulo("RESUMEN GENERAL")
    print(f"  Periodos    : {len(periodos.leer())} (Vigentes: {len(periodos.periodos_activos())})")
    print(f"  Estudiantes : {len(estudiantes.leer())}")
    print(f"  Carreras    : {', '.join(estudiantes.carreras_registradas()) or '-'}")
    print(f"  Materias    : {len(materias.leer())}")
    
    llenas = [m for m in materias.leer() if not m.hay_cupo()]
    print(f"  Sin cupos   : {', '.join(m.codigo for m in llenas) or 'ninguna'}")
    print(f"  Matriculas  : {len(matriculas.leer())}")
    pausa()


# =====================================================================
# MENUS: DICCIONARIOS tecla -> (texto, funcion)
# =====================================================================

MENU_PERIODOS = {
    "1": ("Crear periodo", crear_periodo),
    "2": ("Ver todos", listar_periodos),
    "3": ("Buscar", buscar_periodo),
    "4": ("Ver por id", ver_periodo),
    "5": ("Actualizar", actualizar_periodo),
    "6": ("Eliminar", eliminar_periodo),
    "0": ("Volver", None),
}

MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por id", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por id", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Inscribir estudiante", registrar_matricula),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Asentar calificacion", asentar_calificacion),
    "4": ("Ver reporte academico", ver_reporte),
    "5": ("Anular matricula", anular_matricula),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    """Un solo bucle para los submenus."""
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opcion: ").strip()
        if tecla not in opciones:
            imprimir_error("Opcion no valida")
            pausa()
            continue

        _texto, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA ACADEMICO")
        print("  1. Estudiantes")
        print("  2. Periodos Academicos")  # <--- NUEVA OPCION EN EL MENU
        print("  3. Materias")
        print("  4. Matriculas")
        print("  5. Resumen")
        print("  0. Salir\n")

        tecla = input("Opcion: ").strip()
        if tecla == "1":
            ejecutar_menu("GESTION DE ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("GESTION DE PERIODOS", MENU_PERIODOS)
        elif tecla == "3":
            ejecutar_menu("GESTION DE MATERIAS", MENU_MATERIAS)
        elif tecla == "4":
            ejecutar_menu("GESTION DE MATRICULAS", MENU_MATRICULAS)
        elif tecla == "5":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opcion no valida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")