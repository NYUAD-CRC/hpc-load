import pandas as pd
import plotly
import plotly.express as px

df = pd.read_csv('Jubail_Results.csv')

fig = px.bar(df, x = 'Application', y = 'Cpus', title='Application utilization')
fig.show()
plotly.offline.plot(fig, filename='./Jubail_plot.html')
