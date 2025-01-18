import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Caricamento dei dati
file_path = 'Dataset.csv'  # Assicurati che il file si trovi nella stessa directory dello script
data = pd.read_csv(file_path, delimiter=';')

# Clean the data: remove rows with null values in "Victim sectors" and "gang"
data = data.dropna(subset=['Victim sectors', 'gang'])

# Count occurrences in "Victim sectors"
sector_counts = data['Victim sectors'].value_counts()
sector_counts.to_csv('2_Attacks_by_sector.csv')

# Conversione della colonna "date" in formato datetime e creazione della colonna "year"
data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y', errors='coerce')
data['year'] = data['date'].dt.year.astype('Int64')

# Conteggio delle occorrenze per "Victim Country" con il filtro per anno
attacks_sector_by_year = data.groupby(['year', 'Victim sectors']).size().reset_index(name='count')

# Esportazione del CSV aggiornato
attacks_sector_by_year.to_csv('2_Attacks_by_sector_filtered_by_year.csv', index=False)

# Calculate percentages
total_count = sector_counts.sum()
percentages = (sector_counts / total_count) * 100

# Raggruppamento delle occorrenze sotto il 2% in "other"
above_threshold = percentages[percentages >= 2]
below_threshold = percentages[percentages < 2].sum()

# Aggiungere la categoria "other"
pie_data = above_threshold.copy()
pie_data['Other (<2%)'] = below_threshold

# Creazione della palette globale con grigio per "Other"
countries = pie_data.index
colors_palette = (sns.color_palette("deep") + sns.color_palette("pastel"))# Generazione della palette husl con tanti colori quanti sono i paesi

palette_global = sns.color_palette(colors_palette, n_colors=len(countries) - 1)  # Escludendo "Other"
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
plt.title('Attack Distribution based on the affected Sector', fontsize=16)
plt.ylabel('')  # Rimuovere etichetta dell'asse Y
plt.tight_layout()
plt.show()

# Selezionare i 4 anni specifici
years = [2021, 2022, 2023, 2024]

# Creazione del plot con 4 grafici
fig, axes = plt.subplots(2, 2, figsize=(15, 12))  # 2x2 grid di grafici
axes = axes.flatten()  # Rendere l'array bidimensionale piatto per iterare facilmente

for i, year in enumerate(years[:4]):  # Iterare sui primi 4 anni disponibili
    year_data = attacks_sector_by_year[attacks_sector_by_year['year'] == year]
    year_data = year_data.set_index('Victim sectors')['count']
    percentages = (year_data / year_data.sum()) * 100
    year_data = year_data.sort_values(ascending=False)

    # Raggruppamento delle occorrenze sotto il 3% in "other"
    above_threshold = year_data[percentages >= 4]
    below_threshold = year_data[percentages < 4].sum()

    # Aggiungere la categoria "other" se necessario
    if below_threshold > 0:
        above_threshold['Other (<4%)'] = below_threshold

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

plt.suptitle('Attack Distribution based on the affected Sector by Year', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adattare i grafici al layout
plt.show()

#######################################################################

# Conteggio delle occorrenze per Gang e Victim sectors
grouped_data = data.groupby(['gang', 'Victim sectors']).size().unstack(fill_value=0)
grouped_data.to_csv('2_Gang_attacks_by_sector.csv')

# Calcolo delle percentuali
total_occurrences = grouped_data.sum(axis=1)
percentage_data = grouped_data.div(total_occurrences, axis=0) * 100

# Seleziona le prime 20 gang con il maggior numero di occorrenze
top_20_gangs = total_occurrences.nlargest(20).index
filtered_gangs = percentage_data.loc[top_20_gangs]

# Raggruppare i "Victim sectors" con occorrenze inferiori al 5% nella categoria 'Other'
threshold = 5
filtered_gangs = filtered_gangs.copy()

# Identificare le colonne che hanno occorrenze inferiori al 5%
columns_to_group = filtered_gangs.columns[filtered_gangs.max(axis=0) < threshold]

# Creare una nuova colonna 'Other' che somma i settori 'Victim sectors' con occorrenze < 10%
filtered_gangs['Other'] = filtered_gangs[columns_to_group].sum(axis=1)

# Riordinare le colonne (Victim Sectors) per numero totale di occorrenze e mettere 'Other' come ultimo
ordered_columns = filtered_gangs.sum(axis=0).sort_values(ascending=False).index.tolist()
if 'Other' in ordered_columns:
    ordered_columns.remove('Other')
    ordered_columns.append('Other')
filtered_countries = filtered_gangs[ordered_columns]

# Rimuovere le colonne con occorrenze inferiori al 5%
filtered_gangs = filtered_gangs.drop(columns=columns_to_group)

# Assicurarsi che la somma delle percentuali sia 100% per ogni gang
filtered_gangs = filtered_gangs.div(filtered_gangs.sum(axis=1), axis=0) * 100

# Ordinare i dati filtrati per la percentuale massima
processed_data = filtered_gangs.loc[filtered_gangs.max(axis=1).sort_values(ascending=False).index]

palette_global = sns.color_palette(colors_palette)
# Aggiungi un colore personalizzato per la categoria 'Other' (lightgray)
colors = ['lightgray' if col == 'Other' else sns.color_palette(palette_global)[i] for i, col in enumerate(processed_data.columns)]

# Plot dei dati filtrati
fig, ax = plt.subplots(figsize=(14, 8))

bars = processed_data.plot(
    kind='bar', stacked=True, color=colors, ax=ax
)

# Aggiunta delle percentuali sulle barre
for container in bars.containers:
    for bar in container:
        height = bar.get_height()
        if height > 5:  # Mostra solo valori significativi
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + height / 2),
                        ha='center', va='center', fontsize=6, color='black')


# Personalizzazione del grafico
plt.title('Attack distribution of the 20 most active Ransomware Gangs based on the affected sector', fontsize=16)
plt.xlabel('Ransomware Gang', fontsize=14)
plt.ylabel('% Attacks', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.legend(title='Sectors', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Salvataggio del grafico
# plt.savefig('top_20_gangs.png')
plt.show()

