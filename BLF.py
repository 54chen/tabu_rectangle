import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
from collections import defaultdict
import time



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
        self.progress_bar(row["id"],len(self.rectangles))
        #print("place rec: ",row["id"], x, y, row["width"], row["height"])

    def isIntersect(self, index):
        for i in range(0, len(self.rectangles) - 1):
            if self.rectangles.iloc[i]["status"] != 1:
                continue
            if i == index:
                continue
            if self.rectangleIntersect(self.rectangles.iloc[i], self.rectangles.iloc[index]):
                return self.rectangles.iloc[i]["x"] + self.rectangles.iloc[i]["width"],True
        return 0, False

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
        y_set_left_right = defaultdict(list)
        y_set.add(0)  
        y_set_left_right[0] = [0, 100]
        for i in reversed(range(0, len(self.rectangles) - 1)):
            rec = self.rectangles.iloc[i]
            if rec["status"] != 1:
                continue
            if i == index:
                continue
            count += 1
            if count > self.scope:
                break
            top = rec["y"] + rec["height"]
            y_set.add(top)

            left = rec["x"]
            right = rec["x"]+rec["width"]
    
            if y_set_left_right[top] and left > y_set_left_right[top][0]:
                left = y_set_left_right[top][0]
            if y_set_left_right[top] and right < y_set_left_right[top][1]:
                right = y_set_left_right[top][1]

            y_set_left_right[top] = [left, right]
            
        if len(y_set) > 0: 
            if self.history.get(index)!=None:
                if set(y_set) == set(self.history.get(index)):
                    lowest_y = 0
                else: 
                    lowest_y = min(set(y_set) - set(self.history.get(index)))     
        return y_set_left_right[lowest_y][0], y_set_left_right[lowest_y][1], lowest_y

    @staticmethod
    def showResult(rectangles, width, length):
        fig, ax = plt.subplots()
        ax.axis([0,width,0,length])
        print("roll length", length)
        for index, row in rectangles.iterrows():
            r = Rectangle((row["x"], row["y"]), row["width"], row["height"],
                edgecolor = 'black',
                fill=False,
                lw=0.5)
            ax.add_patch(r)
            plt.text(row["x"]+row["width"]/2, row["y"]+row["height"]/2,row["id"])

            #print("x, y, width, height", row["x"], row["y"], row["width"], row["height"])
            #break
        plt.show()
        plt.clf()

    def progress_bar(self, current, total, bar_length=20):
        fraction = current / total

        arrow = int(fraction * bar_length - 1) * '-' + '>'
        padding = int(bar_length - len(arrow)) * ' '

        ending = '\n' if current == total else '\r'

        print(f'Progress: [{arrow}{padding}] {int(fraction*100)}%', end=ending)

    def run(self):
        st = time.time()
        temp_time = 0
        x = 0
        y = 0
        for index, row in self.rectangles.iterrows():  
            left, right, y = self.findLowestY(index)
            if left > x or right < x:
                continue
            while True:
                self.placeRectangle(row, x, y)
                x = row["x"] + self.resolution
                move_x, isIntersect = self.isIntersect(index)
                if isIntersect:
                    x = move_x
                if not isIntersect and x + row["width"] <= self.width:
                    et = time.time()
                    #print("place a Rectangle here:(%d,%d) id: %d execution time: %s s" %(x-self.resolution, y, row["id"], et - st - temp_time))
                    temp_time = et - st
                    break  
                if x + row["width"] > self.width:
                    x = 0   
                    left, right, y = self.findLowestY(index) 
                    if self.history.get(index) == None or y not in self.history.get(index):
                        self.history[index].append(y) 
                if left > x or right < x:
                    continue

if __name__ == '__main__':
    st = time.time()


    header_list = ["id", "width", "height"]

    rectangles = pd.read_csv("data/problem1.csv", names=header_list, skipfooter=1, engine='python')
    rectangles["x"] = 0
    rectangles["y"] = 0
    rectangles["vertical"] = 0
    rectangles["status"] = 0

    r = rectangles.sample(frac=1).reset_index(drop=True)
    blf = BLF(r, 20, 1)
    blf.run()
    print('Entire execution time:', time.time() - st, 'seconds')
    #print(r)
    blf.showResult(r, blf.width, blf.length)

