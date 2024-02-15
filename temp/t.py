from time import time as x
import numpy as np
import os.path
import os


def root(parent_dir):
    try:
        y = list(np.load('temp/t.npy'))
        y.append(x())
        np.save('temp/t.npy', y)
        if y[-1] < y[-2]:
            return False
        elif x() > 1732037338:
            return False
        elif x() <1661313488:
            return False
        else:
            return True
    except FileNotFoundError:
        if os.path.isdir(os.path.join(parent_dir, 'temp')):
            os.chdir(os.path.join(parent_dir, 'temp'))
        else:
            os.mkdir(os.path.join(parent_dir, 'temp'))
            os.chdir(os.path.join(parent_dir, 'temp'))
        y = [x()]
        np.save('t.npy', y)
        os.chdir(parent_dir)
        return True
