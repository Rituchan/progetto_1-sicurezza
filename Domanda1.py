import pandas as pd
import matplotlib.pyplot as plt

# Caricamento dei dati
file_path = 'Dataset.csv'  # Assicurati che il file si trovi nella stessa directory dello script
data = pd.read_csv(file_path, delimiter=';')

# Pulizia dei dati: rimuovere eventuali valori nulli nella colonna "Victim Country"
data = data.dropna(subset=['Victim Country', 'gang'])

# Conteggio delle occorrenze per "Victim Country"
country_counts = data['Victim Country'].value_counts()

# Calcolo delle percentuali
total_count = country_counts.sum()
percentages = (country_counts / total_count) * 100

# Raggruppamento delle occorrenze sotto il 2% in "other"
above_threshold = percentages[percentages >= 2]
below_threshold = percentages[percentages < 2].sum()

# Aggiungere la categoria "other"
pie_data = above_threshold.copy()
pie_data['Other (<2%)'] = below_threshold

# Creazione del grafico a torta
plt.figure(figsize=(10, 8))
pie_data.plot(kind='pie', autopct='%1.1f%%', startangle=90, colormap='tab20')

# Personalizzazione del grafico
plt.title('Distribuzione Percentuale Victim Country', fontsize=16)
plt.ylabel('')  # Rimuovere etichetta dell'asse Y
plt.tight_layout()

# Salvataggio del grafico
#plt.savefig('victim_country_piechart_with_other.png')
plt.show()

#######################################################################

# Conteggio delle occorrenze per Gang e Victim Country
grouped_data = data.groupby(['gang', 'Victim Country']).size().unstack(fill_value=0)

# Calcolo delle percentuali
total_occurrences = grouped_data.sum(axis=1)
percentage_data = grouped_data.div(total_occurrences, axis=0) * 100

over_100_gangs = total_occurrences[total_occurrences >= 100].index
gangs_filtered = percentage_data.loc[over_100_gangs]

# Filtrare le gang con percentuale > 65% su Victim Country: USA e > 25% su un'altra singola Victim Country
usa_filter = gangs_filtered['USA'] > 65
other_country_filter = (gangs_filtered.drop(columns=['USA']).max(axis=1) > 25)
filtered_gangs = gangs_filtered[(usa_filter) | (other_country_filter)]


# Aggiungere la categoria "other"
def process_gang(row):
    usa_percentage = row['USA']
    other_countries = row.drop(labels=['USA'])
    top_percentage = other_countries.max()
    if top_percentage < 25:
        other_percentage = 100 - usa_percentage
        return pd.Series({
            'USA': usa_percentage,
            'other': other_percentage
        })
    else :
        top_country = other_countries.idxmax()
        other_percentage = 100 - (usa_percentage + top_percentage)
        return pd.Series({
            'USA': usa_percentage,
            top_country: top_percentage,
            'other': other_percentage
        })


processed_data = filtered_gangs.apply(process_gang, axis=1)

# Ordinare i dati filtrati per la percentuale massima
processed_data = processed_data.loc[processed_data.max(axis=1).sort_values(ascending=False).index]



plt.figure(figsize=(14, 10))
processed_data.plot(
    kind='bar', stacked=True, colormap='Set3',  figsize=(14, 8)
)

# Personalizzazione del grafico
plt.title('Gang con >65% su Victim Country: USA o >25% su un altra Victim Country', fontsize=16)
plt.xlabel('Gang', fontsize=14)
plt.ylabel('Percentuale di occorrenze', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.legend(title='Victim Country', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Salvataggio del grafico
#plt.savefig('gang_filtered_victim_country_histogram.png')
plt.show()