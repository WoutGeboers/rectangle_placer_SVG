import csv
import svgwrite
from functools import lru_cache
from svgwrite import cm, mm
import time

with open('to_lasercut2.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

print(data)

GLOBAL_grid_size = 1
GLOBAL_marge = 1
GLOBAL_EDGE_MARGIN=4

class rectangle():
    def __init__(self, width, height):
        self.x_BL = -1
        self.y_BL = -1
        self.width = width + GLOBAL_marge
        self.height = height + GLOBAL_marge

    def calc_topright(self):
        if self.x_BL == -1:
            raise Exception('rectangle hasnt been placed yet')
        x_topright = self.x_BL + self.width
        y_topright = self.y_BL + self.height
        return (x_topright, y_topright)

    def overlap(self, rectangle):
        (self_x_TR, self_y_TR) = self.calc_topright()
        (rect_x_TR, rect_y_TR) = rectangle.calc_topright()
        if self_x_TR < rectangle.x_BL or self.x_BL > rect_x_TR:
            return False
        elif self_y_TR < rectangle.y_BL or self.y_BL > rect_y_TR:
            return False
        return True

    def envelops(self, pos):
        x = pos[0]
        y = pos[1]
        (x_TR, y_TR) = self.calc_topright()
        return (x_TR > x > self.x_BL and y_TR > y > self.y_BL)

    def convert_to_svg_element(self):
        x_upper_left = self.x_BL
        y_upper_left = self.y_BL
        return ((x_upper_left, y_upper_left), (self.width, self.height))


class panel():
    def __init__(self, width, height, grid_size):
        self.width = width
        self.height = height
        self.grid_size = grid_size  # in mm
        self.positions = []
        for x in range(0, width, self.grid_size):
            for y in range(0, height, self.grid_size):
                self.positions.append((x, y))
        self.rectangles = []

    def place(self, rectangle):
        new_positions = []
        for p in self.positions:
            if not rectangle.envelops(p):
                new_positions.append(p)

        self.positions = new_positions
        self.rectangles.append(rectangle)

    # @lru_cache(maxsize=None)
    def can_place(self, rectangle):
        top_right = rectangle.calc_topright()
        if top_right[0] > self.width or top_right[1] > self.height:
            return False
        for rect in self.rectangles:
            if rect.overlap(rectangle):
                return False

        return True


list_of_rectangles = []
for dat in data:
    for i in range(0, int(dat[0])):
        list_of_rectangles.append(rectangle(float(dat[1]), float(dat[2])))
panels = [panel(600-GLOBAL_EDGE_MARGIN*2, 300-GLOBAL_EDGE_MARGIN*2, GLOBAL_grid_size)]
t1 = time.time()
while len(list_of_rectangles) > 0:
    current_rect = list_of_rectangles.pop()
    rectangle_placed = False
    for pan in panels:
        for point in pan.positions:
            current_rect.x_BL = point[0]
            current_rect.y_BL = point[1]
            if pan.can_place(current_rect):
                pan.place(current_rect)
                #print('placed 1 rectangle')
                rectangle_placed = True
                break
        if rectangle_placed:
            break
    if rectangle_placed:
        continue
    temp = panel(600, 300, GLOBAL_grid_size)
    print("placed new panel")
    t2 = time.time()
    print(t2 - t1)
    current_rect.x_BL = 0
    current_rect.y_BL = 0
    temp.place(current_rect)
    panels.append(temp)
drawings = []
i = 1
for pan in panels:
    draw = svgwrite.drawing.Drawing("panel" + str(i) + "gridsize" + str(pan.grid_size) + ".svg", (600 * mm, 300 * mm))
    for rect in pan.rectangles:
        pos, siz = rect.convert_to_svg_element()
        element = draw.rect(((pos[0] + GLOBAL_marge / 2+GLOBAL_EDGE_MARGIN) * mm, (GLOBAL_marge / 2 + pos[1]+GLOBAL_EDGE_MARGIN) * mm),
                            ((siz[0] - GLOBAL_marge) * mm, (siz[1] - GLOBAL_marge) * mm), stroke="red", stroke_width=0.01,
                            fill="none")
        draw.add(element)
    drawings.append(draw)
    draw.save()
    i = i + 1
