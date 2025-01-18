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
    "2022-02": "Start of the Russia-Ukraine war",
    "2023-04": "Finland joins NATO",
    "2023-10": "Hamas attack on Israel",
    "2024-11": "U.S. presidential elections",
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
    label="",
    color="blue",
    linewidth=2,
)

# Aggiungere le linee verticali per gli eventi
for event_date, event_name in updated_key_events.items():
    plt.axvline(x=event_date, color="orange", linestyle="--", alpha=0.7)
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
plt.title("Distribution of attacks in relation to major geopolitical events", fontsize=18)
plt.xlabel("", fontsize=14)
plt.ylabel("# Attacks", fontsize=14)
plt.tight_layout()

# Mostrare il grafico
plt.show()

# Leggere il dataset specificando il delimitatore corretto
dataset = data

# Convertire la colonna "date" in formato datetime
dataset['date'] = pd.to_datetime(dataset['date'], format='%d/%m/%Y', errors='coerce')

# Funzione per aggiungere una linea verticale con testo
def add_vertical_line(ax, date, label):
    ax.axvline(x=date, color='orange', linestyle='--', linewidth=1.5)
    ax.text(
        x=date,
        y=ax.get_ylim()[1] * 0.9,  # Posizionare il testo vicino alla cima del grafico
        s=label,
        color='black',
        fontsize=12,
        rotation=90,
        va='top',
        ha='right',
        fontweight="bold"
    )

# Creare la figura con 3 subplot disposti su 3 righe e 1 colonna
fig, axes = plt.subplots(3, 1, figsize=(14, 18))

# Subplot 1: Attacchi a Paesi Nato, 2023-04-04
attacks_nato = dataset[
    (dataset['Victim Country'].str.lower().isin(['estonia', 'latvia', 'lithuania', 'poland', 'romania', 'bulgaria', 'hungary', 'slovakia', 'czech republic', 'slovenia', 'netherlands', 'belgium', 'france', 'luxembourg', 'germany', 'italy', 'spain', 'portugal', 'norway', 'denmark', 'iceland', 'canada', 'usa'])) &
    (dataset['date'] >= '2023-01-04') & (dataset['date'] <= '2023-07-04')  # 3 mesi prima e dopo
]
daily_attacks_nato = attacks_nato.groupby('date').size()

axes[0].plot(daily_attacks_nato.index, daily_attacks_nato.values, marker='', color='green')
axes[0].set_title('Ransomware attacks targeting NATO countries')
axes[0].set_xlabel('')
axes[0].set_ylabel('# Attacks')
axes[0].grid(True)
add_vertical_line(axes[0], pd.to_datetime('2023-04-04'), 'Finland joins NATO')

# Subplot 2: Attacchi a Israele, 2023-10-07
attacks_israel = dataset[
    (dataset['Victim Country'].str.lower() == 'israel') &
    (dataset['date'] >= '2023-07-07') & (dataset['date'] <= '2024-01-07')  # 3 mesi prima e dopo
]
daily_attacks_israel = attacks_israel.groupby('date').size()

axes[1].plot(daily_attacks_israel.index, daily_attacks_israel.values, marker='', color='blue')
axes[1].set_title('Ransomware attacks targeting Israel')
axes[1].set_xlabel('')
axes[1].set_ylabel('# Attacks')
axes[1].grid(True)
add_vertical_line(axes[1], pd.to_datetime('2023-10-07'), 'Hamas attack on Israel')

# Subplot 3: Attacchi a USA, 2024-11-05
attacks_usa = dataset[
    (dataset['Victim Country'].str.lower() == 'usa') &
    (dataset['date'] >= '2024-08-05') & (dataset['date'] <= '2025-02-05')  # 3 mesi prima e dopo
]
daily_attacks_usa = attacks_usa.groupby('date').size()

axes[2].plot(daily_attacks_usa.index, daily_attacks_usa.values, marker='', color='purple')
axes[2].set_title('Ransomware attacks targeting USA')
axes[2].set_xlabel('')
axes[2].set_ylabel('# Attacks')
axes[2].grid(True)
add_vertical_line(axes[2], pd.to_datetime('2024-11-05'), 'U.S. presidential elections')

# Layout e visualizzazione
plt.tight_layout()
plt.show()


###############################################################################################

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Funzione per convertire un codice paese in una bandiera emoji Unicode
def country_to_flag(country):
    return country.strip().upper()[:2]

# Caricare i file CSV
file1_path = 'Ransomware_Gang_Profile.csv'
file2_path = 'Dataset.csv'

ransomware_gang_profile = pd.read_csv(file1_path, sep=",")
dataset = pd.read_csv(file2_path, sep=";")

# Selezionare le colonne necessarie
ransomware_gang_profile = ransomware_gang_profile[["Gang name", "Country of origin"]]
dataset = dataset[["gang", "Victim Country"]]

# Pulire i dati (rimuovere duplicati e valori mancanti)
ransomware_gang_profile.dropna(subset=["Gang name", "Country of origin"], inplace=True)
dataset.dropna(subset=["gang", "Victim Country"], inplace=True)

# Creare una lista per memorizzare i dati
data = []

# Popolare la lista con i paesi di origine
for _, row in ransomware_gang_profile.iterrows():
    gang_name = row["Gang name"].strip().lower()
    countries_of_origin = map(str.strip, row["Country of origin"].split(";"))
    for country in countries_of_origin:
        data.append({"Gang name": gang_name, "Country type": "origin", "Country": country})

# Popolare la lista con i paesi delle vittime
for _, row in dataset.iterrows():
    gang_name = row["gang"].strip().lower()
    victim_country = row["Victim Country"].strip()
    data.append({"Gang name": gang_name, "Country type": "victim", "Country": victim_country})

# Creare un DataFrame dai dati
result_df = pd.DataFrame(data)

# Filtra le colonne pertinenti
data_filtered = result_df[result_df['Country type'] == 'victim']
data_filtered = data_filtered.merge(ransomware_gang_profile, left_on='Gang name', right_on='Gang name', how='inner')

# Correggi "Russia;Eastern Europe" e rimuovi "Eastern Europe" e "Est EU"
data_filtered.loc[:, 'Country of origin'] = data_filtered['Country of origin'].replace(
    {'Russia;Eastern Europe': 'Russia'}
)
data_filtered = data_filtered.loc[~data_filtered['Country of origin'].isin(['Eastern Europe', 'Est EU'])]

# Filtra le gang che non hanno un "Country of origin"
data_filtered = data_filtered[~data_filtered['Country of origin'].isnull()]

# Calcola le occorrenze totali per ogni gang
total_occurrences_per_gang = data_filtered['Gang name'].value_counts()

# Filtra le gang con almeno 10 occorrenze
eligible_gangs = total_occurrences_per_gang[total_occurrences_per_gang >= 10].index
data_filtered = data_filtered[data_filtered['Gang name'].isin(eligible_gangs)]

# Calcola le occorrenze per ogni combinazione di "Gang name" e "Victim Country"
gang_victim_counts = data_filtered.groupby(['Gang name', 'Country']).size().unstack(fill_value=0)

# Normalizza i dati in percentuali per ogni gang
gang_victim_percentages = gang_victim_counts.div(gang_victim_counts.sum(axis=1), axis=0) * 100

# Conta il numero totale di nazioni attaccate per ogni gang
total_countries_attacked = (gang_victim_counts > 0).sum(axis=1)

# Filtra le gang che attaccano un massimo di 7 nazioni
gangs_max_7_countries = total_countries_attacked[total_countries_attacked < 9]

# Riordina le gang in base al numero totale di nazioni attaccate (crescentemente)
ordered_gangs_total = gangs_max_7_countries.sort_values().index

# Filtra e riordina le percentuali
filtered_percentages_total = gang_victim_percentages.loc[ordered_gangs_total]

# Identifica le nazioni che effettivamente compaiono nel grafico (almeno un valore > 0)
countries_in_graph = filtered_percentages_total.columns[(filtered_percentages_total > 0).any(axis=0)]
countries_in_graph = countries_in_graph.tolist()

# Aggiungi le bandiere accanto ai nomi delle gang
data_filtered['Gang-Country'] = data_filtered['Gang name'] + " (" + data_filtered['Country of origin'] + ")"
gang_country_flags = {
    gang: f"{gang} {country_to_flag(origin)}"
    for gang, origin in data_filtered.set_index('Gang name')['Country of origin'].to_dict().items()
}
filtered_percentages_total.index = filtered_percentages_total.index.map(gang_country_flags)

# Creazione del grafico
colors_palette = (sns.color_palette("dark") + sns.color_palette("deep") + sns.color_palette("pastel") +
                 sns.color_palette("dark") + sns.color_palette("colorblind"))  # Generazione della palette husl con tanti colori quanti sono i paesi

custom_colors = colors_palette[:len(countries_in_graph)]  # Usa solo i colori per le nazioni presenti

ax = filtered_percentages_total[countries_in_graph].plot(
    kind='bar',
    stacked=True,
    figsize=(15, 7),
    color=custom_colors
)

# Aggiungi percentuali sui segmenti > 3%
for bar_group in ax.containers:
    for bar in bar_group:
        height = bar.get_height()
        if height > 3:  # Mostra solo le percentuali > 3%
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
plt.title('Distribution of Ransomware Gang attacks targeting a maximum of 8 countries', fontsize=16)
plt.xlabel('Ransomware Gang', fontsize=12)
plt.ylabel('% Attacks', fontsize=12)
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
