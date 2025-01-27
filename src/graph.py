import pandas as pd

import matplotlib.pyplot as plt

# Load the CSV into a DataFrame
df = pd.read_csv('data.csv', header=[0, 1], index_col=0)
print(f"Loaded data from CSV: {df.head()}")
# Plot each symbol in the DataFrame
for symbol in df.columns.levels[0]:
    print(df[symbol]['price'][2:])
    to_plot = pd.to_numeric(df[symbol]['price'], errors='coerce')
    #to_plot = df[symbol]['price'].replace(symbol, '0', regex=True).replace('price', '0', regex=True).astype(float)
    to_plot.plot(title=symbol)
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend(df[symbol].columns, loc='best')
    plt.xticks(rotation=45)
    plt.tight_layout(pad=2.0)
    plt.show()