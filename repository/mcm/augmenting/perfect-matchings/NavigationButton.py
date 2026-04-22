from livewires import games

class NavigationButton(games.Sprite):
    def __init__(self, responder, plain_image, hover_image, x, y, data,
                 destination_state):
        super(NavigationButton, self).__init__(image = plain_image, x = x,
                                               y = y, is_collideable = False)
        self.data = data # data value obtained from selected button
        # state to which button takes user
        self.destination_state = destination_state
        self.is_hovered = False # whether button is being hovered over
        self.is_selected = False # whether button has been pushed
        self.step_count = 0 # count number of steps since a button push
        self.responder = responder # navigation object from main.py
        self.plain_image = plain_image
        self.hover_image = hover_image

    def update(self):
        if (self.step_count < 20): # provide time between transitions
            self.step_count += 1
        else:
            mouse_touching = False
            for item in self.overlapping_sprites:
                if (item.id == 0):
                    mouse_touching = True
                    break
            if (mouse_touching and (not self.is_hovered)):
                self.is_hovered = True
                self.set_image(self.hover_image)
            elif ((not mouse_touching) and self.is_hovered):
                self.is_hovered = False
                self.set_image(self.plain_image)

            if (mouse_touching and games.keyboard.is_pressed(games.K_SPACE)):
                if ((self.responder.state == 1) and
                    (not (self.responder.left_size == self.data))):
                    self.responder.reset_branches_data(self.data,
                                                       self.responder.right_size)
                    self.responder.delete_all_edges()
                elif ((self.responder.state == 2) and
                      (not (self.responder.right_size == self.data)) and
                      (self.destination_state == 3)):
                    self.responder.reset_branches_data(self.responder.left_size,
                                                       self.data)
                    self.responder.delete_all_edges()
                self.responder.advance(self.destination_state, self.data)
