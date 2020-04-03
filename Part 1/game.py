import pygame as pg
import pymunk as pm
from pymunk import pygame_util

class Game():
	def __init__(self):
		self.caption = 'World of Doo'
		self.fps = 60
		self.camera_width = 400
		self.camera_height = 600

	def game_initialize(self):
		pg.init()
		camera = pg.display.set_mode((self.camera_width,self.camera_height))
		pg.display.set_caption(self.caption)
		clock = pg.time.Clock()

		pm.pygame_util.positive_y_is_up = False

		self.game_run(camera,clock)

	def game_run(self,camera,clock):

		draw_options = pm.pygame_util.DrawOptions(camera)

		space = pm.Space()
		space.gravity = (0.0,900.0)

		while True:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					quit()
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						quit()

			space.step(1/self.fps)

			camera.fill([250,250,250])

			space.debug_draw(draw_options)

			pg.display.flip()
			clock.tick(self.fps)


if __name__ == '__main__':
	new_game = Game()
	new_game.game_initialize()