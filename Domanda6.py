import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Caricamento dei dati
file_path = 'Dataset.csv'  # Assicurati che il file si trovi nella stessa directory dello script
data = pd.read_csv(file_path, delimiter=';')

# Pulizia dei dati: rimuovere eventuali valori nulli nelle colonne "Victim Country" e "Victim sectors"
data = data.dropna(subset=['Victim Country', 'Victim sectors'])

# Conteggio delle occorrenze per Victim Country e Victim Sectors
grouped_data = data.groupby(['Victim Country', 'Victim sectors']).size().unstack(fill_value=0)

# Calcolare il totale delle occorrenze per ogni Victim Country
total_occurrences = grouped_data.sum(axis=1)

# Filtrare le Victim Country con occorrenze maggiori del 2% rispetto al totale
total_threshold = total_occurrences.sum() * 0.02
filtered_countries = grouped_data[total_occurrences > total_threshold]

# Calcolare il totale per ogni Victim Sector
sector_totals = filtered_countries.sum(axis=0)

# Identificare i settori con occorrenze inferiori al 5% del totale
threshold = 1
threshold_value = sector_totals.sum() * (threshold / 100)
columns_to_group = sector_totals[sector_totals < threshold_value].index

# Creare una nuova colonna 'Other' che somma i settori 'Victim sectors' con occorrenze < 5%
filtered_countries = filtered_countries.copy()  # Assicurarsi di lavorare su una copia esplicita
filtered_countries['Other'] = filtered_countries[columns_to_group].sum(axis=1)

# Rimuovere le colonne con occorrenze inferiori al 5%
filtered_countries = filtered_countries.drop(columns=columns_to_group)

# Riordinare le colonne (Victim Sectors) per numero totale di occorrenze e mettere 'Other' come ultimo
ordered_columns = filtered_countries.sum(axis=0).sort_values(ascending=False).index.tolist()
if 'Other' in ordered_columns:
    ordered_columns.remove('Other')
    ordered_columns.append('Other')
filtered_countries = filtered_countries[ordered_columns]

# Calcolare le percentuali per ogni Victim Country
filtered_countries_percentage = filtered_countries.div(filtered_countries.sum(axis=1), axis=0) * 100

# Ordinare i dati per la somma delle occorrenze
processed_data = filtered_countries_percentage.loc[filtered_countries.sum(axis=1).sort_values(ascending=False).index]

# Definire una colormap personalizzata con grigio per 'Other'
colors = plt.cm.tab20.colors  # Prendere i colori di tab20
num_sectors = len(ordered_columns) - 1  # Numero di settori escluso 'Other'
cmap_colors = list(colors[:num_sectors]) + ['#A9A9A9']  # Aggiungere grigio per 'Other'
custom_cmap = ListedColormap(cmap_colors)

# Plot dei dati filtrati
fig, ax = plt.subplots(figsize=(14, 8))

bars = processed_data.plot(
    kind='bar', stacked=True, colormap=custom_cmap, ax=ax
)

# Aggiunta delle percentuali sulle barre
for container in bars.containers:
    for bar in container:
        height = bar.get_height()
        if height > 5:  # Mostra solo valori significativi
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + height / 2),
                        ha='center', va='center', fontsize=10, color='black')

# Personalizzazione del grafico
plt.title('Attacchi in ogni nazione divisi in base al settore attaccato', fontsize=16)
plt.xlabel('Nazione', fontsize=14)
plt.ylabel('% Attacchi', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.legend(title='Settori', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Mostrare il grafico
plt.show()

################################################################################

# Crea una colonna combinata con la tripla "gang - Victim Country - Victim sectors"
data['triplet'] = data['gang'] + " - " + data['Victim Country'] + " - " + data['Victim sectors']

# Calcola le occorrenze di ogni tripla
triplet_counts = data['triplet'].value_counts()

# Filtra le triplette con occorrenze maggiori di 50
triplet_counts_filtered = triplet_counts[triplet_counts > 50]

# Plotta l'istogramma
plt.figure(figsize=(10, 8))
ax = triplet_counts_filtered.sort_values(ascending=True).plot(kind='barh', color='coral')

# Aggiungi il numero delle occorrenze accanto a ciascuna barra
for index, value in enumerate(triplet_counts_filtered.sort_values(ascending=True)):
    plt.text(value + 1, index, str(value), va='center')

plt.xlabel('Numero di attacchi')
plt.ylabel('Triplette (Ransomware Gang - Nazione - Settore)')
plt.title('Pattern ricorrenti (con più di 50 attacchi)')
plt.tight_layout()
plt.show()
