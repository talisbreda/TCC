import copy

# data for the appearance of text, vertex colors, and edge colors at a specific
# step of the algorithm

# Note: all lists are of numbers corresponding to vertex and edge objects, not
# the vertex or edge objects themselves

class FrameRecord(object):
    def __init__(self, title_text, statement_text_A, statement_text_B,
                 statement_text_C, red_edges, green_edges, black_edges,
                 blue_vertices, yellow_vertices, purple_vertices,
                 left_black_vertices, right_black_vertices):
        self.title_text = title_text
        self.statement_text_A = statement_text_A
        self.statement_text_B = statement_text_B
        self.statement_text_C = statement_text_C
        self.red_edges = copy.deepcopy(red_edges)
        self.green_edges = copy.deepcopy(green_edges)
        self.black_edges = copy.deepcopy(black_edges)
        self.blue_vertices = copy.deepcopy(blue_vertices)
        self.yellow_vertices = copy.deepcopy(yellow_vertices)
        self.purple_vertices = copy.deepcopy(purple_vertices)
        self.left_black_vertices = copy.deepcopy(left_black_vertices)
        self.right_black_vertices = copy.deepcopy(right_black_vertices)
