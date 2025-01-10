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

#######################################################################

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Dataset di esempio (sostituisci con il tuo dataset)
file_path = 'Dataset.csv'
data = pd.read_csv(file_path, sep=';')

# Funzione per convertire date con formati multipli
def parse_dates(date):
    for fmt in ('%d/%m/%Y', '%Y-%m-%d %H:%M:%S'):
        try:
            return pd.to_datetime(date, format=fmt)
        except ValueError:
            continue
    return None  # Restituisci None se nessun formato è valido

# Pre-elaborazione dei dati
data['date'] = data['date'].str.strip()
data['date'] = data['date'].apply(parse_dates)
data = data.dropna(subset=['date'])  # Rimuovi righe con date non valide

# Filtra i dati per il 2021 e 2022
data_2021 = data[data['date'].dt.year == 2021]
date_counts_2021 = data_2021['date'].value_counts().sort_index()

data_2022 = data[data['date'].dt.year == 2022]
date_counts_2022 = data_2022['date'].value_counts().sort_index()

# Date ed etichette da evidenziare per il 2021
highlight_2021 = [
    (pd.to_datetime('2021-03-03'), 'CVE-2021-26855 (ProxyLogon)'),
    (pd.to_datetime('2021-04-23'), 'CVE-2021-22893'),
    (pd.to_datetime('2021-07-02'), 'CVE-2021-34527 (PrintNightmare)'),
    (pd.to_datetime('2021-12-10'), 'CVE-2021-44228 (Log4Shell)')
]

# Date ed etichette da evidenziare per il 2022
highlight_2022 = [
    (pd.to_datetime('2022-06-03'), 'CVE-2022-26134 (Atlassian Confluence RCE)')
]

# Creazione della figura con due subplot disposti verticalmente
fig, axes = plt.subplots(2, 1, figsize=(16, 14))

# Primo plot: 2021
axes[0].plot(date_counts_2021.index, date_counts_2021.values, linestyle='-')
for date, label in highlight_2021:
    axes[0].axvline(x=date, color='orange', linestyle='--')
    axes[0].text(date, max(date_counts_2021.values) / 2, label, color='black',
                 rotation=90, fontsize=12, ha='right', va='center', fontweight="bold")
axes[0].set_title('Attacchi ransomware - 2021', fontsize=14)
axes[0].set_xlabel('Mesi - 2021', fontsize=12)
axes[0].set_ylabel('Numero di attacchi', fontsize=12)
axes[0].grid(True)
axes[0].xaxis.set_major_locator(mdates.MonthLocator())
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
axes[0].tick_params(axis='x', rotation=90)

# Secondo plot: 2022
axes[1].plot(date_counts_2022.index, date_counts_2022.values, linestyle='-')
for date, label in highlight_2022:
    axes[1].axvline(x=date, color='orange', linestyle='--')
    axes[1].text(date, max(date_counts_2022.values) / 2, label, color='black',
                 rotation=90, fontsize=12, ha='right', va='center', fontweight="bold")
axes[1].set_title('Attacchi ransomware - 2022', fontsize=14)
axes[1].set_xlabel('Mesi - 2022', fontsize=12)
axes[1].set_ylabel('Numero di attacchi', fontsize=12)
axes[1].grid(True)
axes[1].xaxis.set_major_locator(mdates.MonthLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
axes[1].tick_params(axis='x', rotation=90)

# Layout finale
plt.tight_layout()
plt.show()