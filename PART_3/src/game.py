import pygame as pg 
import pymunk as pm
# Импортируем pygame_util, чтобы направление оси Y совпадало для pygame и pymunk
from pymunk import pygame_util
# Импортируем класс World из файла world
from world import World
# Импортируем класс ShapeCreator из файла shape_creator
from shape_creator import ShapeCreator
# Импортируем класс Graph из файла graph
from graph import Graph


class Game():
	""" Класс, отвечающий за инициализацию и запуск игры.

	Атрибуты:
	----------
	caption : str
		Название игры и заголовок окна игры.
	fps : int
		Верхняя граница частоты обновления кадров в [кадры/секунда].
	camera_width : int
		Ширина экрана игры в пикселях.
	camera_height : int
		Высота экрана игры в пикселях.
	"""
	def __init__(self):
		self.caption 		= 'World of Doo'
		self.fps 			= 60
		self.camera_width 	= 400
		self.camera_height 	= 600


	def game_initialize(self):
		""" Метод для инициализации pygame и запуска инициализации игры.

		Создаем окно (экран) игры с названием нашей игры.
		Создаем объект Clock для работы с частотой кадров.
		Добавляем в игру шрифт для вывода надписей и подсказок.
		Создаем игровую область.
		Переворачиваем ось Y в пространстве симуляции, чтобы она совпадала по направлению с осью Y в Pygame.
		Запускаем игру.
		"""
		pg.init()
		camera = pg.display.set_mode((self.camera_width, self.camera_height))
		pg.display.set_caption(self.caption)
		clock = pg.time.Clock()
		font = pg.font.SysFont('Arial', 14)
		world = World(self.camera_width, self.camera_height, camera)
		pm.pygame_util.positive_y_is_up = False
		self.game_run(camera, clock, font, world)

	def game_run(self, camera, clock, font, world):
		""" Метод для инициализации игровых объектов и запуска игрового цикла.

		Для этой функции сделал (избыточно) подробный комментарий.
		
		Аргументы:
		----------
		camera : pygame.Surface
			Окно (экран) игры. Поверхность для отображения остальных игровых элементов.
		clock : pygame.time.Clock
			Объект, который мы будем использовать для работы с частотой кадров в игре.
		font : pygame.font.Font
			Шрифт для вывода надписей и подсказок.
		world : World
			Игровая область. Используется для отображения пространства симуляции.
		"""
		# Будем отображать пространство симуляции на поверхность world.
		draw_options = pm.pygame_util.DrawOptions(world)
		# Создаем пространство симуляции.
		space = pm.Space()
		# Устанавливаем ускорение свободного падения вдоль оси Y.
		space.gravity = (0.0,900.0)
		# Настраиваем число итераций физических расчетов для одного кадра игры
		# чем больше, тем точнее рассчитывается поведение объектов и меньше всяких отклонений
		# (объектов, проваливающихся сквозь пол и друг друга)
		# по умолчанию = 10.
		space.iterations = 20
		# Создаем обработчики столкновений. В качестве аргументов передаем значения collision_type объектов.
		# С помощью pre_solve мы зададим правила взаимодействия указанных объектов при столкновении.
		# Обрабатываем столкновения свободных Ду с другими свободными Ду.
		ch1 = space.add_collision_handler(0,0)
		ch1.pre_solve = world.collide_doo_with_doo
		# Обрабатываем столкновения свободных Ду с фиксированными Ду.
		ch2 = space.add_collision_handler(0,1)
		ch2.pre_solve = world.collide_doo_with_doo
		# Обрабатываем столкновения фиксированных Ду с другими фиксированными Ду.
		ch3 = space.add_collision_handler(1,1)
		ch3.pre_solve = world.collide_doo_with_doo
		# Создадим экземпляр класса Shape Creator
		shape_creator = ShapeCreator(world, space)
		# Создадим пол = нижнюю границу игровой области:
		shape_creator.create_static_floor()
		# Создадим стены = боковые границы игровой области:
		shape_creator.create_static_wall(0, world.ground_y)
		shape_creator.create_static_wall(world.width-1, world.ground_y)
		# Создадим экземпляр класса Graph, описывающий башню.
		graph = Graph()
		# Создаем стартовую конструкцию (фундамент башни).
		shape_creator.create_start_construction(graph, 300)

		while True:
			# Получаем позицию мыши, чтобы не вызывать данный метод в других местах.
			mouse_pos = pg.mouse.get_pos()
			# Определяем, находится ли под курсором какой-нибудь свободный Ду.
			world.find_free_doo_under_cursor(space, mouse_pos)

			# Обрабатываем события с клавиатуры и мыши.
			for event in pg.event.get():
				if event.type == pg.QUIT:
					quit()
				# Обрабатываем нажатие клавиш.
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						quit()
					# Сброс (перезапуск) игры при нажатии клавиши R.
					if event.key == pg.K_r:
						self.restart(shape_creator, graph)
				# Обрабатываем нажатие кнопок мыши.
				if event.type == pg.MOUSEBUTTONDOWN:
					# Хватание свободного Ду при нажатии левой кнопки мыши (ЛКМ).
					if event.button == 1:
						world.pick_free_doo()
					# Cоздание свободного Ду при нажатии правой кнопки мыши (ПКМ)
					if event.button == 3:
						if world.shape_being_dragged is None and mouse_pos[1] < world.ground_y:
							shape_creator.create_free_doo(mouse_pos[0], mouse_pos[1])
				# Обрабатываем отпускание кнопок мыши
				if event.type == pg.MOUSEBUTTONUP:
					# Отпускание схваченного Ду при отпускании ЛКМ
					if event.button == 1:
						world.release_picked_doo(graph, shape_creator)

			space.step(1/self.fps)
			# Удаляем свободных Ду, вылетевших за пределы игровой области (иногда бывает).
			shape_creator.remove_escaped_doos()
			# Проверяем работает, ли удаление Ду:
			# Выводим в консоли длины массивов
			# print(str(len(space.bodies)) + '    ' + str(len(world.free_doos)))
			# Перетаскивание схваченного Ду
			world.move_picked_doo(mouse_pos)
			if world.shape_being_dragged is not None:
				graph.find_fixed_doo_for_build(world)
			# Заливаем поверхность world фоновым цветом.
			world.fill_me()
			# Отображаем пространство симуляции
			space.debug_draw(draw_options)
			# Рисование подсказок для строительства
			if world.shape_being_dragged is not None:
				world.draw_build_hint(graph)
			# Нарисовать окружность вокруг свободного Ду, находящегося под курсором мыши.
			world.draw_circle()
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
		''' Метод для отображения FPS (часоты кадров) игры на экране.
		
		Это позволит грубо оценивать производительность игры.
		Получаем значение FPS с помощью метода get_fps() объекта Clock. 
		Округляем значение FPS до 2 знаков после запятой с помощью метода format.
		Создаем поверхность с изображением текста c помощью render().
		Выводим изображение на экран.

		Аргументы:
		----------
		camera : pygame.Surface
			Экран игры, на который будет выводить значение частоты кадров.
		clock : pygame.time.Clock
			Объект, с помощью которого получаем значение FPS игры в данный момент.
		font : pygame.font.Font
			Шрифт для вывода текста.
		'''
		fps = font.render('{0:.2f}'.format(clock.get_fps()), True, [50,50,50])
		camera.blit(fps, [10,10])

	def restart(self, shape_creator, graph):
		''' Метод, возврщающий игру к исходному состоянию.
		
		Значительно облегчит тестирование игры.
		Удаляем всех свободных Ду.
		Удаляем башню (всех фиксированных Ду и все пружины).
		Заново создаем фундамент для башни.

		Аргументы:
		----------
		shape_creator : ShapeCreator
			Объект, позволяющий удалить игровые объекты.
		graph : Graph
			Объект, описывающий башню в игре.
		'''
		shape_creator.remove_all_doos()
		shape_creator.remove_construction(graph)
		shape_creator.create_start_construction(graph, 300)

		

if __name__ == '__main__':
	''' Если скрипт запущен самостоятельно, а не вызван из другого скрипта, то:
	
	1. Создать объект класса Game.
	2. Запустить игру.
	'''
	game = Game()
	game.game_initialize()
