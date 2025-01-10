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

# Conversione della colonna "date" in datetime
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')

# Pulizia dei dati
# Rimuovere colonne completamente vuote
data_cleaned = df.dropna(how="all", axis=1)

# Rimuovere righe con date non valide
data_filtered = data_cleaned.dropna(subset=["date"])

# Creare una colonna per il mese e l'anno
data_filtered = data_filtered.copy()
data_filtered["year_month"] = data_filtered["date"].dt.to_period("M")


# Aggregare le attività delle gang per mese
activity_by_month = data_filtered.groupby("year_month").size()

# Convertire a DataFrame per la visualizzazione
activity_by_month_df = activity_by_month.reset_index(name="activity_count")

# Eventi geopolitici chiave
updated_key_events = {
    "2020-11": "CVE-2020-1472 (ZeroLogon)",
    "2021-04": "CVE-2021-22893",
    "2021-07": "CVE-2021-34527 (PrintNightmare)",
    "2021-10": "CVE-2021-44228 (Log4Shell)",
    "2022-06": "CVE-2022-26134",
    "2023-01": "CVE-2022-47966",
    "2023-04": "CVE-2023-27350",
    "2024-09": "CVE-2024-40711",
    "2024-11": "CVE-2024-51378",
}

# Creazione del grafico con aggiunta della griglia grigia per migliorare la leggibilità
plt.figure(figsize=(15, 10))
plt.plot(
    activity_by_month_df["year_month"].astype(str),
    activity_by_month_df["activity_count"],
    label="Attacchi",
    color="blue",
    linewidth=2,
)

# Aggiunta delle linee verticali per gli eventi con il testo ingrandito
for event_date, event_name in updated_key_events.items():
    plt.axvline(x=event_date, color="red", linestyle="--", alpha=0.7)
    plt.text(
        event_date,
        max(activity_by_month_df["activity_count"]) / 2,  # Posizionare le scritte al centro
        event_name,
        rotation=90,
        horizontalalignment="center",
        fontsize=12,  # Testo più grande
        fontweight="bold",  # Aggiunto grassetto per leggibilità
        color="black",
    )

# Aggiunta della griglia grigia
plt.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.7)

# Dettagli del grafico
plt.title("Attacchi ransomware in relazione alle CVE critiche degli ultimi anni", fontsize=18)
plt.xlabel("Anno-Mese", fontsize=14)
plt.ylabel("Numero di attacchi", fontsize=14)
plt.xticks(rotation=90, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=12)
plt.tight_layout()

# Mostrare il grafico
plt.show()
