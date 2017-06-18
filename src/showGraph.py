#!/usr/bin/env python3
"""
Display analog sensor data from arduino
"""

import sys, serial, argparse, time, math, operator, select
import numpy as np
from time import sleep
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# plot class
class SensorAnalyzer:
  # constr
  def __init__(self, strPort, maxTime):
      self.tempcounter = 1;
      # open serial port
      self.ser = serial.Serial(strPort, 115200)
      # Self time the framerate
      self.starttime = 0
      self.endtime = 0
      self.maxTime = maxTime
      self.torefresh = False
      self.refreshTime = int(round(time.time() * 1000))
      self.axs = 0;
      self.axsrange =[];
      # Set up the arduino, and get arguments from it
      self.arduinoArgs = {}
      self.init_serial()
      sensors = self.arduinoArgs["sensors"]
      print(self.arduinoArgs)
      fps = self.maxTime * self.arduinoArgs["fps"]
      self.vals = [deque([0.0]*fps) for _ in range(sensors)]

  def plotwindow(self,i,ax,valmin,valmax):
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    color = colors[i % len(colors)]
    ax.set_xlim([0, self.maxTime * self.arduinoArgs["fps"]-1])
    ax.set_ylim([valmin, valmax])
    for tick in ax.get_yticklabels():
        tick.set_rotation(70)

    return ax.plot([], [],color=color,label=self.arduinoArgs["sensorNames"][i])[0]

  def run(self):
    # set up animation
    fig1 = plt.figure("All sensors")
    # plt.title('Test Title')
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
    #.ion()
    # Set up the axis for the different plots
    self.axs = [fig1.add_subplot(2,len(self.vals) , i) for i in range(1,len(self.vals)+1)]
    #ax = plt.axes(xlim=(0, self.maxTime * self.arduinoArgs["fps"]-1), ylim=(0, 1023))
    self.lines = list([(i,self.plotwindow(i,self.axs[i],self.arduinoArgs["sensorRanges"][i][0],self.arduinoArgs["sensorRanges"][i][1]))
                      for i in range(len(self.vals))])
    # Set up the axis for the combined plots
    axsum = fig1.add_subplot(2, 1 , 2)
    self.lines = self.lines + list([(i,self.plotwindow(i,axsum,0,1023))
                               for i in range(len(self.vals))])
    # # fig1.legend(handles=self.lines,
    #            labels=["a","b","c","d","e"],
    #            ncol=len(self.vals),bbox_transform=axs[1].transAxes,
    #            mode="expand")
    # plt.legend(handles=self.lines, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
    #        ncol=len(self.vals), mode="expand", borderaxespad=0.)
    anim1 = animation.FuncAnimation(fig1, self.updateall,
                                    fargs=self.lines,
                                    interval=1,blit=True)
    for ax in self.axs:
      ax.legend(mode="expand",bbox_to_anchor=(0., 1.02, 1., .102),loc=3)
    self.axs.append(axsum)
    #self.axs[len(self.axs)-1].set_title('Test Title')
    # axsum.set_title('Test Title')
    # self.lines = list([ax.plot([], [],label=self.arduinoArgs["sensorNames"][i])
    #                   for i in range(len(self.vals))])
    # anim = animation.FuncAnimation(fig1, self.updateall,
    #                                fargs=self.lines,
    #                                interval=1,blit=True)


    # show plot
    plt.show()

  # add to buffer
  def addToBuf(self, buf, val):
      if len(buf) < self.maxTime * self.arduinoArgs["fps"]:
          buf.append(val)
      else:
          buf.pop()
          buf.appendleft(val)

  def babyInfo(self, vals):
    strings = ["Wut?","On belly","On back","On left","On right"]
    thistext = self.axs[len(self.axs)-1].get_title()
    idx,_ = max(enumerate(vals), key=operator.itemgetter(1))
    titlestring = strings[idx]

    if(thistext != titlestring):
      self.axs[-1].set_title(titlestring)
      plt.draw()
  # add data to the queue buffers
  def add(self, data):
    self.starttime = self.endtime
    self.endtime = int(round(time.time() * 1000))
    # sys.stdout.write('pulls:{} fps:{} delay:{}     \r'
    #   .format(data[1], math.floor(1000/(self.endtime-self.starttime)),data[0]))
    # sys.stdout.flush()
    dt = [];
    for i in range(len(data)-2):
      self.addToBuf(self.vals[i], data[i+2])
      dt.append(int(data[i+2]))
    self.babyInfo(dt)
    i,o,e = select.select([sys.stdin],[],[],0.0001)
    for s in i:
        if s == sys.stdin:
            inputt = sys.stdin.readline()
            sys.stdout.write("\033[F")
            print(self.tempcounter,dt)
            self.tempcounter += 1

  # update all plots
  def updateall(self, frameNum, *lines):
      try:
          line = self.ser.readline()
          data = [int(val) for val in line[:-2].decode("utf-8").split(",")]
          self.add(data)
          retlines = [val for (index,val) in lines]
          for (index,val) in lines:
              val.set_data(range(self.maxTime * self.arduinoArgs["fps"]), self.vals[index])
              listval = list(self.vals[index])
              minval = max(min(listval),self.arduinoArgs["sensorRanges"][index][0]) -10
              maxval = min(max(listval),self.arduinoArgs["sensorRanges"][index][1]) +10
              oldminval, oldmaxval = self.axs[index].get_ylim()
              delay = (int(round(time.time() * 1000)))-self.refreshTime >1000
              if((oldminval != minval or oldmaxval != maxval) and (maxval-minval)>50 and delay):
                  self.axs[index].set_ylim(minval,maxval)
                  self.torefresh = True


          if (self.torefresh):
            self.refreshTime = int(round(time.time() * 1000))
            plt.draw()
            self.torefresh = False


      except KeyboardInterrupt:
          print('exiting')
      return retlines

  def init_serial(self):
    # Read the initial data from the sensor(Init signal)
    self.ser.write(b"1")
    line = self.ser.readline()
    print(line)
    line = self.ser.readline()
    print(line)
    argscount = int(line[:-2].decode("utf-8").split(":")[1])
    for x in range(0, argscount):
      line = self.ser.readline()
      vals = line[:-2].decode("utf-8").split(":")
      # Hardcode some information from the arduino for easy parsing
      # Convert to int
      if vals[0] in ["fps", "sensors","samplesize"]:
        self.arduinoArgs[vals[0]] = int(vals[1])
      # convert to list of strings
      if vals[0] in ["sensorNames"]:
        self.arduinoArgs[vals[0]] = vals[1].split(",")
      # convert to list of touples of intengers
      if vals[0] in ["sensorRanges"]:
        self.arduinoArgs[vals[0]] = [list(map(int, x.split(","))) for x in vals[1].split("|")]
  def close(self):
      # close serial
      self.ser.flush()
      self.ser.close()

# main() function
def main():
  # create parser
  parser = argparse.ArgumentParser(description="Read serial data from Arduino")
  # add expected arguments
  parser.add_argument('--port', dest='port', required=True)

  # parse args
  args = parser.parse_args()

  #strPort = '/dev/tty.usbserial-A7006Yqh'
  strPort = args.port

  print('reading from serial port %s...' % strPort)

  # plot parameters
  sensorAnalyzer = SensorAnalyzer(strPort, 20)

  print('plotting data...')

  sensorAnalyzer.run()
  # clean up
  sensorAnalyzer.close()

  print('exiting.')


# call main
if __name__ == '__main__':
  main()