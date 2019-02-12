# encoding: utf-8
'''
Created on 2017年7月14日

@author: winston
'''
from collections import OrderedDict
import json
import sys

from matplotlib.animation import FuncAnimation

import matplotlib.pyplot as plt
import numpy as np


d = {"zp__gte": 0.55, "lb30__lt": 0.5, "zp__lt": 0.7, "pct_chg__lt": -9.0}

bprops = OrderedDict(sorted(d.iteritems(), key=lambda x:x[0]))


print bprops

print json.dumps(bprops) 