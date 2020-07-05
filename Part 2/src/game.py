import pygame as pg 
import pymunk as pm
from pymunk import pygame_util
# Импортируем класс World из файла world
from world import World
# Импортируем класс ShapeCreator из файла shape_creator
from shape_creator import ShapeCreator

class Game():
	def __init__(self):
		self.caption 		= 'World of Doo'
		self.fps 			= 60
		self.camera_width 	= 400
		self.camera_height 	= 600


	def game_initialize(self):
		pg.init()
		camera = pg.display.set_mode((self.camera_width, self.camera_height))
		pg.display.set_caption(self.caption)

		clock = pg.time.Clock()

		# Добавляем в игру шрифт для вывода на экран различных надписей и подсказок
		font = pg.font.SysFont('Arial', 14)

		# Добавляем объект World для отображения всей игровой области
		world = World(self.camera_width, self.camera_height, camera)

		pm.pygame_util.positive_y_is_up = False

		self.game_run(camera, clock, font, world)

	def game_run(self, camera, clock, font, world):
		# Изменяем поверхность для отображения на world
		draw_options = pm.pygame_util.DrawOptions(world)

		space = pm.Space()

		space.gravity = (0.0,900.0)
		
		# Настраиваем число итераций физических расчетов для одного кадра игры
		# чем больше, тем точнее рассчитывается поведение объектов и меньше всяких отклонений
		# (объектов, проваливающихся сквозь пол и друг друга)
		# по умолчанию = 10.
		space.iterations = 20

		# Создадим экземпляр класса Shape Creator
		shape_creator = ShapeCreator(world, space)

		# Создадим пол = нижнюю границу игровой области:
		shape_creator.create_static_floor()

		# Создадим стены = боковые границы игровой области:
		shape_creator.create_static_wall(0, world.ground_y)
		shape_creator.create_static_wall(world.width-1, world.ground_y)

		while True:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					quit()
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						quit()
					# Сброс (перезапуск) игры при нажатии клавиши R
					if event.key == pg.K_r:
						self.restart(shape_creator)

				# Обрабатываем нажатие кнопок мыши
				if event.type == pg.MOUSEBUTTONDOWN:
					# Хватание свободного Ду при нажатии левой кнопки мыши (ЛКМ)
					if event.button == 1:
						mouse_pos = pg.mouse.get_pos()
						world.pick_free_doo(space, mouse_pos)

					# Cоздание свободного Ду при нажатии правой кнопки мыши (ПКМ)
					if event.button == 3:
						mouse_pos = pg.mouse.get_pos()
						shape_creator.create_free_doo(mouse_pos[0], mouse_pos[1])

				# Обрабатываем отпускание кнопок мыши
				if event.type == pg.MOUSEBUTTONUP:
					# Отпускание схваченного Ду при отпускании ЛКМ
					if event.button == 1:
						world.release_picked_doo()

			space.step(1/self.fps)

			# Удаляем свободных Ду, вылетевших за пределы игровой области (иногда бывает)
			shape_creator.remove_escaped_doos()

			# # Проверяем работает, ли удаление Ду:
			# # Выводим в консоли длины массивов
			#print(str(len(space.bodies)) + '    ' + str(len(world.free_doos)))

			# Перетаскивание схваченного Ду
			mouse_pos = pg.mouse.get_pos()
			world.move_picked_doo(mouse_pos)

			world.fill_me()

			# Объекты теперь отображаются на поверхности world
			space.debug_draw(draw_options)

			# Отобразить окружность у выделенного Ду
			world.draw_circle(mouse_pos, space)

			# Отобразим world на экране
			world.blit_me()

			
			# Выводим количество кадров в секунду (FPS) поверх всех других изображений.
			# FPS служит для грубой оценки производительности игры.
			# FPS будет уменьшаться при очень большом числе объектов в игре.
			# (метод .tick() объекта Clock ограничивает FPS сверху, но не снизу)
			self.show_fps(camera, clock, font)

			pg.display.flip()
			clock.tick(self.fps)

	def show_fps(self, camera, clock, font):
		'''
		Функция для отображения FPS игры на экране.
		Это позволит грубо оценивать производительность игры.'''

		# Значение FPS получаем с помощью метода get_fps() объекта Clock. 
		# Округляем значение FPS до 2 знаков после запятой с помощью format.
		# Создаем поверхность с изображением текста c помощью render().
		fps = font.render('{0:.2f}'.format(clock.get_fps()), True, [50,50,50])
		# Отображаем FPS на экране
		camera.blit(fps, [10,10])

	def restart(self, shape_creator):
		'''
		Функция, которая возврщает игру к исходному состоянию.
		Значительно облегчит тестирование игры.
		'''
		shape_creator.remove_all_doos()
		

if __name__ == '__main__':
	'''
	Если скрипт запущен самостоятельно, а не вызван из другого скрипта, то:'''
	# Создать объект класса Game
	game = Game()
	# Запустить игру
	game.game_initialize()