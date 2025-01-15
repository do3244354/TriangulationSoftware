import math
import gi
import cairo
import geometry101
import gtk101

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gdk, Gio

#define Main Window class
class MainWindow(Gtk.ApplicationWindow):
	#define variables related to gtk windows along with gtk
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		#see the gtk101 module for more details
		gtk101.basic_window(self)

		#add important variables
		#we would need a matrice representing the current transformation of the canvas
		#the first one is scale_x, scale_y, translate_x, translate_y
		self.transform = [[1,1], [0,0]]

		#add the mouse position and mouse click
		self.x_pos = 0
		self.y_pos = 0
		self.x_click = 0
		self.y_click = 0

		self.last_x_pos = 0
		self.last_y_pos = 0

		#to keep track of the amount of points added
		self.amount_added = 0

		#add dictionary with all the added curves in it
		#calculation lines list from all sort of lines and points will be combined together in order to flip the diagonals 
		self.curves = {
				"sides" : {
					"points" : [],
					"lines" : [],
					"index": [],
					"calculation_lines": {
						"lines": [],
						"index": []
					}
				},
				"punctures" : {
					"points" : [],
					"index": [],
					"overlap_one" :None,
					"pressed_two" :None
				},
				"components" : {
					"center": [],
					"points" : [],
					"number_points" : [],
					"index": [],
					"calculation_lines": {
						"lines": [],
						"index": []
					},
					"overlap_one" :None,
					"pressed_two" :None
				},
				"diagonals" : {
					"points":[],
					"index": [],
					"midpoints": [],
					"calculation_lines": {
						"lines": [],
						"index": []
					},
					"overlap_one": None,
					"pressed_two": None
				}
		}

		#add a list containing all the points
		#will contains list of three elements, first element x_coordinate, second element y_coordinate, thrid element index
		self.all_points = []

		#to know which one of all_points is clicked or overlapped
		self.overlapped_point = None
		self.clicked_point = None

		#add a value to see if the click of the mouse is maintained
		self.maintained = False

		#add a value to see if the image has to be saved
		self.save = False

		#when set to True, make edditing of many values not possible but diagonals can be added
		self.done = False

		#we need to know if we have to follow the mouse with a line
		self.follow_mouse = False

		#so we know if the mouse has been clicked
		self.is_clicked = False

		#a boolean to know if we are in flip diagonal mode (only possible of done as been clicked)
		self.diagonal_flip_mode = False

		#add a variable that will tell you the start and end point of the new diagonal
		self.two_points = [[], []]

		#add a list (dictionary) containing all the lines one would have to compare
		self.all_lines = {
			"lines" : [],
			"index" : []
		}

		#to know the number of punctures
		self.puncture_amount = 0

		#have a list to see which lines are taken into account
		self.test_line = []

		#have a list that contains the quadrilateral with all the sides in order
		self.quadrilateral = [[[], []], [[], []]]

		#list to make calculations of the new diagonal
		self.calc_quadrilateral = []

		#separate the lines from self.calc_quadrilateral
		self.reference_points = []

		#add a list with all the points in the quadrilateral in it
		self.calc_quadrilateral_2 = []

		#add a list to see if everything have been correctly shifted
		self.shift_test = []

		self.shift_test2 = []

		#center of circles (diagonal flip algorithm)
		self.center = []

		#to get the index of a newly added diagonal
		self.endpoint = []

	#the following functions are all about user interaction with buttons, mouse

	#print something when the icon is clicked on
	def about(self, button):
		print("Triangulation Software, Version 101, 2024-08-30")
		print("Using Python, GTK, and Cairo")

	#function to let the program know it can save the image
	def save_image(self, button):
		self.save = True
		#we ask to redraw the drawing area when this happens
		self.drawing_area.queue_draw()

	#function that brings everything back to normal
	def back_to_normal(self, button):
		self.transform = [[1,1], [0,0]]
		self.drawing_area.queue_draw()

	#to something when spinbutton value changes so we can add or remove sides
	def on_value_changed(self, scroll):
		if self.done == False:
			self.amount_added = self.spinbutton.get_value_as_int()
			self.on_event()
		else:
			self.spinbutton.set_value(self.amount_added)

	#add a puncture at the center of the screen
	def add_puncture(self, button):
		self.puncture_amount += 1
		self.curves["punctures"]["points"].append([0, 0])
		self.maintained = False
		self.drawing_area.queue_draw()

	#add a component whenever the button is clicked
	def add_component(self, button):
		#append the center [0,0] and radius [0.1] to the curve dictionary
		self.curves["components"]["center"].append([0, 0, 0.1])
		#add an index to the component added (should be done for the point of the components instead)
		#we append 0 to the number of points because there are 0 point added on the new component
		self.curves["components"]["number_points"].append(0)
		#we add an empty list to the component points part of dictionary to put the point on the component in
		self.curves["components"]["points"].append([])
		#we set self.maintained to be false to avoid an error when clicking on the button
		self.maintained = False
		self.drawing_area.queue_draw()

	#when you click on done, editing is disabled 
	def disable_editing(self, button):
		if self.done == True:
			self.done = False
			#if we click again on self.done, the diagonals disapears
			self.curves["diagonals"]["points"].clear()
			self.curves["diagonals"]["index"].clear()
			self.curves["diagonals"]["midpoints"].clear()
			self.curves["diagonals"]["overlap_one"] = None
		else:
			self.done = True
		self.on_event()


	#functions about user input

	#will record the mouse position and call on_event
	def on_mouse_motion(self, motion, x, y):
		self.last_x_pos = self.x_pos
		self.last_y_pos = self.y_pos
		self.x_pos = x
		self.y_pos = y
		self.on_event()

	#will record the mouse click position and call on_event
	def on_mouse_click(self, gesture, data, x, y):
		self.maintained = True
		self.is_clicked = True 
		self.x_click = x
		self.y_click = y
		self.on_event()


	#will change the boolean value of mouse_maintained when the mouse is released
	def on_mouse_release(self, gesture, data, x, y):
		self.maintained = False
		self.curves["punctures"]["pressed_two"] = None
		self.curves["components"]["pressed_two"] = None
		self.on_event()

	#add an action when a key is pressed
	#allows us to zoom in and out and move around
	def key_press(self, event, keyval, keycode, state):
		width = self.drawing_area.get_width()
		height = self.drawing_area.get_height()
		ref_x = width/2
		ref_y = height/2
		scale_factor = 1.02
		shift_factor = 5
		#zoom in
		if keyval == Gdk.KEY_q:
			self.transform[0][0] = self.transform[0][0]*scale_factor
			self.transform[0][1] = self.transform[0][1]*scale_factor

			self.transform[1][0] = scale_factor*(self.transform[1][0]-ref_x)+ref_x
			self.transform[1][1] = scale_factor*(self.transform[1][1]-ref_y)+ref_y
		#zoom out
		if keyval == Gdk.KEY_e:
			self.transform[0][0] = self.transform[0][0]/scale_factor
			self.transform[0][1] = self.transform[0][1]/scale_factor

			self.transform[1][0] = (1/scale_factor)*(self.transform[1][0]-ref_x)+ref_x
			self.transform[1][1] = (1/scale_factor)*(self.transform[1][1]-ref_y)+ref_y
		#move up
		if keyval == Gdk.KEY_w:
			self.transform[1][1] = self.transform[1][1] + shift_factor

		#move down
		if keyval == Gdk.KEY_s:
			self.transform[1][1] = self.transform[1][1] - shift_factor

		#move right
		if keyval == Gdk.KEY_d:
			self.transform[1][0] = self.transform[1][0] - shift_factor

		#move left
		if keyval == Gdk.KEY_a:
			self.transform[1][0] = self.transform[1][0] + shift_factor

		#all of the following cannot be done if self.done = True
		if self.done == False:
			for i in range(len(self.curves["components"]["center"])):
				#add points to a component
				if keyval == Gdk.KEY_p and self.curves["components"]["pressed_two"] == i:
					if self.curves["components"]["number_points"][i]<10:
						self.curves["components"]["number_points"][i] += 1
				if keyval == Gdk.KEY_o and self.curves["components"]["pressed_two"] == i:
					if self.curves["components"]["number_points"][i]>0:
						self.curves["components"]["number_points"][i] -= 1
				#change radius of the component
				if keyval == Gdk.KEY_k and self.curves["components"]["pressed_two"] == i:
					if self.curves["components"]["center"][i][2]<0.29:
						self.curves["components"]["center"][i][2] = self.curves["components"]["center"][i][2]*1.01
				if keyval == Gdk.KEY_l and self.curves["components"]["pressed_two"] == i:
					if self.curves["components"]["center"][i][2]>0:
						self.curves["components"]["center"][i][2] = self.curves["components"]["center"][i][2]*0.99
				#remove a component
				if keyval == Gdk.KEY_g and self.curves["components"]["pressed_two"] == i:
					self.curves["components"]["points"].pop(i)
					self.curves["components"]["number_points"].pop(i)
					self.curves["components"]["center"].pop(i)
					self.curves["components"]["pressed_two"] = None

			for i in range(len(self.curves["punctures"]["points"])):
				#remove a puncture
				if keyval == Gdk.KEY_g and self.curves["punctures"]["pressed_two"] == i:
					self.puncture_amount -= 1
					self.curves["punctures"]["points"].pop(i)
					self.curves["punctures"]["index"].pop(i)
					self.curves["punctures"]["pressed_two"] = None
				

		self.on_event()
		self.drawing_area.queue_draw()

	#function to call each time something happens
 	#the on_event function must be written again, especially the two add point functions
	def on_event(self):
		#update the positions of mouse based on the transform done
		#we use the values from self.transform: [[scale_x, scale_y], [translate_x, translate_y]]
		updated_x_pos = (self.x_pos - self.transform[1][0])/(self.transform[0][0])
		updated_y_pos = (self.y_pos - self.transform[1][1])/(self.transform[0][1])
		updated_x_click = (self.x_click - self.transform[1][0])/(self.transform[0][0])
		updated_y_click = (self.y_click - self.transform[1][1])/(self.transform[0][1])

		#update the puncture index
		self.curves["punctures"]["index"].clear()
		for i in range(self.puncture_amount):
			#we want the punctures to be put after the sides index wise
			self.curves["punctures"]["index"].append(len(self.curves["sides"]["index"]) + i)

		#get height and width of canvas
		width = self.drawing_area.get_width()
		height = self.drawing_area.get_height()
		
		#add points around the main circle
		def add_points(n):
			#we remove the points, the lines (might not be necessary if we are not triangulation a polygon), and the index
			self.curves["sides"]["points"].clear()
			self.curves["sides"]["lines"].clear()
			self.curves["sides"]["index"].clear()
			for i in range(n):
				#we add points around the circle using the geometry module
				self.curves["sides"]["points"].append([geometry101.circle_coordinate(n, i, 0, 0.3)[0], geometry101.circle_coordinate(n, i, 0, 0.3)[1]])
				#each point added have its own index
				self.curves["sides"]["index"].append(i)
				#add sides (only needed when considering polygons)
				self.curves["sides"]["lines"].append([geometry101.circle_coordinate(n, i, 0, 0.3)[0], geometry101.circle_coordinate(n, i, 0, 0.3)[1],geometry101.circle_coordinate(n, (i+1)%self.amount_added, 0, 0.3)[0], geometry101.circle_coordinate(n, (i+1)%self.amount_added, 0, 0.3)[1]])

			#we also need to create a new list with lines that can approximate a circle
			self.curves["sides"]["calculation_lines"]["lines"].clear()
			self.curves["sides"]["calculation_lines"]["index"].clear()

			#add a linear approximate of a circle to facilitate further calculations
			if self.curves["punctures"]["points"] != [] or self.curves["components"]["center"] != []:
				if n != 0:
					for i in range(n):
						#add an empty list in which a line will be added
						self.curves["sides"]["calculation_lines"]["lines"].append([])
						self.curves["sides"]["calculation_lines"]["index"].append([])
						last_element = len(self.curves["sides"]["calculation_lines"]["index"])-1
						self.curves["sides"]["calculation_lines"]["index"][last_element].append(i)
						for j in range(math.floor(40/n)+1):
							self.curves["sides"]["calculation_lines"]["lines"][len(self.curves["sides"]["calculation_lines"]["lines"])-1].append([geometry101.circle_coordinate(n*math.floor(40/n), j+i*math.floor(40/n), 0, 0.3)[0], geometry101.circle_coordinate(n*math.floor(40/n), j+i*math.floor(40/n), 0, 0.3)[1]])						
						self.curves["sides"]["calculation_lines"]["index"][len(self.curves["sides"]["calculation_lines"]["index"])-1].append((i+1)%n)
			else:
				for i in range(n):
					#add an empty list in which a line will be added
					self.curves["sides"]["calculation_lines"]["lines"].append([])
					self.curves["sides"]["calculation_lines"]["index"].append([])
					self.curves["sides"]["calculation_lines"]["index"][len(self.curves["sides"]["calculation_lines"]["index"])-1].append(i)
					self.curves["sides"]["calculation_lines"]["lines"][len(self.curves["sides"]["calculation_lines"]["lines"])-1].append([geometry101.circle_coordinate(n, i, 0, 0.3)[0], geometry101.circle_coordinate(n, i, 0, 0.3)[1]])
					self.curves["sides"]["calculation_lines"]["lines"][len(self.curves["sides"]["calculation_lines"]["lines"])-1].append([geometry101.circle_coordinate(n, (i+1)%n, 0, 0.3)[0], geometry101.circle_coordinate(n, (i+1)%n, 0, 0.3)[1]])						
					self.curves["sides"]["calculation_lines"]["index"][len(self.curves["sides"]["calculation_lines"]["index"])-1].append((i+1)%n)

		#to add points around a component
		#we have to do a similar thing 
		def add_component_points(n, i):
			self.curves["components"]["points"][i].clear()
			radius = self.curves["components"]["center"][i][2]
			x_pos_center = self.curves["components"]["center"][i][0]
			y_pos_center = self.curves["components"]["center"][i][1]
			self.curves["components"]["index"].clear()
			for j in range(n):
				self.curves["components"]["points"][i].append([x_pos_center + geometry101.circle_coordinate(n, j, 0, radius)[0], y_pos_center + geometry101.circle_coordinate(n, j, 0, radius)[1]])
				self.curves["components"]["index"].append(len(self.curves["sides"]["index"]) + len(self.curves["punctures"]["index"]) + len(self.curves["components"]["calculation_lines"]["index"]))
			#figure out how much you have to offset the next index
			offset2 = 0
			for k in range(i):
				offset2 +=  self.curves["components"]["number_points"][k]-1

			if n != 0:
				for k in range(n):
					#problem with how the index is added
					#add an empty list in which a line will be added
					self.curves["components"]["calculation_lines"]["lines"].append([])
					self.curves["components"]["calculation_lines"]["index"].append([])
					offset = len(self.curves["sides"]["calculation_lines"]["index"])+len(self.curves["punctures"]["index"])+i+offset2
					self.curves["components"]["calculation_lines"]["index"][len(self.curves["components"]["calculation_lines"]["index"])-1].append(offset + k)
					for j in range(math.floor(20/n)+1):
						self.curves["components"]["calculation_lines"]["lines"][len(self.curves["components"]["calculation_lines"]["lines"])-1].append([x_pos_center + geometry101.circle_coordinate(n*math.floor(20/n), j+k*math.floor(20/n), 0, radius)[0], y_pos_center+geometry101.circle_coordinate(n*math.floor(20/n), j+k*math.floor(20/n), 0, radius)[1]])						
					self.curves["components"]["calculation_lines"]["index"][len(self.curves["components"]["calculation_lines"]["index"])-1].append(offset + ((k+1)%n))

		self.curves["components"]["calculation_lines"]["lines"].clear()
		self.curves["components"]["calculation_lines"]["index"].clear()

		#here we can add points around components
		for i in range(len(self.curves["components"]["number_points"])):
			number_to_add = self.curves["components"]["number_points"][i]
			#number to add is the amount that must be added around each puncture
			#i is the ith component added
			add_component_points(number_to_add, i)
		
		#add points with the function above based on the amount added enter via the spinbutton
		add_points(self.amount_added)

		#the following must happen only if self.done is equal to false
		if self.done == False:
			#allows us to interact with the punctures and put them wherever we want
			for i in range(len(self.curves["punctures"]["points"])):
				#we get the position of the puncture
				x_pos_puncture = width/2+self.curves["punctures"]["points"][i][0]*height
				y_pos_puncture = height/2-self.curves["punctures"]["points"][i][1]*height
				#we verify whether our click is clode to the ith puncture
				if math.dist([updated_x_click, updated_y_click], [x_pos_puncture, y_pos_puncture]) < height*0.009:
					#if the click is close enough, then the ith puncture becomes the pressed puncture (the only one that can be moved and that will appear bigger)
					self.curves["punctures"]["pressed_two"] = i	
					#we set the pressed_two value of component to None because we do not want to click on a component and a puncture at the same time
					self.curves["components"]["pressed_two"] = None			

			#this counter will allow us to know whether any of the puncture / component have been clicked on
			counter = 0 

			#if a puncture has been clicked on, we update its position based on the mouse's position
			for i in range(len(self.curves["punctures"]["points"])):
				x_pos_puncture = width/2+self.curves["punctures"]["points"][i][0]*height
				y_pos_puncture = height/2-self.curves["punctures"]["points"][i][1]*height
				#again, we compare the distance of the mouse pos with the one of the puncture
				if math.dist([updated_x_pos, updated_y_pos], [x_pos_puncture, y_pos_puncture])< height*0.09 and self.curves["punctures"]["pressed_two"] == i:
					self.curves["punctures"]["overlap_one"] = i
					#we make sure the mouse click is maintained
					if self.maintained == True:
						#we update the puncture's position based on the mouse position
						self.curves["punctures"]["points"][i][0] = (updated_x_pos-width/2)/height
						self.curves["punctures"]["points"][i][1] = (updated_y_pos-height/2)/-height					
 
				else:
					counter += 1

			#if the counter has the same value as the length of the list, we conclude that none of the punctures have been clicked on
			if counter == len(self.curves["punctures"]["points"]):
				#we therefore set the overlap one value to None
				self.curves["punctures"]["overlap_one"] = None

			#allows us to interact with an added components
			for i in range(len(self.curves["components"]["center"])):
				#get the coordinate of the component's center
				x_center_component = width/2+self.curves["components"]["center"][i][0]*height
				y_center_component = height/2-self.curves["components"]["center"][i][1]*height
				#get distance of mouse from component
				dist_from_component = math.dist([updated_x_click, updated_y_click], [x_center_component, y_center_component])
				#compare the distance
				if abs(dist_from_component-self.curves["components"]["center"][i][2]*height) < height*0.009:
					#adjust the pressed two value accordingly
					self.curves["components"]["pressed_two"] = i
					self.curves["punctures"]["pressed_two"] = None	

			counter = 0
			#make it so the circle that has been clicked on follows the mouse so it can be put anywhere
			for i in range(len(self.curves["components"]["center"])):
				dist_from_component = math.dist([updated_x_pos, updated_y_pos], [width/2+self.curves["components"]["center"][i][0]*height,height/2-self.curves["components"]["center"][i][1]*height])
				if abs(dist_from_component-self.curves["components"]["center"][i][2]*height) < height*0.09 and self.curves["components"]["pressed_two"] == i:
					self.curves["components"]["overlap_one"] = i
					if self.maintained == True:
						updated_last_x_pos = (self.last_x_pos - self.transform[1][0])/(self.transform[0][0])
						updated_last_y_pos = (self.last_y_pos - self.transform[1][1])/(self.transform[0][1])
						self.curves["components"]["center"][i][0] = self.curves["components"]["center"][i][0] + (updated_x_pos-width/2)/height - (updated_last_x_pos-width/2)/height
						self.curves["components"]["center"][i][1] = self.curves["components"]["center"][i][1] + (updated_y_pos-height/2)/-height - (updated_last_y_pos-height/2)/-height

			else:
				counter += 1

			#same counter concept as before
			if counter == len(self.curves["components"]["center"]):
				self.curves["components"]["overlap_one"] = None
		else:
			#if self.done = true, we want to create a list with all the points in it
			self.all_points.clear()
			#create a combined component list
			combined = []
			for i in range(len(self.curves["sides"]["points"])):
				self.all_points.append(self.curves["sides"]["points"][i]+[i, "points"])
			for i in range(len(self.curves["punctures"]["points"])):
				self.all_points.append(self.curves["punctures"]["points"][i]+[len(self.curves["sides"]["points"]) + i, "punctures"])
			for i in range(len(self.curves["components"]["points"])):
				for j in range(len(self.curves["components"]["points"][i])):
					combined = combined + [self.curves["components"]["points"][i][j]]
					#we must fix the way the index is appended here
					self.all_points.append(self.curves["components"]["points"][i][j]+[len(self.curves["sides"]["points"]) + len(self.curves["punctures"]["points"]) + len(combined) -1, "components"])

			#now we must find out if a point in this self.all_point list has been overlapped
			counter = 0
			for i in range(len(self.all_points)):
				point_x_pos = width/2+self.all_points[i][0]*height
				point_y_pos = height/2-self.all_points[i][1]*height
				dist_from_component = math.dist([updated_x_pos, updated_y_pos], [point_x_pos, point_y_pos])
				if dist_from_component < 0.01 * height:
					self.overlapped_point = i
				else:
					counter += 1

			if counter == len(self.all_points):
				self.overlapped_point = None
				self.clicked_point = None

			for i in range(len(self.all_points)):
				point_x_pos = width/2+self.all_points[i][0]*height
				point_y_pos = height/2-self.all_points[i][1]*height
				dist_click_from_component = math.dist([updated_x_click, updated_y_click], [point_x_pos, point_y_pos])
				if dist_click_from_component < 0.01 * height:
					self.clicked_point = i

			#the following must only be called if we clicked on the mouse
			#when finishing a diagonal
			if self.is_clicked == True:
				if self.follow_mouse == True and self.clicked_point != None:
					index = self.clicked_point
					x_point_clicked_on = self.all_points[index][0]
					y_point_clicked_on = self.all_points[index][1]

					self.curves["diagonals"]["points"][len(self.curves["diagonals"]["points"])-1].append([x_point_clicked_on, y_point_clicked_on])
					self.curves["diagonals"]["index"][len(self.curves["diagonals"]["index"])-1].append(self.all_points[index][2])

					self.follow_mouse = False
					#now we must verify if this new diagonal is a fake or real one
					list1 = list(reversed(self.curves["diagonals"]["index"]))
					list2 = list(reversed(self.curves["diagonals"]["points"]))
					#if they come from the same points and are define with only two points, we remove the diagonal
					if list1[0][0] == list1[0][1] and len(self.curves["diagonals"]["points"][0]) == 2:
						index_of_last_diagonal_added = len(self.curves["diagonals"]["points"])-1
						self.curves["diagonals"]["points"].pop(index_of_last_diagonal_added)
						self.curves["diagonals"]["index"].pop(index_of_last_diagonal_added)

				#when starting a diagonal
				#we do not want to add fake diagonals [n, n]
				else:
					if self.clicked_point != None and self.follow_mouse == False:
						self.follow_mouse = True
						index = self.clicked_point
						x_point_clicked_on = self.all_points[index][0]
						y_point_clicked_on = self.all_points[index][1]
						self.curves["diagonals"]["points"].append([])
						self.curves["diagonals"]["points"][len(self.curves["diagonals"]["points"])-1].append([x_point_clicked_on, y_point_clicked_on])
						self.curves["diagonals"]["index"].append([])
						self.curves["diagonals"]["index"][len(self.curves["diagonals"]["index"])-1].append(self.all_points[index][2])

				#when continuing a diagonal
				if self.follow_mouse == True and self.clicked_point == None:
					self.curves["diagonals"]["points"][len(self.curves["diagonals"]["points"])-1].append([(updated_x_click-width/2)/height, (updated_y_click-height/2)/-height])

				self.is_clicked = False

				#we clear the midpoints list
				self.curves["diagonals"]["midpoints"].clear()
				#add middle points in order to interact with the diagonals
				for i in range(len(self.curves["diagonals"]["points"])):
					if geometry101.middle_curve(self.curves["diagonals"]["points"][i], height, width) != []:
						self.curves["diagonals"]["midpoints"].append(geometry101.middle_curve(self.curves["diagonals"]["points"][i], height, width))

				#we want to highlight the diagonal that is overlapped or clicked on
				#here we can interact with the diagonals
				counter = 0
				#we need to create a big list containing all the lines 

				for i in range(len(self.curves["diagonals"]["midpoints"])):
					if math.dist([updated_x_click, updated_y_click], [width/2 + self.curves["diagonals"]["midpoints"][i][0]*height, height/2 - self.curves["diagonals"]["midpoints"][i][1]*height])< height*0.009:
						#if the click is close enough, then the ith puncture becomes the pressed puncture (the only one that can be moved and that will appear bigger)
						self.curves["diagonals"]["pressed_two"] = i	
						#we set the pressed_two value of component to None because we do not want to click on a component and a puncture at the same time
					else:
						counter += 1	

				if len(self.curves["diagonals"]["midpoints"]) == counter:
					self.curves["diagonals"]["pressed_two"] = None	

				self.curves["diagonals"]["calculation_lines"]["lines"].clear()

				#we want to create the diagonal calculation lines
				for i in range(len(self.curves["diagonals"]["points"])):
					self.curves["diagonals"]["calculation_lines"]["lines"].append(self.curves["diagonals"]["points"][i])

				if self.curves["diagonals"]["pressed_two"] != None:
					j = self.curves["diagonals"]["pressed_two"] + len(self.curves["sides"]["points"]) + len(self.curves["components"]["calculation_lines"]["index"])
					i = self.curves["diagonals"]["pressed_two"]
					#create a new list with all lines we need to analyse our triangulations
					#take into account whether the main shape is a circle or a polygon
					#switch arcs of circles with their tangent at their marked points
					#another list (a bit different, will have to be created to actually draw the line from one point to another)
					geometry101.diagonal_points(j, self.all_lines["lines"], self.all_lines["index"], self.two_points, self.test_line, self.quadrilateral, self.endpoint)
					self.curves["diagonals"]["points"].pop(i)
					self.curves["diagonals"]["index"].pop(i)
					self.curves["diagonals"]["midpoints"].pop(i)

		#we create two new list used to make the angle calculation 
		self.all_lines["lines"] = self.curves["sides"]["calculation_lines"]["lines"] + self.curves["components"]["calculation_lines"]["lines"] + self.curves["diagonals"]["calculation_lines"]["lines"]
		self.all_lines["index"] = self.curves["sides"]["calculation_lines"]["index"] + self.curves["components"]["calculation_lines"]["index"] + self.curves["diagonals"]["index"]

		#we create a new list to make the automatic diagonal flip
		if self.quadrilateral[0][0] != []:
			added_list_0_1_0 = list(reversed(self.quadrilateral[0][1][0]))
			added_list_0_1_0.pop(0)
			added_list_1_1_0 = list(reversed(self.quadrilateral[1][1][0]))
			added_list_1_1_0.pop(0)
			self.calc_quadrilateral = [self.quadrilateral[0][0][0]+added_list_0_1_0]
			self.calc_quadrilateral = self.calc_quadrilateral[0]
			self.calc_quadrilateral_2 = [self.quadrilateral[0][0][0]+added_list_0_1_0, self.quadrilateral[1][0][0] + added_list_1_1_0]


		if self.curves["diagonals"]["pressed_two"] != None:
			geometry101.reference_points(self.reference_points, self.calc_quadrilateral)
			geometry101.new_diagonal(self.reference_points, self.calc_quadrilateral_2, self.shift_test2, self.shift_test, self.calc_quadrilateral, self.center)

		if self.curves["diagonals"]["pressed_two"] != None:
			new_list = self.two_points[1]+self.center+self.two_points[0]
			self.curves["diagonals"]["points"].append(list(reversed(new_list)))
			last = len(self.curves["diagonals"]["points"])-1
			self.curves["diagonals"]["index"].append(list(reversed(self.endpoint)))
			self.curves["diagonals"]["pressed_two"] = None
			self.curves["diagonals"]["midpoints"].append(geometry101.middle_curve(self.curves["diagonals"]["points"][last], height, width))


		self.curves["diagonals"]["midpoints"].clear()
		#add middle points in order to interact with the diagonals
		for i in range(len(self.curves["diagonals"]["points"])):
			if geometry101.middle_curve(self.curves["diagonals"]["points"][i], height, width) != []:
				self.curves["diagonals"]["midpoints"].append(geometry101.middle_curve(self.curves["diagonals"]["points"][i], height, width))

		#we want to highlight the diagonal that is overlapped or clicked on
		#here we can interact with the diagonals
		counter = 0
		#we need to create a big list containing all the lines 

		if len(self.curves["diagonals"]["midpoints"]) == counter:
			self.curves["diagonals"]["pressed_two"] = None	

		self.curves["diagonals"]["calculation_lines"]["lines"].clear()

		#we want to create the diagonal calculation lines
		for i in range(len(self.curves["diagonals"]["points"])):
			self.curves["diagonals"]["calculation_lines"]["lines"].append(self.curves["diagonals"]["points"][i])

		self.drawing_area.queue_draw()


	#functions for the popover (compute stuff about the triangulation)

	def diagonal_flip(self, action0, param):
		if self.done == True and self.diagonal_flip_mode == False:
			self.diagonal_flip_mode = True
		else:
			self.diagonal_flip_mode = False

	def quivers(self, action1, param):
		pass

	def cluster_algebra(self, action2, param):
		pass

	def F_polynomials(self, action3, param):
		pass

	def g_vector(self, action4, param):
		pass

	def c_vector(self, action5, param):
		pass


	#this function draws stuff on the cairo canvas

	def draw(self, area, ctx, width, height, data):
		#can do any amount of transform only with a list with one value for scale and one for translate
		def transform(ctx, list_scale_translate):
			ctx.translate(list_scale_translate[1][0], list_scale_translate[1][1])
			ctx.scale(list_scale_translate[0][0], list_scale_translate[0][1])

		#add canvas
		ctx.set_source_rgb(1,1,1)
		ctx.rectangle(0, 0, width, height)
		ctx.fill_preserve()
		ctx.set_source_rgb(0.5,0.5,0.5)
		ctx.set_line_width(2)
		ctx.stroke()

		#scale things inside the canvas with the self.transform list
		transform(ctx, self.transform)

		#add circle
		ctx.set_source_rgb(0.7,0.7,0.7)
		if self.curves["punctures"]["points"] != [] or self.curves["components"]["center"] != []:
			ctx.set_source_rgb(0,0,0)
		#if there is a puncture, the circle is rounded
		ctx.arc(width/2, height/2, height*0.3, 0, 2 * math.pi)
		ctx.stroke()

		#here we add the sides
		for i in range(len(self.curves["sides"]["points"])):
			#add red points to define the polygon
			if self.curves["punctures"]["points"] == [] and self.curves["components"]["points"] == []:
				geometry101.draw_line(0, 0, 0, width/2+self.curves["sides"]["lines"][i][0]*height, height/2-self.curves["sides"]["lines"][i][1]*height, width/2+self.curves["sides"]["lines"][i][2]*height, height/2-self.curves["sides"]["lines"][i][3]*height, 2.5, height, ctx)
			geometry101.draw_point(1, 0, 0, width/2+self.curves["sides"]["points"][i][0]*height, height/2-self.curves["sides"]["points"][i][1]*height, 0.01, height, ctx)

		#add the punctures
		for i in range(len(self.curves["punctures"]["points"])):
			geometry101.draw_point(1, 0, 0, width/2+self.curves["punctures"]["points"][i][0]*height, height/2-self.curves["punctures"]["points"][i][1]*height, 0.01, height, ctx)

		#the puncture will be bigger if we click on it:
		if self.curves["punctures"]["pressed_two"] != None:
			pressed_two = self.curves["punctures"]["pressed_two"]
			geometry101.draw_point(0.9, 0, 0, width/2+self.curves["punctures"]["points"][pressed_two][0]*height, height/2-self.curves["punctures"]["points"][pressed_two][1]*height, 0.015, height, ctx)

		#draw the components
		for i in range(len(self.curves["components"]["center"])):	
				ctx.set_source_rgb(0.9,0.9,0.9)
				ctx.arc(width/2+self.curves["components"]["center"][i][0]*height, height/2-self.curves["components"]["center"][i][1]*height, height*self.curves["components"]["center"][i][2], 0, 2*math.pi)
				ctx.fill()
				ctx.set_source_rgb(0,0,0)
				ctx.arc(width/2+self.curves["components"]["center"][i][0]*height, height/2-self.curves["components"]["center"][i][1]*height, height*self.curves["components"]["center"][i][2], 0, 2*math.pi)
				ctx.stroke()

		#make component blue when clicked on
		if self.curves["components"]["pressed_two"] != None:
			pressed_two = self.curves["components"]["pressed_two"]
			ctx.set_source_rgb(0,0,1)
			ctx.arc(width/2+self.curves["components"]["center"][pressed_two][0]*height, height/2-self.curves["components"]["center"][pressed_two][1]*height, height*self.curves["components"]["center"][pressed_two][2], 0, 2*math.pi)
			ctx.stroke()

		#add points around components
		for i in range(len(self.curves["components"]["points"])):
			for j in range(len(self.curves["components"]["points"][i])):
				geometry101.draw_point(1, 0, 0, width/2+self.curves["components"]["points"][i][j][0]*height, height/2-self.curves["components"]["points"][i][j][1]*height, 0.01, height, ctx)
			
		#what is below is no longer needed but is a good example of how to work with the dictionaries 

		#draw all the points in blue when self.done == True
		if self.done == True:
			#when we overlap a point it becomes bigger and changes color
			if self.overlapped_point != None:
				index = self.overlapped_point
				geometry101.draw_point(0.7, 0, 0, width/2+self.all_points[index][0]*height, height/2-self.all_points[index][1]*height, 0.015, height, ctx)
			if self.clicked_point != None:
				index = self.clicked_point
				geometry101.draw_point(0.5, 0, 0, width/2+self.all_points[index][0]*height, height/2-self.all_points[index][1]*height, 0.015, height, ctx)

			if self.follow_mouse == True:
				updated_x_pos = (self.x_pos - self.transform[1][0])/(self.transform[0][0])
				updated_y_pos = (self.y_pos - self.transform[1][1])/(self.transform[0][1])
				#find last point added inside of the self.diagonals
				last_x_appended = self.curves["diagonals"]["points"][len(self.curves["diagonals"]["points"])-1][len(self.curves["diagonals"]["points"][len(self.curves["diagonals"]["points"])-1])-1][0]
				last_y_appended = self.curves["diagonals"]["points"][len(self.curves["diagonals"]["points"])-1][len(self.curves["diagonals"]["points"][len(self.curves["diagonals"]["points"])-1])-1][1]
				#problem here when zooming in 
				geometry101.draw_line(0.7, 0.7, 0.7, width/2+last_x_appended*height, height/2-last_y_appended*height, updated_x_pos, updated_y_pos, 1.5, height, ctx)

			#draw the added diagonals
			for i in range(len(self.curves["diagonals"]["points"])):
				geometry101.draw_curve_from_list(self.curves["diagonals"]["points"][i], 0, 0, 0, 2.5, ctx, height, width)

			#if we are in flip mode, we add mid points to the diagonals
			if self.diagonal_flip_mode == True:
				#draw the midpoints of the diagonals
				for i in range(len(self.curves["diagonals"]["midpoints"])):
					geometry101.draw_point(0, 0, 1, width/2+self.curves["diagonals"]["midpoints"][i][0]*height, height/2-self.curves["diagonals"]["midpoints"][i][1]*height, 0.01, height, ctx)

		#if self.save is already activated when clicking on the button, self.save is set to False
		if self.save == True:
			self.save = False
			src_surface = ctx.get_target()
			dst_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, math.floor(self.drawing_area.get_width()), math.floor(self.drawing_area.get_height()))
			dst_context = cairo.Context(dst_surface)
			dst_context.set_source_surface(src_surface, 0, 0)
			dst_context.paint()
			dst_surface.write_to_png("test.png")	

def on_activate(app):
	#creates an instance of the class main window
	win = MainWindow(application=app)
	win.present()

app = Gtk.Application()
app.connect('activate', on_activate)

app.run(None)
