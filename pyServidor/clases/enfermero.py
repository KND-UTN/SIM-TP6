from abc import ABC, abstractmethod


class Enfermero:

    def __init__(self):
        self.estado: EnfermeroState = Libre()
        self.cola = []
        self.tiempo_remanente = None
        self.paciente_actual = None

        self.estado_cortado = None

    def add_paciente(self, paciente):
        if isinstance(self.estado, Libre):
            self.paciente_actual = paciente
            self.paciente_actual.estado.examinar(self.paciente_actual)
            self.estado = Ocupado()
            return 1    # Fue atendido en el momento

        self.cola.append(paciente)
        return 0    # Fue añadido a la cola

    def atender_siguiente(self):
        anterior = self.paciente_actual
        if len(self.cola) > 0:
            self.paciente_actual = self.cola.pop(0)
            self.paciente_actual.estado.examinar(self.paciente_actual)
        else:
            self.estado = Libre()
        return anterior

    def esta_ocupado(self):
        return isinstance(self.estado, Ocupado)

    def get_fila(self):
        if self.esta_ocupado():
            return [self.estado.toString() + " (P" + str(self.paciente_actual.id) + ")", str(self.tiempo_remanente),  len(self.cola)]
        return [self.estado.toString(), str(self.tiempo_remanente), len(self.cola)]

    def purgar(self, reloj, finalizada):
        if self.paciente_actual is not None:
            self.tiempo_remanente = finalizada - reloj
            self.paciente_actual.estado.al_purgatorio(self.paciente_actual)
        self.estado_cortado = self.estado
        self.estado = Purgando()


    def desPurgar(self, reloj):

        remanente_anterior = self.tiempo_remanente
        self.tiempo_remanente = None
        self.estado = self.estado_cortado
        self.estado_cortado = None
        if self.paciente_actual is not None:
            self.paciente_actual.estado.atender(self.paciente_actual)
            return remanente_anterior + reloj

        return False

class EnfermeroState(ABC):
    @abstractmethod
    def toString(self):
        pass


class Ocupado(EnfermeroState):
    def toString(self):
        return 'Ocupado'


class Libre(EnfermeroState):
    def toString(self):
        return 'Libre'

class Purgando(EnfermeroState):
    def toString(self):
        return 'Purgando'