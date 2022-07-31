import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
from collections import defaultdict
import time

def showResult(rectangles, width, height):
    fig, ax = plt.subplots()
    ax.axis([0,width,0,height])
    print("roll length", height)
    for index, row in rectangles.iterrows():
        r = Rectangle((row["x"], row["y"]), row["width"], row["height"],
             edgecolor = 'black',
             fill=False,
             lw=0.5)
        ax.add_patch(r)
        plt.text(row["x"]+row["width"]/2, row["y"]+row["height"]/2,index)

        print("x, y, width, height", row["x"], row["y"], row["width"], row["height"])
        #break
    plt.show()
    plt.clf()

"""
rectangle [x,y,with,height,vertical,id]
"""
class BLF(object):
    def __init__(self, rectangles, scope, resolution) -> None:
        self.width = 100
        self.length = 0
        self.rectangles = rectangles
        self.resolution = resolution
        self.history = defaultdict(list)
        self.scope = scope

    def placeRectangle(self, row, x, y):
        row["status"] = 1
        row["x"] = x
        row["y"] = y
        if self.length < y + row["height"]:
            self.length = y + row["height"]
        #print("place rec: ",row["id"], x, y, row["width"], row["height"])

    def isIntersect(self, index):
        for i in range(0, len(self.rectangles) - 1):
            if self.rectangles.loc[i]["status"] != 1:
                continue
            if i == index:
                continue
            if self.rectangleIntersect(self.rectangles.loc[i], self.rectangles.loc[index]):
                return True
        return False

    def rectangleIntersect(self, row1, row2):
        first = row1["x"] >= (row2["x"]+row2["width"])
        second = (row1["x"]+row1["width"]) <= row2["x"]
        third = (row1["y"]+row1["height"]) <= row2["y"]
        fourth = row1["y"] >= (row2["y"]+row2["height"])
        return not first and not second and not third and not fourth

    def findLowestY(self, index):
        lowest_y = 0 
        y_set = set()
        count = 0
        for i in reversed(range(0, len(self.rectangles) - 1)):
            rec = self.rectangles.loc[i]
            if rec["status"] != 1:
                continue
            if i == index:
                continue
            count += 1
            if count > self.scope:
                continue
            top = rec["y"] + rec["height"]
            y_set.add(top)
            y_set.add(0)                

        if len(y_set) > 0: 
            if self.history.get(index)!=None:
                lowest_y = min(set(y_set) - set(self.history.get(index)))     
        return lowest_y

    def run(self):
        st = time.time()
        temp_time = 0
        x = 0
        y = 0
        for index, row in self.rectangles.iterrows():  
            y = self.findLowestY(index)
            while True:
                self.placeRectangle(row, x, y)
                x = row["x"] + self.resolution
                if not self.isIntersect(index) and x + row["width"] <= self.width:
                    et = time.time()
                    print("palce a Rectangle here:(%d,%d) index: %d execution time: %s s" %(x, y, index, et - st - temp_time))
                    temp_time = et - st
                    break  
                if x + row["width"] > self.width:
                    x = 0   
                    y = self.findLowestY(index) 
                    if self.history.get(index) == None or y not in self.history.get(index):
                        self.history[index].append(y) 

if __name__ == '__main__':
    st = time.time()


    header_list = ["id", "width", "height"]

    rectangles = pd.read_csv("data/problem1.csv", names=header_list, skipfooter=1, engine='python')
    rectangles["x"] = 0
    rectangles["y"] = 0
    rectangles["vertical"] = 0
    rectangles["status"] = 0

    blf = BLF(rectangles, 20, 1)
    blf.run()
    print('Entire execution time:', time.time() - st, 'seconds')

    showResult(rectangles,blf.width,blf.length)

