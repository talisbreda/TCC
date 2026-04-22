from livewires import games
import constants

class Edge(games.Sprite):
    def __init__(self, responder, left_vertex, right_vertex, left_branch_size,
                 right_branch_size):
        left_y = 60 * left_vertex + 270 - 60 * int((left_branch_size - 1) / 2)
        right_y = 60 * right_vertex + 270 - 60 * int((right_branch_size - 1) / 2)
        stable_left_y = left_y
        stable_right_y = right_y
        offset = int((right_y - left_y) / 60)
        x_offset = 0
        y_offset = 0
        new_y = 0
        if (offset <= 0):
            (x_offset, y_offset) = constants.UP_OFFSETS[-offset]
            edge_image = games.load_image("images/up-edges/edge-" +
                                          str(-offset) + ".png")
            self.edge_image = edge_image
            hovered_image = games.load_image("images/hovered-up-edges/edge-" +
                                             str(-offset) + ".png")
            self.hovered_image = hovered_image
            selected_image = games.load_image("images/selected-up-edges/edge-" +
                                              str(-offset) + ".png")
            self.selected_image = selected_image
        else:
            (x_offset, y_offset) = constants.DOWN_OFFSETS[offset]
            edge_image = games.load_image("images/down-edges/edge-" +
                                          str(offset) + ".png")
            self.edge_image = edge_image
            hovered_image = games.load_image("images/hovered-down-edges/edge-" +
                                             str(offset) + ".png")
            self.hovered_image = hovered_image
            selected_image = games.load_image("images/selected-down-edges/" +
                                              "edge-" + str(offset) + ".png")
            self.selected_image = selected_image
        left_y += y_offset
        super(Edge, self).__init__(image = edge_image, x = 60 + x_offset,
                                   y = left_y, is_collideable = False)
        self.left_vertex = left_vertex
        self.right_vertex = right_vertex
        self.offset = offset
        self.hovered = False
        self.responder = responder
        # slope of edge on screen
        self.slope = (stable_right_y - stable_left_y) / 340
        # y-intercept of line through edge
        self.intercept = stable_left_y - 60 * self.slope
        self.is_selected = False
        self.is_counting = False
        self.step_count = 0

    def __str__(self):
        rep = '(' + str(self.left_vertex) + ', ' + str(self.right_vertex)
        rep += ')'
        return rep

    def update(self):
        if (self.is_counting):
            self.step_count += 1
            if (self.step_count == 20):
                self.is_counting = False
                self.step_count = 0
        else:
            if (((self.responder.state == 7) or (self.responder.state == 8))
                and (not self.hovered) and self.mouse_touching() and
                (not self.is_selected) and (not self.is_incident())):
                self.responder.hovered_edges.append(self)
                self.set_image(self.hovered_image)
                self.hovered = True
            elif ((self.hovered) and (not self.mouse_touching())):
                self.hovered = False
                self.responder.hovered_edges.remove(self)
                if (not self.is_selected):
                    self.set_image(self.edge_image)

            if (((self.responder.state == 7) or (self.responder.state == 8))
                and self.mouse_touching() and
                games.keyboard.is_pressed(games.K_SPACE) and
                (not self.is_selected) and (not self.is_incident())):
                self.is_selected = True
                self.is_counting = True
                self.responder.matching_list.append(self)
                self.set_image(self.selected_image)
                if (self.responder.has_maximum_matching()):
                    self.responder.set_congratulation()
            elif (((self.responder.state == 7) or (self.responder.state == 8))
                  and self.mouse_touching() and
                  games.keyboard.is_pressed(games.K_SPACE) and
                  self.is_selected):
                self.is_selected = False
                self.is_counting = True
                self.responder.matching_list.remove(self)
                self.set_image(self.edge_image)

            if (self.responder.has_congratulation and
                (not self.responder.has_maximum_matching())):
                self.responder.remove_congratulation()

            if (((self.responder.state == 9) or (self.responder.state == 12))
                and self.is_contained()):
                self.set_image(self.selected_image) 

    def mouse_touching(self):
        if (games.mouse.x < 60):
            return False
        elif (games.mouse.x > 400):
            return False
        function_val = games.mouse.x * self.slope + self.intercept
        if ((-10 > (function_val - games.mouse.y)) or
            ((function_val - games.mouse.y) > 10)):
            return False
        return True

    # check if the edge is incident to an edge already in the matching
    def is_incident(self):
        for edge in self.responder.matching_list:
            if ((self.left_vertex == edge.left_vertex) or
                (self.right_vertex == edge.right_vertex)):
                return True
        return False

    # check if edge is in the matching itself
    def is_contained(self):
        for edge in self.responder.matching_list:
            if ((self.left_vertex == edge.left_vertex) and
                (self.right_vertex == edge.right_vertex)):
                return True
        return False
