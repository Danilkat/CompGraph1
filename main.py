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
    bezier_curve_n = 10 #Amount of base lines in single bezier curve

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.bezier_curves_count = 0
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

                point = self.get_point_by_id(self.start_point)
                point.x, point.y = event.x, event.y

                startstart_point = 0
                endend_point = 0

                for line in self.line_mapping:
                    line_tuple = self.line_mapping[line]
                    if self.start_point in line_tuple:
                        self.update_bezier_line(line_tuple[0], line_tuple[1], recalculate_anchors= True)
                        if line_tuple[0] == self.start_point:
                            endend_point = line_tuple[1]
                        else:
                            startstart_point = line_tuple[0]

                for line in self.line_mapping:
                    line_tuple = self.line_mapping[line]
                    if endend_point in line_tuple and endend_point == line_tuple[0] or \
                            startstart_point in line_tuple and startstart_point == line_tuple[1]:
                        self.update_bezier_line(line_tuple[0], line_tuple[1])



    def line_start(self, event):
        overlapped = self.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        if len(overlapped) > 0:
            for item in overlapped:
                if "base_point" in self.gettags(item):
                    self.dragging = True
                    print("user holding button!")
                    self.start_point = item

    def update_bezier_line(self, p0, p1, recalculate_anchors = False):
        bezier_tag = 0

        if isinstance(p0, int):
            start_point = self.get_point_by_id(p0)
        else:
            start_point = p0

        if isinstance(p1, int):
            end_point = self.get_point_by_id(p1)
        else:
            end_point = p1

        if start_point is not None and end_point is not None:
            for key, value in self.line_mapping.items():
                if (start_point.id, end_point.id) == value:
                    #self.line_mapping.pop(key)
                    bezier_tag = key
                    self.delete(key)

                    if recalculate_anchors:
                        start_point.inbound_bezier_anchor, start_point.outbound_bezier_anchor = calculate_bezier_anchors(
                            self.get_point_by_id(start_point.inbound_line_point),
                            start_point,
                            end_point
                        )

                        end_point.inbound_bezier_anchor, end_point.outbound_bezier_anchor = calculate_bezier_anchors(
                            start_point,
                            end_point,
                            self.get_point_by_id(end_point.outbound_line_point)
                        )

                    curve = BezierCurve(self.bezier_curve_n,
                                        start_point,
                                        start_point.outbound_bezier_anchor,
                                        end_point.inbound_bezier_anchor,
                                        end_point)

                    curve_points = curve.get_all_points()

                    for i in range(0, len(curve_points) - 1):
                        self.create_base_line(curve_points[i], curve_points[i+1], [bezier_tag])


    def create_bezier_line(self, start_point_id, end_point_id):
        start_point = None
        end_point = None
        for point in self.Points:
            if point == start_point_id:
                start_point = point
                point.outbound_line_point = end_point_id
            if point == end_point_id:
                end_point = point
                point.inbound_line_point = start_point_id

        startstart_point = self.get_point_by_id(start_point.inbound_line_point)
        endend_point = self.get_point_by_id(end_point.outbound_line_point)

        start_point.inbound_bezier_anchor, start_point.outbound_bezier_anchor = calculate_bezier_anchors(
            startstart_point,
            start_point,
            end_point
        )

        end_point.inbound_bezier_anchor, end_point.outbound_bezier_anchor = calculate_bezier_anchors(
            start_point,
            end_point,
            endend_point
        )

        curve = BezierCurve(self.bezier_curve_n,
                            start_point,
                            start_point.outbound_bezier_anchor,
                            end_point.inbound_bezier_anchor,
                            end_point)

        curve_points = curve.get_all_points()

        bezier_tag = f"bezier{self.bezier_curves_count}"
        self.bezier_curves_count += 1

        for i in range(0, len(curve_points) - 1):
            self.create_base_line(curve_points[i], curve_points[i+1], [bezier_tag])

        self.update_bezier_line(startstart_point, start_point)
        self.update_bezier_line(end_point, endend_point)

        return bezier_tag

    def create_base_line(self, p0, p1, tags):
        if isinstance(p0, int):
            start_coords = self.ellipse_to_point(p0)
        else:
            start_coords = p0

        if isinstance(p1, int):
            end_coords = self.ellipse_to_point(p1)
        else:
            end_coords = p1

        line_id = self.create_line(start_coords[0], start_coords[1], end_coords[0], end_coords[1], tags=["base_line", *tags])
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
                                line_id = self.create_bezier_line(self.start_point, item)
                                print("spawned line!")
                                self.line_mapping[line_id] = (self.start_point, item)


    def get_point_by_id(self, id):
        try:
            return self.Points[self.Points.index(id)]
        except ValueError:
            return None


    def points_not_in_use(self, start_point_id, end_point_id):
        start_point = self.get_point_by_id(start_point_id)
        end_point = self.get_point_by_id(end_point_id)
        return \
            (start_point_id, end_point_id) not in self.line_mapping \
            and (end_point_id, start_point_id) not in self.line_mapping \
            and start_point.outbound_line_point is None \
            and end_point.inbound_line_point is None

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

                        inbound_point = self.get_point_by_id(point.inbound_line_point)
                        inbound_point.outbound_line_point = None
                        point.inbound_line_point = None
                        break

            if point.outbound_line_point is not None:
                for key, value in self.line_mapping.items():
                    if (id[0], point.outbound_line_point) == value:
                        self.line_mapping.pop(key)
                        self.delete(key)
                        print(f"deleted line {key}!")

                        outbound_point = self.get_point_by_id(point.outbound_line_point)
                        outbound_point.inbound_line_point = None
                        point.outbound_line_point = None
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
    def __init__(self, x, y, id, points = None):
        self.x, self.y = x, y
        self.id = id
        self.points = points

        self.inbound_line_point = None
        self.outbound_line_point = None

        self.inbound_bezier_anchor = None
        self.outbound_bezier_anchor = None

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError()

    def __setattr__(self, name, value):
        if name == "inbound_line_point":
            pass
            #calculate_bezier_anchors(self.p0, self, None)
        self.__dict__[name] = value
        return self.__dict__[name]

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
            point = self.pow3arg * t ** 3 + self.pow2arg * t ** 2 + self.pow1arg * t + self.p0
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
    points = []
    a = Point(1, 1, 0, points)
    points.append(a)
    b = Point(3, 3, 1, points)
    points.append(b)
    c = Point(5, 5, 2, points)
    points.append(c)
    p0, p1 = calculate_bezier_anchors(None, b, c)
    print(str(p0) + " " + str(p1))
    print(tuple(a))

    root = App()

    root.mainloop()

if __name__ == '__main__':
    main()
