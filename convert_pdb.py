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

##### 
# reads in 2 column file and adds 2nd column to pdb beta factor column

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



parser = argparse.ArgumentParser(description='Converts CG representation into atomistic', epilog='Enjoy the program and best of luck!', allow_abbrev=True)
parser.add_argument('-c', help='coarse grain coordinates',metavar='pdb/gro',type=str)
parser.add_argument('-name', help='additional fragment library location',metavar='fragments folder',type=str, default='')
parser.add_argument('-reset', help='resets residue numbers', action='store_true')
args = parser.parse_args()
options = vars(args)


def pdbatom(line):
### get information from pdb file
### atom number, atom name, residue name,chain, resid,  x, y, z, backbone (for fragment), connect(for fragment)
    try:
        return dict([('atom_number',str(line[7:11]).replace(" ", "")),('atom_name',str(line[12:16]).replace(" ", "")),('residue_name',str(line[17:21]).replace(" ", "")),('chain',line[21]),('residue_id',int(line[22:26])), ('x',float(line[30:38])),('y',float(line[38:46])),('z',float(line[46:54])), ('backbone',int(float(line[56:60]))),('connect',int(float(line[60:67])))])
    except:
        sys.exit('\npdb line is wrong:\t'+line) 

def create_pdb(file_name):
    pdb_output = open(file_name, 'w')
    pdb_output.write('REMARK    GENERATED BY sys_setup_script\nTITLE     SELF-ASSEMBLY-MAYBE\nREMARK    Good luck\n\
'+box_vec+'MODEL        1\n')
    return pdb_output

def ave(a, n) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

atoms={}
with open(args.c, 'r') as pdb_input:
    resid_prev = -1
    for line_nr, line in enumerate(pdb_input.readlines()):
        if line.startswith('CRYST'): ### collects box vectors from pdb
            box_vec=line
        if line.startswith('ATOM'):
            line_sep = pdbatom(line)
            if line_sep['residue_id'] != resid_prev:
                if 'resid' not in locals():
                    resid = 0
                else:
                    resid +=1
                atoms[resid]={}
                resid_prev=line_sep['residue_id']
            atoms[resid][line_sep['atom_number']]=line_sep
# all_xvgs=np.array([])
xvg=[]
for repeat in range(1, 4):
    xvg.append([])
    with open(args.name+'rmsf-r'+str(repeat)+'.xvg', 'r') as xvg_input:
        for line_nr, line in enumerate(xvg_input.readlines()):
            if len(line) > 0:
                if line[0] not in ['@','#']:
                    xvg[repeat-1].append(float(line.split()[1]))
mean=np.mean(xvg, axis=0)

rmsd, time=[],[]
for repeat in range(1, 4):
    rmsd.append([])
    time.append([])
    with open(args.name+'rmsd-r'+str(repeat)+'.xvg', 'r') as xvg_input:
        for line_nr, line in enumerate(xvg_input.readlines()):
            if len(line) > 0:
                if line[0] not in ['@','#']:
                    time[repeat-1].append(float(line.split()[0])/1000)
                    rmsd[repeat-1].append(float(line.split()[1]))
rmsd_mean=np.mean(rmsd, axis=0)
time_mean=np.mean(time, axis=0)


pdb_output = create_pdb(args.name+'rmsf_mean.pdb')
pdbline = "ATOM  %5d %4s %4s%1s%4d    %8.3f%8.3f%8.3f%6.2f%6.2f"
chain_sep=[[]]
residue_id=[[]]
resid_counter = 0
for resid, residue in enumerate(atoms):
    for at in atoms[residue]:
        pdb_output.write(pdbline%((int(at),atoms[residue][at]['atom_name'],atoms[residue][at]['residue_name'],' ',atoms[residue][at]['residue_id'],\
atoms[residue][at]['x'],atoms[residue][at]['y'],atoms[residue][at]['z'],1,mean[resid]))+'\n')

    if 'prev_residue' in globals():
        if atoms[residue][at]['residue_id'] != prev_residue+1:
            chain_sep.append([])
            residue_id.append([])
    chain_sep[-1].append(mean[resid])
    if args.reset:
        residue_id[-1].append(resid_counter)
        resid_counter += 1
    else:
        residue_id[-1].append(atoms[residue][at]['residue_id'])
    prev_residue=atoms[residue][at]['residue_id']



yl=0.6
yls=0.2
plt.figure(1, figsize=(15,15))
plt.title('WaaL apo',  fontproperties=font1, fontsize=30,y=1.1)
for i in range(len(chain_sep)):
    if np.round(max(residue_id[i])) < 25:
        xtick_int = 5 
    elif np.round(max(residue_id[i])) < 100:
        xtick_int = 25
    else:
        xtick_int = 50
    plt.subplot(3,1,1)
    plt.plot(residue_id[i], xvg[0], color='green',linewidth=2, alpha=0.6, label='repeat 1')
    plt.plot(residue_id[i], xvg[1], color='blue',linewidth=2, alpha=0.6, label='repeat 2')
    plt.plot(residue_id[i], xvg[2], color='red',linewidth=2, alpha=0.6, label='repeat 3')
    plt.plot(residue_id[i], chain_sep[i], color='black',linewidth=4, label='average')
    if np.round(min(residue_id[i]), -2) == 0 :
        min_resid = 0
    else:
        min_resid = np.round(min(residue_id[i]), -2)-25
    if i+1 != 1:
        plt.xticks(np.arange(min_resid, np.round(max(residue_id[i]), -2)+50,xtick_int), fontproperties=font1,  fontsize=30)#
    else:
        plt.xticks(np.arange(min_resid, np.round(max(residue_id[i]), -2)+50,xtick_int), fontproperties=font1,  fontsize=30)#

    plt.yticks(np.arange(0, 1.21,yls), fontproperties=font1,  fontsize=30)#
    plt.ylim(0,yl)
    plt.xlim(np.round(min(residue_id[i]), -1)-xtick_int, np.round(max(residue_id[i]), -1)+xtick_int-0.1)
    # if i+1 != len(chain_sep):
    #   plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False,labelbottom=False)
    # else:
    plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False)

    plt.ylabel('RMSF (nm)', fontproperties=font2,fontsize=30) 
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0.,  fontsize=20)

plt.xlabel('Residue', fontproperties=font2,fontsize=30) 

# plt.subplots_adjust( top=0.968, bottom=0.12, left=0.1,right=0.991, wspace=0.2, hspace=0.2)

# plt.savefig('rmsf.png', dpi=300)
# plt.show()


# plt.figure(2, figsize=(15,15))
for i in range(len(chain_sep)):
    plt.subplot(3,1,2)
    if np.round(max(time_mean)) < 25:
        xtick_int = 5 
    elif np.round(max(time_mean)) < 100:
        xtick_int = 25
    else:
        xtick_int = 50
    plt.plot(ave(time_mean, 10), ave(rmsd[0],10), color='green',linewidth=2, alpha=0.6)
    plt.plot(ave(time_mean, 10), ave(rmsd[1],10), color='blue',linewidth=2, alpha=0.6)
    plt.plot(ave(time_mean, 10), ave(rmsd[2],10), color='red',linewidth=2, alpha=0.6)
    plt.plot(ave(time_mean, 10), ave(rmsd_mean,10), color='black',linewidth=4)
    if i+1 != 1:
        plt.xticks(np.arange(0, np.round(np.max(ave(time_mean, 10)), -2)+50,xtick_int), fontproperties=font1,  fontsize=30)#
    else:
        plt.xticks(np.arange(0, np.round(np.max(ave(time_mean, 10)), -2)+50,xtick_int), fontproperties=font1,  fontsize=30)#

    plt.yticks(np.arange(0, 1.21,yls), fontproperties=font1,  fontsize=30)#
    plt.ylim(0,yl)
    plt.xlim(np.round(min(time_mean), -1)-10, np.round(max(time_mean), -1)+10)
    # if i+1 != len(chain_sep):
    #   plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False,labelbottom=False)
    # else:
    plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False)

    plt.ylabel('RMSD (nm)', fontproperties=font2,fontsize=30) 
plt.xlabel('time (ns)', fontproperties=font2,fontsize=30) 

plt.subplots_adjust( top=0.9, bottom=0.12, left=0.1,right=0.991, wspace=0.3, hspace=0.3)

plt.savefig(args.name+'convergence.png', dpi=300)



plt.figure(2, figsize=(15,15))
plt.title('WaaL apo',  fontproperties=font1, fontsize=30,y=1)
for i in range(len(chain_sep)):
    if np.round(max(residue_id[i])) < 25:
        xtick_int = 5 
    elif np.round(max(residue_id[i])) < 50:
        xtick_int = 25
    else:
        xtick_int = 50
    plt.subplot(3,1,i+1)
    plt.plot(residue_id[i], chain_sep[i], color='black',linewidth=4)
    if np.round(min(residue_id[i]), -2) == 0 :
        min_resid = 0
    else:
        min_resid = np.round(min(residue_id[i]), -2)-25
    if i+1 != 1:
        plt.xticks(np.arange(min_resid, np.round(max(residue_id[i]), -2)+50,xtick_int), fontproperties=font1,  fontsize=30)#
    else:
        plt.xticks(np.arange(min_resid, np.round(max(residue_id[i]), -2)+50,xtick_int), fontproperties=font1,  fontsize=30)#

    plt.yticks(np.arange(0, 1.21,yls), fontproperties=font1,  fontsize=30)#

    plt.ylim(0,yl)
    plt.xlim(np.round(min(residue_id[i]), -1)-xtick_int, np.round(max(residue_id[i]), -1)+xtick_int-0.1)
    # if i+1 != len(chain_sep):
    #   plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False,labelbottom=False)
    # else:
    plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False)

    plt.ylabel('RMSF (nm)', fontproperties=font2,fontsize=30) 

plt.xlabel('Residue', fontproperties=font2,fontsize=30) 

plt.subplots_adjust( top=0.968, bottom=0.12, left=0.1,right=0.991, wspace=0.2, hspace=0.2)

# plt.savefig('rmsf.png', dpi=300)
# plt.show()


# plt.figure(2, figsize=(15,15))
for i in range(len(chain_sep)):
    plt.subplot(3,1,i+2)
    plt.plot(ave(time_mean, 10), ave(rmsd_mean,10), color='black',linewidth=4)
    if i+1 != 1:
        plt.xticks(np.arange(0, np.round(max(residue_id[i]), -2)+50,25), fontproperties=font1,  fontsize=30)#
    else:
        plt.xticks(np.arange(0, np.round(max(residue_id[i]), -2)+50,50), fontproperties=font1,  fontsize=30)#

    plt.yticks(np.arange(0, 1.21,yls), fontproperties=font1,  fontsize=30)#
    plt.ylim(0,yl)
    plt.xlim(np.round(min(time_mean), -1)-10, np.round(max(time_mean), -1)+10)
    # if i+1 != len(chain_sep):
    #   plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False,labelbottom=False)
    # else:
    plt.tick_params(axis='both', which='major', width=3, length=5, labelsize=30, direction='in', pad=10, right=False, top=False)

    plt.ylabel('RMSD (nm)', fontproperties=font2,fontsize=30) 
plt.xlabel('time (ns)', fontproperties=font2,fontsize=30) 

plt.subplots_adjust( top=0.968, bottom=0.12, left=0.1,right=0.991, wspace=0.3, hspace=0.3)

plt.savefig(args.name+'convergence_mean.png', dpi=300)