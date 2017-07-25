#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import normal
from scipy.optimize import curve_fit
import argparse

def make_model_function(*args):
    """
    args[0] is the number of the model
    if model==2 or model==4 then args[1] is the initial mass.
    """
    model_num=args[0]
    if model_num==2:
        m0=args[1]
        def f(t, mi, k):
            return (m0-mi)*np.exp(-k*t)+mi

    elif model_num==3:
        def f(t, C1, C2, m0, r1, r2):
            return C1*np.exp(r1*t)+C2*np.exp(r2*t)+m0-C1-C2

    elif model_num==4:
        m0=args[1]
        def f(t, C1, C2, r1, r2):
           return C1*np.exp(r1*t)+C2*np.exp(r2*t)+m0-C1-C2

    else:
        def f(t, m0, mi, k):
            return (m0-mi)*np.exp(-k*t)+mi

    return f

def parse_data(content):
    x_data = np.array([])
    y_data = np.array([])
    for row in content:
        element = row.split() 
        x_data = np.append(x_data, [float(element[0])])
        y_data = np.append(y_data, [float(element[1])])
    return x_data, y_data

def select_fit_points(x_data,y_data,fit_range):
    if fit_range==None: return x_data, y_data
    print "selecting fit points with range: ", fit_range
    r = fit_range.split(':')
    xmin = float(r[0])
    xmax = float(r[1])
    x_selected=np.array([])
    y_selected=np.array([])
    for i, time in enumerate(x_data):
        if xmin <= time and xmax >= time:
            x_selected = np.append(x_selected, [x_data[i]])
            y_selected = np.append(y_selected, [y_data[i]])
    return x_selected, y_selected
            
       
parser = argparse.ArgumentParser(description='Wood evaporated mass estimation')
 
parser.add_argument('-r', '--fit-range', type=str, help='fit range in hours given as min:max')
parser.add_argument('-m', '--model', type=int, help='mathematical model')
parser.add_argument('filename', type=str)

args = parser.parse_args()
filename = args.filename
model_num = args.model
fit_range = args.fit_range

print "model:", model_num

with open(filename) as f:
    content = f.readlines()

x_data, y_data = parse_data(content)
x_data = x_data/60.
m0=y_data[0]
mlast=y_data[-1]

x_selected, y_selected = select_fit_points(x_data,y_data,fit_range)
model=make_model_function(model_num,m0)

if model_num==1: initial = [m0,200.,0.02]
if model_num==2: initial = [200.,0.02]
if model_num==3: initial = [71.4, -24.2, m0, -0.00543, 0.00543]
if model_num==4: initial = [71.4, -24.2, -0.00543, 0.00543]

parameter, covariance_matrix = curve_fit(model, x_selected, y_selected,initial)

if model_num==1:
    m0 = parameter[0]
    mi = parameter[1]
    k  = parameter[2]
    print "m0\tmi\tk\tmlast"
    print m0,"\t",mi,"\t",k,"\t",mlast
if model_num==2:
    mi = parameter[0]
    k  = parameter[1]
    print "m0\tmi\tk\tmlast"
    print m0,"\t",mi,"\t",k,"\t",mlast 
if model_num==3:
    m0 = parameter[2]
    C1 = parameter[0]
    C2 = parameter[1]
    mi = m0-C1-C2
    print "m0\tmi\tmlast"
    print m0,"\t",mi,"\t",mlast 
if model_num==4:
    C1 = parameter[0]
    C2 = parameter[1]
    mi = m0-C1-C2
    print "m0\tmi\tmlast"
    print m0,"\t",mi,"\t",mlast 

evap_final_p = np.round((m0-mi)/mi*100., 1)
evap_final = np.round(m0-mi)
evap_last_p = np.round((mlast-mi)/mi*100., 1)
evap_last = np.round(mlast-mi)

msg = "Total evaporated mass at final state: "
msg += str(evap_final) + "g (" + str(evap_final_p) + "%)\n"
sys.stdout.write(msg)
msg = "Evaporation mass left: "
msg += str(evap_last) + "g (" + str(evap_last_p) + "%)\n"
sys.stdout.write(msg)


x = np.linspace(min(x_data), max(x_data)+2*24., 1000)
plt.plot(x_data, y_data, 'rx', label='data')
plt.plot(x, model(x, *parameter), 'b-', label='fit')  
plt.show()


