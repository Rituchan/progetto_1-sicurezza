import pandas as pd
import matplotlib.pyplot as plt

# Caricamento del dataset
file_path = 'Dataset.csv'
df = pd.read_csv(file_path, delimiter=';')


# Conversione della colonna 'date' in formato datetime
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')

# Filtrare righe con date valide
df = df.dropna(subset=['date']) # Rimuove le righe con date mancanti

# Creazione delle colonne 'Trimestre' e 'Semestre'
df['Trimestre'] = df['date'].dt.to_period('Q')#to_period('Q') restituisce il trimestre in formato 'YYYYQ1'
df['Semestre'] = df['date'].dt.year.astype(str) + '-H' + ((df['date'].dt.month > 6) + 1).astype(str) # Semestre in formato 'YYYY-H1'

# Conteggio degli attacchi per trimestre e semestre
trimestrale = df['Trimestre'].value_counts().sort_index() # Ordinamento per trimestre
semestrale = df['Semestre'].value_counts().sort_index() # Ordinamento per semestre

# Aggiunta dei valori sulle colonne dei grafici e formattazione delle label dei trimestri

fig, axes = plt.subplots(2, 1, figsize=(10, 12))

# Grafico trimestrale
trimestrale.index = trimestrale.index.astype(str)  # Formattazione 'yyyy-Q'
trimestrale.plot(kind='bar', ax=axes[0], color='skyblue', edgecolor='black')

# Aggiunta dei valori sulle colonne
for i, v in enumerate(trimestrale):
    axes[0].text(i, v + 1, str(v), ha='center', fontsize=10)

axes[0].set_title('Andamento trimestrale degli attacchi', fontsize=14)
axes[0].set_xlabel('Trimestre', fontsize=12)
axes[0].set_ylabel('Numero di attacchi', fontsize=12)
axes[0].grid(axis='y', linestyle='--', alpha=0.7)

# Grafico semestrale
semestrale.plot(kind='bar', ax=axes[1], color='lightgreen', edgecolor='black')

# Aggiunta dei valori sulle colonne
for i, v in enumerate(semestrale):
    axes[1].text(i, v + 1, str(v), ha='center', fontsize=10)

axes[1].set_title('Andamento semestrale degli attacchi', fontsize=14)
axes[1].set_xlabel('Semestre', fontsize=12)
axes[1].set_ylabel('Numero di attacchi', fontsize=12)
axes[1].grid(axis='y', linestyle='--', alpha=0.7)

# Mostra i grafici con le modifiche
plt.tight_layout()
plt.show()

