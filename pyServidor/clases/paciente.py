from abc import ABC, abstractmethod


class Paciente:
    countId = 0

    def __init__(self, reloj):
        self.id = Paciente.countId
        self.estado = EsperaExamen()
        self.caso = SinExamenCompletado()
        self.hora_inicio_espera = reloj
        self.hora_salida_sistema = None

    def get_fila(self):
        json_retornar = {
            "paciente": self.id,
            "estado": self.estado.toString(),
            "caso": self.caso.toString(),
            "hes": self.hora_inicio_espera,
            "hss": self.hora_salida_sistema
        }
        return json_retornar

    def atencion_completa(self, reloj):
        self.estado = AtencionCompleta()
        self.hora_salida_sistema = reloj


# ----- ESTADOS DEL PACIENTE -----

class PacienteState(ABC):
    @abstractmethod
    def toString(self):
        pass


class AtencionCompleta(PacienteState):
    def toString(self):
        return 'Terminado'


class EsperaExamen(PacienteState):
    def examinar(self, paciente):
        paciente.estado = SiendoExaminado()

    def toString(self):
        return 'EE'


class SiendoExaminado(PacienteState):
    def espera_comun(self, paciente):
        paciente.estado = EsperaComun()

    def espera_urgencia(self, paciente):
        paciente.estado = EsperaUrgencia()

    def atendido_comun(self, paciente):
        paciente.estado = SiendoAtendidoComun()

    def atendido_urgencia(self, paciente):
        paciente.estado = SiendoAtendidoUrgencia()

    def al_purgatorio(self, paciente):
        paciente.estado = EsperaEnPurgatorio()

    def toString(self):
        return 'SE'


class EsperaComun(PacienteState):
    def toString(self):
        return 'EC'


class SiendoAtendidoComun(PacienteState):
    def suspender(self, paciente):
        paciente.estado = Suspendido()

    def toString(self):
        return 'SAC'


class SiendoAtendidoUrgencia(PacienteState):
    def toString(self):
        return 'SAU'


class EsperaUrgencia(PacienteState):
    def atendido_urgencia(self, paciente):
        paciente.estado = SiendoAtendidoUrgencia()

    def toString(self):
        return 'EU'


class Suspendido(PacienteState):
    def atender(self, paciente):
        paciente.estado = SiendoAtendidoComun()

    def toString(self):
        return 'Suspendido'


# --- CASOS DEL PACIENTE ---

class PacienteCase(ABC):
    @abstractmethod
    def toString(self):
        pass


class SinExamenCompletado(PacienteCase):
    def urgencia(self, paciente):
        paciente.caso = Urgente()

    def caso_comun(self, paciente):
        paciente.caso = Comun()

    def toString(self):
        return 'SEC'


class Comun(PacienteCase):
    def toString(self):
        return 'Comun'


class Urgente(PacienteCase):
    def toString(self):
        return 'Urgente'


class EsperaEnPurgatorio(PacienteCase):
    def atender(self, paciente):
        paciente.estado = SiendoExaminado()

    def toString(self):
        return 'En el Purgatorio'
