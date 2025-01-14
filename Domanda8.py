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

# Mappare i numeri dei mesi ai nomi abbreviati
month_names = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}

# Generare etichette personalizzate per l'asse x
xticks = [
    period[:4] if period.endswith("-01") else month_names[period[5:]]
    for period in activity_by_month_df["year_month"].astype(str)
]

# Creazione del grafico
plt.figure(figsize=(15, 10))
plt.plot(
    activity_by_month_df["year_month"].astype(str),
    activity_by_month_df["activity_count"],
    label="Attacchi",
    color="blue",
    linewidth=2,
)

# Aggiungere le linee verticali per gli eventi
for event_date, event_name in updated_key_events.items():
    plt.axvline(x=event_date, color="red", linestyle="--", alpha=0.7)
    plt.text(
        event_date,
        max(activity_by_month_df["activity_count"]) / 2,
        event_name,
        rotation=90,
        horizontalalignment="right",
        fontsize=12,
        fontweight="bold",
        color="black",
    )

# Applicare le etichette personalizzate all'asse x
plt.xticks(
    ticks=range(len(xticks)),
    labels=xticks,
    rotation=90,
    fontsize=12,
)

# Dettagli del grafico
plt.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.7)
plt.title("Attacchi ransomware in relazione ai principali eventi geopolitici", fontsize=18)
plt.xlabel("Anno-Mese", fontsize=14)
plt.ylabel("Numero di attacchi", fontsize=14)
plt.legend(fontsize=12)
plt.tight_layout()

# Mostrare il grafico
plt.show()

###############################################################################################

# Funzione per convertire un codice paese in una bandiera emoji Unicode
def country_to_flag(country):
    return country.strip().upper()[:2]

# Caricamento del file CSV
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

# Conta il numero totale di nazioni attaccate per ogni gang
total_countries_attacked = (gang_victim_counts > 0).sum(axis=1)

# Filtra le gang che attaccano un massimo di 10 nazioni
gangs_max_10_countries = total_countries_attacked[total_countries_attacked < 8]

# Riordina le gang in base al numero totale di nazioni attaccate (crescentemente)
ordered_gangs_total = gangs_max_10_countries.sort_values().index

# Filtra e riordina le percentuali
filtered_percentages_total = gang_victim_percentages.loc[ordered_gangs_total]

# Identifica le nazioni che effettivamente compaiono nel grafico (almeno un valore > 0)
countries_in_graph = filtered_percentages_total.columns[(filtered_percentages_total > 0).any(axis=0)]
countries_in_graph = countries_in_graph.tolist()

# Aggiungi le bandiere accanto ai nomi delle gang
data_filtered['Gang-Country'] = data_filtered['Gang name'] + " (" + data_filtered['Country of Origin'] + ")"
gang_country_flags = {
    gang: f"{gang} {country_to_flag(origin)}"
    for gang, origin in data_filtered.set_index('Gang name')['Country of Origin'].to_dict().items()
}
filtered_percentages_total.index = filtered_percentages_total.index.map(gang_country_flags)

# Creazione del grafico
colors_palette = (sns.color_palette("dark") + sns.color_palette("deep") + sns.color_palette("pastel") +
                 sns.color_palette("dark") + sns.color_palette("colorblind"))# Generazione della palette husl con tanti colori quanti sono i paesi

custom_colors = colors_palette[:len(countries_in_graph)]  # Usa solo i colori per le nazioni presenti

ax = filtered_percentages_total[countries_in_graph].plot(
    kind='bar',
    stacked=True,
    figsize=(15, 7),
    color=custom_colors
)

# Aggiungi percentuali sui segmenti > 5%
for bar_group in ax.containers:
    for bar in bar_group:
        height = bar.get_height()
        if height > 3:  # Mostra solo le percentuali > 5%
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
plt.title('Distribuzione degli attacchi delle ransomware gang che prendono di mira al massimo 7 nazioni', fontsize=16)
plt.xlabel('Ransomware Gang', fontsize=12)
plt.ylabel('% Attacchi', fontsize=12)
plt.xticks(rotation=45, ha='right')

# Ricrea la legenda solo con le nazioni presenti
plt.legend(
    handles=ax.get_legend_handles_labels()[0],
    labels=countries_in_graph,
    title='Nazione',
    bbox_to_anchor=(1.05, 1),
    loc='upper left'
)

plt.tight_layout()

# Mostra il grafico
plt.show()
