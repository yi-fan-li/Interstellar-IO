import numpy as np
import pygame as pg

class Camera:
    def __init__(self, follow_obj, screen) -> None:
        self.obj = follow_obj
        self.screen = screen
        self.init_pos = follow_obj.pos.copy() + np.array([self.screen.get_size()[0]/2 - self.obj.pos[0], self.screen.get_size()[1]/2 - self.obj.pos[1]])# np.array([self.obj.pos[0] -self.screen.get_size()[0], self.obj.pos[1] - self.screen.get_size()[1]])
        self.offset = np.array([0, 0.0])
        
    def update(self):
        """
        Update camera position according to the player
        """
        print(self.offset)
        self.offset = self.obj.pos - self.init_pos
        
    def draw(self, objs):
        # pg.draw.circle(self.screen, (0, 0, 0), (self.screen.get_size()[0]/2, self.screen.get_size()[1]/2), self.obj.radius)
        for i in objs:
            if True:
                pg.draw.circle(self.screen, (0, 0, 0), (i.pos[0] - self.offset[0], i.pos[1] - self.offset[1]), i.radius)
            
        