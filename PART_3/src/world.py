import pygame as pg
import pymunk as pm
from pymunk.pygame_util import to_pygame
import math	# Нужен квадратный корень при нахождении расстояний.


class World(pg.Surface):
	''' Класс, регулирующий игровой процесс и служащий для отображения всей игровой области. Также содержит вспомогательные методы.

	Этот класс является модификацией класса pg.Surface.
	Мы не создаем класс с нуля, чтобы использовать возможность отображения на объекте класса World чего-либо. 
	При этом мы добавляем необходимые нам атрибуты и методы, сохраняя атрибуты и методы родительского класса.

	Аргументы:
	----------
	width : int
		Ширина игровой области в пикселях.
	height : int
		Высота игровой области в пикселях.
	camera : pygame.Surface
		Экран игры, на который будем отображать игровую область.
	color : list или tuple
		Фоновый цвет игровой области в формате RGB.

	Атрибуты: (добавленные и переопределенные в классе World)
	----------
	width : int
		Ширина игровой области в пикселях.
	height : int
		Высота игровой области в пикселях.
	camera : pygame.Surface
		Экран игры, на который будем отображать игровую область.
	color : list или tuple
		Фоновый цвет игровой области в формате RGB.
	free_doos : list
		Список, содержащий всех свободных Ду в игре.
	free_doo_under_cursor : None or DooFree
		Переменная для хранения свободного Ду, находящегося под курсором мыши в данный момент.
	shape_being_dragged : None or DooFree
		Переменная для хранения свободного Ду, схваченного игроком при нажатии ЛКМ. Значение None означает, что никакой свободный Ду не был схвачен.
	ground_y : int
		Значение Y в пикселях, которое соответствует уровню земли (пола). Y отсчитывается от верха поверхности world.
	'''

	def __init__(self, width, height, camera, color=[250,250,250]):
		super().__init__([width, height])
		self.width 					= width
		self.height 				= height
		self.camera 				= camera
		self.color 					= color
		self.free_doos 				= []
		self.free_doo_under_cursor 	= None
		self.shape_being_dragged 	= None
		self.ground_y 				= self.height - 10


	def fill_me(self):
		''' Метод для заливки игровой области фоновым цветом.
		'''
		self.fill(self.color)

	def blit_me(self):
		''' Метод для отображения игровой области на экране (= поверхность camera).
		'''
		self.camera.blit(self, [0,0])

	def find_free_doo_under_cursor(self, space, mouse_pos):
		''' Метод, определяющий, находится ли свободный Ду под курсором мыши в данный момент.

		Находим ближайший к позиции мыши объект с помощью метода point_query_nearest объекта space.
		Этот метод принимает следующие аргументы:
			mouse_pos - некоторая точка, относительно которой будет производиться поиск объекта, в данной ситуации это координаты курсора мыши.
			0 - радиус, в котором ищутся объекты класса Shape относительно указанной точки. 0 означает, что возвращаемый объект должен находиться прямо под курсором мыши.
		Метод возвращает объект класса PointQueryInfo.
		В атрибуте shape этого объекта содержится ссылка на найденный объект Shape (если что-то было возвращено).
		Для объекта shape мы можем проверить атрибут collision_type.
		Если он равен 0, то под курсором оказался свободный Ду.
		Этого Ду сохраняем в переменную free_doo_under_cursor, чтобы потом его перемещать.

		Аргументы:
		----------
		space : pymunk.Space
			Пространство симуляции, в котором находится искомый свободный Ду.
		mouse_pos : tuple или list
			Координаты курсора мыши. Ищем свободного Ду, которых находится под курсором мыши.
		'''
		self.free_doo_under_cursor = None
		query_info = space.point_query_nearest(mouse_pos, 0, pm.ShapeFilter())
		if query_info != None:
			if query_info.shape.collision_type == 0:
				self.free_doo_under_cursor = query_info.shape
				
	def pick_free_doo(self):
		""" Метод, отвечающий за захват свободного Ду при нажатии на него ЛКМ.
	
		Если под курсором находится свободный Ду сохраняем его в переменную shape_being_dragged.
		"""
		if self.free_doo_under_cursor != None:
				self.shape_being_dragged = self.free_doo_under_cursor

	def release_picked_doo(self, graph, shape_creator):
		''' Метод описывающий, что происходит со схваченным Ду при отпускании ЛКМ.

		Если для схваченного Ду есть подходящие фиксированные Ду в башне, то достраиваем башню.
		Иначе просто отпускаем схваченного Ду и убираем free_doo_under_cursor, иначе будет баг при строительстве.

		Аргументы:
		----------
		graph : Graph
			Башня из фиксированных Ду.
		shape_creator : ShapeCreator
			Используем метод для строительства башни данного объекта.
		'''
		if self.shape_being_dragged is not None:
			if len(graph.fixed_doo_for_build)==2:
				shape_creator.build(graph)
			self.shape_being_dragged = None

	def move_picked_doo(self, mouse_pos):
		''' Метод, отвечающий за перемещение схваченного Ду.

		Если курсор ниже уровня пола, то отпускаем схваченного Ду. 
		Это не даст игроку затолкать Ду под пол и позволит избежать ошибок при строительстве.
		Если курсор выше уровня пола, то ТЕЛЕПОРТИРУЕМ схваченного Ду в позицию курсора мыши.
		При этом важно обнулить скорость Ду, иначе он не будет следовать за курсором, а будет биться в конвульсиях, набирая очень большую скорость.

		# ПРИМЕЧАНИЕ
		В документации Chipmunk написано, что лучше избегать таких ТЕЛЕПОРТАЦИЙ для динамических тел.
		Автор физического движка предлагает использовать для перетаскивания динамических тел объекты constraints.
		Но код для ТЕЛЕПОРТАЦИЙ очень прост и вроде работает без ошибок, поэтому я оставил так.
		
		Аргументы:
		----------
		mouse_pos : tuple или list
			Координаты курсора мыши.
		'''
		if self.shape_being_dragged != None:
			if mouse_pos[1] < self.ground_y:
				self.shape_being_dragged.body.position = mouse_pos
				self.shape_being_dragged.body.velocity = 0,0
			else:
				self.shape_being_dragged = None

	def draw_circle(self, r=12, width=1):
		''' Метод для рисования окружности около Ду, находящегося под курсором мыши.

		Перед рисованием находим координаты центра Ду в координатной системе поверхности world.
		Так как окружность рисуем именно на этой поверхности.

		Аргументы:
		----------
		r : int
			Радиус окружности в пикселях.
		width : int
			Толщина окружности в пикселях.
		'''
		if self.free_doo_under_cursor != None:
			doo_center = to_pygame(self.free_doo_under_cursor.body.position, self)
			pg.draw.circle(self, [200,0,0], doo_center, r, width)

	def distance_between_bodies(self, b1, b2):
		""" Метод для нахождения расстояния между двумя телами.

		Аргументы:
		----------
		b1 : pymunk.Body
			Первое тело.
		b2 : pymunk.Body
			Второе тело.

		Возвращаемое значение:
		----------
		float : Расстояние между двумя телами.
		"""
		dx = b1.position.x - b2.position.x
		dy = b1.position.y - b2.position.y
		return math.sqrt(dx*dx + dy*dy)

	def collide_doo_with_doo(self, arbiter, space, data):
		''' Метод описывающий поведение свободных Ду при их столкновении друг с другом.
		
		False означает, что объекты проходят сквозь друг друга без взаимодействия.
		По умолчанию возвращается True и объекты сталкиваются друг с другом.

		Аргументы:
		----------
		Требует CollisionHandler, хотя в самом методе аргументы не используются. Без них выдает ошибку.

		Возвращаемое значение:
		----------
		False
		'''
		return False

	def draw_build_hint(self, graph, r=8, linewidth=1):
		''' Метод для рисования подсказки на экране во время строительства.

		Подсказка разная для двух случаев (аналогичны случаям при строительстве, см. метод build в ShapeCreator):
		Если подходящие для строительства узлы не соседи друг другу, то рисуем линию между ними.
		Если подходящие для строительства узлы соседи друг другу, то рисуем круг, там где будет новый узел, и 2 линии.
		
		Аргументы:
		----------
		graph : Graph
			Объект, который даст нам доступ к фиксированным Ду, подходящим для строительства.
		r : int
			Радиус рисуемого круга.
		'''
		if len(graph.fixed_doo_for_build) == 2:
			if graph.fixed_doo_for_build[0] in graph[graph.fixed_doo_for_build[1]]:
				pg.draw.line(self, (0, 200, 0), to_pygame(graph.fixed_doo_for_build[0].body.position, self), to_pygame(self.shape_being_dragged.body.position, self), linewidth)
				pg.draw.line(self, (0, 200, 0), to_pygame(graph.fixed_doo_for_build[1].body.position, self), to_pygame(self.shape_being_dragged.body.position, self), linewidth)
				pg.draw.circle(self, (0, 200, 0), to_pygame(self.shape_being_dragged.body.position, self), r)
			else:
				pg.draw.line(self, (0, 200, 0), to_pygame(graph.fixed_doo_for_build[0].body.position, self), to_pygame(graph.fixed_doo_for_build[1].body.position, self))
