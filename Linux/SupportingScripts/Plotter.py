#!/usr/bin/env python3

import matplotlib.pyplot as plt 
import pandas as pd 
import numpy as np 

def main():
    #
    dataSet = pd.read_csv(r"C:\\Users\\robert.gaines\\Desktop\\dataset.csv")
    #
    BoundaryBox = ((117.0460,116.9426,46.7071,46.7493))
    #
    city = plt.imread("C:\\Users\\robert.gaines\\Desktop\\moscow.png")
    #
    figure,axis = plt.subplots(figsize=(8,7))
    #
    axis.scatter(dataSet.longitude,dataSet.latitude,zorder=1,alpha=.95,c='r',s=10)
    #
    axis.set_title("Wireless AP's")
    #
    axis.set_xlim(BoundaryBox[0],BoundaryBox[1])
    #
    axis.set_ylim(BoundaryBox[2],BoundaryBox[3])
    #
    axis.imshow(city,zorder=0,extent=BoundaryBox,aspect='equal')
    #
    plt.show()
    

main()


