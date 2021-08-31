import random
import geopy.distance
import math
import os
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageOps

@dataclass
class City:
    name: str
    longitude: float
    latitude: float
    px_x: int
    px_y: int


class TSP_SA_Solver:

    def __init__(self, filename):
        self.cities = []
        self.filename = filename
        with open(filename + '/cities.csv', 'r') as infile:
            lines = infile.readlines()
            for line in lines:
                data = line.split(',')
                self.cities.append(City(data[0], float(data[1]), float(data[2]), int(data[3]), int(data[4])))

    def Generate_Successor(self, prev):
        i, j = random.sample(range(0, len(prev)), 2)
        op = random.randint(1, 3)
        if op == 1:
            new = self.Inverse_Successor(prev, i, j)
        elif op == 2:
            new = self.Insert_Successor(prev, i, j)
        elif op == 3:
            new = self.Swap_Successor(prev, i, j)
        return new

    def Inverse_Successor(self, prev, i, j):
        if i > j: i, j = j, i
        return prev[:i] + prev[i:j+1][::-1] + prev[j+1:]
        
    def Insert_Successor(self, prev, i, j):
        ret = prev.copy()
        tmp = ret.pop(j)
        ret.insert(i, tmp)
        return ret

    def Swap_Successor(self, prev, i, j):
        ret = prev.copy()
        ret[i], ret[j] = ret[j], ret[i]
        return ret

    def Calc_Distance(self, lo1, la1, lo2, la2):
        c1 = (lo1, la1)
        c2 = (lo2, la2)
        return geopy.distance.distance(c1, c2).km

    def Calc_Path(self, cities):
        ret = 0
        for i in range(1, len(cities)):
            ret += self.Calc_Distance(cities[i-1].longitude, cities[i-1].latitude, cities[i].longitude, cities[i].latitude)
        return ret + self.Calc_Distance(cities[0].longitude, cities[0].latitude, cities[-1].longitude, cities[-1].latitude)
        
    def Solve(self, MAX_ITERS, FRAME_PER_ITERS):
        prev = random.sample(self.cities, len(self.cities))
        images = []
        for k in range(MAX_ITERS):
            if k % FRAME_PER_ITERS == 0:
                print(k/MAX_ITERS)
                print(round(self.Calc_Path(prev), 3))
                print('-----')
                im = Image.open(self.filename + '/map.jpg')
                draw = ImageDraw.Draw(im)
                for i in range(1, len(prev)):
                    draw.line((prev[i-1].px_x,prev[i-1].px_y,prev[i].px_x,prev[i].px_y), fill=(0,255,0), width=4)
                draw.line((prev[0].px_x,prev[0].px_y,prev[-1].px_x,prev[-1].px_y), fill=(0,255,0), width=4)
                images.append(im)
            t = 1 - (k/MAX_ITERS)
            new = self.Generate_Successor(prev)
            prev_cost = self.Calc_Path(prev)
            new_cost = self.Calc_Path(new)
            if new_cost < prev_cost:
                prev = new
            elif math.exp(-1 * (new_cost - prev_cost) / t) >= random.random():
                prev = new
        images[0].save(self.filename + '/final.gif',
            save_all=True, append_images=images[1:], optimize=True, duration=100, loop=0)
        ret = []
        for i in prev:
            ret.append(i.name)
        return ret

x = TSP_SA_Solver('tx')
ret = x.Solve(10000, 100)
x = TSP_SA_Solver('us')
ret = x.Solve(10000, 100)
x = TSP_SA_Solver('world')
ret = x.Solve(10000, 100)