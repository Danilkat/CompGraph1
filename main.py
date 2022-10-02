import tkinter as tk

class CanvasSpline(tk.Canvas):
    pass

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple):
            return Point(self.x + other[0], self.y + other[1])
        raise TypeError(f"unsupported operand type(s) for +: {type(self)} and {type(other)}")

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        if isinstance(other, tuple):
            return Point(self.x - other[0], self.y - other[1])
        raise TypeError(f"unsupported operand type(s) for +: {type(self)} and {type(other)}")

    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)

    def __mul__(self, other):
        return Point(self.x * other, self.y * other)

    def __str__(self):
        return f"({self.x}, {self.y})"

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

def hit_point(event):
    print(event)

def main():
    a = Point(1, 1)
    b = Point(3, 3)
    c = Point(5, 5)
    p0, p1 = calculate_bezier_anchors(None, b, c)
    print(str(p0) + " " + str(p1))

    root = tk.Tk()

    # Label() it display box
    # where you can put any text.
    canva = tk.Canvas(root, width=400, height=400, bg='white')
    canva.pack()

    canva.bind('<Button-1>', hit_point)

    # running the main loop
    root.mainloop()

if __name__ == '__main__':
    main()
