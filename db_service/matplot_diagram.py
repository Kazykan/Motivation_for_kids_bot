import numpy as np
import matplotlib.pyplot as plt


def get_diagram_image(vals, labels, child_id):
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot()
    ax.pie(vals, labels=labels, shadow=True, wedgeprops=dict(width=0.6),
        autopct=lambda p:f'{p*sum(vals)/100 :.0f} ₽')
    plt.savefig(f'{child_id}.png', bbox_inches='tight')
    # plt.show()


# vals = [10, 40]
# labels = ['Toyota', 'BMW', 'Lexus', 'Audi', 'Lada']
# vals = [10, 40, 23, 30, 7]
# labels = ['Toyota', 'BMW']