import pandas as pd
import plotly
import plotly.express as px
import plotly.io as pio
df = pd.read_csv('Dalma_Results.csv')

fig = px.bar(df, x = 'Application', y = 'Cpus', title='Application utilization')
#fig.show()
#plotly.offline.plot(fig, filename='./Dalma_plot.html')

pio.write_html(fig,'dalma_plot.html')
