import tkinter as tk
from enum import Enum

class State(Enum):
    MOVE = 1
    DRAW_LINE = 2

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = tk.Frame(self)
        self.frame.pack()
        self.state = State.MOVE

        self.button1 = tk.Button(self.frame, text="move", state=["disabled"], command=self.set_moving)
        self.button2 = tk.Button(self.frame, text="draw line", command=self.set_drawingline)
        self.button1.pack()
        self.button2.pack()

        canva = CanvasSpline(self, width=400, height=400, bg='white')
        canva.pack()

    def set_moving(self):
        self.state = State.MOVE
        self.button1['state'] = 'disabled'
        self.button2['state'] = 'normal'

    def set_drawingline(self):
        self.state = State.DRAW_LINE
        self.button1['state'] = 'normal'
        self.button2['state'] = 'disabled'



class CanvasSpline(tk.Canvas):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.Points = []
        self.line_mapping = dict()
        self.highlighted_point = None
        self.dragging = False
        self.start_point = None

        self.bind('<Button-1>', self.line_start)
        self.bind('<Button-1>', self.add_point, add="+")
        self.bind('<ButtonRelease-1>', self.line_end)

    def move_point(self, event):
        if self.dragging and self.master.state == State.MOVE:
            init_coords = self.ellipse_to_point(self.start_point)
            if self.highlighted_point is not None and self.start_point == self.highlighted_point:
                self.move(self.start_point, event.x - init_coords[0], event.y - init_coords[1])
                for line in self.line_mapping:
                    line_tuple = self.line_mapping[line]
                    if self.start_point in line_tuple:
                        self.update_base_line(line_tuple[0], line_tuple[1], line)


    def line_start(self, event):
        overlapped = self.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        if len(overlapped) > 0:
            for item in overlapped:
                if "base_point" in self.gettags(item):
                    self.dragging = True
                    print("user holding button!")
                    self.start_point = item

    def create_base_line(self, start_point_id, end_point_id):
        start_coords = self.ellipse_to_point(start_point_id)
        end_coords = self.ellipse_to_point(end_point_id)
        line_id = self.create_line(start_coords[0], start_coords[1], end_coords[0], end_coords[1], tags=["base_line"])
        print(f"created line {line_id}!")
        return line_id

    def update_base_line(self, start_point_id, end_point_id, line_id):
        start_coords = self.ellipse_to_point(start_point_id)
        end_coords = self.ellipse_to_point(end_point_id)
        self.coords(line_id, (start_coords[0], start_coords[1], end_coords[0], end_coords[1]))

    def line_end(self, event):
        if self.dragging:
            print("user stopped holding a button!")
            self.dragging = False
            if self.master.state == State.DRAW_LINE:
                overlapped = self.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
                if len(overlapped) > 0:
                    for item in overlapped:
                        if "base_point" in self.gettags(item):
                            self.highlight_point(event)
                            if self.points_not_in_use(self.start_point, item) and self.start_point != item:
                                line_id = self.create_base_line(self.start_point, item)
                                print("spawned line!")
                                self.line_mapping[line_id] = (self.start_point, item)
                                for point in self.Points:
                                    if point == self.start_point:
                                        point.outbound_line_point = item
                                    if point == item:
                                        point.inbound_line_point = self.start_point

    def points_not_in_use(self, start_point_id, end_point_id):
        start_point = self.Points[self.Points.index(start_point_id)]
        end_point = self.Points[self.Points.index(end_point_id)]
        return \
            (start_point_id, end_point_id) not in self.line_mapping \
            and (end_point_id, start_point_id) not in self.line_mapping \
            and start_point.outbound_line_point is None \
            and end_point.inbound_line_point is None

    def find_line_endpoint(self, start_point):
        if start_point.outbound_line is not None:
            for line in self.line_mapping:
                line_tuple = self.line_mapping[line]
                if start_point.outbound_line in line_tuple:
                    if start_point.outbound_line == line_tuple[0]:
                        return self.Points[self.Points.index(line_tuple[1])]
        return None

    def find_line_startpoint(self, end_point):
        if end_point.inbound_line is not None:
            for line in self.line_mapping:
                line_tuple = self.line_mapping[line]
                if end_point.inbound_line in line_tuple:
                    if end_point.inbound_line == line_tuple[1]:
                        return self.Points[self.Points.index(line_tuple[0])]
        return None

    def add_point(self, event):
        overlapped = self.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        if len(overlapped) <= 0 and self.dragging == False:
            id = self.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill='black', tags=["base_point"])
            self.tag_bind(id, '<Button-2>', self.del_point)
            self.tag_bind(id, '<Button-3>', self.del_point)
            self.tag_bind(id, '<Motion>', self.move_point)
            self.tag_bind(id, '<Button-1>', self.highlight_point)
            self.Points.append(Point(event.x, event.y, id))

    def del_point(self, event):
        id = self.find_closest(event.x, event.y)
        self.delete(id[0])
        if id[0] == self.highlighted_point:
            self.highlighted_point = None
        try:
            i = self.Points.index(id[0])
            point = self.Points[i]

            if point.inbound_line_point is not None:
                for key, value in self.line_mapping.items():
                    if (point.inbound_line_point, id[0]) == value:
                        self.line_mapping.pop(key)
                        self.delete(key)
                        print(f"deleted line {key}!")
                        i = self.Points.index(point.inbound_line_point)

                        point.inbound_line_point = None
                        self.Points[i].outbound_line_point = None
                        break

            if point.outbound_line_point is not None:
                for key, value in self.line_mapping.items():
                    if (id[0], point.outbound_line_point) == value:
                        self.line_mapping.pop(key)
                        self.delete(key)
                        print(f"deleted line {key}!")
                        i = self.Points.index(point.outbound_line_point)

                        point.outbound_line_point = None
                        self.Points[i].inbound_line_point = None
                        break

            print(f"removed point {id[0]}!")
            self.Points.remove(id[0])
        except ValueError:
            pass

    def highlight_point(self, event):
        id = self.find_closest(event.x, event.y)
        if "base_point" in self.gettags(id):
            if self.highlighted_point is not None:
                self.itemconfig(self.highlighted_point, outline='black', width=0)
            self.highlighted_point = id[0]
            self.itemconfig(self.highlighted_point, outline='green', width=2)

    def ellipse_to_point(self, ellipse_id):
        coords = self.coords(ellipse_id)
        return (coords[2] + coords[0]) / 2, (coords[3] + coords[1]) / 2


class Point:
    def __init__(self, x, y, id):
        self.x, self.y = x, y
        self.id = id
        self.inbound_line_point = None
        self.outbound_line_point = None

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError()

    def __iter__(self):
        yield self.x
        yield self.y

    def __add__(self, other):
        if isinstance(other, Point) or isinstance(other, tuple):
            return Point(self.x + other[0], self.y + other[1], self.id)
        raise TypeError(f"unsupported operand type(s) for +: {type(self)} and {type(other)}")

    def __sub__(self, other):
        if isinstance(other, Point) or isinstance(other, tuple):
            return Point(self.x - other[0], self.y - other[1], self.id)
        raise TypeError(f"unsupported operand type(s) for +: {type(self)} and {type(other)}")

    def __truediv__(self, other):
        return Point(self.x / other, self.y / other, self.id)

    def __mul__(self, other):
        return Point(self.x * other, self.y * other, self.id)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        if isinstance(other, int):
            return self.id == other

    @staticmethod
    def to_screen(point, width, height):
        """

        :rtype: tuple
        """
        x_screen = point[0] + width/2
        y_screen = height/2 - point[1]
        return x_screen, y_screen

    @staticmethod
    def to_cartesian(point, width, height):
        """

        :rtype: tuple
        """
        x_cart = width/2 - point[0]
        y_cart = height/2 - point[1]
        return x_cart, y_cart

    @staticmethod
    def get_length_between_points(p0, p1):
        return ((p0.x - p1.x) ** 2 + (p0.y - p1.y) ** 2) ** .5

class BezierCurve:
    def __init__(self, n, p0 = None, p1 = None, p2 = None, p3 = None):
        self.p0, self.p1, self.p2, self.p3 = p0, p1, p2, p3
        self.curr_t = 0.0
        self.step = 1.0/n

        p0x3 = self.p0 * 3
        p1x3 = self.p1 * 3
        p2x3 = self.p2 * 3

        self.pow3arg = self.p3 - p2x3 + p1x3 - self.p0
        self.pow2arg = p0x3 - p1x3 * 2 + p2x3
        self.pow1arg = p1x3 - p0x3

    def get_next_point(self):
        point = None
        if self.curr_t < 1.0:
            point = self.pow3arg * self.curr_t ** 3 + self.pow2arg * self.curr_t ** 2 + self.pow1arg * self.curr_t + self.p0
            self.curr_t += self.step
        return point

    def get_all_points(self):
        points = []
        t = 0.0
        while t <= 1.0:
            point = self.pow3arg * self.curr_t ** 3 + self.pow2arg * self.curr_t ** 2 + self.pow1arg * self.curr_t + self.p0
            points.append(point)
            t += self.step
        return points

def calculate_bezier_anchors(p0: Point, p1: Point, p2: Point):
    if p0 is None:
        p0 = p1
    elif p2 is None:
        p2 = p1
    a0 = (p0 + p1) / 2
    a1 = (p1 + p2) / 2
    l1 = Point.get_length_between_points(p0, p1)
    l2 = Point.get_length_between_points(p1, p2)
    b = a0 * (l1 / (l1 + l2)) + a1 * (l2 / (l1 + l2))
    diff = p1 - b

    return a0 + diff, a1 + diff

def main():
    a = Point(1, 1, 0)
    b = Point(3, 3, 1)
    c = Point(5, 5, 2)
    p0, p1 = calculate_bezier_anchors(None, b, c)
    print(str(p0) + " " + str(p1))
    print(tuple(a))

    root = App()

    root.mainloop()

if __name__ == '__main__':
    main()
