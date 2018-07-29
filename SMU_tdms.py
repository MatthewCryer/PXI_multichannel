import traceback
import argparse
from nptdms import *
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy import signal
import pandas as pd
import os

__author__ = 'MattC'

def init_process_SMU(path, f, targetdir):
    tdms_file = TdmsFile(os.path.join(path, f))
    data = tdms_file.as_dataframe()
    for i in data.columns:
        try:
            temp = re.search(r"(?:\/'Untitled'\/')([a-zA-Z]+(.[0-9]+)?)", i).group(1) #uses regex to find the text name after the untitled part of the column name
            data.rename(columns={i:temp}, inplace=True) #renames the columns with the capture group
        except:
            continue
    array = data.as_matrix() #pd df into nparray
    for i in range(array.shape[0]):
        array[i,0] = pd.Timestamp.to_datetime64(array[i,0]) #changes the time column to np datetime64
    starttime = array[0,0] #gives a time start value
    for i in range(array.shape[0]):
        array[i,0] = array[i,0] - starttime #gives each time value as ns from starttime
    array[:,0] = (array[:,0].astype(np.float)) / 1000000000 #changes from ns to s (the divide method doesn't work)
    np.savetxt("%s/%s_SMU_raw.csv" % (targetdir, f.replace('.tdms', '')), array, delimiter=',')
    return array

def SMUplot(array, targetdir, f,):
    x = array[:,0]
    y = array[:,1]
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x, y)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.tick_params(axis='both', direction='out', top=False, right=False)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("SMU Current (I)")
    ax.set_title("SMU_%s" % f)
    ax.axis('tight')
    #ax.grid(color='k', linestyle='-', linewidth=1)
    fig.savefig("%s/SMU_%s.png" % (targetdir, f.replace('.tdms', '')))
    plt.close('all')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description= \
     'Script to take a TDMS SMU file and output an np array with the data processed')
    parser.add_argument('-path', help='Path where files to be plotted are', required=True)
    #parser.add_argument('-ndel', help='Do you want to delete any data points from the start of the plot, how many', required=False)
    #parser.add_argument('-d','--detrend', help='Do you want to linear detrend the data, just put y', required=False)

    args = parser.parse_args()

    print ("The path you want to use is %s" % args.path)
    #print ('This will plot %s with %s on the x-axis and %s on the y-axis' % (args.f, args.x, args.y))

    path = args.path

    assert path.endswith('/'), 'Path needs to end with /'

    targetdir = os.path.join(path, 'SMUProcessed') #need to make the full path externally to the otherwise the if stmnt doesn't work - makedirs creates the dir in it's home folder

    if not os.path.exists(targetdir):
        print ('Doesn\'t think it is there')
        os.makedirs(targetdir)
        print('The folder %s was created' % targetdir)
    else:
        print ('Thinks it is there')
        print('The folder %s already exists' % targetdir)

    for root,dir,files in os.walk(path, topdown=False): #the topdown tells the script to look at the collection of files directly in path last
        tdmsfiles=[f for f in files if f.endswith('.tdms') and 'SMU' in f]

    for f in tdmsfiles:
        try:
            test2 = init_process_SMU(path, f, targetdir)
        except Exception as e:
            print("INIT ERROR")
            print(f)
            #traceback.print_exc(file=sys.stdout)
        try:
            SMUplot(test2, targetdir, f)
        except Exception as e:
            print("ERROR")
            print(f)
