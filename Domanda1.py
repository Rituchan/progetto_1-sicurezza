import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Caricamento dei dati
file_path = 'Dataset.csv'  # Assicurati che il file si trovi nella stessa directory dello script
data = pd.read_csv(file_path, delimiter=';')

# Pulizia dei dati: rimuovere eventuali valori nulli nella colonna "Victim Country"
data = data.dropna(subset=['Victim Country', 'gang'])

# Contare il numero di vittime uniche per ogni gang
victims_per_country = data.groupby('Victim Country')['victim'].nunique()
victims_per_country.sort_values(ascending=False).to_csv('1_Victims_by_country.csv', header=['Unique Victims'])

# Conversione della colonna "date" in formato datetime e creazione della colonna "year"
data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y', errors='coerce')
data['year'] = data['date'].dt.year.astype('Int64')

# Raggruppamento dei dati per "victim" e selezione dell'ultima occorrenza
unique_victims = data.groupby('victim').last().reset_index()

# Conteggio delle occorrenze per "Victim Country" con il filtro per anno
country_counts_by_year = unique_victims.groupby(['year', 'Victim Country']).size().reset_index(name='count')

# Esportazione del CSV aggiornato
country_counts_by_year.to_csv('1_Victims_by_country_filtered_by_year.csv', index=False)

# Conteggio aggregato delle occorrenze per "Victim Country"
country_counts = unique_victims['Victim Country'].value_counts()
total_count = country_counts.sum()
percentages = (country_counts / total_count) * 100

# Raggruppamento delle occorrenze sotto il 2% in "other"
above_threshold = percentages[percentages >= 2]
below_threshold = percentages[percentages < 2].sum()

# Aggiungere la categoria "other"
pie_data = above_threshold.copy()
pie_data['Other (<2%)'] = below_threshold

# Creazione della palette globale con grigio per "Other"
countries = pie_data.index
palette_global = sns.color_palette("deep", n_colors=len(countries) - 1)  # Escludendo "Other"
colors_mapping = dict(zip(countries, list(palette_global) + ['lightgray']))  # Aggiungere grigio per "Other"

# Creazione del grafico aggregato
plt.figure(figsize=(10, 8))
pie_data.plot(
    kind='pie',
    autopct='%1.1f%%',
    startangle=90,
    colors=[colors_mapping[country] for country in pie_data.index]
)

# Personalizzazione del grafico aggregato
plt.title('Victim Distribution based on their Country of residence', fontsize=16)
plt.ylabel('')  # Rimuovere etichetta dell'asse Y
plt.tight_layout()
plt.show()

# Selezionare i 4 anni specifici
years = [2021, 2022, 2023, 2024]

# Creazione del plot con 4 grafici
fig, axes = plt.subplots(2, 2, figsize=(15, 12))  # 2x2 grid di grafici
axes = axes.flatten()  # Rendere l'array bidimensionale piatto per iterare facilmente

for i, year in enumerate(years[:4]):  # Iterare sui primi 4 anni disponibili
    year_data = country_counts_by_year[country_counts_by_year['year'] == year]
    year_data = year_data.set_index('Victim Country')['count']
    percentages = (year_data / year_data.sum()) * 100
    year_data = year_data.sort_values(ascending=False)

    # Raggruppamento delle occorrenze sotto il 3% in "other"
    above_threshold = year_data[percentages >= 3]
    below_threshold = year_data[percentages < 3].sum()

    # Aggiungere la categoria "other" se necessario
    if below_threshold > 0:
        above_threshold['Other (<3%)'] = below_threshold

    # Creazione del grafico a torta con colori coerenti
    above_threshold.plot(
        kind='pie',
        autopct='%1.1f%%',
        startangle=90,
        colors=[colors_mapping.get(country, 'lightgray') for country in above_threshold.index],
        ax=axes[i]
    )

    # Personalizzazione
    axes[i].set_title(f'Year {year}', fontsize=14)
    axes[i].set_ylabel('')  # Rimuovere etichetta dell'asse Y

# Nascondere gli assi inutilizzati se ci sono meno di 4 anni
for j in range(len(years), 4):
    axes[j].axis('off')

plt.suptitle('Victim Distribution based on their Country of residence by Year', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adattare i grafici al layout
plt.show()

#######################################################################

# Filtrare le gang con almeno 10 occorrenze prima della normalizzazione
total_occurrences = data.groupby('gang').size()
over_100_gangs = total_occurrences[total_occurrences >= 10].index
filtered_data = data[data['gang'].isin(over_100_gangs)]

# Conteggio delle occorrenze per Gang e Victim Country
grouped_data = filtered_data.groupby(['gang', 'Victim Country']).size().unstack(fill_value=0)
grouped_data.to_csv('1_Gang_attacks_by_country.csv')

# Calcolo delle percentuali
percentage_data = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

# Filtrare le gang con percentuale > 80% su Victim Country: USA e > 50% su un'altra singola Victim Country
usa_filter = percentage_data['Usa'] > 80
other_country_filter = (percentage_data.drop(columns=['Usa']).max(axis=1) > 50)
filtered_gangs = percentage_data[(usa_filter) | (other_country_filter)]

# Aggiungere la categoria "other"
def process_gang(row):
    usa_percentage = row['Usa']
    other_countries = row.drop(labels=['Usa'])
    top_percentage = other_countries.max()
    if top_percentage < 50:
        other_percentage = 100 - usa_percentage
        return pd.Series({
            'Usa': usa_percentage,
            'other': other_percentage
        })
    else:
        top_country = other_countries.idxmax()
        other_percentage = 100 - top_percentage
        return pd.Series({
            top_country: top_percentage,
            'other': other_percentage
        })

processed_data = filtered_gangs.apply(process_gang, axis=1)

# Ordinare i dati filtrati per la percentuale massima
processed_data = processed_data.loc[processed_data.max(axis=1).sort_values(ascending=False).index]

# Seaborn palette
sns.set_palette("deep")  # Usa la palette 'deep' di seaborn

# Creazione del grafico a barre con annotazioni
fig, ax = plt.subplots(figsize=(14, 8))

# Aggiungi un colore personalizzato per la categoria 'other' (lightgray)
colors = ['lightgray' if col == 'other' else sns.color_palette("deep")[i] for i, col in enumerate(processed_data.columns)]

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
plt.title('Ransomware Gangs which mainly target one country', fontsize=16)
plt.xlabel('Ransomware Gang', fontsize=14)
plt.ylabel('% Attacks', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.legend(title='Countries', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.text(x=9.7, y=0, s='Countries considered if:\nUSA > 80%\nOR\nOther countries > 50%',
         bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.2'))
plt.tight_layout()

# Salvataggio del grafico
plt.show()
