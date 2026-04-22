from livewires import games, color
import NavigationButton as NB
import Vertex as VE
import Edge as ED
import random
import GraphAlgorithm as GA
import AlgorithmDisplay as AD
import MyText as MT

games.init(screen_width = 832, screen_height = 624, fps = 50)

####################################
# IDs:
#   0 - PhantomMouse
#   1 - MyText
####################################

####################################
# States:
#   0 - Not entered application
#   1 - Choose left branch size (1 - 10)
#   2 - Choose right branch size (1 - 10)
#   3 - Choose edges (manually or randomly)
#   4 - If choosing edges manually, make choices on provided bipartite graph
#   5 - Choose operation after choosing edges manually:
#         - automatically find a maximum matching
#         - find a maximum matching manually
#         - watch procedure of algorithm to find a maximum matching
#         - watch procedure of algorithm to find a maximum matching with steps
#   6 - Choose operation after choosing edges randomly:
#         - automatically find a maximum matching
#         - find a maximum matching manually
#         - watch procedure of algorithm to find a maximum matching
#         - watch procedure of algorithm to find a maximum matching with steps
#   7 - Execute graph operation (edges chosen manually)
#   8 - Execute graph operation (edges chosen randomly)
#   9 - If manual, automatically find MM
#  10 - If manual, watch algorithm to find MM
#  11 - If manual, watch algorithm to find MM with steps
#  12 - If random, automatically find MM
#  13 - If random, watch algorithm to find MM
#  14 - If random, watch algorithm to find MM with steps
####################################

# this class is used to check mouse hovers by having a very small sprite image
# follow the path of the mouse
class PhantomMouse(games.Sprite):
    def __init__(self, sprite_image):
        super(PhantomMouse, self).__init__(image = sprite_image)
        self.id = 0

    def update(self):
        self.x = games.mouse.x
        self.y = games.mouse.y


# class to monitor changes in input; this class is loosely based on the 'Game'
# class of the final astrocrash game described on page 402 of 'Python
# Programming for the Absolute Beginner, Third Edition', by Michael Dawson,
# Chapter 12: Sound, Animation, and Program Development: The Astrocrash Game
class Responses(object):
    def __init__(self):
        self.state = 0
        self.main_text_sprite = None # Text sprite for main content
        self.button_list = [] # list of navigation buttons
        self.text_list = [] # list of text sprites appearing on buttons
        self.left_size = 0 # size of the left branch of the bipartite graph
        self.right_size = 0 # size of the right branch of the bipartite graph
        self.left_branch = [] # list of vertex objects in left branch
        self.right_branch = [] # list of vertex objects in right branch
        self.left_vertex = -1 # id of selected left vertex
        self.right_vertex = -1 # id of selected right vertex
        self.edges = [] # the list of edge sprite objects which appear on screen
        self.left_neighbors = [] # list of adjacency lists for left branch
        self.right_neighbors = [] # list of adjacency lists for right branch
        self.hovered_edges = [] # list of all edges that are hovered over
        self.matching_list = [] # list of edge objects in the matching
        # whether congratulation text for finding a perfect matching appears
        # on screen
        self.has_congratulation = False
        self.congratulation = None # text sprite showing congratulations
        self.display = None # AlgorithmDisplay object
        self.pause_button = None
        self.pause_text = None
        # whether a reference matching has been generated
        self.has_generated_matching = False
        self.full_matching = [] # reference matching
        self.forward_button = None
        self.forward_text = None
        self.backward_button = None
        self.backward_text = None

    # check for a maximum matching
    def has_maximum_matching(self):
        if (not self.has_generated_matching):
            self.full_matching = GA.maximum_matching(self.left_size,
                                                     self.right_size,
                                                     self.left_neighbors)
            self.has_generated_matching = True
        return (len(self.full_matching) == len(self.matching_list))

    # set a congratulatory message on the screen for finding a maximum matching
    def set_congratulation(self):
        self.congratulation = MT.MyText('You found a maximum matching!', 30,
                                        color.black, 630, 150)
        games.screen.add(self.congratulation)
        self.has_congratulation = True

    # remove a congratulatory message on the screen
    def remove_congratulation(self):
        if (self.congratulation):
            self.congratulation.destroy()
            self.congratulation = None
        self.has_congratulation = False

    # set the currently selected vertex of a branch
    def set_vertex(self, branch, vertex_number):
        if (branch == 'left'):
            for vertex in self.left_branch:
                if (vertex.data == self.left_vertex):
                    vertex.unselect()
                    break
            self.left_vertex = vertex_number
        else:
            for vertex in self.right_branch:
                if (vertex.data == self.right_vertex):
                    vertex.unselect()
                    break
            self.right_vertex = vertex_number

    # unselect all vertices in transition from state 4 to states 3, 5
    def unselect_all(self):
        for vertex in self.left_branch:
            if (vertex.is_selected):
                vertex.unselect()
            vertex.set_image(vertex.plain_image)
        for vertex in self.right_branch:
            if (vertex.is_selected):
                vertex.unselect()
            vertex.set_image(vertex.plain_image)
        # make sure that there is not a currently selected left or right vertex
        self.left_vertex = -1
        self.right_vertex = -1

    # toggle the existence of an edge between the current left vertex and the
    # current right vertex
    def toggle_edge(self):
        is_present = False
        selected_edge = None
        for edge in self.edges:
            if ((edge.left_vertex == self.left_vertex) and
                (edge.right_vertex == self.right_vertex)):
                is_present = True
                edge.destroy()
                selected_edge = edge
                break
        if (is_present):
            self.edges.remove(selected_edge)
            # update adjacency lists
            self.left_neighbors[self.left_vertex].remove(self.right_vertex)
            self.right_neighbors[self.right_vertex].remove(self.left_vertex)
        else:
            new_edge = ED.Edge(self, self.left_vertex, self.right_vertex,
                               self.left_size, self.right_size)
            games.screen.add(new_edge)
            self.edges.append(new_edge)
            # update adjacency lists
            self.left_neighbors[self.left_vertex].append(self.right_vertex)
            self.right_neighbors[self.right_vertex].append(self.left_vertex)
            # re-sort lists
            self.left_neighbors[self.left_vertex].sort()
            self.right_neighbors[self.right_vertex].sort()
        # unselect current left and right vertices and set to -1
        self.left_branch[self.left_vertex].unselect()
        self.right_branch[self.right_vertex].unselect()
        self.left_vertex = -1
        self.right_vertex = -1

    # remove all buttons from the screen
    def clear_buttons(self):
        for b in self.button_list:
            b.destroy() # remove the corresponding sprite from the screen
        self.button_list = []
        for t in self.text_list:
            t.destroy() # remove the corresponding text sprite from the screen
        self.text_list = []
        if (self.forward_button):
            self.forward_button.destroy()
            self.forward_button = None
            self.forward_text.destroy()
            self.forward_text = None
        if (self.backward_button):
            self.backward_button.destroy()
            self.backward_button = None
            self.backward_text.destroy()
            self.backward_text = None

    # change text
    def reset_text(self, new_text):
        if (self.main_text_sprite):
            self.main_text_sprite.set_value(new_text)
        else:
            self.main_text_sprite = MT.MyText(new_text, 30, color.black, 600,
                                              30)
            games.screen.add(self.main_text_sprite)

    # if the left branch size or right branch size has been changed, change
    # the data entries for self.left_branch and self.right_branch
    def reset_branches_data(self, new_left_size, new_right_size):
        self.left_neighbors = []
        self.right_neighbors = []
        for i in range(new_left_size):
            self.left_neighbors.append([])
        for i in range(new_right_size):
            self.right_neighbors.append([])

    # like the above function, if the left branch size or right branch size has
    # been changed, delete all edges in the graph
    def delete_all_edges(self):
        for edge in self.edges:
            edge.destroy()
        self.edges = []

    # place all buttons (with their corresponding text) on screen, based on the
    # contents of self.button_list and self.text_list
    def render_buttons(self):
        for b in self.button_list:
            games.screen.add(b)
        for t in self.text_list:
            games.screen.add(t)

    # set up the back button for the state; this function will not render the
    # button to the screen, just include the associated button and text in the
    # corresponding lists
    def set_back_button(self, button_image, hovered_image, to_state):
        self.button_list.append(NB.NavigationButton(self, button_image,
                                                    hovered_image, 600, 510, -1,
                                                    to_state))
        self.text_list.append(MT.MyText('Go Back', 20, color.black, 600, 510))

    # set up number buttons in states for choosing left and right branch sizes
    def set_number_buttons(self, image, hovered_image, to_state):
        for i in range(5):
            for j in range(2):
                self.button_list.append(NB.NavigationButton(self, image,
                                                            hovered_image,
                                                            550 + 150 * j,
                                                            90 + 55 * i,
                                                            2*i + j + 1,
                                                            to_state))
                self.text_list.append(MT.MyText(str(2*i + j + 1), 20,
                                                color.black, 550 + 150 * j,
                                                90 + 55 * i))

    # add edge to data list
    def add_edge_data(self, left_vertex, right_vertex):
        self.left_neighbors[left_vertex].append(right_vertex)
        self.left_neighbors[left_vertex].sort()
        self.right_neighbors[right_vertex].append(left_vertex)
        self.right_neighbors[right_vertex].sort()

    # add edge to data list and screen
    def add_edge_screen(self, left_vertex, right_vertex):
        new_edge = ED.Edge(self, left_vertex, right_vertex, self.left_size,
                           self.right_size)
        self.edges.append(new_edge)
        games.screen.add(new_edge)

    # choose the edges that will appear randomly
    def set_random_edges(self):
        self.reset_branches_data(self.left_size, self.right_size)
        self.delete_all_edges()
        for i in range(self.left_size):
            for j in range(self.right_size):
                if (random.randrange(5) <= 1):
                    self.add_edge_data(i, j)
                    self.add_edge_screen(i, j)

    # reset all edges' appearance so that they do not appear selected
    def unselect_all_edges(self):
        for edge in self.edges:
            edge.set_image(edge.edge_image)
            edge.hovered = False
            edge.is_selected = False
        self.matching_list = []

    # include initial application graphics
    def initialize_board(self):
        self.state = 1
        background = games.load_image("images/bady-qb-42758-unsplash.jpg")
        games.screen.background = background
        self.set_left_branch_query()
        games.screen.mainloop()

    # to state 1
    def set_left_branch_query(self):
        self.state = 1
        self.reset_text('Left branch size:')
        self.clear_buttons()
        button_image = games.load_image("images/button.png")
        hovered_image = games.load_image("images/hovered-button.png")

        self.set_number_buttons(button_image, hovered_image, 2)
        self.render_buttons()

    # remove all vertices in a single branch from the corresponding array and
    # also remove them from the screen
    def erase_branch(self, branch):
        if (branch == 'left'):
            for vertex in self.left_branch:
                vertex.destroy()
                self.left_branch = []
        else:
            for vertex in self.right_branch:
                vertex.destroy()
                self.right_branch = []

    # set attributes about a branch size and vertex list; also set vertices
    # on screen
    def set_branch_bipartite(self, data, branch):
        start = 270 - 60 * int((data - 1) / 2)
        if (branch == 'left'):
            self.left_size = data
            self.erase_branch('left')
            for i in range(data):
                self.left_branch.append(VE.Vertex(self, 60, start + 60 * i, i,
                                                  'left'))
            for vertex in self.left_branch:
                games.screen.add(vertex)
        else:
            self.right_size = data
            self.erase_branch('right')
            for i in range(data):
                self.right_branch.append(VE.Vertex(self, 400, start + 60 * i,
                                                   i, 'right'))
            for vertex in self.right_branch:
                games.screen.add(vertex)
     

    # to state 2
    def set_right_branch_query(self, data):
        self.state = 2
        self.reset_text('Right branch size:')
        self.clear_buttons()
        button_image = games.load_image("images/button.png")
        hovered_image = games.load_image("images/hovered-button.png")

        self.set_number_buttons(button_image, hovered_image, 3)
        self.set_back_button(button_image, hovered_image, 1)
        self.render_buttons()
        if not (data == -1):
            self.set_branch_bipartite(data, 'left')
            

    # to state 3
    def set_edge_choice_query(self, data):
        self.state = 3
        self.reset_text('How do you want to choose edges?')
        self.clear_buttons()
        button_image = games.load_image("images/button.png")
        hovered_image = games.load_image("images/hovered-button.png")
        self.button_list.append(NB.NavigationButton(self, button_image,
                                                    hovered_image, 600, 150, 5,
                                                    4))
        self.text_list.append(MT.MyText('Manually', 20, color.black, 600, 150))
        self.button_list.append(NB.NavigationButton(self, button_image,
                                                    hovered_image, 600, 240, 6,
                                                    6))
        self.text_list.append(MT.MyText('Randomly', 20, color.black, 600, 240))
        self.set_back_button(button_image, hovered_image, 2)
        self.render_buttons()
        if not (data == -1):
            self.set_branch_bipartite(data, 'right')
        # unselect any selected vertices
        self.unselect_all()

    # to state 4
    def set_manual_edge_choice_query(self):
        if (self.state == 3):
            self.delete_all_edges()
            self.reset_branches_data(self.left_size, self.right_size)
        self.state = 4
        self.has_generated_matching = False
        self.reset_text('Make your edge choices on the graph.')
        if (self.state == 4):
            self.main_text_sprite.set_x(620)
        self.clear_buttons()
        button_image = games.load_image("images/button.png")
        hovered_image = games.load_image("images/hovered-button.png")
        self.button_list.append(NB.NavigationButton(self, button_image,
                                                    hovered_image, 600, 150, 7,
                                                    5))
        self.text_list.append(MT.MyText('Done', 20, color.black, 600, 150))
        self.set_back_button(button_image, hovered_image, 3)
        self.render_buttons()

    # remove text from displays for states 10 and 13 when transitioning back
    # to states 5 and 6, respectively
    def remove_step_text(self):
        if (self.display):
            self.display.title_text.destroy()
            self.display.statement_text_A.destroy()
            self.display.statement_text_B.destroy()
            self.display.statement_text_C.destroy()
            self.display.destroy()
            self.display = None

    # remove option buttons for states 10,11,13,14
    def remove_option_buttons(self):
        if (self.pause_button):
            self.pause_button.destroy()
            self.pause_button = None
            self.pause_text.destroy()
            self.pause_text = None
        if (self.forward_button):
            self.forward_button.destroy()
            self.forward_button = None
            self.forward_text.destroy()
            self.forward_text = None
        if (self.backward_button):
            self.backward_button.destroy()
            self.backward_button = None
            self.backward_text.destroy()
            self.backward_text = None

    # to state 5
    def manual_operations_query(self):
        self.state = 5
        self.reset_text('Choose Procedure For')
        self.clear_buttons()
        self.remove_step_text()
        self.unselect_all()
        self.unselect_all_edges()
        self.remove_option_buttons()
        # add additional line of prompt text
        self.text_list.append(MT.MyText('Maximal Matching (MM).', 30,
                                        color.black, 620, 60))
        button_image = games.load_image("images/button.png")
        hovered_image = games.load_image("images/hovered-button.png")
        long_button_image = games.load_image("images/long-button.png")
        hovered_long_image = games.load_image("images/hovered-long-button.png")
        self.button_list.append(NB.NavigationButton(self, long_button_image,
                                                    hovered_long_image, 600,
                                                    150, 2, 7))
        self.text_list.append(MT.MyText('Find MM Manually', 20, color.black,
                                        600, 150))
        self.button_list.append(NB.NavigationButton(self, long_button_image,
                                                    hovered_long_image, 600,
                                                    240, 1, 9))
        self.text_list.append(MT.MyText('Automatically Find MM', 20,
                                        color.black, 600, 240))
        self.button_list.append(NB.NavigationButton(self, long_button_image,
                                                    hovered_long_image, 600,
                                                    330, 3, 10))
        self.text_list.append(MT.MyText('Watch Algorithm To Find MM', 20,
                                        color.black, 600, 330))
        self.button_list.append(NB.NavigationButton(self, long_button_image,
                                                    hovered_long_image, 600,
                                                    420, 4, 11))
        self.text_list.append(MT.MyText('Watch Algorithm To Find MM With Steps',
                                        20, color.black, 600, 420))
        self.set_back_button(button_image, hovered_image, 4)
        self.render_buttons()
        if (self.has_congratulation):
            self.remove_congratulation()
        self.matching_list = []

    # to state 6
    def random_operations_query(self):
        if (self.state == 3):
            self.set_random_edges()
        self.state = 6
        self.reset_text('Choose Procedure For')
        self.has_generated_matching = False
        self.clear_buttons()
        self.remove_option_buttons()
        self.remove_step_text()
        self.unselect_all()
        self.unselect_all_edges()
        # add additional line of prompt text
        self.text_list.append(MT.MyText('Maximal Matching (MM).', 30,
                                        color.black, 600, 60))
        button_image = games.load_image("images/button.png")
        hovered_image = games.load_image("images/hovered-button.png")
        long_button_image = games.load_image("images/long-button.png")
        hovered_long_image = games.load_image("images/hovered-long-button.png")
        self.button_list.append(NB.NavigationButton(self, long_button_image,
                                                    hovered_long_image, 600,
                                                    150, 2, 8))
        self.text_list.append(MT.MyText('Find MM Manually', 20, color.black,
                                        600, 150))
        self.button_list.append(NB.NavigationButton(self, long_button_image,
                                                    hovered_long_image, 600,
                                                    240, 1, 12))
        self.text_list.append(MT.MyText('Automatically Find MM', 20,
                                        color.black, 600, 240))
        self.button_list.append(NB.NavigationButton(self, long_button_image,
                                                    hovered_long_image, 600,
                                                    330, 3, 13))
        self.text_list.append(MT.MyText('Watch Algorithm To Find MM', 20,
                                        color.black, 600, 330))
        self.button_list.append(NB.NavigationButton(self, long_button_image,
                                                    hovered_long_image, 600,
                                                    420, 4, 14))
        self.text_list.append(MT.MyText('Watch Algorithm To Find MM With Steps',
                                        20, color.black, 600, 420))
        self.set_back_button(button_image, hovered_image, 3)
        self.render_buttons()
        if (self.has_congratulation):
            self.remove_congratulation()
        self.matching_list = []

    # reset screen for the algorithm operation
    def prepare_operations(self, return_state):
        self.reset_text('')
        self.clear_buttons()
        button_image = games.load_image("images/button.png")
        hovered_image = games.load_image("images/hovered-button.png")
        self.set_back_button(button_image, hovered_image, return_state)
        left_start = 270 - 60 * int((self.left_size - 1) / 2)
        right_start = 270 - 60 * int((self.right_size - 1) / 2)
        for i in range(self.left_size):
            self.text_list.append(MT.MyText(str(i), 30, color.black, 30,
                                            left_start + 60 * i))
        for i in range(self.right_size):
            self.text_list.append(MT.MyText(str(i), 30, color.black, 430,
                                            right_start + 60 * i))
        self.render_buttons()
    
    # to state 7
    def execute_manual_find_manual(self):
        self.state = 7
        self.prepare_operations(5)

    # to state 8
    def execute_random_find_manual(self):
        self.state = 8
        self.prepare_operations(6)

    # update matching_list based on results of graph algorithm
    def update_matching_list(self, edge_arr):
        self.matching_list = []
        for (a,b) in edge_arr:
            self.matching_list.append(ED.Edge(self, a, b, self.left_size,
                                              self.right_size))

    # to state 9
    def execute_manual_find_automatically(self):
        self.state = 9
        self.prepare_operations(5)
        edge_arr = GA.maximum_matching(self.left_size, self.right_size,
                                       self.left_neighbors)
        self.update_matching_list(edge_arr)

    # set up pause button
    def set_pause_button(self):
        button_image = games.load_image("images/button.png")
        self.pause_button = games.Sprite(image = button_image, x = 600, y = 300)
        self.pause_text = MT.MyText('Pause', 20, color.black, 600, 300)
        games.screen.add(self.pause_button)
        games.screen.add(self.pause_text)

    # to state 10
    def execute_manual_algorithm(self):
        self.state = 10
        self.prepare_operations(5)
        self.display = AD.AlgorithmDisplay(self, False)
        games.screen.add(self.display)
        self.set_pause_button()

    def set_step_buttons(self):
        button_image = games.load_image("images/button.png")
        self.forward_button = games.Sprite(image = button_image, x = 680,
                                           y = 300, is_collideable = False)
        self.backward_button = games.Sprite(image = button_image, x = 530,
                                            y = 300)
        self.forward_text = MT.MyText('Forward', 20, color.black, 680, 300)
        self.backward_text = MT.MyText('Backward', 20, color.black, 530, 300)
        games.screen.add(self.forward_button)
        games.screen.add(self.backward_button)
        games.screen.add(self.forward_text)
        games.screen.add(self.backward_text)

    # to state 11
    def execute_manual_algorithm_steps(self):
        self.state = 11
        self.prepare_operations(5)
        self.display = AD.AlgorithmDisplay(self, True)
        games.screen.add(self.display)
        self.set_step_buttons()

    # to state 12
    def execute_random_find_automatically(self):
        self.state = 12
        self.prepare_operations(6)
        edge_arr = GA.maximum_matching(self.left_size, self.right_size,
                                       self.left_neighbors)
        self.update_matching_list(edge_arr)

    # to state 13
    def execute_random_algorithm(self):
        self.state = 13
        self.prepare_operations(6)
        self.display = AD.AlgorithmDisplay(self, False)
        games.screen.add(self.display)
        self.set_pause_button()

    # to state 14
    def execute_random_algorithm_steps(self):
        self.state = 14
        self.prepare_operations(6)
        self.display = AD.AlgorithmDisplay(self, True)
        games.screen.add(self.display)
        self.set_step_buttons()

    def advance(self, new_state, data):
        if (new_state == 1):
            self.set_left_branch_query()
        elif (new_state == 2):
            self.set_right_branch_query(data)
        elif (new_state == 3):
            self.set_edge_choice_query(data)
        elif (new_state == 4):
            self.set_manual_edge_choice_query()
        elif (new_state == 5):
            self.manual_operations_query()
        elif (new_state == 6):
            self.random_operations_query()
        elif (new_state == 7):
            self.execute_manual_find_manual()
        elif (new_state == 8):
            self.execute_random_find_manual()
        elif (new_state == 9):
            self.execute_manual_find_automatically()
        elif (new_state == 10):
            self.execute_manual_algorithm()
        elif (new_state == 11):
            self.execute_manual_algorithm_steps()
        elif (new_state == 12):
            self.execute_random_find_automatically()
        elif (new_state == 13):
            self.execute_random_algorithm()
        elif (new_state == 14):
            self.execute_random_algorithm_steps()
        else:
            print('hello')


def main():
    # set up sprite to follow mouse path, so as to register sprite overlaps
    phantom_mouse_image = games.load_image("images/phantom-pizza.bmp")
    pm = PhantomMouse(phantom_mouse_image)
    games.screen.add(pm)

    # object to control responses to buttons and navigation through options
    controller = Responses()
    controller.initialize_board()

main()
