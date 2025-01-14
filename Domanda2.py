import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns

# Caricamento dei dati
file_path = 'Dataset.csv'  # Assicurati che il file si trovi nella stessa directory dello script
data = pd.read_csv(file_path, delimiter=';')

# Clean the data: remove rows with null values in "Victim sectors" and "gang"
data = data.dropna(subset=['Victim sectors', 'gang'])

# Count occurrences in "Victim sectors"
sector_counts = data['Victim sectors'].value_counts()
sector_counts.to_csv('2_Attacks_by_sector.csv')

# Calculate percentages
total_count = sector_counts.sum()
percentages = (sector_counts / total_count) * 100

# Group occurrences under 2% into "other"
above_threshold = percentages[percentages >= 2]
below_threshold = percentages[percentages < 2].sum()

# Add "Other (<2%)" category
pie_data = above_threshold.copy()
pie_data['Other (<2%)'] = below_threshold

#una sola palette non è sufficiente per rappresentare tutti
colors_palette = (sns.color_palette("deep") + sns.color_palette("pastel") + sns.color_palette("bright") +
                 sns.color_palette("dark") + sns.color_palette("colorblind"))# Generazione della palette husl con tanti colori quanti sono i paesi
palette = sns.color_palette(colors_palette, n_colors=len(above_threshold))

# Aggiungere il colore grigio per "Other (<2%)"
colors = list(palette) + ['lightgray']  # Ultima fetta "Other (<2%)" in grigio

# Create a pie chart
plt.figure(figsize=(10, 8))
pie_data.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=colors, fontsize=14)

# Customize the chart
plt.title('Attack distribution based on the affected sector', fontsize=16)
plt.ylabel('')  # Remove Y-axis label
plt.tight_layout()

# Show the chart
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


# Aggiungi un colore personalizzato per la categoria 'Other' (lightgray)
colors = ['lightgray' if col == 'Other' else sns.color_palette(colors_palette)[i] for i, col in enumerate(processed_data.columns)]

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

