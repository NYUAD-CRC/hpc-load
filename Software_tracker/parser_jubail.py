import pandas as pd
import plotly
import plotly.express as px
import plotly.io as pio

df = pd.read_csv('Jubail_Results.csv')

fig = px.bar(df, x = 'Application', y = 'Processes', title='Application utilization')
#fig.show()
#plotly.offline.plot(fig, filename='./Jubail_plot.html')
pio.write_html(fig,'jubail_plot_2.html')

