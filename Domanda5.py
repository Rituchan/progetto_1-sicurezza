import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import seaborn as sns


# Funzione per convertire i valori nella colonna 'NumberN/AofN/Aemployees'
def parse_employee_count(value):
    """
    Convertire i valori non numerici in numeri utilizzando simboli di confronto e medie per i range.
    """
    try:
        # Range: prendi il valore medio
        if '-' in value:
            start, end = map(float, value.split('-'))
            return (start + end) / 2
        # Simboli di confronto: restituisci il limite -1
        elif '<' in value:
            return float(value.replace('<', '').replace('K', '000').replace('M', '000000')) - 1
        elif '>' in value:
            return float(value.replace('>', '').replace('K', '000').replace('M', '000000')) + 1
        # Valori numerici validi
        elif value.replace('.', '').isdigit():
            return float(value)
        # Valori mal formattati
        else:
            return np.nan
    except:
        return np.nan

# Caricare i dati dal file CSV
file_path = 'Dataset.csv'
data = pd.read_csv(file_path, delimiter=';')

# Applicare la funzione di parsing
data['ParsedEmployees'] = data['NumberN/AofN/Aemployees'].apply(lambda x: parse_employee_count(str(x)))
valid_counts = data['ParsedEmployees'].dropna()

# Step 2: Remove values containing "N/A"
sales_column = data['Sales']
cleaned_sales = sales_column[~sales_column.str.contains('N/A', na=False)]

# Step 3: Remove spaces before or after "M" and "B"
cleaned_sales = cleaned_sales.str.replace(r'\s*([MB])\s*$', r'\1', regex=True)

# Step 4: Convert non-dollar units (€ and £) to dollars using generic exchange rates
def convert_to_dollars(value):
    if isinstance(value, str):
        if '€' in value:
            return value.replace('€', '').strip() + ' * 1.1'
        elif '£' in value:
            return value.replace('£', '').strip() + ' * 1.3'
    return value

converted_sales = cleaned_sales.apply(convert_to_dollars)

# Step 5: Replace commas with dots
converted_sales = converted_sales.str.replace(',', '.', regex=False)

# Step 6: Handle ranges by computing the average
def handle_ranges(value):
    if isinstance(value, str) and '-' in value:
        try:
            low, high = map(lambda x: float(x.replace('$', '').replace('m', '').replace('M', '').replace('B', '')), value.split('-'))
            return f"${np.mean([low, high]):.2f}M"
        except ValueError:
            return value
    return value

handled_sales = converted_sales.apply(handle_ranges)

# Step 7: Remove the "<" symbol
def adjust_less_than(value):
    if isinstance(value, str) and '<' in value:
        try:
            numeric_value = float(value.replace('<', '').replace('$', '').replace('M', '').replace('B', ''))
            return f"${numeric_value - 1:.2f}M"
        except ValueError:
            return value
    return value

handled_sales = handled_sales.apply(adjust_less_than)

# Step 8: Discard values not ending in "m", "M", or "B"
final_sales = handled_sales[handled_sales.str.endswith(('m', 'M', 'B'), na=False)]

def convert_to_numeric(value):
    if value.endswith('m'):
        return float(value.replace('$', '').replace('m', '')) / 1000  # Convert to millions
    elif value.endswith('M'):
        return float(value.replace('$', '').replace('M', ''))  # Already in millions
    elif value.endswith('B'):
        return float(value.replace('$', '').replace('B', '')) * 1000  # Convert to millions
    return None

sales_numeric = final_sales.apply(convert_to_numeric).dropna()

# Configurazione dei dati per il primo istogramma
# Raggruppiamo il numero di dipendenti
group_limits = [0, 25, 90, 200, 1000, 10000, 1500000]
group_labels = [f'{group_limits[i]}-{group_limits[i+1]}' for i in range(len(group_limits) - 1)]
data['Group'] = pd.cut(valid_counts, bins=group_limits, labels=group_labels, include_lowest=True)
group_counts = data['Group'].value_counts().sort_index()
group_counts.to_csv('5_Attacks_by_employees.csv', header=['Number of Attacks'], index_label='# Employees')

# Configurazione dei dati per il secondo istogramma
# Raggruppiamo le vendite
group_limits2 = [0, 10, 30, 100, 500, 1000, 501000]
group_labels2 = [f'{group_limits2[i]}-{group_limits2[i+1]}' for i in range(len(group_limits2) - 1)]
data['Group2'] = pd.cut(sales_numeric, bins=group_limits2, labels=group_labels2, include_lowest=True)
group_counts2 = data['Group2'].value_counts().sort_index()
group_counts2.to_csv('5_Attacks_by_revenue.csv', header=['Number of Attacks'], index_label='Revenue (in millions)')

# Creazione della figura con due sottotrame
fig, axes = plt.subplots(2, 1, figsize=(12, 12))

# Primo istogramma: distribuzione del numero di dipendenti (orizzontale)
bars1 = axes[0].barh(group_labels, group_counts, color='purple', alpha=0.7, edgecolor='black')
axes[0].set_title('Distribution of attacks based on the number of employees', fontsize=14)
axes[0].set_xlabel('# Attacks', fontsize=12)
axes[0].set_ylabel('Number of employees', fontsize=12)
axes[0].grid(axis='x', linestyle='--', alpha=0.7)
for bar in bars1:
    width = bar.get_width()
    axes[0].text(width, bar.get_y() + bar.get_height() / 2, f'{int(width)}', ha='left', va='center', fontsize=10)

# Secondo istogramma: distribuzione delle vendite (orizzontale)
bars2 = axes[1].barh(group_labels2, group_counts2, color='green', alpha=0.7, edgecolor='black')
axes[1].set_title('Distribution of attacks based on revenue', fontsize=14)
axes[1].set_xlabel('# Attacks', fontsize=12)
axes[1].set_ylabel('Revenue (in millions)', fontsize=12)
axes[1].grid(axis='x', linestyle='--', alpha=0.7)
for bar in bars2:
    width = bar.get_width()
    axes[1].text(width, bar.get_y() + bar.get_height() / 2, f'{int(width)}', ha='left', va='center', fontsize=10)

# Adattiamo il layout
plt.tight_layout()
plt.show()

#######################################################################################

# Filtra le top 10 gang in base al numero di occorrenze
top_gangs = data['gang'].value_counts().nlargest(10).index
filtered_data = data[data['gang'].isin(top_gangs)]

# Filtra i dati con "Unknown" eliminati per Victim Country e Victim sectors
filtered_data = filtered_data[
    (filtered_data['Victim Country'] != 'Unknown') &
    (filtered_data['Victim sectors'] != 'Unknown')
]

# Combina Victim Country e Victim sectors per creare i segmenti
filtered_data['segment'] = filtered_data['Victim Country'] + ' - ' + filtered_data['Victim sectors']

# Conta le occorrenze per ogni gang e segmento
segment_counts = filtered_data.groupby(['gang', 'segment']).size().reset_index(name='counts')

# Determina la soglia per la categoria "other" (0.2%)
total_counts = segment_counts['counts'].sum()
threshold = total_counts * 0.0015

# Raggruppa i segmenti con occorrenze minori della soglia in "other"
segment_counts['segment'] = segment_counts.apply(
    lambda x: 'Other' if x['counts'] < threshold else x['segment'], axis=1
)

# Riconta i dati dopo il raggruppamento e ordina la categoria "Other" in fondo
final_counts = segment_counts.groupby(['gang', 'segment'])['counts'].sum().unstack(fill_value=0)
if 'Other' in final_counts.columns:
    other_column = final_counts.pop('Other')
    final_counts['Other'] = other_column

# Ordina le gang in base al totale decrescente delle occorrenze
final_counts = final_counts.loc[final_counts.sum(axis=1).sort_values(ascending=False).index]

#una sola palette non è sufficiente per rappresentare tutti
colors_palette = (sns.color_palette("deep") + sns.color_palette("pastel") + sns.color_palette("bright") +
                 sns.color_palette("dark") + sns.color_palette("colorblind"))# Generazione della palette husl con tanti colori quanti sono i paesi
palette = sns.color_palette(colors_palette)

# Aggiungi un colore personalizzato per la categoria 'Other' (lightgray)
colors = ['lightgray' if col == 'Other' else sns.color_palette(colors_palette)[i] for i, col in enumerate(final_counts.columns)]

# Plot dei dati filtrati
fig, ax = plt.subplots(figsize=(14, 8))

bars = final_counts.plot(
    kind='bar', stacked=True, color=colors, ax=ax
)

# Aggiunta delle percentuali sulle barre
for container in bars.containers:
    for bar in container:
        height = bar.get_height()
        if height > 50:  # Mostra solo valori significativi
            ax.annotate(f'{height:.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + height / 2),
                        ha='center', va='center', fontsize=9, color='black')

# Configurazione del grafico
plt.title('Distribution of attacks of the 10 most active Ransomware Gangs based on affected countries and sectors')
plt.xlabel('Ransomware Gang')
plt.ylabel('# Attacks')
plt.legend(title='Countries + Sectors', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

#######################################################################################

# Contiamo le occorrenze per la colonna 'gang'
victim_counts = data['victim'].value_counts()

# Filtriamo le gang con più di 500 occorrenze
top_victims = victim_counts[victim_counts > 2]

# Raggruppiamo le vittime in base al numero di attacchi subiti
attack_groups = victim_counts.value_counts().sort_index()

# Calcoliamo le percentuali
total_attacks = victim_counts.sum()
attack_groups_percentage = (attack_groups / total_attacks) * 100

# Creiamo una figura con due sottotrame (subplots)
fig, axes = plt.subplots(2, 1, figsize=(12, 12))

# Primo istogramma: Vittime colpite più di 2 volte
top_victims.plot(kind='barh', color='orange', edgecolor='black', ax=axes[0])
axes[0].set_title('Victims hit more than two times', fontsize=16)
axes[0].set_ylabel('Victims', fontsize=14)
axes[0].set_xlabel('# Attacks Suffered', fontsize=14)
axes[0].xaxis.set_major_locator(MaxNLocator(integer=True))

# Secondo istogramma: Distribuzione delle percentuali
bars = axes[1].bar(attack_groups_percentage.index, attack_groups_percentage, color='steelblue', edgecolor='black')
for bar in bars:
    height = bar.get_height()
    axes[1].text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}%', ha='center', va='bottom', fontsize=10)

axes[1].set_title('Distribution of victims based on the percentage of attacks suffered', fontsize=16)
axes[1].set_xlabel('# Attacks Suffered', fontsize=14)
axes[1].set_ylabel('% Attacks', fontsize=14)
axes[1].xaxis.set_major_locator(MaxNLocator(integer=True))

# Adattiamo i layout per evitare sovrapposizioni
plt.tight_layout()
plt.show()
