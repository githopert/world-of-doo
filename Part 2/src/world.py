import pygame as pg
import pymunk as pm

class World(pg.Surface):
	'''
	Класс, регулирующий игровой процесс и служащий для отображения
	всей игровой области. Этот класс является модификацией класса pg.Surface.
	Мы не создаем класс с нуля, чтобы использовать возможность отображения на объекте
	класса World чего-либо. При этом мы добавляем необходимые нам атрибуты и методы, сохраняя
	атрибуты и методы родительского класса.'''

	def __init__(self, width, height, camera, color=[250,250,250]):
		'''
		Создаем экземпляр надкласса pg.Surface, чтобы получить
		его атрибуты внутри экземпляра класса World, а затем
		добавляем свои дополнительные атрибуты.
		'''
		# Создаем экземпляр класса pg.Surface, вызывая метод
		# __init__() родительского класса
		super().__init__([width, height])

		# Добавляем свои атрибуты
		self.width 					= width
		self.height 				= height
		self.color 					= color
		self.camera 				= camera
		# Список (массив) всех свободных Doo
		self.free_doos 				= []
		# Переменная для хранения объекта Doo, который
		# был схвачен игроком при нажатии ЛКМ.
		self.shape_being_dragged 	= None
		# Уровень пола
		self.ground_y 				= self.height - 10


	def fill_me(self):
		'''
		Фоновая заливка игровой области.'''
		self.fill(self.color)

	def blit_me(self):
		'''
		Функция для отображения игровой области на экране (= поверхность camera).'''
		self.camera.blit(self, [0,0])

	def pick_free_doo(self, space, mouse_pos):
		'''
		Функция, отвечающая за захват свободного Ду при нажатии на него ЛКМ.
		'''
		# Находим ближайший объект к позиции мыши:
		# Метод point_query_nearest принимает следующие аргументы:
		# mouse_pos - позиция мыши, 0 - радиус, в котором метод ищет объекты класса Shape.
		# Метод возвращает объект класса PointQueryInfo
		# в его атрибуте .shape содержится ссылка на найденный объект Shape (если что-то было возвращено).
		query_info = space.point_query_nearest(mouse_pos, 0, pm.ShapeFilter())
		if query_info != None:
			# Если есть какой-то объект класса Shape под курсором мыши, то
			# проверяем, является ли он Ду. Ду соответствует collision_type = 0 (мы задали это в классе DooFree).
			if query_info.shape.collision_type == 0:
				# Сохраняем ссылку на захваченного Ду в переменную shape_being_dragged
				# чтобы потом перемещать его.
				self.shape_being_dragged = query_info.shape

	def release_picked_doo(self):
		'''
		Отпустить захваченного Ду.
		'''
		self.shape_being_dragged = None

	def move_picked_doo(self, mouse_pos):
		'''
		Функция, отвечающая за перемещение захваченного Ду.
		'''
		if self.shape_being_dragged != None:
			# Ставим условие на позицию мыши по высоте,
			# иначе захваченного Ду можно будет затолкать под пол
			if mouse_pos[1] < self.ground_y:
				self.shape_being_dragged.body.position = mouse_pos
				self.shape_being_dragged.body.velocity = 0,0	# ВАЖНО: ОБНУЛЯЕМ СКОРОСТЬ. Иначе Ду не будет точно следовать за курсором.

	def draw_circle(self, mouse_pos, space, r=12, width=1):
		'''
		Функция для рисования окружности около Ду, находящегося под курсором мыши.'''
		query_info = space.point_query_nearest(mouse_pos, 0, pm.ShapeFilter())
		if query_info != None:
			if query_info.shape.collision_type == 0:
				# Перевести координаты pymunk в координаты pygame
				doo_center = pm.pygame_util.to_pygame(query_info.shape.body.position, self)
				pg.draw.circle(self, [200,0,0], doo_center, r, width)