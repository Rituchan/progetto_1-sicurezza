import pandas as pd
import matplotlib.pyplot as plt

# Caricamento dei dati
file_path = 'Dataset.csv'  # Assicurati che il file si trovi nella stessa directory dello script
data = pd.read_csv(file_path, delimiter=';')

# Pulizia dei dati: rimuovere eventuali valori nulli nella colonna "Victim sectors"
data = data.dropna(subset=['Victim sectors', 'gang'])

# Conteggio delle occorrenze per "Victim sectors"
country_counts = data['Victim sectors'].value_counts()

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
plt.title('Distribuzione Percentuale Victim sectors', fontsize=16)
plt.ylabel('')  # Rimuovere etichetta dell'asse Y
plt.tight_layout()

# Salvataggio del grafico
#plt.savefig('victim_country_piechart_with_other.png')
plt.show()

#######################################################################
# Conteggio delle occorrenze per Gang e Victim sectors
grouped_data = data.groupby(['gang', 'Victim sectors']).size().unstack(fill_value=0)

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

# Rimuovere le colonne con occorrenze inferiori al 5%
filtered_gangs = filtered_gangs.drop(columns=columns_to_group)

# Assicurarsi che la somma delle percentuali sia 100% per ogni gang
filtered_gangs = filtered_gangs.div(filtered_gangs.sum(axis=1), axis=0) * 100

# Ordinare i dati filtrati per la percentuale massima
processed_data = filtered_gangs.loc[filtered_gangs.max(axis=1).sort_values(ascending=False).index]

# Plot dei dati filtrati
plt.figure(figsize=(14, 10))
processed_data.plot(
    kind='bar', stacked=True, colormap='tab20', figsize=(14, 8)
)

# Personalizzazione del grafico
plt.title('Top 20 Gang con le maggiori occorrenze', fontsize=16)
plt.xlabel('Gang', fontsize=14)
plt.ylabel('Percentuale di occorrenze', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.legend(title='Victim sectors', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Salvataggio del grafico
# plt.savefig('top_20_gangs.png')
plt.show()

