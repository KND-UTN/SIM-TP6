from abc import abstractmethod, ABC

from clases.estadisticas import Estadisticas


class Medicos:

    def __init__(self):
        self.estado_m1 = Libre()
        self.estado_m2 = Libre()
        self.cola_comun = []
        self.cola_urgente = []
        self.atendiendo_m1 = None
        self.atendiendo_m2 = None

        self.suspendido_m1 = None
        self.suspendido_m2 = None
        self.tiempo_remanente_m1 = None
        self.tiempo_remanente_m2 = None

    def nuevo_comun(self, paciente, reloj):
        if isinstance(self.estado_m1, Libre):
            self.estado_m1 = AtendiendoComun()
            self.atendiendo_m1 = paciente
            paciente.estado.atendido_comun(paciente)
            Estadisticas.ac_espera_comun += reloj - paciente.hora_inicio_espera
            Estadisticas.ac_pacientes_comunes += 1
            return 1  # Fue atendido por el medico 1
        if isinstance(self.estado_m2, Libre):
            self.estado_m2 = AtendiendoComun()
            self.atendiendo_m2 = paciente
            paciente.estado.atendido_comun(paciente)
            Estadisticas.ac_espera_comun += reloj - paciente.hora_inicio_espera
            Estadisticas.ac_pacientes_comunes += 1
            return 2  # Fue atendido por el medico 2
        self.cola_comun.append(paciente)
        return 0  # No fue atendido (en cola)

    def nuevo_urgencia(self, paciente, reloj, fin_atencion_m1, fin_atencion_m2):
        if isinstance(self.estado_m1, Libre):
            self.estado_m1 = AtendiendoUrgente()
            self.atendiendo_m1 = paciente
            paciente.estado.atendido_urgencia(paciente)
            Estadisticas.espera_urgente = reloj - paciente.hora_inicio_espera
            return 1  # Fue atendido por el medico 1
        if isinstance(self.estado_m2, Libre):
            self.estado_m2 = AtendiendoUrgente()
            self.atendiendo_m2 = paciente
            paciente.estado.atendido_urgencia(paciente)
            Estadisticas.espera_urgente = reloj - paciente.hora_inicio_espera
            return 2  # Fue atendido por el medico 2
        if isinstance(self.estado_m1, AtendiendoComun):
            self.estado_m1 = AtendiendoUrgente()
            self.suspendido_m1 = self.atendiendo_m1
            self.suspendido_m1.estado.suspender(self.suspendido_m1)
            self.atendiendo_m1 = paciente
            self.atendiendo_m1.estado.atendido_urgencia(self.atendiendo_m1)
            self.tiempo_remanente_m1 = fin_atencion_m1 - reloj
            Estadisticas.espera_urgente = reloj - paciente.hora_inicio_espera
            Estadisticas.ac_interrupciones += 1
            return 1  # Fue atendido por el medico 1
        if isinstance(self.estado_m2, AtendiendoComun):
            self.estado_m2 = AtendiendoUrgente()
            self.suspendido_m2 = self.atendiendo_m2
            self.suspendido_m2.estado.suspender(self.suspendido_m2)
            self.atendiendo_m2 = paciente
            self.atendiendo_m2.estado.atendido_urgencia(self.atendiendo_m2)
            self.tiempo_remanente_m2 = fin_atencion_m2 - reloj
            Estadisticas.espera_urgente = reloj - paciente.hora_inicio_espera
            Estadisticas.ac_interrupciones += 1
            return 2  # Fue atendido por el medico 2
        self.cola_urgente.append(paciente)
        paciente.estado.espera_urgencia(paciente)

        return 0    # No lo atendio nadie; Esta en espera

    def siguiente_m1(self, reloj):
        self.atendiendo_m1.atencion_completa(reloj)
        if len(self.cola_urgente) > 0:
            self.estado_m1 = AtendiendoUrgente()
            self.atendiendo_m1 = self.cola_urgente.pop(0)
            self.atendiendo_m1.estado.atendido_urgencia(self.atendiendo_m1)
            Estadisticas.espera_urgente = reloj - self.atendiendo_m1.hora_inicio_espera
            return False
        if self.suspendido_m1 is not None:
            self.atendiendo_m1 = self.suspendido_m1
            self.suspendido_m1 = None
            self.estado_m1 = AtendiendoComun()
            self.atendiendo_m1.estado.atender(self.atendiendo_m1)
            Estadisticas.ac_espera_comun += self.tiempo_remanente_m1
            return True
        if len(self.cola_comun) > 0:
            self.estado_m1 = AtendiendoComun()
            self.atendiendo_m1 = self.cola_comun.pop(0)
            self.atendiendo_m1.estado.atendido_comun(self.atendiendo_m1)
            Estadisticas.ac_pacientes_comunes += 1
            Estadisticas.ac_espera_comun += reloj - self.atendiendo_m1.hora_inicio_espera
            return False
        self.estado_m1 = Libre()
        return False

    def siguiente_m2(self, reloj):
        self.atendiendo_m2.atencion_completa(reloj)
        if len(self.cola_urgente) > 0:
            self.estado_m2 = AtendiendoUrgente()
            self.atendiendo_m2 = self.cola_urgente.pop(0)
            self.atendiendo_m2.estado.atendido_urgencia(self.atendiendo_m2)
            Estadisticas.espera_urgente = reloj - self.atendiendo_m2.hora_inicio_espera
            return False
        if self.suspendido_m2 is not None:
            self.atendiendo_m2 = self.suspendido_m2
            self.suspendido_m2 = None
            self.estado_m2 = AtendiendoComun()
            self.atendiendo_m2.estado.atender(self.atendiendo_m2)
            Estadisticas.ac_espera_comun += self.tiempo_remanente_m2
            return True
        if len(self.cola_comun) > 0:
            self.estado_m2 = AtendiendoComun()
            self.atendiendo_m2 = self.cola_comun.pop(0)
            self.atendiendo_m2.estado.atendido_comun(self.atendiendo_m2)
            Estadisticas.ac_pacientes_comunes += 1
            Estadisticas.ac_espera_comun += reloj - self.atendiendo_m2.hora_inicio_espera
            return False
        self.estado_m2 = Libre()
        return False

    def medico1_esta_ocupado(self):
        return isinstance(self.estado_m1, AtendiendoComun) or isinstance(self.estado_m1, AtendiendoUrgente)

    def medico2_esta_ocupado(self):
        return isinstance(self.estado_m2, AtendiendoComun) or isinstance(self.estado_m2, AtendiendoUrgente)

    def get_fila(self, simulacion):
        if self.medico1_esta_ocupado() and self.medico2_esta_ocupado():
            simulacion.pacientes_mostrar[self.atendiendo_m1.id] = self.atendiendo_m1
            simulacion.pacientes_mostrar[self.atendiendo_m2.id] = self.atendiendo_m2
            return [self.estado_m1.toString() + " (P" + str(self.atendiendo_m1.id) + ")", self.tiempo_remanente_m1, self.estado_m2.toString() + " (P" + str(self.atendiendo_m2.id) + ")", self.tiempo_remanente_m2, len(self.cola_comun), len(self.cola_urgente)]
        if self.medico1_esta_ocupado():
            simulacion.pacientes_mostrar[self.atendiendo_m1.id] = self.atendiendo_m1
            return [self.estado_m1.toString() + " (P" + str(self.atendiendo_m1.id) + ")", self.tiempo_remanente_m1, self.estado_m2.toString(), self.tiempo_remanente_m2, len(self.cola_comun), len(self.cola_urgente)]
        if self.medico2_esta_ocupado():
            simulacion.pacientes_mostrar[self.atendiendo_m2.id] = self.atendiendo_m2
            return [self.estado_m1.toString(), self.tiempo_remanente_m1, self.estado_m2.toString() + " (P" + str(self.atendiendo_m2.id) + ")", self.tiempo_remanente_m2, len(self.cola_comun), len(self.cola_urgente)]
        return [self.estado_m1.toString(), self.tiempo_remanente_m1, self.estado_m2.toString(), self.tiempo_remanente_m2, len(self.cola_comun), len(self.cola_urgente)]


class MedicoState(ABC):
    @abstractmethod
    def toString(self):
        pass


class Libre(MedicoState):
    def toString(self):
        return 'Libre'


class AtendiendoComun(MedicoState):
    def toString(self):
        return 'AC'


class AtendiendoUrgente(MedicoState):
    def toString(self):
        return 'AU'
