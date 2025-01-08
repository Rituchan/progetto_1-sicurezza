import pandas as pd
import matplotlib.pyplot as plt

# Caricamento dei dati
file_path = 'Dataset.csv'  # Assicurati che il file si trovi nella stessa directory dello script
data = pd.read_csv(file_path, delimiter=';')

# Pulizia dei dati: rimuovere eventuali valori nulli nella colonna "gang"
data = data.dropna(subset=['gang'])

# Contare il numero di vittime uniche per ogni gang
victims_per_gang = data.groupby('gang')['victim'].nunique()

# Selezionare solo le top 20 gang con più vittime uniche
top_20_victims_per_gang = victims_per_gang.sort_values(ascending=False).head(20)

# Creare l'istogramma
plt.figure(figsize=(10, 6))
top_20_victims_per_gang.plot(kind='bar', color='skyblue', edgecolor='black')

# Personalizzare il grafico
plt.title('Numero di vittime uniche per le top 20 gang', fontsize=16)
plt.xlabel('Gang', fontsize=14)
plt.ylabel('Numero di vittime uniche', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Mostrare il grafico
plt.tight_layout()
plt.show()
