import os, sys
import numpy as np
from subprocess import Popen, PIPE
import subprocess, shlex
from time import gmtime, strftime
import math
import multiprocessing as mp
import argparse
import copy
from shutil import copyfile
from distutils.dir_util import copy_tree
import time
# from numba import njit, jit
from string import ascii_uppercase
from pathlib import Path
import re
import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
import matplotlib.patches as patches


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



parser = argparse.ArgumentParser(description='Converts CG representation into atomistic', epilog='Enjoy the program and best of luck!', allow_abbrev=True)
parser.add_argument('-in1', help='input location 1',metavar='pdb/gro',type=str)
parser.add_argument('-in2', help='input location 2',metavar='fragments folder',type=str, default='')
parser.add_argument('-in3', help='input location 2',metavar='fragments folder',type=str, default='')
parser.add_argument('-f', help='file name',metavar='dist_r',type=str, default='')
args = parser.parse_args()
options = vars(args)




in1=[]
for repeat in range(1, 4):

    with open(args.in1+'/'+args.f+str(repeat), 'r') as xvg_input:
        for line_nr, line in enumerate(xvg_input.readlines()):
            if len(line) > 0:
                if line[0] not in ['@','#']:
                    in1.append(float(line.split()[1])*10)
mean1=np.mean(in1, axis=0)

in2=[]
for repeat in range(1, 4):
    with open(args.in2+'/'+args.f+str(repeat), 'r') as xvg_input:
        for line_nr, line in enumerate(xvg_input.readlines()):
            if len(line) > 0:
                if line[0] not in ['@','#']:
                    in2.append(float(line.split()[1])*10)

if len(args.in3) > 0:
    in3=[]
    for repeat in range(1, 4):
        with open(args.in3+'/'+args.f+str(repeat), 'r') as xvg_input:
            for line_nr, line in enumerate(xvg_input.readlines()):
                if len(line) > 0:
                    if line[0] not in ['@','#']:
                        in3.append(float(line.split()[1])*10)




yl=0.6
ylsd=0.04
yls=0.05
plt.figure(1, figsize=(15,15))

# plt.title('Ca distance: resid 187-237',  fontproperties=font1, fontsize=30,y=1.025)
print(max(in1)-min(in1), max(in2)-min(in2))
plt.subplot(3,1,1)
weights = np.ones_like(in1)/float(len(in1))
plt.hist(in1, bins=int((max(in1)-min(in1))/0.25), weights=weights, density=False, orientation="vertical", color='red', alpha=0.3,label='apo')
print('apo',np.mean(in1), np.std(in1))
weights = np.ones_like(in2)/float(len(in2))
plt.hist(in2, bins=int((max(in2)-min(in2))/0.25), weights=weights, density=False, orientation="vertical", color='blue', alpha=0.3,label='udp2')
print('udp',np.mean(in2), np.std(in2))
if len(args.in3) > 0:
    weights = np.ones_like(in3)/float(len(in3))
    plt.hist(in3, bins=int((max(in3)-min(in3))/0.25), weights=weights, density=False, orientation="vertical", color='black', alpha=0.3,label='udp2 + KDO-LipidA')
    print('ramp',np.mean(in3), np.std(in3))
# plt.axvline(0.433,ymin=-10, ymax=210, linewidth=2,color='k') # LHUHBU
# plt.axvline(2.248,ymin=-10, ymax=210, linewidth=2,color='k') # EH
plt.axvline(19.90975,ymin=-10, ymax=210, linewidth=4,color='k') # LHBU

# plt.axvline(2.071587,ymin=-10, ymax=210, linewidth=2,color='k') # UH
plt.xticks(np.arange(0, max(in1)+10,5), fontproperties=font1,  fontsize=30)#
plt.yticks(np.arange(0, 40.01,yls), fontproperties=font1,  fontsize=30)#
plt.ylim(0,0.1)
# plt.xlim(2.5, 4)
plt.xlim(14, 31)
# plt.xlim(00, 1)
plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False)
plt.xlabel('Distance (nm)', fontproperties=font2,fontsize=30)
# plt.xlabel('Angle (r)', fontproperties=font2,fontsize=30)
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0.,  fontsize=20)




# plt.subplot(3,1,2)
# plt.plot(diff, color='black',linewidth=4, label='average')

# plt.xticks(np.arange(0, len(diff)+50,xtick_int), fontproperties=font1,  fontsize=30)#
# plt.yticks(np.arange(-1.12, 1.126,ylsd), fontproperties=font1,  fontsize=30)#
# plt.ylim(-0.12,0.12)
# plt.xlim(0-xtick_int, np.round(len(diff), -1)+xtick_int-0.1)
# # if i+1 != len(chain_sep):
# #   plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False,labelbottom=False)
# # else:
# plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False)

# plt.ylabel('RMSF difference(nm)', fontproperties=font2,fontsize=30) 
# # plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0.,  fontsize=20)

# plt.xlabel('Residue', fontproperties=font2,fontsize=30) 
plt.subplots_adjust( top=0.9, bottom=0.12, left=0.15,right=0.981, wspace=0.3, hspace=0.1)

# plt.savefig('dist_EHBU.png', dpi=300)
# plt.savefig('dist_UHBU.png', dpi=300)
# plt.savefig('angle_LHUHBU.png', dpi=300)
plt.savefig('dist_LHBU.png', dpi=300)
plt.show()
