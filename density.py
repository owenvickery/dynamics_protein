import os, sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
import matplotlib.patches as patches
import numpy as np


def greater(current, check):
    if check > current:
        return check
    else:
        return current
def less(current, check):
    if check < current:
        return check
    else:
        return current

def get_density(file_name):
    in1=[]
    with open(file_name, 'r') as xvg_input:
        for line_nr, line in enumerate(xvg_input.readlines()):
            if len(line) > 0:
                if line[0] not in ['@','#']:
                    in1.append([float(line.split()[0]),float(line.split()[1])])
    in1 = np.array(in1)
    return in1[:,0], in1[:,1] 

# Fonts

alignment = {'horizontalalignment': 'center', 'verticalalignment': 'baseline'}
families = ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']
styles = ['normal', 'italic', 'oblique']
font = FontProperties()

#  tick fonts
font1 = font.copy()
font1.set_family('sans-serif')
font1.set_style('normal')

# label fonts
font2 = font.copy()
font2.set_family('sans-serif')
font2.set_style('normal')
font2.set_weight('normal')
plt.rcParams['mathtext.default'] = 'regular'
plt.rcParams['axes.linewidth'] = 6
bbox = dict(boxstyle="round", fc="0.8")
cmaps = [('Perceptually Uniform Sequential', [
            'viridis', 'plasma', 'inferno', 'magma']),
         ('Sequential', [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
         ('Sequential (2)', [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']),
         ('Diverging', [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
         ('Qualitative', [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c']),
         ('Miscellaneous', [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar'])]





density = ['system.xvg', 'water.xvg', 'tail_all.xvg', 'chol.xvg', 'head_all.xvg', 'PO4.xvg', 'glycerol_all.xvg']
density = ['system.xvg', 'water.xvg', 'tail_all.xvg', 'chol.xvg', 'head_PO4_glycerol.xvg']#'head_PO4.xvg', 'glycerol_all.xvg']
                  
plt.figure(1, figsize=(15,15))
for i in density:
    x, y = get_density(i)
    plt.plot(x, y, linewidth=4)
    plt.fill_between(x, np.zeros(len(x)), y, alpha= 0.2)
plt.axvline(0,ymin=-10, ymax=2000, linewidth=4, color='k') # LHUHBU

plt.xticks(np.arange(-10, 10, 1), fontproperties=font1,  fontsize=30)#
plt.yticks(np.arange(0, 300,2), fontproperties=font1,  fontsize=30)#
plt.ylim(0,12)
# plt.ylim(0,120)
plt.xlim(-4, 4)
# plt.xlim(3, 7)
# plt.xlabel('Area per lipids (nm$^2$)', fontproperties=font2,fontsize=40)
# plt.ylabel('Frequency', fontproperties=font2,fontsize=40)

# # plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0.,  fontsize=20)
# plt.legend(loc = 'upper left',  fontsize=35)
plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=40, direction='in', pad=20, right=False, top=False)
plt.subplots_adjust(top=0.9, bottom=0.13,left=0.17,right=0.97, hspace=0.2, wspace=0.16)

plt.savefig('complex_density.png', dpi=300)
# plt.show()


