import plotly.express as px
import pandas as pd
import plotly.io as pio
import numpy as np
import matplotlib.pyplot as plt

# Reading applications' names and change it to a list
apps=np.loadtxt("Final_apps",dtype="str")
apps_list=list(apps)

# Reading dalma' results and change it to a list
dalma=np.loadtxt("dalma_apps_final",dtype="int")
dalma_list=list(dalma)

# Reading jubail' results and change it to a list
jubail=np.loadtxt("jubail_apps_final",dtype="int")
jubail_list=list(jubail)

# Getting number of applications 
length=len(apps_list)

# Creating empty list for accumulation
Biglist = []

# Creating list with format [[dalma_result_for_first_app,jubail_result_for_first_app],[dalma_result_for_second_app,jubail_result_for_second_app] and so on till yje end]
for i in range(length):
    List = []
    List.append(dalma_list[i])
    List.append(jubail_list[i])
    Biglist.append(List)
   
# The comparison criteria
types = ["Dalma", "jubail"]

# Creating a stacked chart
fig=px.bar(
    pd.DataFrame(Biglist, columns=types, index=apps_list).reset_index().melt(id_vars="index"),
    x="index",
    y="value",
    color="variable",
)

# Updating axeses names
fig.update_xaxes(title_text="Application")
fig.update_yaxes(title_text="Processes")

#Writing the utput to html
pio.write_html(fig,'accumulated_chart.html')
