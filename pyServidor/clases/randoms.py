from random import Random as RandomOriginal

# Clase estatica de numeros randoms para facilitar el Debug
class Random:
    debug = False
    debug_random_llegada = [0.39, 0.00, 0.00, 0.00, 1.00, 1.00]
    debug_random_examen = [0.00, 0.05, 0.00, 0.00, 1.00]
    debug_random_caso = [1.00, 1.00, 0.00, 0.00]
    debug_random_atencion = [1, 1, 0, 0.5]

    @staticmethod
    def randomLlegada():
        if Random.debug:
            return Random.debug_random_llegada.pop(0)
        else:
            return RandomOriginal().random()

    @staticmethod
    def randomExamen():
        if Random.debug:
            return Random.debug_random_examen.pop(0)
        else:
            return RandomOriginal().random()

    @staticmethod
    def randomCaso():
        if Random.debug:
            return Random.debug_random_caso.pop(0)
        else:
            return RandomOriginal().random()

    @staticmethod
    def randomAtencion():
        if Random.debug:
            return Random.debug_random_atencion.pop(0)
        else:
            return RandomOriginal().random()
