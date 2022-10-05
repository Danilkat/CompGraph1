import tkinter as tk

class CanvasSpline(tk.Canvas):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.Points = []
        self.highlighted_point = None
        self.dragging = False
        self.start_point = None

        self.bind('<Button-1>', self.line_start)
        self.bind('<Button-1>', self.add_point, add="+")
        self.bind('<Motion>', self.move_point)
        self.bind('<ButtonRelease-1>', self.line_end)

    def move_point(self, event):
        if self.dragging:
            init_coords = self.coords(self.start_point)
            init_coords = (init_coords[0] + (init_coords[2] - init_coords[0] ) / 2, init_coords[1] + (init_coords[3] - init_coords[1]) / 2)
            self.move(self.start_point, event.x - init_coords[0], event.y - init_coords[1])
            if self.highlighted_point is not None and self.start_point == self.highlighted_point[1]:
                self.move(self.highlighted_point[0], event.x - init_coords[0], event.y - init_coords[1])


    def line_start(self, event):
        overlapped = self.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        if len(overlapped) > 0:
            self.dragging = True
            self.start_point = overlapped[0]
            print("user holding button!")

    def line_end(self, event):
        if self.dragging:
            print("user stopped holding a button!")
            self.dragging = False

    def add_point(self, event):
        overlapped = self.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        if len(overlapped) <= 0 and self.dragging == False:
            id = self.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill='black')
            self.tag_bind(id, '<Button-2>', self.del_point)
            self.tag_bind(id, '<Button-3>', self.del_point)
            self.tag_bind(id, '<Button-1>', self.highlight_point)
            self.Points.append(Point(event.x, event.y))

    def del_point(self, event):
        id = self.find_closest(event.x, event.y)
        if self.highlighted_point is not None and (id[0] == self.highlighted_point[0] or id[0] == self.highlighted_point[1]):
            self.delete(self.highlighted_point[0])
            self.delete(self.highlighted_point[1])
            self.highlighted_point = None
        else:
            self.delete(id[0])

    def highlight_point(self, event):
        if self.highlighted_point is not None:
            self.delete(self.highlighted_point[0])
        id = self.find_closest(event.x, event.y)
        coords = self.coords(id)
        highlighted_point = self.create_oval(coords[0], coords[1], coords[2], coords[3], outline = 'green', width = 2)
        print(len(self.find_all()))
        self.tag_bind(highlighted_point, '<Button-2>', self.del_point)
        self.tag_bind(highlighted_point, '<Button-3>', self.del_point)
        self.highlighted_point = (highlighted_point, id[0])


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError()

    def __add__(self, other):
        if isinstance(other, Point) or isinstance(other, tuple):
            return Point(self.x + other[0], self.y + other[1])
        raise TypeError(f"unsupported operand type(s) for +: {type(self)} and {type(other)}")

    def __sub__(self, other):
        if isinstance(other, Point) or isinstance(other, tuple):
            return Point(self.x - other[0], self.y - other[1])
        raise TypeError(f"unsupported operand type(s) for +: {type(self)} and {type(other)}")

    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)

    def __mul__(self, other):
        return Point(self.x * other, self.y * other)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

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
    a = Point(1, 1)
    b = Point(3, 3)
    c = Point(5, 5)
    p0, p1 = calculate_bezier_anchors(None, b, c)
    print(str(p0) + " " + str(p1))

    root = tk.Tk()

    global canva
    canva = CanvasSpline(root, width=400, height=400, bg='white')
    canva.pack()

    root.mainloop()

if __name__ == '__main__':
    main()
