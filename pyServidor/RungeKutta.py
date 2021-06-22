import math
import json
import mpmath
import pandas as pd


# pd.set_option("display.max_rows", None, "display.max_columns", None)
class RungeKutta:
    def __init__(self):
        print('Generando tabla de inestabilidad...')
        tabla1, self.tiempos = self.tabla_inestabilidad()
        self.tablita_inestabilidad = tabla1
        print('Generando tabla de purga...')
        tabla2, self.tiempo = self.tabla_purga()
        self.tablita_purga = tabla2
        print('Runge Kutta procesado.')
        self.guardar_excel(tabla1, tabla2)
        self.tablita_inestabilidad.reset_index(inplace=True)
        self.tablita_purga.reset_index(inplace=True)
        #self.get_json(tabla1, tabla2)

    def tabla_inestabilidad(self):
        tiempos = []
        columnas = ['t', 'E', 'k1', 'k2', 'k3', 'k4', 't(i+1)', 'E(i+1)']
        # -- Definicion de variables --
        h = .1
        to = 0
        eo = 15

        # El tiempo promedio de 60 llegadas es de 300 minutos, por lo que la ecuacion de "a" nos queda
        a = mpmath.ln(20 / 3) / 300

        # b es igual a cero
        b = 0

        # -- Procesamiento --
        vector = [None, None, None, None, None, None, to, eo]
        tabla = pd.DataFrame([vector], columns=columnas)
        nuevoe = 0
        nuevoti1 = to
        nuevoei1 = eo

        while nuevoe <= 100:
            nuevot = nuevoti1
            nuevoe = nuevoei1
            if nuevoe >= 50 and vector[1] < 50:
                tiempos.append(nuevot)
            if nuevoe >= 70 and vector[1] < 70:
                tiempos.append(nuevot)
            if nuevoe >= 100 and vector[1] < 100:
                tiempos.append(nuevot)

            nuevok1 = a * nuevoe + b
            nuevok2 = a * (nuevoe + (h / 2) * nuevok1) + b
            nuevok3 = a * (nuevoe + (h / 2) * nuevok2) + b
            nuevok4 = a * (nuevoe + h * nuevok3) + b
            nuevoti1 = nuevot + h
            nuevoei1 = nuevoe + (h / 6) * (nuevok1 + 2 * nuevok2 + 2 * nuevok3 + nuevok4)

            vector = [nuevot, nuevoe, nuevok1, nuevok2, nuevok3, nuevok4, nuevoti1, nuevoei1]
            tabla = tabla.append(pd.DataFrame([vector], columns=columnas))
        return tabla, tiempos

    def tabla_purga(self):
        columnas = ['t', 'L', 'k1', 'k2', 'k3', 'k4', 't(i+1)', 'L(i+1)', 'L(i-1) - L(i)']
        # -- Definicion de variables --
        h = 1
        to = 0
        lo = 60

        # El tiempo promedio de 60 llegadas es de 300 minutos, por lo que la ecuacion de "a" nos queda
        a = -(mpmath.ln(20 / 3) / 300)*0.5

        # b es igual a cero
        b = 0

        # -- Procesamiento --
        vector = [None, None, None, None, None, None, to, lo, math.inf]
        tabla = pd.DataFrame([vector], columns=columnas)
        diferencia = math.inf
        nuevoti1 = to
        nuevoli1 = lo

        while diferencia >= .02:
            nuevot = nuevoti1
            nuevol = nuevoli1
            nuevok1 = a * nuevol + b
            nuevok2 = a * (nuevol + (h / 2) * nuevok1) + b
            nuevok3 = a * (nuevol + (h / 2) * nuevok2) + b
            nuevok4 = a * (nuevol + h * nuevok3) + b
            nuevoti1 = nuevot + h
            nuevoli1 = nuevol + (h / 6) * (nuevok1 + 2 * nuevok2 + 2 * nuevok3 + nuevok4)
            if vector[1] is not None:
                diferencia = vector[1] - nuevol

            vector = [nuevot, nuevol, nuevok1, nuevok2, nuevok3, nuevok4, nuevoti1, nuevoli1, diferencia]
            tabla = tabla.append(pd.DataFrame([vector], columns=columnas))
        tiempo = nuevot / 100
        return tabla, tiempo

    def guardar_excel(self, tabla1, tabla2):
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter('RungeKutta.xlsx')

        # Write each dataframe to a different worksheet.
        tabla1.to_excel(writer, sheet_name='Sheet1')
        tabla2.to_excel(writer, sheet_name='Sheet2')
        writer.save()

    def get_json(self, tabla1, tabla2):
        a1 = open("inestabilidad.json", "w")
        a2 = open("purga.json", "w")
        tabla1.reset_index(inplace=True)
        tabla2.reset_index(inplace=True)
        a1.write(str(tabla1.reset_index().to_json(orient='records', default_handler=str)))
        a2.write(str(tabla2.reset_index().to_json(orient='records', default_handler=str)))
        a1.close()
        a2.close()

    def get_tiempo_inestabilidad(self, random):
        if random < .5:
            return self.tiempos[0]
        if random < .7:
            return self.tiempos[1]
        if random < 1:
            return self.tiempos[2]

    def get_tiempo_purga(self):
        return self.tiempo

    def json_inestabilidad(self):
        return json.loads(self.tablita_inestabilidad.reset_index().to_json(orient='records', default_handler=float))

    def json_purga(self):
        return json.loads(self.tablita_purga.reset_index().to_json(orient='records', default_handler=float))




if __name__ == '__main__':
    rk = RungeKutta()
    print(rk.get_tiempo_inestabilidad(.1))
    print(rk.get_tiempo_inestabilidad(.6))
    print(rk.get_tiempo_inestabilidad(.9))
    print(rk.get_tiempo_purga())
    print(rk.json_purga())
