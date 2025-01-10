import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Lettura del dataset
file_path = "Dataset.csv"  # Sostituisci con il percorso del tuo file
data = pd.read_csv(file_path, delimiter=";")

# Conversione della colonna "date" in datetime
data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y', errors='coerce')

# Pulizia dei dati
# Rimuovere colonne completamente vuote
data_cleaned = data.dropna(how="all", axis=1)

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
    "2022-02": "Inizio guerra Russia-Ucraina",
    "2022-08": "Visita di Pelosi a Taiwan",
    "2022-09": "Proteste in Iran (morte di Mahsa Amini)",
    "2023-04": "La Finlandia entra nella NATO",
    "2023-07": "Vertice NATO a Vilnius",
    "2023-10": "Attacco di Hamas a Israele",
    "2024-11": "Elezioni presidenziali USA",
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
plt.title("Attacchi ransomware in relazione ai principali eventi geopolitici", fontsize=18)
plt.xlabel("Anno-Mese", fontsize=14)
plt.ylabel("Numero di attacchi", fontsize=14)
plt.xticks(rotation=90, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=12)
plt.tight_layout()

# Mostrare il grafico
plt.show()

###############################################################################################

# Funzione per convertire un codice paese in una bandiera emoji Unicode
def country_to_flag(country):
    return country.strip().upper()[:2]


# Carica il file CSV
file_path = 'Updated_Dataset.csv'  # Sostituisci con il percorso del tuo file
data = pd.read_csv(file_path, sep=',', engine='python', on_bad_lines='skip')

# Filtra le colonne pertinenti
data_filtered = data[['Gang name', 'Victim Country', 'Country of Origin']]

# Correggi "Russia;Eastern Europe" e rimuovi "Eastern Europe" e "Est EU"
data_filtered.loc[:, 'Country of Origin'] = data_filtered['Country of Origin'].replace(
    {'Russia;Eastern Europe': 'Russia'}
)
data_filtered = data_filtered.loc[~data_filtered['Country of Origin'].isin(['Eastern Europe', 'Est EU'])]

# Calcola le occorrenze totali per ogni gang
total_occurrences_per_gang = data_filtered['Gang name'].value_counts()

# Filtra le gang con almeno 10 occorrenze
eligible_gangs = total_occurrences_per_gang[total_occurrences_per_gang >= 10].index
data_filtered = data_filtered[data_filtered['Gang name'].isin(eligible_gangs)]

# Calcola le occorrenze per ogni combinazione di "Gang name" e "Victim Country"
gang_victim_counts = data_filtered.groupby(['Gang name', 'Victim Country']).size().unstack(fill_value=0)

# Normalizza i dati in percentuali per ogni gang
gang_victim_percentages = gang_victim_counts.div(gang_victim_counts.sum(axis=1), axis=0) * 100

# Trova la percentuale massima per ciascuna gang
max_percentages_per_gang = gang_victim_percentages.max(axis=1)

# Seleziona le top 20 gang in base alla percentuale massima
top_20_gangs = max_percentages_per_gang.nlargest(20).index

# Filtra i dati normalizzati per queste gang
filtered_percentages = gang_victim_percentages.loc[top_20_gangs]

# Identifica le colonne con percentuali inferiori al 5%
low_percentage_columns = filtered_percentages.columns[filtered_percentages.max(axis=0) < 5]

# Somma queste colonne e aggiungile come "Other"
filtered_percentages['Other'] = filtered_percentages[low_percentage_columns].sum(axis=1)

# Rimuovi le colonne con percentuali inferiori al 5%
filtered_percentages = filtered_percentages.drop(columns=low_percentage_columns)

# Aggiungi le bandiere accanto ai nomi delle gang
data_filtered['Gang-Country'] = data_filtered['Gang name'] + " (" + data_filtered['Country of Origin'] + ")"
gang_country_flags = {
    gang: f"{gang} {country_to_flag(origin)}"
    for gang, origin in data_filtered.set_index('Gang name')['Country of Origin'].to_dict().items()
}
filtered_percentages.index = filtered_percentages.index.map(gang_country_flags)

# Numero di categorie (inclusa "Other")
num_colors = len(filtered_percentages.columns)

# Generazione della palette `deep` e aggiunta del grigio
palette = sns.color_palette("pastel", num_colors - 1)  # Palette `deep` per le categorie
custom_colors = list(palette) + ['darkgray']  # Aggiungi il grigio per "Other"

# Creazione del grafico
ax = filtered_percentages.plot(
    kind='bar',
    stacked=True,
    figsize=(15, 7),
    color=custom_colors
)

# Aggiungi percentuali sui segmenti > 5%
for bar_group in ax.containers:
    for bar in bar_group:
        height = bar.get_height()
        if height > 5:  # Mostra solo le percentuali > 5%
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + height / 2,
                f'{height:.1f}%',
                ha='center',
                va='center',
                fontsize=8,
                color='black'
            )

# Personalizzazione del grafico
plt.title('Correlazione tra nazione di origine della ransomware gang e nazioni attaccate', fontsize=16)
plt.xlabel('Ransomware Gang (Nazione di origine)', fontsize=12)
plt.ylabel('% Attacchi', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.legend(title='Nazione', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Mostra il grafico
plt.show()