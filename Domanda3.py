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
plt.title('Top 20 ransomware gang più attive in base al numero di vittime', fontsize=16)
plt.xlabel('Ransomware Gang', fontsize=14)
plt.ylabel('Numero di vittime uniche', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Mostrare il grafico
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

# Filtrare le gang con percentuale > 80% su Victim Country: USA e > 50% su un'altra singola Victim Country
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

#una sola palette non è sufficiente per rappresentare tutti
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
plt.title('Ransomware Gang che colpiscono principalmente un settore (>40%)', fontsize=16)
plt.xlabel('Ransomware Gang', fontsize=14)
plt.ylabel('Percentuale di attacchi', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.legend(title='Settore', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Salvataggio del grafico
plt.show()
