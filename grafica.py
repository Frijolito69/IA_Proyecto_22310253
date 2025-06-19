import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style

style.use("fivethirtyeight")

# Cargar el CSV generado por el bot
df = pd.read_csv("usermetrics.csv", names=['time', 'online', 'idle', 'offline'])

# Convertir el timestamp a fecha
df['date'] = pd.to_datetime(df['time'], unit='s')

# Calcular el total de usuarios (opcional)
df['total'] = df['online'] + df['idle'] + df['offline']

# Eliminar la columna "time" original (timestamp)
df.drop("time", axis=1, inplace=True)

# Usar la fecha como índice para graficar por tiempo
df.set_index("date", inplace=True)

# Mostrar los primeros datos en consola
print(df.head())

# Graficar solo los usuarios en línea
df['online'].plot()
plt.title("Usuarios en línea")
plt.ylabel("Cantidad")
plt.xlabel("Tiempo")
plt.tight_layout()
plt.legend()

# Mostrar la gráfica
plt.show()

# Guardarla en imagen
plt.savefig("online.png")
