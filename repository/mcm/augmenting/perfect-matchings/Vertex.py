from livewires import games

class Vertex(games.Sprite):
    def __init__(self, responder, x, y, data, branch):
        vertex_image = games.load_image("images/vertex.png")
        hovered_image = games.load_image("images/hovered-vertex.png")
        selected_image = games.load_image("images/selected-vertex.png")
        if (branch == 'left'):
            unmatched_image = games.load_image("images/vertex-left-unmatched" +
                                               ".png")
        else:
            unmatched_image = games.load_image("images/vertex-right-unmatched" +
                                               ".png")
        in_s = games.load_image("images/vertex-in-s.png")
        super(Vertex, self).__init__(image = vertex_image, x = x, y = y,
                                     is_collideable = False)
        self.data = data # number of vertex in branch
        self.branch = branch # which branch: 'left' or 'right'
        self.plain_image = vertex_image
        self.hovered_image = hovered_image
        self.selected_image = selected_image
        self.unmatched_image = unmatched_image
        self.in_s = in_s
        self.is_selectable = False # whether the vertex may be selected
        self.responder = responder
        self.step_count = 0 # counter to give time between button selections
        self.is_counting = False # whether counter is currently incrementing
        self.is_hovered = False # whether the mouse is hovering over vertex
        self.is_selected = False # whether the vertex is currently selected

    # if the vertex is selected and must become unselected
    def unselect(self):
        self.is_selected = False
        self.is_counting = True
        self.set_image(self.plain_image)

    def update(self):
        if (self.is_counting):
            self.step_count += 1
            if (self.step_count == 20):
                self.is_counting = False
                self.step_count = 0
        else:
            mouse_touching = False
            for item in self.overlapping_sprites:
                if (item.id == 0):
                    mouse_touching = True
                    break
            # hoverings
            if (mouse_touching and (not self.is_hovered) and
                (self.responder.state == 4) and (not self.is_selected)
                and (not self.is_counting)):
                self.is_hovered = True
                self.set_image(self.hovered_image)
            elif ((not mouse_touching) and self.is_hovered and
                  (not self.is_selected) and (self.responder.state == 4)):
                self.is_hovered = False
                self.set_image(self.plain_image)
            # selection
            if (mouse_touching and (not self.is_selected) and
                games.keyboard.is_pressed(games.K_SPACE) and
                (not self.is_counting) and (self.responder.state == 4)):
                self.is_selected = True
                self.is_counting = True
                self.set_image(self.selected_image)
                # unselect any already selected vertices in the same branch
                if (self.branch == 'left'):
                    self.responder.set_vertex('left', self.data)
                    # if a vertex from right branch has been selected, toggle
                    # edge between them
                    if (not (self.responder.right_vertex == -1)):
                        self.responder.toggle_edge()
                else:
                    self.responder.set_vertex('right', self.data)
                    if (not (self.responder.left_vertex == -1)):
                        self.responder.toggle_edge()
            elif (mouse_touching and self.is_selected and
                  games.keyboard.is_pressed(games.K_SPACE) and
                  (not self.is_counting) and (self.responder.state == 4)):
                self.unselect()
                if (self.branch == 'left'):
                    self.responder.set_vertex('left', -1)
                else:
                    self.responder.set_vertex('right', -1)
