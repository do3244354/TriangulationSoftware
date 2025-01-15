import math
import cairo

#find the coordinate of a circle
def circle_coordinate(n, i, rotation, radius):
	coordinate = [(radius*(math.cos((i)*2*math.pi/(n)+rotation))),(radius*(math.sin((i)*2*math.pi/(n)+rotation)))]
	return coordinate

#the following are functions related to drawing
#to draw a line
def draw_line(color1, color2, color3, x1, y1, x2, y2, line_width, height, ctx):
	ctx.set_source_rgb(color1, color2, color3)
	ctx.set_line_width(line_width)
	ctx.move_to(x1, y1)
	ctx.line_to(x2, y2)
	ctx.stroke()

#to draw a point
def draw_point(color1, color2, color3, x1, y2, scalling_factor, height, ctx):
	ctx.set_source_rgb(color1, color2, color3)
	ctx.arc(x1, y2, height*scalling_factor, 0, 2*math.pi)
	ctx.fill()

#to transform the lines into a smooth bezier curve
def draw_curve_from_list(point_list, color1, color2, color3, line_width, ctx, height, width):
	curvature = 1/2
	ctx.set_source_rgb(color1, color2, color3)
	ctx.set_line_width(line_width)
	#verify if it is just a normal line
	if len(point_list) == 2:
		ctx.move_to(width/2 + point_list[0][0]*height, height/2 - point_list[0][1]*height)
		ctx.line_to(width/2 + point_list[1][0]*height, height/2 - point_list[1][1]*height)
	else:	
		for i in range(len(point_list)-2):
			#if i == 0, we draw a line for the first two thirds of the the first line
			if i == 0:
				#we want to compute the 2/3 points between i and i+1 (call it 2/3i)
				mid2_3_x = point_list[i][0] + (point_list[i+1][0] - point_list[i][0])*(1-curvature)
				mid2_3_y = point_list[i][1] + (point_list[i+1][1] - point_list[i][1])*(1-curvature)
				ctx.move_to(width/2 + point_list[i][0]*height, height/2 - point_list[i][1]*height) #i
				ctx.line_to(width/2 + mid2_3_x*height, height/2 - mid2_3_y*height) #2/3i
			#else, we draw one third of it at the middle
			else:
				#we want to compute 1/3 and 2/3 between i and i+1 (1/3i and 2/3i)
				mid1_3_x = point_list[i][0] + (point_list[i+1][0] - point_list[i][0])*(curvature)
				mid1_3_y = point_list[i][1] + (point_list[i+1][1] - point_list[i][1])*(curvature)
				mid2_3_x = point_list[i][0] + (point_list[i+1][0] - point_list[i][0])*(1-curvature)
				mid2_3_y = point_list[i][1] + (point_list[i+1][1] - point_list[i][1])*(1-curvature)
				ctx.move_to(width/2 + mid1_3_x*height, height/2 - mid1_3_y*height) #1/3i
				ctx.line_to(width/2 + mid2_3_x*height, height/2 - mid2_3_y*height) #2/3i
			#if this is the last i of the list, we finish with a line (draw last third with line)
			if i == len(point_list)-3:
				#we want to compute 2/3 of i+1 to i+2
				mid1_3_x = point_list[i+1][0] + (point_list[i+2][0] - point_list[i+1][0])*(curvature)
				mid1_3_y = point_list[i+1][1] + (point_list[i+2][1] - point_list[i+1][1])*(curvature)
				ctx.move_to(width/2 + mid1_3_x*height, height/2 - mid1_3_y*height) #2/3(i+1)
				ctx.line_to(width/2 + point_list[i+2][0]*height, height/2 - point_list[i+2][1]*height) #i+2
			#if it is not the last, we draw a bézier curves 

			#we want to compute 2/3 between i and i+1 and 1/3 between i+1 and i+2, with i+1 as control point
			mid2_3_x = point_list[i][0] + (point_list[i+1][0] - point_list[i][0])*(1-curvature)
			mid2_3_y = point_list[i][1] + (point_list[i+1][1] - point_list[i][1])*(1-curvature)
			mid1_3_x = point_list[i+1][0] + (point_list[i+2][0] - point_list[i+1][0])*(curvature)
			mid1_3_y = point_list[i+1][1] + (point_list[i+2][1] - point_list[i+1][1])*(curvature)
			ctx.move_to(width/2 + mid2_3_x*height, height/2 - mid2_3_y*height)
			ctx.curve_to(width/2 + point_list[i+1][0]*height, height/2 - point_list[i+1][1]*height, width/2 + point_list[i+1][0]*height, height/2 - point_list[i+1][1]*height, width/2 + mid1_3_x*height, height/2 - mid1_3_y*height)
	ctx.stroke()

#functions that chooses a point in the middle of the curve
#the curve value is a list of points (only one curve)
def middle_curve(curve, height, width):
	#we calculate the len of the curve
	i = 0 
	dist = 0
	dist_list = []
	middle_point = []
	yes = None

	for i in range(len(curve)-1):
		dist += math.dist([curve[i][0], curve[i][1]], [curve[(i+1) % len(curve)][0], curve[(i+1) % len(curve)][1]])
		dist_list.append(dist)

	#now we consider half the length
	half_dist = dist/2
	
	i = 0
	#it is as if we remain in the loop indefinitely
	while i < len(dist_list):
		if dist_list[i] <= half_dist:
			i+=1
		else: 
			yes = i
			middle_point.clear()
			if type(curve[i]) != bool and type(curve[i+1]) != bool:
				middle_point.append(curve[i][0]+(curve[i+1][0]-curve[i][0])/2)
				middle_point.append(curve[i][1]+(curve[i+1][1]-curve[i][1])/2)
			break		

	return middle_point

#calculates the angle relative to the x axis
#x1 and y1 must be the point both lines have in common
def angle_relative_to_x_axis(x1, y1, x2, y2):
	#get it in vector form (vector starting at origin)
	angle = 0 
	v = [x1-x2, y1-y2]
	if v[0] != 0:
		angle_of_triangle = math.atan(abs(v[1])/(abs(v[0])))
		if v[0] >= 0 and v[1] >= 0:
			angle = angle_of_triangle
		if v[0] <= 0 and v[1] >= 0:
			angle = math.pi - angle_of_triangle
		if v[0] <= 0 and v[1] <= 0:
			angle = math.pi + angle_of_triangle
		if v[0] >= 0 and v[1] <= 0:
			angle = 2*math.pi - angle_of_triangle
	else:
		if v[1] >= 0:
			angle = math.pi/2
		else:
			angle = 3*math.pi/2

	return angle*(180/math.pi)

#we must figure out a way of determining the starting and ending point of the new diagonal created by a flip
#curves: list of all curves, index: list of all index
#end1 has all points of one extremity of the diagonal, end2 has all others
#test is only used to draw the point found
def diagonal_points(i, curves, index, test, line_draw, quadrilateral_list, endpoints):
	quadrilateral_list[0][0].clear()
	quadrilateral_list[0][1].clear()
	quadrilateral_list[1][0].clear()
	quadrilateral_list[1][1].clear()
	end1 = []
	end2 = []  
	line_draw.clear()

	two_points = [[], []]

	for j in range(len(index)):
	#for j in range(len(index)-1):
		if index[j][0] == index[i][0] and j != i:
			end1.append([j, True, index[j][1]])

		#there is often a mistake at this line
		if index[j][1] == index[i][0] and j != i:
			end1.append([j, False, index[j][0]])

		if index[j][0] == index[i][1] and j != i:
			end2.append([j, True, index[j][1]])

		if index[j][1] == index[i][1] and j != i:
			end2.append([j, False, index[j][0]])

	#now we calculate the angle for end1
	calculate_angle_from_list(i, curves, index, test, line_draw, end1, two_points, curves[i], quadrilateral_list[0], endpoints)
	calculate_angle_from_list(i, curves, index, test, line_draw, end2, two_points, list(reversed(curves[i])), quadrilateral_list[1], None)

#this function is meant to be used in the function above
def calculate_angle_from_list(i, curves, index, test, line_draw, end, two_points, curves_i, quadrilateral_list, endpoints):
	two_points[0].clear()
	two_points[1].clear()
	for j in range(len(end)):
		if end[j][1] == True:
			a = (angle_relative_to_x_axis(curves[end[j][0]][1][0], curves[end[j][0]][1][1], curves[end[j][0]][0][0], curves[end[j][0]][0][1]))%360
			b = (angle_relative_to_x_axis(curves_i[1][0], curves_i[1][1], curves_i[0][0], curves_i[0][1]))
			line_draw.append([curves[end[j][0]][1][0], curves[end[j][0]][1][1], curves[end[j][0]][0][0], curves[end[j][0]][0][1]])

			new_angle = (b-a)%360
			point_comparison(two_points[0], [curves[end[j][0]][len(curves[end[j][0]])-1][0], curves[end[j][0]][len(curves[end[j][0]])-1][1]], new_angle, quadrilateral_list[0], end[j][0], True, curves, end[j][2])
			
			new_angle1 = (a-b)%360
			point_comparison(two_points[1], [curves[end[j][0]][len(curves[end[j][0]])-1][0], curves[end[j][0]][len(curves[end[j][0]])-1][1]], new_angle1, quadrilateral_list[1], end[j][0], True, curves, end[j][2])

		else:
			last = len(curves[end[j][0]])-1
			a = (angle_relative_to_x_axis(curves[end[j][0]][last-1][0], curves[end[j][0]][last-1][1], curves[end[j][0]][last][0], curves[end[j][0]][last][1]))%360
			b = (angle_relative_to_x_axis(curves_i[1][0], curves_i[1][1], curves_i[0][0], curves_i[0][1]))
			line_draw.append([curves[end[j][0]][last][0], curves[end[j][0]][last][1], curves[end[j][0]][last-1][0], curves[end[j][0]][last-1][1]])

			new_angle = (b-a)%360
			point_comparison(two_points[0], [curves[end[j][0]][0][0], curves[end[j][0]][0][1]], new_angle, quadrilateral_list[0], end[j][0], False, curves, end[j][2])

			new_angle1 = (a-b)%360
			point_comparison(two_points[1], [curves[end[j][0]][0][0], curves[end[j][0]][0][1]], new_angle1, quadrilateral_list[1], end[j][0], False, curves, end[j][2])

	#in point comparison we figure out which point is closest to the diagonal clockwise of counterclockwise
	#one of the two points must be considered the first in the separated line
	if endpoints != None:
		endpoints.clear()

	if two_points[0] != []:
		test[0].clear()
		test[0].append(two_points[0][0])
		if endpoints != None:
			endpoints.append(two_points[0][2])

	if two_points[1] != []:
		test[1].clear()
		test[1].append(two_points[1][0])
		if endpoints != None:
			endpoints.append(two_points[1][2])

#the list has the point as first element, and the angle as second element
#point is a list which contains the new point to compare with 
#new_angle is the angle of the point
def point_comparison(list1, point, new_angle, quadrilateral_list, j, bool, curves, end_index):
	if list1 == []:
		list1.append(point)
		list1.append(new_angle)
		list1.append(end_index)
		if bool == True:
			quadrilateral_list.append(list(reversed(curves[j])))
		else:
			quadrilateral_list.append(curves[j])
	else:
		if list1[1] > new_angle:
			list1.clear()
			list1.append(point)
			list1.append(new_angle)
			list1.append(end_index)
			quadrilateral_list.clear()
			if bool == True:
				quadrilateral_list.append(list(reversed(curves[j])))
			else:
				quadrilateral_list.append(curves[j])

#we want a function that will take a list (which represents a line) and will separate it in 20 parts
#we take the line info from line_calc_list and add the information to reference_points_list
def reference_points(reference_points_list, line_calc_list):
	#after every reference point, we must indicate to which line_calc is belongs
	#we want to take the line_calc_list and measure its length
	#print the len (in units of the line_calc_list)
	#there is a problem with the length calculated
	reference_points_list.clear()
	list_of_length = []
	total_length = 0
	len_list = len(line_calc_list)
	list_of_length.append(0)
	for i in range(len(line_calc_list)-1):
		x = math.dist([line_calc_list[i][0], line_calc_list[i][1]], [line_calc_list[(i+1) % len_list][0], line_calc_list[(i+1) % len_list][1]])
		total_length += x
		list_of_length.append(total_length)
	#try to draw a point at the middle of the curve
	if list_of_length != []:
		for j in range(30):
			middle = total_length*(j+1)/31
			len_list = len(list_of_length)
			i = 0
			while list_of_length[i % len_list] < middle:
				if list_of_length[(i+1) % len_list] >= middle:
					delta = 0.01
					a = middle-list_of_length[i]
					b = list_of_length[(i+1) % len_list] - list_of_length[i]
					x = line_calc_list[i][0]+a/b*(line_calc_list[(i+1) % len_list][0]-line_calc_list[i][0])
					y = line_calc_list[i][1]+a/b*(line_calc_list[(i+1) % len_list][1]-line_calc_list[i][1])
					reference_points_list.append([x, y, i])
				i+=1

#now we must take the reference point in the list and also the calc_quadrilateral_2 list. We will try to find the biggest circle tangent to the
#line of the reference point that fits completely inside the close shape. For that, we set the the point of reference as the origin and shift than rotate all the points making the points
#according to this transformation

def new_diagonal(reference_points, all_quadrilateral_lines, shift_test_list2, shift_test_list, line_calc_list, center_list):
	center_list.clear()
	for l in range(29):
		biggest_circle_at_reference_point(reference_points, all_quadrilateral_lines, shift_test_list2, shift_test_list, line_calc_list, center_list, l)
		#one of the problem is with l=8, 11, 12, 13
		#there are seven bad points in total
		#there is likely a problem with how horizontal and vertical lines are handled 

def biggest_circle_at_reference_point(reference_points, all_quadrilateral_lines, shift_test_list2, shift_test_list, line_calc_list, center_list, l):
	if reference_points != []:
		line_of_ref_point = reference_points[l][2]

		ln = len(line_calc_list)

		#print(ln)

		#the diagonals were always added from clockwise to counterclockwise. this might not be the case with the newly added diagonals
		angle_of_rotation = angle_relative_to_x_axis(line_calc_list[line_of_ref_point][0], line_calc_list[line_of_ref_point][1], line_calc_list[(line_of_ref_point + 1) % ln][0], line_calc_list[(line_of_ref_point + 1) % ln][1])
		angle_of_rotation = (-angle_of_rotation)%360
		angle_of_rotation = (math.pi * angle_of_rotation) / 180

		shift_test_list.clear()

		shift_test_list2.clear()

		#we shift all points accoring to a given reference point
		for i in range(len(all_quadrilateral_lines[0])):
			#breakpoint()

			new_point_x = all_quadrilateral_lines[0][i][0] - reference_points[l][0]
			new_point_y = all_quadrilateral_lines[0][i][1] - reference_points[l][1]

			new_point_x_1 = new_point_x*math.cos(angle_of_rotation) - new_point_y*math.sin(angle_of_rotation)
			new_point_y_1 = new_point_x*math.sin(angle_of_rotation) + new_point_y*math.cos(angle_of_rotation)

			shift_test_list.append([new_point_x_1, new_point_y_1])

		for i in range(len(all_quadrilateral_lines[1])):

			new_point_x = all_quadrilateral_lines[1][i][0] - reference_points[l][0]
			new_point_y = all_quadrilateral_lines[1][i][1] - reference_points[l][1]

			new_point_x_1 = new_point_x*math.cos(angle_of_rotation) - new_point_y*math.sin(angle_of_rotation)
			new_point_y_1 = new_point_x*math.sin(angle_of_rotation) + new_point_y*math.cos(angle_of_rotation)

			shift_test_list2.append([new_point_x_1, new_point_y_1])

		#we will first find the middle point according to the first reference point
		radius = None

		smallest_radius = None

		for i in range(len(shift_test_list2)-1):
			len_list = len(shift_test_list2)

			x1 = shift_test_list2[i][0]
			y1 = shift_test_list2[i][1]
			x2 = shift_test_list2[(i+1) % len_list][0]
			y2 = shift_test_list2[(i+1) % len_list][1]

			if x2 != x1:
				slope = (y2 - y1)/(x2 - x1)
			else:
				slope = None

			if slope != None:
				b = y1 - (slope)*x1
			else:
				#this is the case when we get an equation x = k
				b = None

			#we must find the radius of the biggest circle that intersects the line at only one point

			if slope == None:
				radius = abs(x1)
			elif abs(slope) < 0.000001:
				if b > 0:
					radius = b/2
				#this is a mistake...
				if b <= 0:
					radius = None
			else:
				if b > 0:
					radius = (b/(slope**2))*(math.sqrt(1+slope**2)-1)
				if b <= 0:
					radius = (b/(slope**2))*(-math.sqrt(1+slope**2)-1)
					#radius = None

			#get the point of intersection between the line and the circle
			if radius != None:
				if slope != None:
					x_intersect = -(2*slope*b-2*slope*radius)/(2*(1+slope**2))
					y_intersect = slope*(x_intersect)+b
				else:
					x_intersect = x1
					#y_intersect = math.sqrt(math.sqrt(radius**2-(x_intersect)**2) + radius)
					y_intersect = radius
			

				if ((x1 <= x_intersect <= x2) or (x1 >= x_intersect >= x2)) or ((y1 <= y_intersect <= y2) or (y1 >= y_intersect >= y2)):
					#if smallest_radius == None or abs(radius) < abs(smallest_radius):
					if smallest_radius == None or radius < smallest_radius:
						smallest_radius = radius
				else:
					if y1 > 0.0000000001:
						radius1 = (x1**2+y1**2)/(2*y1)
					else:
						radius1 = None
					if y2 > 0.0000000001:
						radius2 = (x2**2+y2**2)/(2*y2)
					else:
						#radius = abs(x1)
						radius2 = None
					if radius1 != None and radius2 != None:
						radius = min(radius1, radius2)
					elif radius1 == None and radius2 != None:
						radius = radius2
					elif radius1 != None:
						radius = radius1
					else:
						radius = None
					
			if radius != None:
				if (smallest_radius == None or radius < smallest_radius):
					smallest_radius = radius

		for i in range(len(shift_test_list)-1):

			if i != reference_points[l][2]:
				len_list = len(shift_test_list)

				x1 = shift_test_list[i][0]
				y1 = shift_test_list[i][1]
				x2 = shift_test_list[i+1][0]
				y2 = shift_test_list[i+1][1]

				if abs(x2 - x1) > 0.0000001:
					slope = (y2 - y1)/(x2 - x1)
				else:
					slope = None

				if slope != None:
					b = y1 - (slope)*x1
				else:
					#this is the case when we get an equation x = k
					b = None

				#there is a bug related with the punctured triangle
				#we must find the radius of the biggest circle that intersects the line at only one point

				if slope == None:
					radius = abs(x1) 
				elif abs(slope) < 0.0000001:
					if b > 0:
						radius = b/2
					if b <= 0:
						radius = None
				else:
					if b > 0:
						radius = (b/(slope**2))*(math.sqrt(1+slope**2)-1)
					if b <= 0:
						radius = (b/(slope**2))*(-math.sqrt(1+slope**2)-1)
						#radius = None

				#get the point of intersection between the line and the circle
				if radius != None:
					if slope != None:
						x_intersect = -(2*slope*b-2*slope*radius)/(2*(1+slope**2))
						y_intersect = slope*(x_intersect)+b
					else:
						x_intersect = x1
						#y_intersect = math.sqrt(math.sqrt(radius**2-(x_intersect)**2) + radius)
						y_intersect = radius

					if ((x1 <= x_intersect <= x2) or (x1 >= x_intersect >= x2)) or ((y1 <= y_intersect <= y2) or (y1 >= y_intersect >= y2)):
						#if smallest_radius == None or abs(radius) < abs(smallest_radius):
						if smallest_radius == None or radius < smallest_radius:
							smallest_radius = None
					else:

						if y1 > 0.0000000001:
							radius1 = (x1**2+y1**2)/(2*y1)
						else:
							radius1 = None
						if y2 > 0.0000000001:
							radius2 = (x2**2+y2**2)/(2*y2)
						else:
							#radius = abs(x1)
							radius2 = None
						if radius1 != None and radius2 != None:
							radius = min(radius1, radius2)
						elif radius1 == None and radius2 != None:
							radius = radius2
						elif radius1 != None:
							radius = radius1
						else:
							radius = None

				if radius != None:
					if smallest_radius == None:
						smallest_radius = None
					elif radius < smallest_radius:
						smallest_radius = None

		#find the center of the smallest radius circle
		if smallest_radius != None:
			x_center = 0
			y_center = smallest_radius

			x_center1 = - y_center*math.sin(-angle_of_rotation)
			y_center1 =  y_center*math.cos(-angle_of_rotation)

			x_center = x_center1 + reference_points[l][0]
			y_center = y_center1 + reference_points[l][1]

			center_list.append([x_center, y_center])


