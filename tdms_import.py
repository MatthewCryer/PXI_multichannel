#!/usr/bin/env python
import traceback
import argparse
import faulthandler
from nptdms import *
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy import signal
import pandas as pd
import os

__author__ = 'MattC'

def init_process(path, f, targetdir):
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
    np.savetxt("%s/%s_pre_processing.csv" % (targetdir, f.replace('.tdms', '')), array, delimiter=',')
    array = np.delete(array, np.s_[0:ndel], 0) # manually deletes the first ndel rows including the header row, uses the np slice function
    if detrend:
        for i in range(1,16): # i.e. doesn't detrend Time
            array[:,i] = signal.detrend(array[:,i])
            print("went into detrend")
    else:
        print ("didn't detrend")
    return array

def medfiltandplot(array, targetdir, f,):
    x = array[:,0]
    for i in range(1, 16):
        yfilt = signal.medfilt(array[:,i], 3)
        array[:,i] = yfilt
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x, yfilt)
        #ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        #ax.tick_params(axis='both', direction='out', top='off', right='off')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Voltage (V)")
        ax.set_title("Channel_%s" % i)
        ax.axis('tight')
        #ax.grid(color='k', linestyle='-', linewidth=1)
        fig.savefig("%s/%schannel%s.png" % (targetdir, f.replace('.tdms', ''), i))
        plt.close('all')
    np.savetxt("%s/%s_processed.csv" % (targetdir, f.replace('.tdms', '')), array, delimiter=',')

def medfiltandplotdevI(array, targetdir, f,):
    x = array[:,0]
    for i in range(1, 16):
        yfilt = signal.medfilt(array[:,i], 3)
        yfilt = yfilt / 5000 # just gets current (which is constant) through bottom 5K res
        array[:,i] = yfilt
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x, yfilt)
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        #ax.tick_params(axis='both', direction='out', top='off', right='off')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Pixel Current (I)")
        ax.set_title("Channel_%s" % i)
        ax.axis('tight')
        #ax.grid(color='k', linestyle='-', linewidth=1)
        fig.savefig("%s/%schannel%s_device_I.png" % (targetdir, f.replace('.tdms', ''), i))
        plt.close('all')
    np.savetxt("%s/%s_processed_device_I.csv" % (targetdir, f.replace('.tdms', '')), array, delimiter=',')
    return array

def medfiltandplotstacked(array, targetdir, f,):
    x = array[:,0]
    fig, axarr = plt.subplots(15, sharex=True, figsize=(9, 16), dpi=120)
    for i in range(1, 16):
        #yfilt = signal.medfilt(array[:,i], 3)
        #yfilt = yfilt / 5000 # just gets current (which is constant) through bottom 5K res
        #array[:,i] = yfilt
        y = array[:,i]
        axarr[i-1].plot(x, y)
        axarr[i-1].set_yticks([])
    # plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    #ax.tick_params(axis='both', direction='out', top='off', right='off')
    plt.xlabel("Time (s)")
    # plt.yticks([])
    axarr[0].set_title("All_Channels_%s" % f)
    plt.axis('tight')
    #ax.grid(color='k', linestyle='-', linewidth=1)
    plt.savefig("%s/%s_stacked_%s_device_I.png" % (targetdir, f.replace('.tdms', ''), i))
    plt.close('all')

def normalisechannel(array): # 15 wanted data channels (ignore time)
    newarray = np.empty(np.shape(array))
    newarray[:,0] = array[:,0]
    for i in range(1,17):#just do all
        minval = np.min(array[:,[i]])
        newarray[:,[i]] = array[:,[i]] + (minval*1.001) #to remove divide by zero problem and works if are -ve vals following detrend
        #array[:,[i]] = array[:,[i]] - (minval*0.999) #to remove divide by zero problem
        maxval = np.max(array[:,[i]])
        if maxval == 0.0:
            continue
        newarray[:,[i]] = newarray[:,[i]] / maxval
        for row in range(len(newarray)):
            if newarray[row,[i]] < 0:
                newarray[row,[i]] = 0
    return newarray

if __name__ == "__main__":
    faulthandler.enable()
    parser = argparse.ArgumentParser(description= \
     'Script to take a TDMS file and output an np array with the data processed')
    parser.add_argument('-path', help='Path where files to be plotted are', required=True)
    parser.add_argument('-ndel', help='Do you want to delete any data points from the start of the plot, how many', required=False)
    parser.add_argument('-d','--detrend', help='Do you want to linear detrend the data, just put y', required=False)

    args = parser.parse_args()

    print ("The path you want to use is %s" % args.path)
    #print ('This will plot %s with %s on the x-axis and %s on the y-axis' % (args.f, args.x, args.y))

    path = args.path
    ndel = args.ndel
    if ndel:
        ndel = int(args.ndel)
    else:
        ndel = int(0)
    detrend = args.detrend
    if detrend:
        detrend = 1
    else:
        detrend = 0

    assert path.endswith('/'), 'Path needs to end with /'

    targetdir = os.path.join(path, 'Processed') #need to make the full path externally to the otherwise the if stmnt doesn't work - makedirs creates the dir in it's home folder

    if not os.path.exists(targetdir):
        print ('Doesn\'t think it is there')
        os.makedirs(targetdir)
        print('The folder %s was created' % targetdir)
    else:
        print ('Thinks it is there')
        print('The folder %s already exists' % targetdir)

    for root,dir,files in os.walk(path, topdown=False): #the topdown tells the script to look at the collection of files directly in path last
        tdmsfiles=[f for f in files if f.endswith('.tdms') and 'SMU' not in f]

    for f in tdmsfiles:
        try:
            test2 = init_process(path, f, targetdir)
        except Exception as e:
            print("INIT ERROR")
            print(f)
            #traceback.print_exc(file=sys.stdout)
        try:
            medfiltandplot(test2, targetdir, f)
            array = medfiltandplotdevI(test2, targetdir, f)
            medfiltandplotstacked(array, targetdir, f)
        except Exception as e:
            print("ERROR")
            print(f)
            #traceback.print_exc(file=sys.stdout)




#test2filt = medfiltandplot(test2, targetdir, f, 2)

# def linear_detrend(ndel, nparray): #linear detrend, deletes first ndel points, assumes 16 voltage channels
#     array = np.delete(nparray, np.s_[0:ndel], 0) # manually deletes the first 340 rows including the header row, uses the np slice function
#     #volt_values2 = (np.squeeze(volt_values)).astype(np.float)
#     x = (np.squeeze(array[:, [0]])) # because time stamps already
#     for i in range(1,16):
#         y = array[:, i].astype(np.float)
#         m, b, r_val, p_val, std_err = stats.linregress(x, y) # find linear regression line, subtract off data to detrend
#         detrend_y = y - (m*x + b)
#         array[:, i] = np.asarray(detrend_y)
#     return array


# def thresholding_algo(y, lag, threshold, influence):
#     signals = np.zeros(len(y))
#     filteredY = np.array(y)
#     avgFilter = [0]*len(y)
#     stdFilter = [0]*len(y)
#     initAvg = avgFilter[lag - 1] = np.mean(y[0:lag])
#     initStd = stdFilter[lag - 1] = np.std(y[0:lag])
#     for i in range(lag, len(y) - 1):
#         if (y[i] - avgFilter[i-1]) > threshold * stdFilter [i-1]:
#             # if y[i] > avgFilter[i-1]:
#             signals[i] = 1
#             #else:
#                 #signals[i] = -1
#
#             filteredY[i] = influence * y[i] + (1 - influence) * filteredY[i-1]
#             if np.mean(filteredY[(i-lag):i]) > initAvg:
#                 avgFilter[i] = np.mean(filteredY[(i-lag):i])
#             else:
#                 avgFilter[i] = initAvg
#             #avgFilter[i] = np.mean(filteredY[(i-lag):i])
#             if np.std(filteredY[(i-lag):i]) > initStd:
#                 stdFilter[i] = np.std(filteredY[(i-lag):i])
#             else:
#                 stdFilter[i] = initStd
#         else:
#             signals[i] = 0
#             filteredY[i] = y[i]
#             if np.mean(filteredY[(i-lag):i]) > initAvg:
#                 avgFilter[i] = np.mean(filteredY[(i-lag):i])
#             else:
#                 avgFilter[i] = initAvg
#             #avgFilter[i] = np.mean(filteredY[(i-lag):i])
#             if np.std(filteredY[(i-lag):i]) > initStd:
#                 stdFilter[i] = np.std(filteredY[(i-lag):i])
#             else:
#                 stdFilter[i] = initStd
#
#             #avgFilter[i] = np.mean(filteredY[(i-lag):i])
#             #stdFilter[i] = np.std(filteredY[(i-lag):i])
#
#     return dict(signals = np.asarray(signals),
#                 avgFilter = np.asarray(avgFilter),
#                 stdFilter = np.asarray(stdFilter))

# Settings: lag = 30, threshold = 5, influence = 0
# lag = 100        # lag = the lag of the moving window, For example, a lag of 5 will use the last 5 observations to smooth the data
# threshold = 5  # threshold = the z-score at which the algorithm signals, A threshold of 3.5 will signal if a datapoint is 3.5 standard deviations away from the moving mean
# influence = 0   #  influence = the influence (between 0 and 1) of new signals on the mean and standard deviation, And an influence of 0.5 gives signals half of the
#                 # influence that normal datapoints have. Likewise, an influence of 0 ignores signals completely for recalculating the new threshold:
                # an influence of 0 is therefore the most robust option; 1 is the least.

# def simpler(y, baseperiod, threshold, path, figname):
#     initAvg = np.mean(y[0:baseperiod])
#     avgVals = np.full(len(y), initAvg)
#     initStd = np.std(y[0:baseperiod])
#     stdVals = np.full(len(y), threshold * initStd)
#     signals = np.zeros(len(y))
#     for i in range(len(y)):
#         if y[i] - initAvg > threshold * initStd:
#             signals[i] = 1
#     pylab.subplot(211)
#     pylab.plot(np.arange(1, len(y)+1), y)
#     pylab.plot(np.arange(1, len(y)+1),
#                avgVals, color="cyan", lw=2)
#     pylab.plot(np.arange(1, len(y)+1),
#                stdVals, color="green", lw=2)
#     pylab.subplot(212)
#     pylab.step(np.arange(1, len(y)+1), signals, color="red", lw=2)
#     pylab.ylim(0, 1.5)
#     pylab.savefig(os.path.join(path,'z-score%s.png' % figname), dpi=300)
#     pylab.close()
#     return signals


#def plot_zscore(yvals, path, figname): #figname and path must be strings, yvals must be a 1-d array of y-vals.
    # pylab.subplot(211)
    # pylab.plot(np.arange(1, len(yvals)+1), yvals)
    # pylab.plot(np.arange(1, len(yvals)+1),
    #            result["avgFilter"], color="cyan", lw=2)
    # pylab.plot(np.arange(1, len(yvals)+1),
    #            result["avgFilter"] + threshold * result["stdFilter"], color="green", lw=2)
    # pylab.plot(np.arange(1, len(yvals)+1),
    #            result["avgFilter"] - threshold * result["stdFilter"], color="green", lw=2)
    # pylab.subplot(212)
    # pylab.step(np.arange(1, len(yvals)+1), result["signals"], color="red", lw=2)
    # pylab.ylim(0, 1.5)
    # pylab.savefig(os.path.join(path,'z-score%s.png' % figname), dpi=300)
    # pylab.close()
#signal = simpler(array[:,1], 100, 5000, path, "test2B")

# from graphics import *
# import colorsys
# import time
#
# def main2():
#     win = GraphWin('Colour Run', 300, 300)
#
#     #set = [x *0.01 for x in range(50, 100, 5)]
#     for i in signal:
#         rect = Rectangle(Point(50, 50), Point(150, 150))
#         color1 = colorsys.hsv_to_rgb(0.0, 1.0, i)
#         rect.setFill(color_rgb(color1[0]*255, color1[1]*255, color1[2]*255))
#         rect2 = Rectangle(Point(150, 150), Point(250, 250))
#         color2 = colorsys.hsv_to_rgb(0.6, 0.76, i)
#         rect2.setFill(color_rgb(color2[0]*255, color2[1]*255, color2[2]*255))
#         rect3 = Rectangle(Point(150, 50), Point(250, 150))
#         color3 = colorsys.hsv_to_rgb(0.32, 0.8, i)
#         rect3.setFill(color_rgb(color3[0]*255, color3[1]*255, color3[2]*255))
#         rect4 = Rectangle(Point(50, 150), Point(150, 250))
#         color4 = colorsys.hsv_to_rgb(0.8, 1.0, i)
#         rect4.setFill(color_rgb(color4[0]*255, color4[1]*255, color4[2]*255))
#         rect.draw(win)
#         rect2.draw(win)
#         rect3.draw(win)
#         rect4.draw(win)
#         update(100)
#     win.getMouse()
#     win.close()

#main2()
