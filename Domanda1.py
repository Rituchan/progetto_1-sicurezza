import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Caricamento dei dati
file_path = 'Dataset.csv'  # Assicurati che il file si trovi nella stessa directory dello script
data = pd.read_csv(file_path, delimiter=';')

# Pulizia dei dati: rimuovere eventuali valori nulli nella colonna "Victim Country"
data = data.dropna(subset=['Victim Country', 'gang'])

# Raggruppamento dei dati per "victim" e selezione dell'ultima occorrenza
unique_victims = data.groupby('victim').last().reset_index()

# Conteggio delle occorrenze per "Victim Country"
country_counts = unique_victims['Victim Country'].value_counts()
country_counts.sort_values(ascending=False).to_csv('1_Attacks_by_country.csv')

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
# Generazione della palette husl con tanti colori quanti sono i paesi
palette = sns.color_palette("deep", n_colors=len(above_threshold))
# Aggiungere il colore grigio per "Other (<2%)"
colors = list(palette) + ['lightgray']  # Ultima fetta "Other (<2%)" in grigio
pie_data.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=colors)

# Personalizzazione del grafico
plt.title('Victim distribution based on their country of residence', fontsize=16)
plt.ylabel('')  # Rimuovere etichetta dell'asse Y
plt.tight_layout()

# Salvataggio del grafico
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
