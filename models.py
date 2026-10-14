from datetime import date
from typing import Dict, Any


# =====================================================================
# CLASE BASE: lo que los modelos comparten
# =====================================================================
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento comun."""

    def __init__(self, id_registro: int) -> None:
        """
        Inicializa la entidad base con su identificador unico.

        Args:
            id_registro (int): Identificador numerico unico para el registro.

        Returns:
            None
        """
        self.id = int(id_registro)

    # ---- UNICO METODO DE CLASE DEL PROYECTO ----
    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "ModeloBase":
        """
        Diccionario -> objeto. Escrito UNA vez y usado por todos los modelos.
        cls es la clase que llamo: PeriodoAcademico, Estudiante, Materia o Matricula.

        Args:
            datos (Dict[str, Any]): Diccionario con los datos leidos del JSON.

        Returns:
            ModeloBase: Instancia de la clase que hizo la llamada.
        """
        datos_copia = dict(datos)                  # copia, para no tocar el original
        id_registro = datos_copia.pop("id")        # saco el id
        return cls(id_registro, **datos_copia)     # el resto son los campos del modelo

    # ---- METODOS DE INSTANCIA ----
    def a_diccionario(self) -> Dict[str, Any]:
        """
        Objeto -> diccionario. Cada hijo agrega sus campos.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario base conteniendo solo el id.
        """
        return {"id": self.id}

    def etiqueta(self) -> str:
        """
        POLIMORFISMO: cada hijo la reescribe a su manera para listados.

        Args:
            Ninguno

        Returns:
            str: Texto generico con el numero de registro.
        """
        return f"registro {self.id}"

    def __str__(self) -> str:
        """
        Lo que se ve al hacer print(objeto). Llama a etiqueta(),
        asi que cada modelo se imprime distinto sin cambiar esta linea.

        Args:
            Ninguno

        Returns:
            str: Representacion final formateada para la consola.
        """
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# PERIODO ACADEMICO: Ciclos lectivos o semestres oficiales
# =====================================================================
class PeriodoAcademico(ModeloBase):
    """Ciclo lectivo o semestre en el cual se inscriben las matriculas."""

    def __init__(
        self, id_registro: int, codigo: str, nombre: str = "", 
        fecha_inicio: str = "", fecha_fin: str = "", activo: bool = True
    ) -> None:
        """
        Inicializa un Periodo Academico.

        Args:
            id_registro (int): Identificador numerico unico.
            codigo (str): Codigo corto del ciclo (ej: '2026-1S', '2026-2S').
            nombre (str, opcional): Denominacion oficial (ej: 'Primer Semestre 2026'). Por defecto "".
            fecha_inicio (str, opcional): Fecha ISO de inicio (YYYY-MM-DD). Por defecto "".
            fecha_fin (str, opcional): Fecha ISO de finalizacion (YYYY-MM-DD). Por defecto "".
            activo (bool, opcional): Indica si el periodo esta vigente para inscripciones. Por defecto True.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.codigo = codigo
        self.nombre = nombre or codigo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.activo = bool(activo)

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Serializa los campos de PeriodoAcademico a un diccionario para JSON.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con id, codigo, nombre, fechas y estado activo.
        """
        datos = super().a_diccionario()
        datos["codigo"] = self.codigo
        datos["nombre"] = self.nombre
        datos["fecha_inicio"] = self.fecha_inicio
        datos["fecha_fin"] = self.fecha_fin
        datos["activo"] = self.activo
        return datos

    def etiqueta(self) -> str:
        """
        Representacion concisa del periodo para pantallas y listas de seleccion.

        Args:
            Ninguno

        Returns:
            str: Codigo, nombre, fechas y estado de vigencia.
        """
        vigencia = " [VIGENTE]" if self.activo else " [CERRADO]"
        fechas = f" ({self.fecha_inicio} a {self.fecha_fin})" if self.fecha_inicio and self.fecha_fin else ""
        return f"[{self.codigo}] {self.nombre}{fechas}{vigencia}"


# =====================================================================
# HERENCIA: Persona es la base de Estudiante
# =====================================================================
class Persona(ModeloBase):
    """Todo lo que tiene una persona del sistema."""

    def __init__(self, id_registro: int, nombre: str, apellido: str, email: str) -> None:
        """
        Inicializa una Persona con sus datos civiles basicos.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre de la persona.
            apellido (str): Apellido de la persona.
            email (str): Correo electronico de contacto.

        Returns:
            None
        """
        super().__init__(id_registro)      # el padre guarda el id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self) -> str:
        """
        Concatena de forma limpia el nombre y el apellido.

        Args:
            Ninguno

        Returns:
            str: Nombre y apellido unidos por un espacio.
        """
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Agrega los atributos de Persona al diccionario del padre.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con id, nombre, apellido y email.
        """
        datos = super().a_diccionario()    # {"id": ...} que arma el padre
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self) -> str:
        """
        Sobrescribe la representacion base para devolver el nombre completo.

        Args:
            Ninguno

        Returns:
            str: Nombre completo.
        """
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona, con carnet y carrera."""

    def __init__(
        self, id_registro: int, nombre: str, apellido: str, email: str, 
        carnet: str = "", carrera: str = ""
    ) -> None:
        """
        Inicializa un Estudiante integrando sus datos academicos.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre del estudiante.
            apellido (str): Apellido del estudiante.
            email (str): Correo electronico de contacto.
            carnet (str, opcional): Codigo de identificacion. Por defecto "".
            carrera (str, opcional): Programa academico. Por defecto "".

        Returns:
            None
        """
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Extiende el diccionario de Persona agregando carnet y carrera.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario completo del Estudiante.
        """
        datos = super().a_diccionario()    # reutiliza lo de Persona
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self) -> str:
        """
        Sobrescribe y EXTIENDE la etiqueta del padre (Persona).

        Args:
            Ninguno

        Returns:
            str: Representacion con nombre, carnet y carrera.
        """
        return f"{super().etiqueta()} · {self.carnet or 'sin carnet'} · {self.carrera}"


# =====================================================================
# UNICA CLASE CON ATRIBUTOS Y METODOS ESTATICOS
# =====================================================================
class Materia(ModeloBase):
    """Materia ES UN ModeloBase. Aqui viven los ejemplos de lo estatico para el sistema."""

    # ATRIBUTOS ESTATICOS (de clase): existen una sola vez, no por objeto
    CUPOS_MAXIMOS = 30           # regla del negocio, igual para todas las materias
    NOTA_APROBACION = 14         # calificacion minima para aprobar
    total_creadas = 0            # contador compartido

    def __init__(
        self, id_registro: int, nombre: str, codigo: str, 
        creditos: int = 0, cupos: int = 30
    ) -> None:
        """
        Inicializa una asignatura academica.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre de la asignatura.
            codigo (str): Codigo institucional de la asignatura.
            creditos (int, opcional): Valor en creditos academicos. Por defecto 0.
            cupos (int, opcional): Plazas disponibles. Por defecto 30.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = int(creditos)
        self.cupos = int(cupos)
        Materia.total_creadas += 1         # se modifica en la CLASE, no en self

    # METODOS ESTATICOS: reglas que no necesitan ninguna materia concreta
    @staticmethod
    def es_nota_valida(valor: Any) -> bool:
        """
        Valida que un ingreso numerico este dentro del rango permitido (0 a 20).

        Args:
            valor (Any): Valor a evaluar, usualmente string o numerico.

        Returns:
            bool: True si es valido, False si hay error de tipo o rango.
        """
        try:
            nota = float(valor)
            return 0 <= nota <= 20
        except (TypeError, ValueError):
            return False

    # METODOS DE INSTANCIA: necesitan los datos de ESTE producto
    def hay_cupo(self) -> bool:
        """
        Verifica si la materia aun cuenta con plazas disponibles.

        Args:
            Ninguno

        Returns:
            bool: True si hay cupos restantes.
        """
        return self.cupos > 0

    def ocupar_cupo(self) -> None:
        """
        Resta 1 a la disponibilidad si es que todavia hay cupos.

        Args:
            Ninguno

        Returns:
            None
        """
        if self.hay_cupo():
            self.cupos -= 1

    def liberar_cupo(self) -> None:
        """
        Suma 1 a la disponibilidad, sin exceder el maximo configurado en la clase.

        Args:
            Ninguno

        Returns:
            None
        """
        if self.cupos < Materia.CUPOS_MAXIMOS:
            self.cupos += 1

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Objeto -> diccionario agregando los datos de la asignatura.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Datos para el JSON.
        """
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self) -> str:
        """
        Genera el formato de lectura para la asignatura y alerta si esta llena.

        Args:
            Ninguno

        Returns:
            str: Texto con codigo, nombre y cupos restantes.
        """
        alerta = " ⚠ LLENA" if not self.hay_cupo() else ""
        return f"[{self.codigo}] {self.nombre} ({self.creditos} Cr) · cupos {self.cupos}/{Materia.CUPOS_MAXIMOS}{alerta}"


# =====================================================================
# MATRICULA: Vinculada al Periodo Academico (1 a 1 intacta)
# =====================================================================
class Matricula(ModeloBase):
    """Matricula simple: une a un estudiante con una materia en un periodo especifico."""

    def __init__(
        self, id_registro: int, estudiante_id: int, materia_id: int, 
        periodo: str = "", nota: float = 0.0, fecha: str = "", periodo_id: int = 0
    ) -> None:
        """
        Inicializa la relacion transaccional entre estudiante, materia y periodo.

        Args:
            id_registro (int): Identificador de la matricula.
            estudiante_id (int): ID de la entidad Estudiante.
            materia_id (int): ID de la entidad Materia.
            periodo (str, opcional): Codigo textual del ciclo (ej: '2026-1S'). Por defecto "".
            nota (float, opcional): Calificacion. Por defecto 0.0.
            fecha (str, opcional): Fecha de registro. Por defecto se usa la de hoy.
            periodo_id (int, opcional): ID de la entidad PeriodoAcademico vinculada. Por defecto 0.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = periodo
        self.periodo_id = int(periodo_id)
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self) -> bool:
        """
        Consulta la regla estatica de Materia para saber si la nota es aprobatoria.
        Se calcula cada vez para no quedar desactualizado si la nota cambia.

        Args:
            Ninguno

        Returns:
            bool: True si es mayor o igual a la NOTA_APROBACION.
        """
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self) -> str:
        """
        Convierte la validacion de aprobacion en un estado legible.

        Args:
            Ninguno

        Returns:
            str: 'Aprobada' o 'Reprobada'.
        """
        return "Aprobada" if self.esta_aprobada() else "Reprobada"

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Devuelve el diccionario que se persistira en la transaccion.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con referencias, calificacion y periodo_id.
        """
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["periodo_id"] = self.periodo_id
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self) -> str:
        """
        Formato de lectura que resume la situacion academica de la inscripcion.

        Args:
            Ninguno

        Returns:
            str: Historial formateado.
        """
        info_periodo = self.periodo or f"Periodo #{self.periodo_id}"
        return (f"{self.fecha} · estudiante {self.estudiante_id} · "
                f"materia {self.materia_id} ({info_periodo}) "
                f"-> Nota: {self.nota} [{self.estado()}]")