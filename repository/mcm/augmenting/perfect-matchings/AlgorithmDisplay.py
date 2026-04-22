import GraphAlgorithm as GA
from livewires import games, color
import MyText as MT
import FrameRecord as FR
import copy

class AlgorithmDisplay(games.Sprite):
    def __init__(self, responder, steps):
        self.responder = responder
        self.steps = steps
        self.left_size = responder.left_size
        self.right_size = responder.right_size
        self.left_neighbors = responder.left_neighbors
        image = games.load_image('images/phantom-pizza.bmp')
        super(AlgorithmDisplay, self).__init__(image = image, x = 0, y = 0,
                                               is_collideable = False)
        self.is_counting = False
        self.ticker = 0
        self.ticker_adder = 1
        self.button_click = False
        self.backward_ticker = 0 # time to delay for re-push of backward button
        self.forward_ticker = 0 # time to delay for re-push of forward button
        self.forward_hover = False # whether forward button is hovered
        self.backward_hover = False # whether backward button is hovered
        self.button_ticker = 0 
        self.forward_click = True # whether forward button can be clicked
        self.backward_click = True # whether backward button can be clicked
        self.has_highlighted_edge = False # whether an edge is being examined
        self.highlighted_edge = None # currently examined edge
        self.matching = []
        self.title_text = MT.MyText(new_value =
                                    'First find a matching greedily.',
                                    new_size = 30, new_color = color.black,
                                    new_x = 630, new_y = 50)
        games.screen.add(self.title_text)
        self.statement_text_A = MT.MyText(new_value = '', new_size = 30,
                                          new_color = color.black, new_x = 600,
                                          new_y = 150)
        self.statement_text_B = MT.MyText(new_value = '', new_size = 30,
                                          new_color = color.black, new_x = 600,
                                          new_y = 180)
        self.statement_text_C = MT.MyText(new_value = '', new_size = 30,
                                          new_color = color.black, new_x = 600,
                                          new_y = 210)
        games.screen.add(self.statement_text_A)
        games.screen.add(self.statement_text_B)
        games.screen.add(self.statement_text_C)

        # state of algorithm: 1, 2, 3, or 4 (see meanings below)
        self.state = 1
        self.U = [] # list of left int vertices that are unmatched
        self.W = [] # list of right int vertices that are unmatched
        self.S = [] # list of reachable int vertices in left branch
        self.left_unmatched = [] # list of unmatched left vertex objects
        self.right_unmatched = [] # list of unmatched right vertex objects
        self.reachables = [] # list of reachable left vertex objects
        self.queue = [] # queue of vertex numbers to attempt to increase S from
        self.paths = [] # numerical lists of paths to vertices in S from U
        self.found_addition = 0
        self.left_index = 0
        self.right_index = 0
        self.edge_list = [] # list of edges to be highlighted
        self.flip = 0 # how to restore edge colors, 0 the same, 1 flipped

        # frame attributes for steps display
        self.frames = [] # list of FrameRecord objects
        self.tt = 'First find a matching greedily.'
        self.sA = ''
        self.sB = ''
        self.sC = ''
        self.re = []
        self.ge = []
        self.be = []
        self.bv = []
        self.yv = []
        self.pv = []
        self.lbv = [i for i in range(self.left_size)]
        self.rbv = [i for i in range(self.right_size)]

        for i in range(self.left_size):
            for j in self.left_neighbors[i]:
                self.be.append((i,j))
        self.add_frame()
        self.frame_index = 0
        if (self.steps):
            self.generate_steps()

    # return the edge object corresponding to a pair of numerical vertices
    def get_edge(self, left_vertex, right_vertex):
        for edge in self.responder.edges:
            if ((edge.left_vertex == left_vertex) and
                (edge.right_vertex == right_vertex)):
                return edge
        return None

    # return the vertex object corresponding to a number and branch
    def get_vertex(self, v_num, branch):
        if (branch == 'left'):
            for v in self.responder.left_branch:
                if (v.data == v_num):
                    return v
            return None
        else:
            for v in self.responder.right_branch:
                if (v.data == v_num):
                    return v
            return None

    def clear_highlights(self):
        self.clear_statement_text()
        for i in range(len(self.edge_list)):
            if (((i + self.flip) % 2) == 0):
                self.edge_list[i].set_image(self.edge_list[i].edge_image)
            else:
                self.edge_list[i].set_image(
                    self.edge_list[i].selected_image)
        self.flip = 0

    def clear_vertex_highlights(self):
        for v in self.responder.left_branch:
            v.set_image(v.plain_image)
        for v in self.responder.right_branch:
            v.set_image(v.plain_image)

    def add_frame(self):
        f = FR.FrameRecord(self.tt, self.sA, self.sB, self.sC,
                           copy.deepcopy(self.re), copy.deepcopy(self.ge),
                           copy.deepcopy(self.be), copy.deepcopy(self.bv),
                           copy.deepcopy(self.yv), copy.deepcopy(self.pv),
                           copy.deepcopy(self.lbv), copy.deepcopy(self.rbv))
        self.frames.append(f)

    # handle state 1
    def handle_A(self):
        if (self.left_index == self.left_size):
            self.state = 2
            if (self.steps):
                self.tt = 'Search For Ways To Augment Paths'
                self.sA = ''
                self.sB = ''
                self.sC = ''
            else:
                self.title_text.set_value('Search For Ways To Augment Paths')
                self.clear_statement_text()
                self.is_counting = True
        elif (not self.has_highlighted_edge):
            self.find_potential_edge()
        elif (self.has_highlighted_edge):
            self.add_or_reject_edge()

    # handle state 2
    def handle_B(self):
        if (self.steps):
            for i in range(len(self.edge_list)):
                r = (self.edge_list[i].left_vertex,
                     self.edge_list[i].right_vertex)
                if (((i + self.flip) % 2) == 0):
                    if (not (r in self.be)):
                        self.be.append(r)
                    if (r in self.re):
                        self.re.remove(r)
                    if (r in self.ge):
                        self.ge.remove(r)
                else:
                    if (not (r in self.re)):
                        self.re.append(r)
                    if (r in self.be):
                        self.be.remove(r)
                    if (r in self.ge):
                        self.ge.remove(r)
            self.sA = ''
            self.sB = ''
            self.sC = ''
            self.bv = []
            self.yv = []
            self.pv = []
            self.lbv = [i for i in range(self.left_size)]
            self.rbv = [i for i in range(self.right_size)]
            self.add_frame()
        else:
            self.clear_highlights()
            self.clear_vertex_highlights()
        self.edge_list = []
            
        if (len(self.matching) == self.left_size):
            self.state = 4
        else:
            self.left_unmatched = self.get_unmatched_left()
            self.right_unmatched = self.get_unmatched_right()
            self.reachables = self.get_unmatched_left()
            self.U = GA.set_left_unmatched(self.left_size, self.matching)
            self.W = GA.set_right_unmatched(self.right_size, self.matching)
            self.S = copy.deepcopy(self.U)
            self.queue = copy.deepcopy(self.U)
            self.paths = list(map(lambda x: [x], self.S))
            self.found_addition = 0
            self.display_unmatched()
            self.left_index = -1
            self.right_index = -1
            self.state = 3
            if (not self.steps):
                self.is_counting = True


    # handle state 3
    def handle_C(self):
        self.clear_highlights()
        self.edge_list = []
        while ((not self.found_addition) and
               ((len(self.queue) > 0) or
                (self.right_index <
                 len(self.left_neighbors[self.left_index])))):
            # iteration step
            if (not (self.left_index == -1)):
                self.right_index += 1
            while (((self.left_index == -1) or
                    (self.right_index >=
                     len(self.left_neighbors[self.left_index]))) and
                   (len(self.queue) > 0)):
                self.left_index = self.queue[0]
                self.queue = self.queue[1:]
                self.right_index = 0
            # check whether vertex adds to algorithm search at all
            if ((not (self.left_index == -1)) and
                (self.right_index < len(self.left_neighbors[self.left_index]))):
                left = self.left_index
                right = self.left_neighbors[left][self.right_index]
                if (not ((left, right) in self.matching)):
                    if (GA.right_is_already_matched(right, self.matching)):
                        v = GA.right_match(right, self.matching)
                        if (not (v in self.S)):
                            self.found_addition = 1
                    else:
                        self.found_addition = 2

        if (self.found_addition == 1):
            left = self.left_index
            right = self.left_neighbors[left][self.right_index]
            v = GA.right_match(right, self.matching)
            self.edge_list.append(self.get_edge(left, right))
            self.edge_list.append(self.get_edge(v, right))
            v_obj = self.get_object(v)
            self.queue.append(v)
            self.S.append(v)
            self.reachables.append(v_obj)
            left_path = GA.get_path(self.paths, left)
            v_path = copy.deepcopy(left_path)
            v_path.append(right)
            v_path.append(v)
            self.paths.append(v_path)
            self.found_addition = 0

            if (self.steps):
                self.sA = 'Add left vertex ' + str(v)
                self.sB = 'to S.'
                self.sC = ''
                for e in self.edge_list:
                    r = (e.left_vertex, e.right_vertex)
                    if (not (r in self.ge)):
                        self.ge.append(r)
                    if (r in self.re):
                        self.re.remove(r)
                    if (r in self.be):
                        self.be.remove(r)
                self.pv.append(v)
                self.lbv.remove(v)
                self.add_frame()
            else:
                for e in self.edge_list:
                    e.set_image(e.hovered_image)
                v_obj.set_image(v_obj.in_s)
                self.clear_statement_text()
                self.statement_text_A.set_value('Add left vertex ' + str(v))
                self.statement_text_B.set_value('to S.')
                self.is_counting = True
            self.state = 5

        elif (self.found_addition == 2):
            left = self.left_index
            right = self.left_neighbors[left][self.right_index]
            left_path = GA.get_path(self.paths, left)
            right_path = copy.deepcopy(left_path)
            right_path.append(right)
            for i in range(len(right_path) - 1):
                if ((i % 2) == 0):
                    self.edge_list.append(self.get_edge(right_path[i],
                                                        right_path[i+1]))
                else:
                    self.edge_list.append(self.get_edge(right_path[i+1],
                                                        right_path[i]))

            self.matching = GA.flip_path(right_path, self.matching)
            self.flip = 1
            if (self.steps):
                for e in self.edge_list:
                    r = (e.left_vertex, e.right_vertex)
                    self.ge.append(r)
                    if (r in self.re):
                        self.re.remove(r)
                    if (r in self.be):
                        self.be.remove(r)
                self.sA = 'Augment the path from left'
                self.sB = 'vertex ' + str(right_path[0]) + ' to right vertex '
                self.sB += str(right)
                self.sC = ''
                self.add_frame()
            else:
                for e in self.edge_list:
                    e.set_image(e.hovered_image)
                self.statement_text_A.set_value('Augment the path from left')
                self.statement_text_B.set_value('vertex ' + str(right_path[0])
                                                + ' to right vertex ' +
                                                str(right))
                self.statement_text_C.set_value('')
                self.is_counting = True
            self.state = 2

        else:
            self.state = 4

    # handle state 4
    def handle_D(self):
        if (self.steps):
            self.bv = []
            self.yv = []
            self.pv = []
            self.lbv = [i for i in range(self.left_size)]
            self.rbv = [i for i in range(self.right_size)]
            self.tt = ''
            self.sA = 'Maximum matching!'
            self.sB = ''
            self.sC = ''
            self.add_frame()
        else:
            self.clear_vertex_highlights()
            self.statement_text_A.set_value('Maximum matching!')
            self.title_text.set_value('')
    

    # handle state 5
    def handle_E(self):
        if (self.steps):
            self.sA = ''
            self.sB = ''
            self.sC = ''
            for i in range(len(self.edge_list)):
                r = (self.edge_list[i].left_vertex,
                     self.edge_list[i].right_vertex)
                if (((i + self.flip) % 2) == 0):
                    if (not r in self.be):
                        self.be.append(r)
                    if (r in self.ge):
                        self.ge.remove(r)
                    if (r in self.re):
                        self.re.remove(r)
                else:
                    if (not r in self.re):
                        self.re.append(r)
                    if (r in self.be):
                        self.be.remove(r)
                    if (r in self.ge):
                        self.ge.remove(r)
            self.add_frame()
        else:
            self.clear_highlights()
            self.is_counting = True
        self.edge_list = []
        self.state = 3


    # generate the frame list of all steps in the algorithm
    def generate_steps(self):
        while (not (self.state == 4)):
            if (self.state == 1):
                self.handle_A()
            elif (self.state == 2):
                self.handle_B()
            elif (self.state == 3):
                self.handle_C()
            elif (self.state == 5):
                self.handle_E()
        self.handle_D()


    # update the appearing graph with the frame data
    def show_graph(self, frame):
        self.title_text.set_value(frame.title_text)
        self.statement_text_A.set_value(frame.statement_text_A)
        self.statement_text_B.set_value(frame.statement_text_B)
        self.statement_text_C.set_value(frame.statement_text_C)
        for (a,b) in frame.red_edges:
            e = self.get_edge(a,b)
            e.set_image(e.selected_image)
        for (a,b) in frame.green_edges:
            e = self.get_edge(a,b)
            e.set_image(e.hovered_image)
        for (a,b) in frame.black_edges:
            e = self.get_edge(a,b)
            e.set_image(e.edge_image)
        for a in frame.blue_vertices:
            v = self.get_vertex(a, 'left')
            v.set_image(v.unmatched_image)
        for a in frame.yellow_vertices:
            v = self.get_vertex(a, 'right')
            v.set_image(v.unmatched_image)
        for a in frame.purple_vertices:
            v = self.get_vertex(a, 'left')
            v.set_image(v.in_s)
        for a in frame.left_black_vertices:
            v = self.get_vertex(a, 'left')
            v.set_image(v.plain_image)
        for a in frame.right_black_vertices:
            v = self.get_vertex(a, 'right')
            v.set_image(v.plain_image)
        
    # updates delays for clicking forward button
    def update_forward_ticker(self):
        if (not self.forward_click):
            self.forward_ticker += 1
            if (self.forward_ticker == 20):
                self.forward_ticker = 0
                self.forward_click = True

    # update delays for clicking backward button
    def update_backward_ticker(self):
        if (not self.backward_click):
            self.backward_ticker += 1
            if (self.backward_ticker == 20):
                self.backward_ticker = 0
                self.backward_click = True

    def set_forward_hover(self, forward_touching):
        if (forward_touching and (not self.forward_hover)):
            self.forward_hover = True
            hover_image = games.load_image('images/hovered-button.png')
            self.responder.forward_button.set_image(hover_image)
        elif ((not forward_touching) and self.forward_hover):
            self.forward_hover = False
            button_image = games.load_image('images/button.png')
            self.responder.forward_button.set_image(button_image)

    def set_backward_hover(self, backward_touching):
        if (backward_touching and (not self.backward_hover)):
            self.backward_hover = True
            hover_image = games.load_image('images/hovered-button.png')
            self.responder.backward_button.set_image(hover_image)
        elif ((not backward_touching) and self.backward_hover):
            self.backward_hover = False
            button_image = games.load_image('images/button.png')
            self.responder.backward_button.set_image(button_image)

    def set_forward_select(self, forward_touching):
        if (forward_touching and self.forward_click and
            games.keyboard.is_pressed(games.K_SPACE)):
            self.forward_click = False
            self.frame_index += 1
            if (self.frame_index >= len(self.frames)):
                self.frame_index = 0
            self.show_graph(self.frames[self.frame_index])

    def set_backward_select(self, backward_touching):
        if (backward_touching and self.backward_click and
            games.keyboard.is_pressed(games.K_SPACE)):
            self.backward_click = False
            self.frame_index -= 1
            if (self.frame_index < 0):
                self.frame_index = len(self.frames) - 1
            self.show_graph(self.frames[self.frame_index])

    # update operation for when steps are being shown
    def update_steps(self):
        forward_touching = False
        backward_touching = False
        if (self.responder.forward_button):
            for item in self.responder.forward_button.overlapping_sprites:
                if (item.id == 0):
                    forward_touching = True
                    break
        if (self.responder.backward_button):
            for item in self.responder.backward_button.overlapping_sprites:
                if (item.id == 0):
                    backward_touching = True
                    break
        self.set_forward_hover(forward_touching)
        self.set_backward_hover(backward_touching)
        self.set_forward_select(forward_touching)
        self.set_backward_select(backward_touching)
        self.update_forward_ticker()
        self.update_backward_ticker()

    def update(self):
        if (self.steps):
            self.update_steps()
        else:
            mouse_touching = False
            if (self.responder.pause_button):
                for item in self.responder.pause_button.overlapping_sprites:
                    if (item.id == 0):
                        mouse_touching = True
                        break

                if (mouse_touching):
                    hover_image = games.load_image("images/hovered-button.png")
                    self.responder.pause_button.set_image(hover_image)

                elif (not mouse_touching):
                    main_image = games.load_image("images/button.png")
                    self.responder.pause_button.set_image(main_image)
            
            if (self.button_click and games.keyboard.is_pressed(games.K_SPACE)
                and mouse_touching):
                self.button_click = False
                self.ticker_adder = 1 - self.ticker_adder
                if (self.ticker_adder == 0):
                    self.responder.pause_text.set_value('Play')
                else:
                    self.responder.pause_text.set_value('Pause')

            if (not self.button_click):
                self.button_ticker += 1
                if (self.button_ticker == 20):
                    self.button_ticker = 0
                    self.button_click = True

            if (self.is_counting):
                self.ticker += self.ticker_adder
                if (self.ticker == 100):
                    self.ticker = 0
                    self.is_counting = False

            elif (self.state == 1):
                self.handle_A()

            elif (self.state == 2):
                self.handle_B()

            elif (self.state == 3):
                self.handle_C()

            elif (self.state == 4):
                self.handle_D()

            elif (self.state == 5):
                self.handle_E()


    def clear_statement_text(self):
        self.statement_text_A.set_value('')
        self.statement_text_B.set_value('')
        self.statement_text_C.set_value('')

    def display_unmatched(self):
        if (self.steps):
            for vertex in self.left_unmatched:
                self.lbv.remove(vertex.data)
                self.bv.append(vertex.data)
            for vertex in self.right_unmatched:
                self.rbv.remove(vertex.data)
                self.yv.append(vertex.data)
                self.sA = 'Highlight unmatched left '
                self.sB = 'vertices in blue and unmatched '
                self.sC = 'right vertices in yellow.'
            self.add_frame()
        else:
            for vertex in self.left_unmatched:
                vertex.set_image(vertex.unmatched_image)
            for vertex in self.right_unmatched:
                vertex.set_image(vertex.unmatched_image)
            self.statement_text_A.set_value('Highlight unmatched left ')
            self.statement_text_B.set_value('vertices in blue and unmatched ')
            self.statement_text_C.set_value('right vertices in yellow.')

    def is_in_right_unmatched(self, vertex_number):
        for v in self.right_unmatched:
            if (v.data == vertex_number):
                return True
        return False

    # get the vertex object corresponding to a left vertex int
    def get_object(self, vertex_number):
        for v_obj in self.responder.left_branch:
            if (v_obj.data == vertex_number):
                return v_obj
        return None
    

    def get_unmatched_left(self):
        return list(filter(lambda x: not GA.left_is_already_matched(
            x.data, self.matching), self.responder.left_branch))

    def get_unmatched_right(self):
        return list(filter(lambda x: not GA.right_is_already_matched(
            x.data, self.matching), self.responder.right_branch))


    def find_potential_edge(self):
        while ((self.left_index < self.left_size) and
                   (len(self.left_neighbors[self.left_index]) == 0)):
                self.left_index += 1
        if ((self.left_index < self.left_size) and
            (self.right_index < len(self.left_neighbors[self.left_index]))):
            edge = self.get_edge(self.left_index,
                                 self.left_neighbors[self.left_index][self.right_index])
            self.has_highlighted_edge = True
            self.highlighted_edge = edge
            if (self.steps):
                r = (edge.left_vertex, edge.right_vertex)
                self.ge.append(r)
                self.be.remove(r)
                self.sA = 'Test if edge (' + str(edge.left_vertex) + ', '
                self.sA += str(edge.right_vertex) + ')'
                self.sB = 'can be added.'
                self.sC = ''
                self.add_frame()
            else:
                edge.set_image(edge.hovered_image)
                self.is_counting = True
                self.statement_text_A.set_value(
                    'Test if edge (' + str(edge.left_vertex) + ', ' +
                    str(edge.right_vertex) + ')')
                self.statement_text_B.set_value('can be added.')
                self.statement_text_C.set_value('')

    def add_or_reject_edge(self):
        if (GA.right_is_already_matched(self.highlighted_edge.right_vertex,
                                        self.matching)):
            if (self.right_index ==
                (len(self.left_neighbors[self.left_index]) - 1)):
                self.left_index += 1
                self.right_index = 0
            else:
                self.right_index += 1
            
            if (self.steps):
                r = (self.highlighted_edge.left_vertex,
                     self.highlighted_edge.right_vertex)
                if (r in self.re):
                    self.re.remove(r)
                if (r in self.ge):
                    self.ge.remove(r)
                if (not r in self.be):
                    self.be.append(r)
                self.sA = 'Right vertex '
                self.sA += str(self.highlighted_edge.right_vertex)
                self.sB = 'is already matched.'
                self.add_frame()
            else:
                self.highlighted_edge.set_image(
                    self.highlighted_edge.edge_image)
                self.statement_text_A.set_value(
                    'Right vertex ' + str(self.highlighted_edge.right_vertex))
                self.statement_text_B.set_value('is already matched.')
                self.is_counting = True
        else:
            self.matching.append((self.left_index,
                                  self.left_neighbors[self.left_index][self.right_index]))
            self.left_index += 1
            self.right_index = 0
            if (self.steps):
                r = (self.highlighted_edge.left_vertex,
                     self.highlighted_edge.right_vertex)
                if (r in self.be):
                    self.be.remove(r)
                if (r in self.ge):
                    self.ge.remove(r)
                if (not r in self.re):
                    self.re.append(r)
                self.sA = 'The edge was added!'
                self.sB = ''
                self.sC = ''
                self.add_frame()
            else:
                self.highlighted_edge.set_image(
                    self.highlighted_edge.selected_image)
                self.statement_text_A.set_value('The edge was added!')
                self.statement_text_B.set_value('')
                self.statement_text_C.set_value('')
                self.is_counting = True

        self.highlighted_edge = None
        self.has_highlighted_edge = False
