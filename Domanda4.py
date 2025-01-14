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

axes[0].set_title('Quarterly trend of attacks', fontsize=14)
axes[0].set_xlabel('', fontsize=12)
axes[0].set_ylabel('Attacks', fontsize=12)
axes[0].grid(axis='y', linestyle='--', alpha=0.7)

# Grafico semestrale
semestrale.plot(kind='bar', ax=axes[1], color='lightgreen', edgecolor='black')

# Aggiunta dei valori sulle colonne
for i, v in enumerate(semestrale):
    axes[1].text(i, v + 1, str(v), ha='center', fontsize=10)

axes[1].set_title('Six-monthly trend of attacks', fontsize=14)
axes[1].set_xlabel('', fontsize=12)
axes[1].set_ylabel('# Attacks', fontsize=12)
axes[1].grid(axis='y', linestyle='--', alpha=0.7)

# Mostra i grafici con le modifiche
plt.tight_layout()
plt.show()

#######################################################################

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Caricamento del dataset
file_path = 'Dataset.csv'  # Sostituire con il percorso corretto se necessario
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

# Definizione delle date di CVE e di due date casuali
highlight_dates = {
    '2021': [
        (pd.to_datetime('2021-03-03'), 'CVE-2021-26855 (ProxyLogon)'),
        (pd.to_datetime('2021-04-23'), 'CVE-2021-22893'),
        (pd.to_datetime('2021-07-02'), 'CVE-2021-34527 (PrintNightmare)')
    ],
    '2022': [
        (pd.to_datetime('2022-04-11'), 'CVE-2022-22954'),
        (pd.to_datetime('2022-06-03'), 'CVE-2022-26134 (Atlassian Confluence RCE)'),
        (pd.to_datetime('2022-07-17'), 'CVE-2022-26352')
    ],
    '2023': [
        (pd.to_datetime('2023-03-12'), 'CVE-2023-48788')
    ],
    '2024': [
        (pd.to_datetime('2024-01-24'), 'CVE-2024-23897'),
        (pd.to_datetime('2024-02-21'), 'CVE-2024-1709')
    ]
}

# Creazione della griglia 3x3
fig, axes = plt.subplots(3, 3, figsize=(18, 18))
axes = axes.flatten()

# Indicizzazione dei subplot
plot_index = 0

for year, highlights in highlight_dates.items():
    for cve_date, label in highlights:
        # Definizione del range di ±7 giorni attorno alla data della CVE
        start_date = cve_date - pd.Timedelta(days=7)
        end_date = cve_date + pd.Timedelta(days=7)

        # Filtraggio dei dati nel range
        data_range = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
        date_counts = data_range['date'].value_counts().sort_index()

        # Creazione del grafico
        ax = axes[plot_index]
        ax.plot(date_counts.index, date_counts.values, linestyle='-', marker='o')
        ax.axvline(x=cve_date, color='orange', linestyle='--', label=label)

        # Imposta il titolo con mese e anno
        ax.set_title(f"{label}", fontsize=12)

        # Modifica l'asse X per mostrare mese e giorno
        ax.set_xlabel('Month-Day', fontsize=10)
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.set_ylabel('# Attacks', fontsize=10)
        ax.grid(True)
        ax.tick_params(axis='x', rotation=90)
        ax.legend(fontsize=8)
        plot_index += 1

# Disattivazione dei subplot inutilizzati
for idx in range(plot_index, len(axes)):
    axes[idx].axis('off')

# Layout finale
plt.tight_layout()
plt.show()

