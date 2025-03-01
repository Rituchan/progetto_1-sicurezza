import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Caricamento dei dati
file_path = 'Dataset.csv'  # Assicurati che il file si trovi nella stessa directory dello script
data = pd.read_csv(file_path, delimiter=';')

# Pulizia dei dati: rimuovere eventuali valori nulli nella colonna "gang"
data = data.dropna(subset=['gang'])

# Contare il numero di vittime uniche per ogni gang
victims_per_gang = data.groupby('gang')['victim'].nunique()
victims_per_gang.sort_values(ascending=False).to_csv('3_Victims_by_gang.csv', header=['Unique Victims'])

# Conversione della colonna "date" in formato datetime e creazione della colonna "year"
data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y', errors='coerce')
data['year'] = data['date'].dt.year.astype('Int64')

# Raggruppamento dei dati per "victim" e selezione dell'ultima occorrenza
unique_victims = data.groupby('victim').last().reset_index()

# Conteggio delle occorrenze per "Victim Country" con il filtro per anno
gang_victims_by_year = unique_victims.groupby(['year', 'gang']).size().reset_index(name='count')

# Esportazione del CSV aggiornato
gang_victims_by_year.to_csv('3_Victims_by_gang_filtered_by_year.csv', index=False)

# Selezionare solo le top 20 gang con più vittime uniche
top_20_victims_per_gang = victims_per_gang.sort_values(ascending=False).head(20)

# Creare l'istogramma
plt.figure(figsize=(10, 6))
ax = top_20_victims_per_gang.plot(kind='bar', color='skyblue', edgecolor='black')

# Aggiungere i valori sulle barre
for bar in ax.patches:
    ax.text(
        bar.get_x() + bar.get_width() / 2,  # Posizione X
        bar.get_height() + 0.5,            # Posizione Y
        f'{int(bar.get_height())}',        # Testo da mostrare
        ha='center',                       # Allineamento orizzontale
        va='bottom',                       # Allineamento verticale
        fontsize=10                        # Dimensione del font
    )

# Personalizzare il grafico
plt.title('Top 20 most active Ransomware Gangs by number of victims', fontsize=16)
plt.xlabel('Ransomware Gang', fontsize=14)
plt.ylabel('Number of Unique Victims', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Mostrare il grafico
plt.tight_layout()
plt.show()

# Convert the date column to datetime format and extract the year
data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y', errors='coerce')
data['year'] = data['date'].dt.year

# Filter data for the years 2021, 2022, 2023, 2024
filtered_data = data[data['year'].isin([2021, 2022, 2023, 2024])]

# Calculate unique victims per gang for each year
unique_victims_by_year = (
    filtered_data.groupby(['year', 'gang'])['victim']
    .nunique()
    .reset_index(name='unique_victims')
    .sort_values(['year', 'unique_victims'], ascending=[True, False])
    .groupby('year')
    .head(10)
)

# Define years for the subplots
years = [2021, 2022, 2023, 2024]

# Create subplots for each year with vertical bar plots
fig, axes = plt.subplots(2, 2, figsize=(16, 12), sharey=True)

# Plot each year's data
for i, year in enumerate(years):
    ax = axes[i // 2, i % 2]
    yearly_data = unique_victims_by_year[unique_victims_by_year['year'] == year]

    sns.barplot(
        data=yearly_data,
        x='gang',
        y='unique_victims',
        hue='gang',  # Assigning x to hue to avoid warnings
        dodge=False,
        palette='coolwarm',
        ax=ax
    )

    # Add values on top of the bars
    for bar in ax.patches:
        bar_height = bar.get_height()
        if bar_height > 0:  # Avoid cluttering with zero values
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # X position
                bar.get_height() + 0.5,  # Y position
                int(bar_height),  # Text (number of victims)
                ha='center',  # Horizontal alignment
                va='bottom',  # Vertical alignment
                fontsize=10  # Font size
            )

    ax.set_title(f'Top 10 Ransomware Gangs in {year} (Unique Victims)', fontsize=14)
    ax.set_xlabel('', fontsize=12)
    ax.set_ylabel('Number of Unique Victims', fontsize=12)
    ax.set_xticks(range(len(yearly_data)))
    ax.set_xticklabels(yearly_data['gang'], rotation=45, ha='right', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout
plt.tight_layout()
plt.show()

#########################################################################################

# Filtrare le gang con almeno 10 occorrenze prima della normalizzazione
total_occurrences = data.groupby('gang').size()
over_100_gangs = total_occurrences[total_occurrences >= 10].index
filtered_data = data[data['gang'].isin(over_100_gangs)]

# Conteggio delle occorrenze per Gang e Victim Country
grouped_data = filtered_data.groupby(['gang', 'Victim sectors']).size().unstack(fill_value=0)

# Calcolo delle percentuali
percentage_data = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

# Filtrare le gang con percentuale > 40% su un settore
filtered_gangs = percentage_data[(percentage_data.max(axis=1) > 40)]

# Aggiungere la categoria "other" per i settori colpiti meno del 2%
def process_sectors(row):
    above_threshold = row[row >= 2]
    below_threshold = row[row < 2].sum()
    processed_row = above_threshold.copy()
    if below_threshold > 0:
        processed_row['other'] = below_threshold
    return processed_row

processed_data = filtered_gangs.apply(process_sectors, axis=1)

# Ordinare i dati filtrati per la percentuale massima
processed_data = processed_data.loc[processed_data.max(axis=1).sort_values(ascending=False).index]

# Creazione del grafico a barre con annotazioni
fig, ax = plt.subplots(figsize=(14, 8))

# Creazione dinamica della palette
colors_palette = (sns.color_palette("deep") + sns.color_palette("pastel"))# Generazione della palette husl con tanti colori quanti sono i paesi
colors = sns.color_palette(colors_palette, n_colors=len(processed_data.columns))
if 'other' in processed_data.columns:
    colors[-1] = 'darkgray'

bars = processed_data.plot(
    kind='bar', stacked=True, ax=ax, color=colors
)

# Aggiunta delle percentuali sulle barre
for container in bars.containers:
    for bar in container:
        height = bar.get_height()
        if height > 0:  # Mostra solo valori significativi
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + height / 2),
                        ha='center', va='center', fontsize=6, color='black')

# Personalizzazione del grafico
plt.title('Ransomware Gangs which mainly target one sector (>40%)', fontsize=16)
plt.xlabel('Ransomware Gang', fontsize=14)
plt.ylabel('% Attacks', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.legend(title='Sectors', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Salvataggio del grafico
plt.show()
