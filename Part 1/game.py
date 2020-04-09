import pygame as pg 
import pymunk as pm
from pymunk import pygame_util	# Модуль для отображения pymunk-симуляции на pygame-экран

class Game():
	'''
	Класс отвечающий за запуск игры и игровой цикл.'''
	def __init__(self):
		self.caption = 'World of Doo'
		self.fps = 60
		# Ширина и высота экрана игры:
		self.camera_width = 400
		self.camera_height = 600


	def game_initialize(self):
		'''
		Функция для запуска игры и создания тех объектов, которые
		не будут пересоздаваться при сбросе (перезапуске) игры с помощью клавиши R.'''

		pg.init()
		camera = pg.display.set_mode((self.camera_width,self.camera_height))
		pg.display.set_caption(self.caption)

		# Объект Clock для ограничения FPS и вывода значения FPS на экран.
		clock = pg.time.Clock()

		# Переворачиваем ось Y для правильного отображения Pymunk-симуляции.
		pm.pygame_util.positive_y_is_up = False

		self.game_run(camera,clock)

	def game_run(self,camera,clock):
		'''
		Функция для создания игровых тех объектов, которые будут
		созданы заново при сбросе (перезапуске) игры с помощью клавиши R.'''
		
		# Создаем объект Draw Options и передаем в него поверхность,
		# на которую будем отображать Pymunk-симуляцию.
		draw_options = pm.pygame_util.DrawOptions(camera)

		# Создаем пространство симуляции, позже добавим в него объекты
		space = pm.Space()

		# Устанавливаем ускорение свободного падения по оси Y.
		# 900, а не 9.8, как у поверхности Земли -- автор Pymunk
		# часто подчеркивает, что важно не точное соответствие реальности
		# (это игра, а не физические расчеты), а то, как выглядит движение
		# на экране. Нужно подобрать гравитацию (а затем и массы, коэффициенты трения Doo,
		# жесткости пружин), чтобы движение выглядело так, как задумано геймдизайнером(т.е Вами).
		space.gravity = (0.0,900.0)

		while True:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					quit()
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						quit()

			# Обновляем физическую симуляцию, сдвигая её
			# вперед во времени на 1/FPS секунд (в данном примере на 1/60 секунды).
			space.step(1/self.fps)

			camera.fill([250,250,250])

			# Вызываем функцию отображения пространства симуляции,
			# аргументом передаём ранее определенный объект Draw Options.
			space.debug_draw(draw_options)

			pg.display.flip()
			clock.tick(self.fps)


if __name__ == '__main__':
	new_game = Game()
	new_game.game_initialize()