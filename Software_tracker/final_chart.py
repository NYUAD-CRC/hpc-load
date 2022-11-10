import numpy as np
import matplotlib.pyplot as plt

apps=np.loadtxt("Apps.csv",dtype="str")
print(apps)

dalma=np.loadtxt("dalma_apps_final",dtype="int")
print(dalma)

jubail=np.loadtxt("jubail_apps_final",dtype="int")
print(jubail)

# plot bars in stack manner
plt.bar(apps, dalma, color='r')
plt.bar(apps, jubail, bottom=dalma, color='b')
plt.xlabel("Application")
plt.ylabel("Processes")
plt.legend(["Dalma", "Jubail"])
plt.title("Application utilization")
plt.show()
