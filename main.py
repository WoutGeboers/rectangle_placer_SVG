import csv
import svgwrite
from functools import lru_cache
from svgwrite import cm, mm
import time

with open('to_lasercut4.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

print(data)
with open('movement trays2.csv', newline='') as f2:
    reader2 = csv.reader(f2)
    movement_data = list(reader2)
GLOBAL_grid_size = 1
GLOBAL_marge = 0
GLOBAL_EDGE_MARGIN=4




class movement_tray():
    def __init(self, ranks, files, inner_rectangle_size, outer_rectangle_size):
        self.x_BL = -1
        self.y_BL = -1
        self.ranks = ranks
        self.files = files
        self.inner_rectangle_size = inner_rectangle_size
        self.outer_rectangle_size = outer_rectangle_size
        self.horizontal_play = (outer_rectangle_size[0] - inner_rectangle_size[0]) / 2.0
        self.vertical_play = (outer_rectangle_size[1] - inner_rectangle_size[1]) / 2.0
        self.width = self.calc_outer_dimensions()[0] + GLOBAL_marge
        self.height = self.calc_outer_dimensions()[1] + GLOBAL_marge
    def calc_outer_dimensions(self):
        width= self.outer_rectangle_size[0] * self.files
        height=self.outer_rectangle_size[1]*self.ranks
        return(width, height)





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

class rectangle_with_circle(rectangle):
    def __init__(self, width, height,**kwargs):
        super(rectangle_with_circle, self).__init__(width, height)
        try:
            self.diameter=kwargs.diameter
        except AttributeError:
            print("automatically filled the diameter to 5")
            self.diameter=5

    def calc_positions_of_circles(self):
        if 18>self.width>32 and 18>self.height>32:
            #infantry base
            xpos=float(self.width)/2.0
            ypos=float(self.height)/2.0
            return([(xpos,ypos)])
        elif 18>self.width>32 and 32>self.height>55:
            #cavalry base
            xpos1 = float(self.width) / 2.0
            ypos1 = float(self.height) / 3.0
            xpos2 = float(self.width) / 2.0
            ypos2 = float(self.height) *2.0/ 3.0
            return([(xpos1,ypos1),(xpos2,ypos2)])
        elif 35>self.width>55 and 35>self.height>55:
            #mosntrous infantry and small monster
            xpos1 = float(self.width) / 2.0
            ypos1 = float(self.height) / 3.0
            xpos2 = float(self.width) / 3.0
            ypos2 = float(self.height) * 2.0 / 3.0
            xpos3 = float(self.width) *2.0/ 3.0
            ypos3 = float(self.height) * 2.0 / 3.0
            return ([(xpos1, ypos1), (xpos2, ypos2),(xpos3, ypos3)])
        else:
            print("there are no magnets for bases of size "+self.width+"-"+self.height)





class movement_tray_inherited(rectangle):
    def __init__(self,  files, ranks, outer_rectangle_size,inner_rectangle_size):
        self.x_BL = -1
        self.y_BL = -1
        self.ranks = ranks
        self.files = files
        self.inner_rectangle_size = inner_rectangle_size
        self.outer_rectangle_size = outer_rectangle_size
        self.horizontal_play = (outer_rectangle_size[0] - inner_rectangle_size[0]) / 2.0
        self.vertical_play = (outer_rectangle_size[1] - inner_rectangle_size[1]) / 2.0
        self.width = self.calc_outer_dimensions()[0] + GLOBAL_marge
        self.height = self.calc_outer_dimensions()[1] + GLOBAL_marge

    def calc_outer_dimensions(self):
        width = self.outer_rectangle_size[0] * self.files
        height = self.outer_rectangle_size[1] * self.ranks
        return (width, height)
    # def convert_to_svg_element(self):
    #     x_upper_left = self.x_BL
    #     y_upper_left = self.y_BL
    #     return ((x_upper_left, y_upper_left), (self.width, self.height))
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
for dat in movement_data:
    for i in range(0, int(dat[0])):
        files=float(dat[1])
        ranks=float(dat[2])
        outer_rect=(float(dat[3]),float(dat[4]))
        inner_rect=(float(dat[5]),float(dat[6]))
        list_of_rectangles.append(movement_tray_inherited(files,ranks,outer_rect,inner_rect))
        list_of_rectangles.append(movement_tray_inherited(files, ranks, outer_rect, inner_rect))
        list_of_rectangles.append(rectangle(movement_tray_inherited(files, ranks, outer_rect, inner_rect).width-GLOBAL_marge,movement_tray_inherited(files, ranks, outer_rect, inner_rect).height-GLOBAL_marge))

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
n = 1
for pan in panels:
    draw = svgwrite.drawing.Drawing("panel" + str(n) + "gridsize" + str(pan.grid_size) + ".svg", (600 * mm, 300 * mm))
    for obj in pan.rectangles:
        if type(obj) is rectangle:

            pos, siz = obj.convert_to_svg_element()
            element = draw.rect(((pos[0] + GLOBAL_marge / 2 + GLOBAL_EDGE_MARGIN) * mm,
                                 (GLOBAL_marge / 2 + pos[1] + GLOBAL_EDGE_MARGIN) * mm),
                                ((siz[0] - GLOBAL_marge) * mm, (siz[1] - GLOBAL_marge) * mm), stroke="red",
                                stroke_width=0.01,
                                fill="none")
            draw.add(element)
        elif type(obj) is rectangle_with_circle:
            pos, siz = obj.convert_to_svg_element()
            element = draw.rect(((pos[0] + GLOBAL_marge / 2 + GLOBAL_EDGE_MARGIN) * mm,
                                 (GLOBAL_marge / 2 + pos[1] + GLOBAL_EDGE_MARGIN) * mm),
                                ((siz[0] - GLOBAL_marge) * mm, (siz[1] - GLOBAL_marge) * mm), stroke="red",
                                stroke_width=0.01,
                                fill="none")
            draw.add(element)
            for position in obj.calc_positions_of_circles():
                pos=position
                element = draw.circle(((pos[0] + GLOBAL_marge / 2 + GLOBAL_EDGE_MARGIN) * mm,
                                     (GLOBAL_marge / 2 + pos[1] + GLOBAL_EDGE_MARGIN) * mm),
                                    (obj.diameter* mm), stroke="red",
                                    stroke_width=0.01,
                                    fill="none")
                draw.add(element)
        elif type(obj) is movement_tray_inherited:
            pos, siz = obj.convert_to_svg_element()
            # figure out magic with marge
            # draw outer rectangle
            new_pos=((pos[0] + GLOBAL_marge / 2 + GLOBAL_EDGE_MARGIN),
                                 (GLOBAL_marge / 2 + pos[1] + GLOBAL_EDGE_MARGIN))
            element = draw.rect((new_pos[0] * mm,
                                 new_pos[1] * mm),
                                ((siz[0] - GLOBAL_marge) * mm, (siz[1] - GLOBAL_marge) * mm), stroke="red",
                                stroke_width=0.01,
                                fill="none")
            draw.add(element)
            # draw smaller rectangles to cut
            for i in range(int(obj.ranks)):
                for j in range(int(obj.files)):
                    xpos = new_pos[0]+obj.horizontal_play + j * obj.outer_rectangle_size[0]
                    ypos = new_pos[1]+obj.vertical_play + i * obj.outer_rectangle_size[1]
                    size = obj.inner_rectangle_size




                    element = draw.rect(((xpos ) * mm,
                                        (ypos  )* mm),
                                        ((size[0])  * mm, (size[1]) * mm), stroke="red",
                                       stroke_width=0.01,
                                       fill="none")
                    draw.add(element)

            # draw lines to engrave for larger rectangles
            for i in range(1,int( obj.ranks)):
                # skip zero position, draw horizontal lines
                xpos1 = 0+new_pos[0]
                ypos1 = i * obj.outer_rectangle_size[1]+new_pos[1]

                xpos2 = obj.files * obj.outer_rectangle_size[0]+new_pos[0]
                ypos2 = ypos1
                element=draw.line((xpos1* mm,ypos1* mm),(xpos2* mm,ypos2* mm), stroke="black",
                                       stroke_width=0.01,
                                       fill="none")
                draw.add(element)
            for j in range(1, int(obj.files)):
                xpos1 = j * obj.outer_rectangle_size[0]+new_pos[0]
                ypos1 = 0+new_pos[1]

                xpos2 = xpos1
                ypos2 = obj.ranks * obj.outer_rectangle_size[1]+new_pos[1]
                element=draw.line((xpos1* mm,ypos1* mm),(xpos2* mm,ypos2* mm), stroke="black",
                                       stroke_width=0.01,
                                       fill="none")
                draw.add(element)


        else:
            raise Exception('this type is not supported to be added to the panel')

        #code for rectangle
    drawings.append(draw)
    draw.save()
    n = n + 1
