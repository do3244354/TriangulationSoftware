import gi

#add a help button for the software

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gdk, Gio

#here we have functions using gtk 

def basic_window(self):
	#box layout and basic parameters
	self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	self.set_child(self.box)
	self.set_default_size(700, 500)
	self.set_title("Triangulation Software")

	#add two boxes, one for the canvas, one for the footer 
	self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	self.box.append(self.box1)
	self.box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
	self.box.append(self.box2)

	#add icon of app and header buttons
	self.header = Gtk.HeaderBar()
	self.set_titlebar(self.header)

	#add a button with the icon of the app
	self.icon_button = Gtk.Button(label="Icone")
	self.image = Gtk.Image.new_from_file("TriangulationSoftwareIcon.png")
	self.icon_button.set_child(self.image)
	self.icon_button.set_has_frame(True)
	self.header.pack_start(self.icon_button)
	self.icon_button.connect('clicked', self.about)

	#to create a new action for flipping diagonals
	action0 = Gio.SimpleAction.new("diagonal_flip", None)
	action0.connect("activate", self.diagonal_flip)
	self.add_action(action0)

	#to create a new action for quivers
	action1 = Gio.SimpleAction.new("quivers", None)
	action1.connect("activate", self.quivers)
	self.add_action(action1)

	#to create a new action for cluster algebra
	action2 = Gio.SimpleAction.new("cluster_algebra", None)
	action2.connect("activate", self.cluster_algebra)
	self.add_action(action2)

	#to create a new action for F-polynomials
	action3 = Gio.SimpleAction.new("F_polynomials", None)
	action3.connect("activate", self.F_polynomials)
	self.add_action(action3)

	#to create a new action for g-vector
	action4 = Gio.SimpleAction.new("g_vector", None)
	action4.connect("activate", self.g_vector)
	self.add_action(action4)

	#to create a new action for c-vector
	action5 = Gio.SimpleAction.new("c_vector", None)
	action5.connect("activate", self.c_vector)
	self.add_action(action5)

	#create new menu
	menu = Gio.Menu.new()
	menu.append("Diagonal flip", "win.diagonal_flip")
	menu.append("Quiver", "win.quivers")
	menu.append("Cluster Algebra", "win.cluster_algebra")
	menu.append("F-polynomials", "win.F_polynomials")
	menu.append("g-vector", "win.g_vector")
	menu.append("c-vector", "win.c_vector")

	#create popover
	self.popover = Gtk.PopoverMenu()
	self.popover.set_menu_model(menu)
	
	#add a button that is associated with the popover
	self.header_button3 = Gtk.MenuButton()
	self.header_button3.set_popover(self.popover)
	self.header_button3.set_icon_name("open-menu-symbolic")
	self.header.pack_start(self.header_button3)

	#create a new button (to save the image)
	self.header_button2 = Gtk.Button(label="File")
	self.header_button2.set_icon_name("document-open-symbolic")
	self.header.pack_start(self.header_button2)
	self.header_button2.connect('clicked', self.save_image)

	#add a drawing area
	self.drawing_area = Gtk.DrawingArea()
	self.drawing_area.set_hexpand(True)
	self.drawing_area.set_vexpand(True)
	self.drawing_area.set_draw_func(self.draw, None)
	self.box1.append(self.drawing_area)

	#add label sides
	self.label1 = Gtk.Label(label="  Sides:")
	self.box2.append(self.label1)

	#add entries and labels and buttons
	adjustment = Gtk.Adjustment(upper=20, step_increment=1, page_increment=10)
	self.spinbutton = Gtk.SpinButton()
	self.spinbutton.set_adjustment(adjustment)
	self.spinbutton.connect("value-changed", self.on_value_changed)
	self.box2.append(self.spinbutton)

	#add label punctures
	self.label2 = Gtk.Label(label="  Add puncture:")
	self.box2.append(self.label2)

	#add puncture button
	self.button1 = Gtk.Button(label = "+")
	self.button1.set_icon_name("list-add-symbolic")
	self.box2.append(self.button1)
	self.button1.connect('clicked', self.add_puncture)

	#add label component
	self.label3 = Gtk.Label(label="  Add component:")
	self.box2.append(self.label3)

	#add component button
	self.button2 = Gtk.Button(label = "+")
	self.button2.set_icon_name("list-add-symbolic")
	self.box2.append(self.button2)
	self.button2.connect('clicked', self.add_component)

	#add done button (will disable the other buttons when clicked)
	self.button3 = Gtk.ToggleButton(label = "Done")
	self.box2.append(self.button3)
	self.button3.connect('clicked', self.disable_editing)

	#add 1 button (will rescale and retranslate everything to the normal view)
	self.button4 = Gtk.Button(label = "1")
	self.box2.append(self.button4)
	self.button4.connect('clicked', self.back_to_normal)

	#mouse events
	event_controller_click = Gtk.GestureClick.new()
	event_controller_click.connect("pressed", self.on_mouse_click)
	event_controller_click.connect("released", self.on_mouse_release)
	self.box.add_controller(event_controller_click)

	#motion controller
	event_controller_motion = Gtk.EventControllerMotion.new()
	event_controller_motion.connect("motion", self.on_mouse_motion)
	self.box.add_controller(event_controller_motion)

	#key controller
	event_controller_key = Gtk.EventControllerKey.new()
	event_controller_key.connect("key-pressed", self.key_press)
	self.box.add_controller(event_controller_key)

