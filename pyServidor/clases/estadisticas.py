class Estadisticas:
    max_cola_comun = 0
    max_cola_urgente = 0
    espera_urgente = 0
    max_espera_urgente = 0
    ac_espera_comun = 0
    ac_pacientes_comunes = 0
    ac_interrupciones = 0
    ac_tiempo_espera_examen = 0
    cant_pacientes_examinados = 0
    tiempo_ocioso_medico_1 = 0
    tiempo_ocioso_medico_2 = 0

    @staticmethod
    def get_fila():
        return [Estadisticas.max_cola_comun, Estadisticas.max_cola_urgente, Estadisticas.espera_urgente, Estadisticas.max_espera_urgente,
                Estadisticas.ac_espera_comun, Estadisticas.ac_pacientes_comunes, Estadisticas.ac_interrupciones, Estadisticas.ac_tiempo_espera_examen,
                Estadisticas.cant_pacientes_examinados, Estadisticas.tiempo_ocioso_medico_1, Estadisticas.tiempo_ocioso_medico_2]

    @staticmethod
    def reiniciar_estadisticas():
        Estadisticas.max_cola_comun = 0
        Estadisticas.max_cola_urgente = 0
        Estadisticas.espera_urgente = 0
        Estadisticas.max_espera_urgente = 0
        Estadisticas.ac_espera_comun = 0
        Estadisticas.ac_pacientes_comunes = 0
        Estadisticas.ac_interrupciones = 0
        Estadisticas.ac_tiempo_espera_examen = 0
        Estadisticas.cant_pacientes_examinados = 0
        Estadisticas.tiempo_ocioso_medico_1 = 0
        Estadisticas.tiempo_ocioso_medico_2 = 0
