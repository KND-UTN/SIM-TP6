from random import Random
from RungeKutta import RungeKutta
from clases.paciente import Paciente
from clases.randoms import Random
from clases.eventos import Eventos
from clases.enfermero import Enfermero
from clases.medicos import Medicos
from clases.estadisticas import Estadisticas
import json

import pandas as pd


class Simulacion:
    pacientes_mostrar = None

    def __init__(self, cant_filas, desde, hasta, runge_kutta: RungeKutta):
        # Inicializamos la fila
        self.nombre_evento = 'Inicializacion'
        self.reloj = 0
        self.eventos = Eventos(runge_kutta)
        self.enfermero = Enfermero()
        self.medicos = Medicos()
        self.estadisticas = Estadisticas



        Simulacion.pacientes_mostrar = {}

        self.fila = [[self.nombre_evento, self.reloj] + \
                     self.eventos.get_fila() + self.enfermero.get_fila() + self.medicos.get_fila(Simulacion) + self.estadisticas.get_fila() + [Paciente.countId]]
        columnas = ["nombre_evento", "reloj", "rnd_llegada", "tiempo_llegada", "proxima_llegada", "rnd_examen",
                    "tiempo_examen", "proximo_examen", "rnd_urgente", "urgente", "rnd_atencion", "tiempo_atencion",
                    "fin_atencion_m1", "fin_atencion_m2", 'rnd_prox_inestabilidad', 'tiempo_prox_inestabilidad', 'prox_inestabilidad', 'tiempo_purga', 'fin_purga', "estado", 'tiempo_remanente', "cola", "estado_M1", "remanente_M1", "estado_M2", "remanente_M2", "cola_comun",
                    "cola_urgente", "max_cola_comun", "max_cola_urgente", "espera_urgente", "max_espera_urgente",
                    "ac_tiempo_espera_comun", "ac_pacientes_atendidos", "interrupciones", "ac_tiempo_examen",
                    "cant_pacientes_examinados", "tiempo_ocioso_M1", "tiempo_ocioso_M2", "cant_pacientes"]
        self.tabla = pd.DataFrame(self.fila, columns=columnas)
        self.reloj_anterior = 0

        anterior_m1_libre = True
        anterior_m2_libre = True

        self.mostrar = False
        for n in range(cant_filas):
            if desde <= n <= hasta:
                self.mostrar = True
            else:
                self.mostrar = False

            self.proxima_fila()

            # Inicio estadisticas
            self.estadisticas.max_cola_comun = max(self.estadisticas.max_cola_comun, len(self.medicos.cola_comun))
            self.estadisticas.max_cola_comun = max(self.estadisticas.max_cola_comun, len(self.medicos.cola_urgente))
            self.estadisticas.max_espera_urgente = max(self.estadisticas.max_espera_urgente,
                                                       self.estadisticas.espera_urgente)
            if not self.medicos.medico1_esta_ocupado():
                if anterior_m1_libre:
                    Estadisticas.tiempo_ocioso_medico_1 += self.reloj - self.reloj_anterior
                anterior_m1_libre = True
            else:
                if anterior_m1_libre:
                    Estadisticas.tiempo_ocioso_medico_1 += self.reloj - self.reloj_anterior
                anterior_m1_libre = False

            if not self.medicos.medico2_esta_ocupado():
                if anterior_m2_libre:
                    Estadisticas.tiempo_ocioso_medico_2 += self.reloj - self.reloj_anterior
                anterior_m2_libre = True
            else:
                if anterior_m2_libre:
                    Estadisticas.tiempo_ocioso_medico_2 += self.reloj - self.reloj_anterior
                anterior_m2_libre = False
            # Fin estadisticas

            if desde <= n <= hasta:

                # Solo si hay que mostrar la linea, hacemos esto
                self.fila = [self.nombre_evento, self.reloj] + self.eventos.get_fila() + \
                             self.enfermero.get_fila() + self.medicos.get_fila(Simulacion) + self.estadisticas.get_fila() + [Paciente.countId]
                self.tabla = self.tabla.append(pd.DataFrame([self.fila], columns=columnas))
                # Hasta aca


            self.reloj_anterior = self.reloj

            # Reiniciamos algunas estadisticas
            Estadisticas.espera_urgente = 0
            # Fin del reinicio

        self.fila = [self.nombre_evento, self.reloj] + self.eventos.get_fila() + \
                    self.enfermero.get_fila() + self.medicos.get_fila(Simulacion) + self.estadisticas.get_fila() + [Paciente.countId]
        self.tabla = self.tabla.append(pd.DataFrame([self.fila], columns=columnas))
        Estadisticas.reiniciar_estadisticas()
        Paciente.countId = 0
        self.tabla.to_excel("output.xlsx", sheet_name="h1")
        a1 = open("principal.json", "w")
        a1.write(str(self.tabla.reset_index().to_json(orient='records', default_handler=str)))
        a1.close()

    def proxima_fila(self):
        self.reloj, self.nombre_evento = self.eventos.get_proximo_evento()
        if self.nombre_evento != "sistema_inestable":
            self.eventos.arrastrar_inestabilidad()
        if self.nombre_evento != "fin_purga":
            self.eventos.arrastrar_purga()
        if self.nombre_evento == "llegada_paciente":
            self.llegada_paciente()
        elif self.nombre_evento == "fin_examen":
            self.fin_examen()
        elif self.nombre_evento == "fin_atencion (M1)":
            self.fin_atencion_m1()
        elif self.nombre_evento == "fin_atencion (M2)":
            self.fin_atencion_m2()
        elif self.nombre_evento == "sistema_inestable":
            self.sistema_inestable()
        elif self.nombre_evento == "fin_purga":
            self.fin_purga()
        else:
            raise Exception("FATAL ERROR: Por alguna razon, no hay proximo evento.")

    def llegada_paciente(self):
        Paciente.countId += 1
        self.nombre_evento += " (P" + str(Paciente.countId) + ")"
        self.eventos.calcular_proxima_llegada(self.reloj)
        nuevo_paciente = Paciente(self.reloj)
        if self.mostrar:
            Simulacion.pacientes_mostrar[nuevo_paciente.id] = nuevo_paciente
        if self.enfermero.add_paciente(nuevo_paciente) == 1:  # El paciente fue atendido en el momento
            self.eventos.calcular_fin_examen(self.reloj)
        else:
            self.eventos.arrastrar_fin_examen()
        self.eventos.arrastrar_fin_atencion()
        self.eventos.limpiar_urgente()

    def fin_examen(self):
        self.eventos.arrastrar_llegada_paciente()
        paciente_examinado = self.enfermero.atender_siguiente()
        if self.mostrar:
            Simulacion.pacientes_mostrar[paciente_examinado.id] = paciente_examinado
        self.nombre_evento += " (P" + str(paciente_examinado.id) + ")"
        if self.enfermero.esta_ocupado():  # Si hay alguien en la cola y se lo acaba de empezar a examinar
            self.eventos.calcular_fin_examen(self.reloj)
        else:  # No habia nadie en la cola -> no se esta examinando a nadie
            self.eventos.limpiar_fin_examen()
        Estadisticas.cant_pacientes_examinados += 1
        Estadisticas.ac_tiempo_espera_examen += self.reloj - paciente_examinado.hora_inicio_espera
        urgente = self.eventos.calcular_urgente()
        if urgente:
            paciente_examinado.caso.urgencia(paciente_examinado)
            fue_atendido = self.medicos.nuevo_urgencia(paciente_examinado, self.reloj, self.eventos.fin_atencion_m1, self.eventos.fin_atencion_m2)
        else:
            paciente_examinado.caso.caso_comun(paciente_examinado)
            fue_atendido = self.medicos.nuevo_comun(paciente_examinado, self.reloj)

        if fue_atendido == 1:
            self.eventos.calcular_fin_atencion_m1(self.reloj)
        elif fue_atendido == 2:
            self.eventos.calcular_fin_atencion_m2(self.reloj)
        else:
            self.eventos.arrastrar_fin_atencion()

    def fin_atencion_m1(self):
        self.eventos.arrastrar_llegada_paciente()
        self.eventos.arrastrar_fin_examen()
        self.eventos.limpiar_urgente()
        atendido_suspendido = self.medicos.siguiente_m1(self.reloj)
        if not atendido_suspendido:
            if self.medicos.medico1_esta_ocupado():
                self.eventos.calcular_fin_atencion_m1(self.reloj)
            else:
                self.eventos.limpiar_fin_atencion_m1()
        else:
            self.eventos.calcular_fin_atencion_m1_con_remanencia(self.reloj, self.medicos.tiempo_remanente_m1)
            self.medicos.tiempo_remanente_m1 = None

    def fin_atencion_m2(self):
        self.eventos.arrastrar_llegada_paciente()
        self.eventos.arrastrar_fin_examen()
        self.eventos.limpiar_urgente()
        atendido_suspendido = self.medicos.siguiente_m2(self.reloj)
        if not atendido_suspendido:
            if self.medicos.medico2_esta_ocupado():
                self.eventos.calcular_fin_atencion_m2(self.reloj)
            else:
                self.eventos.limpiar_fin_atencion_m2()
        else:
            self.eventos.calcular_fin_atencion_m2_con_remanencia(self.reloj, self.medicos.tiempo_remanente_m2)
            self.medicos.tiempo_remanente_m2 = None

    def get_table(self):
        self.tabla.reset_index(inplace=True)
        return json.loads(self.tabla.reset_index().to_json(orient='records'))

    def sistema_inestable(self):
        self.eventos.calcular_fin_purga(self.reloj, Paciente.countId)
        self.eventos.limpiar_inestabilidad()
        self.enfermero.purgar(self.reloj, self.eventos.fin_examen)
        self.eventos.arrastrar_llegada_paciente()
        self.eventos.arrastrar_fin_atencion()
        self.eventos.limpiar_fin_examen()

    def fin_purga(self):
        self.eventos.calcular_prox_inestabilidad(self.reloj)
        self.eventos.limpiar_purga()
        self.eventos.arrastrar_llegada_paciente()
        self.eventos.arrastrar_fin_atencion()
        tiempo_remanente = self.enfermero.desPurgar(self.reloj)
        if tiempo_remanente is not None:
            self.eventos.fin_examen = tiempo_remanente




    @staticmethod
    def get_pacientes_json():
        tablita = []
        for pacienteId in Simulacion.pacientes_mostrar:
            tablita.append(Simulacion.pacientes_mostrar[pacienteId].get_fila())
        return tablita



if __name__ == '__main__':
    # Hacemos que se tomen los randoms preestablecidos
    Random.debug = False
    simulacion = Simulacion(500, 0, 500, RungeKutta())

    #print(simulacion.get_table())
    #print(simulacion.get_pacientes_json())

    #print(Simulacion(10, 0, 10).get_table().to_string())

    # Random.debug = False
    # Simulacion(100, 0, 100).get_table().to_excel("output_lara.xlsx", sheet_name="h1")
    # Simulacion(100, 0, 100).get_table().to_excel("output_flor.xlsx", sheet_name="h1")
    # Simulacion(100, 0, 100).get_table().to_excel("output_lei.xlsx", sheet_name="h1")

    #print(json.dumps(json.loads(Simulacion(100, 0, 100).get_table().reset_index().to_json(orient='records')), indent=2))
    # for fila in Simulacion(10).get_table_pacientes():
    #     print(fila)
