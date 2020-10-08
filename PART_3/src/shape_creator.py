import pymunk as pm
# Импортируем классы DooFree и DooFixed из файла doo.py
from doo import DooFree, DooFixed


class ShapeCreator():
	''' Класс, содержащий методы для создания и удаления объектов разных типов.

	Аргументы:
	----------
	world : World
		Объект, хранящий объекты некоторых типов и содержащий методы для нахождения расстояний.
	space : pymunk.Space
		Пространство симуляции, в которое будут добавляться создаваемые объекты.

	Атрибуты:
	----------
	world : World
		Объект, хранящий объекты некоторых типов и содержащий методы для нахождения расстояний.
	space : pymunk.Space
		Пространство симуляции, в которое будут добавляться создаваемые объекты.
	spring_strength : int или float
		Жесткость пружины. Значение подобрано эмпирически.
		При низких значениях башня схлопывается, а при крайне высоких -- башня не изгибается так, как в исходной игре.
	damping : int или float
		Коэффициент затухания колебаний пружины. Определяет то, как быстро пружины перестают колебаться. Значение подобрано эмпирически.
	'''
	def __init__(self, world, space):
		self.world = world
		self.space = space
		self.spring_strength = 10000
		self.damping = 100
		

	def create_free_doo(self, x, y):
		''' Метод для создания свободного Ду.

		Для динамических тел в пространство симуляции добавляются и body, и shape.
		Свободных Ду также добавляем в массив free_doos.

		Аргументы:
		----------
		x : float или int
			Позиция центра масс (body) свободного Ду в пространстве симуляции по оси X.
		y : float или int
			озиция центра масс (body) свободного Ду в пространстве симуляции по оси Y.
		'''
		free_doo = DooFree(x,y)
		self.space.add(free_doo.body, free_doo)
		self.world.free_doos.append(free_doo)

	def create_fixed_doo(self, x, y, mass=10):
		""" Метод для создания фиксированных Ду.

		Для динамических тел в пространство симуляции добавляются и body, и shape.

		Аргументы:
		----------
		x : float или int
			Позиция центра масс (body) свободного Ду в пространстве симуляции по оси X.
		y : float или int
			Позиция центра масс (body) свободного Ду в пространстве симуляции по оси Y.
		mass : float или int
			Масса фиксированного Ду. Иногда нужно задать массу отличную от значения по умолчанию.

		Возвращаемое значение:
		----------
		DooFixed : Возвращаем фиксированного Ду для дальнейшей работы с ним.
		"""
		fixed_doo = DooFixed(x, y, mass=mass)
		self.space.add(fixed_doo.body, fixed_doo)
		return fixed_doo

	def create_spring(self, b1, b2):
		""" Метод для создания пружины.
		
		(0, 0) и (0, 0) означают, что концы пружин будут находиться там же где и body указанных Ду.
		Добавляем созданную пружину в пространство симуляции.
		
		Аргументы:
		----------
		b1 : DooFixed
			Первый фиксированный Ду.
		b2 : DooFixed
			Второй фиксированный Ду.
		lenght : float или int
			Длина пружины в расслабленном состоянии (без воздействия внешних сил).
		"""
		d = self.world.distance_between_bodies(b1, b2)
		ds = pm.DampedSpring(b1, b2, (0, 0), (0, 0), d, self.spring_strength, self.damping)
		self.space.add(ds)

	def remove_escaped_doos(self):
		''' Метод для удаления Ду, вышедших за границы игровой области.

		Для динамических тел нужно удалять из пространства симуляции и body, и shape.
		Свободных Ду так же удаляем из списка free_doos.
		'''
		for doo in self.world.free_doos:
			if doo.body.position.y > self.world.height:
				self.world.free_doos.remove(doo)
				self.space.remove(doo.body, doo)
			elif doo.body.position.x < 0 or doo.body.position.x > self.world.width:
				self.world.free_doos.remove(doo)
				self.space.remove(doo.body, doo)

	def remove_all_doos(self):
		''' Метод для удаления всех свободных Ду. 

		Используется для рестарта игры.
		Для динамических тел нужно удалять из пространства симуляции и body, и shape.
		Очищаем список free_doos.
		Очищаем переменную shape_being_dragged.
		'''
		self.world.shape_being_dragged = None
		for free_doo in self.world.free_doos:
			self.space.remove(free_doo.body, free_doo)
		self.world.free_doos.clear()

	def create_static_floor(self, height=15, friction=10):
		''' Метод для создания пола, т.е. нижней границы игровой области.

		Для статических тел в пространство симуляции добавляется только shape.
		Переопределяем значения атрибутов friction и collision_type.
		Collision_type равный 2 будет соответствовать полу.
		Выбрал форму Poly, а не Segment в надежде, что Ду не будут пролетать сквозь пол при больших скоростях движения.
		(Например, при падении с большой высоты)

		Аргументы:
		----------
		height : float или int
			Толщина пола. Значение выбрано совершенно произвольно.
		friction : float или int
			Коэффициент трения пола. Значение подобрано эмпирически.
			В Pymunk используется модель Кулона для трения. 
			Результирующий коэффициент трения находится перемножением коэффициентов трения соприкасающихся шейпов.
		'''
		body = pm.Body(body_type = pm.Body.STATIC)
		body.position = [self.world.width/2, self.world.ground_y]
		semiwidth = self.world.width/2
		vs = [(-semiwidth,0), (semiwidth,0), (-semiwidth,height), (semiwidth,height)]
		poly = pm.Poly(body,vs)
		poly.friction = friction
		poly.collision_type = 2
		self.space.add(poly)

	def create_static_wall(self, x, y, width=1, friction=100):
		''' Метод для создания вертикальных стен, которые буду боковыми границами игровой области.

		Для статических тел в пространство симуляции добавляется только shape.
		Переопределяем значения атрибутов friction и collision_type.
		Collision_type равный 3 будет соответствовать стенам.
		Центр масс стены расположен в нижней вершине.

		Аргументы:
		----------
		x : float или int
			Позиция центра масс (body) стены в пространстве симуляции по оси X.
		y : float или int
			Позиция центра масс (body) стены в пространстве симуляции по оси Y.
		width : int
			Толщина стены. Значение выбрано совершенно произвольно.
		friction : float или int
			Коэффициент трения стен. Значение подобрано эмпирически. 
			В Pymunk используется модель Кулона для трения. 
			Результирующий коэффициент трения находится перемножением коэффициентов трения соприкасающихся шейпов.
		'''
		body = pm.Body(body_type = pm.Body.STATIC)
		body.position = [x,y]
		line = pm.Segment(body,(0,0),(0,-self.world.height), width)
		line.friction = friction
		line.collision_type = 3
		self.space.add(line)

	def create_start_construction(self, graph, y, semiwidth_bottom=70, semiwidth_top=55, height=122):
		""" Метод для создания стартовой конструкции из четырех вершин, которая будет служить фундаментом башни.

		Создаем фиксированных Ду, образующих вершины трапеции.
		Заполняем граф.
		Находим расстояния между парами соседей (2 значения повторяются, поэтому рассчитываем только 4 из 6).
		Необходимо предварительно рассчитать длины пружин, чтобы в конструкции не было напряжения, и её не дёргало.
		Соединяем соседних Ду пружинами.

		Аргументы:
		----------
		graph : Graph
			Объект, описывающий башню в игре.
		y : float или int
			Положение нижнего основания фундамента башни в пространстве симуляции по оси Y.
			Откуда он будет падать вниз на старте.
		semiwidth_bottom : float или int
			Полуширина нижнего основания фундамента башни. Значение выбрано совершенно произвольно.
		semiwidth_top : float или int
			Полуширина верхнего основания фундамента башни. Значение выбрано совершенно произвольно.
		height : float или int
			Высота стартовой конструкции. Значение выбрано совершенно произвольно.
		"""
		fd_1 = self.create_fixed_doo(self.world.width//2-semiwidth_bottom, y, mass=1000)
		fd_2 = self.create_fixed_doo(self.world.width//2+semiwidth_bottom, y, mass=1000)
		fd_3 = self.create_fixed_doo(self.world.width//2-semiwidth_top, y-height)
		fd_4 = self.create_fixed_doo(self.world.width//2+semiwidth_top, y-height)
		graph[fd_1] = [fd_2, fd_3, fd_4]
		graph[fd_2] = [fd_1, fd_3, fd_4]
		graph[fd_3] = [fd_1, fd_2, fd_4]
		graph[fd_4] = [fd_1, fd_2, fd_3]
		self.create_spring(fd_1.body, fd_2.body)
		self.create_spring(fd_1.body, fd_3.body)
		self.create_spring(fd_1.body, fd_4.body)
		self.create_spring(fd_2.body, fd_3.body)
		self.create_spring(fd_2.body, fd_4.body)
		self.create_spring(fd_3.body, fd_4.body)

	def remove_construction(self, graph):
		""" Метод для удаления башни из игры. 

		Используется для рестарта игры.
		Надо удалить фиксированных Ду (узлы графа) и пружины (ребра графа) и очистить сам граф.
		Для получения доступа к пружинам используем атрибут constraints тел фиксированных Ду.

		Аргументы:
		----------
		graph : Graph
			Объект, описывающий башню в игре.
		"""
		for fixed_doo in graph.keys():
			self.space.remove(fixed_doo.body.constraints)
			self.space.remove(fixed_doo.body, fixed_doo)
		graph.clear()

	def build(self, graph):
		''' Метод, позволяющий игроку строить башню.

		При строительстве возникают 2 случая:
			1. Подходящие фиксированные Ду не являются соседями друг другу.
			2. Подходящие фиксированные Ду (в fixed_doo_for_build) соседи друг другу.
		В первом случае просто соединяем фиксированных Ду пружиной.
		Во втором случае на месте схваченного Ду создаем фиксированного Ду, которого соединяем с башней двумя пружинами.
		Нужно обновить граф башни.
		В конце удаляем схваченного свободного Ду из пространства симуляции и списка free_doos.
		Для динамических тел нужно удалять из пространства симуляции и body, и shape.

		Аргументы:
		----------
		graph : Graph
			Объект, описывающий башню в игре.
		'''
		free_doo = self.world.shape_being_dragged	# Просто, чтобы сократить длину нескольких строчек кода

		if graph.fixed_doo_for_build[0] in graph[graph.fixed_doo_for_build[1]]:
			### ВТОРОЙ СЛУЧАЙ
			new_fixed_doo= self.create_fixed_doo(free_doo.body.position.x, free_doo.body.position.y)
			graph[graph.fixed_doo_for_build[0]].append(new_fixed_doo)
			graph[graph.fixed_doo_for_build[1]].append(new_fixed_doo)
			graph[new_fixed_doo] = [graph.fixed_doo_for_build[0], graph.fixed_doo_for_build[1]]
			self.create_spring(new_fixed_doo.body, graph.fixed_doo_for_build[0].body)
			self.create_spring(new_fixed_doo.body, graph.fixed_doo_for_build[1].body)
		else:
			### ПЕРВЫЙ СЛУЧАЙ
			graph[graph.fixed_doo_for_build[0]].append(graph.fixed_doo_for_build[1])
			graph[graph.fixed_doo_for_build[1]].append(graph.fixed_doo_for_build[0])
			self.create_spring(graph.fixed_doo_for_build[0].body, graph.fixed_doo_for_build[1].body)
		self.world.free_doos.remove(free_doo)
		self.space.remove(free_doo.body, free_doo)
