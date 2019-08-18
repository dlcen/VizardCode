# import necessary modules
import viz, vizshape, vizmat, math
import numpy as np

# Create the objects in the scene
# Create the ground - can use this as the parent, to fix other objects
def groundCreator():
	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(100, 0, -100)
	viz.texCoord(1,0) 
	viz.vertex(100, 0, 100)
	viz.texCoord(1,1) 
	viz.vertex(-100, 0, 100)
	viz.texCoord(0,1)  
	viz.vertex(-100, 0, -100)
	ground = viz.endLayer()

	AreaScale_f = [16, 16 ,1]

	matrix_area_f = vizmat.Transform()
	matrix_area_f.setScale(AreaScale_f)
	
	ground.texmat(matrix_area_f)

	wallTex = viz.addTexture('wallTex.jpg')
	wallTex.wrap(viz.WRAP_T,viz.REPEAT)
	wallTex.wrap(viz.WRAP_S,viz.REPEAT)

	ground.texture(wallTex)

	return ground

# Create the poles
def poleCreator(node, length, width, h, number, rad = 0.05):
	# pole colors
	poleColours = [[0.51, 0.79, 0.98], [0.84, 0.96, 0.96], [0.8, 0.998, 0.36], [1, 1, 0], [1, 0.9, 0.71], [1, 0.8, 0.64], [0.9, 0.4, 0.09], [0.77, 0.54, 0.09], [0.68, 0.66, 0.43], [0.98, 0.59, 0.42],[0.58, 0.27, 0.21], [0.49, 0.02, 0.32], [0.91, 0.68, 0.67], [0.99, 0.87, 1], [0.74, 0.23, 0.56], [0.37, 0.35, 0.5], [0.57, 0.45, 0.93], [0.91, 0.81, 0.93], [0.31, 0.54, 0.46], [0.29, 0.63, 0.17]]
	polePaper = viz.addTexture("walltex-w.jpg")

	a = np.arange(rad, width, 2*rad)
	x = np.repeat(a, len(a)) - width/2
	z = np.tile(a, len(a)/2 - 1) - rad
	x_right = x[ np.where( x> 0.1 ) ]
	x_left = x[ np.where( x < -0.05) ]
	pool_right = np.vstack((x_right, z))
	pool_right = np.transpose(pool_right)
	pool_left = np.vstack((x_left, z))
	pool_left = np.transpose(pool_left)
	# ind = np.random.choice(len(pool_right), number/2, replace=False)
	ind = np.round(np.random.uniform(0, 1, number/2) * len(x_right))
	ind = ind.astype( int )
	positions_right = pool_right[ind]
	ind = np.round(np.random.uniform(0, 1, number/2) * len(x_left))
	ind = ind.astype( int )
	positions_left = pool_left[ind]

	poles = viz.addGroup()
	polelist = []

	#add poles on the left side
	for i in range(number/2):

		# position for this pole
		thisX = positions_right[i, 0]
		thisZ = positions_right[i, 1]	

		#Load a pole
		pole= vizshape.addCylinder(height=h, radius=rad, yAlign=vizshape.ALIGN_MIN)
		pole.setParent(node)

		# Set the color
		pole.color(poleColours[i])
		pole.texture(polePaper)
		pole.appearance(viz.TEXMODULATE)

		#Set position
		pole.setPosition( [thisX, 0, thisZ] )

		#Append the pole to a list of poles
		pole.setParent(poles)
		
	#add poles on the left side
	for i in range(number/2):

		# position for this pole
		thisX = positions_left[i, 0]
		thisZ = positions_left[i, 1]	

		#Load a pole
		pole= vizshape.addCylinder(height=h, radius=rad, yAlign=vizshape.ALIGN_MIN)
		pole.setParent(node)
		
		# Set the color
		pole.color(poleColours[i + number/2])
		pole.texture(polePaper)
		pole.appearance(viz.TEXMODULATE)

		#Set position
		pole.setPosition( [thisX, 0, thisZ] )

		#Append the pole to a list of poles
		pole.setParent(poles)
		polelist.append(pole)

	poles.setParent(node)
	return (poles, polelist)

# Create the targets
def targetCreator(h, targetColor, rad=0.02):
	global Target
	# Target = viz.addGroup()
	Target = vizshape.addCylinder(height = h, radius=rad, yAlign=vizshape.ALIGN_MIN) #Change the diameter of the target
	Target.color(targetColor)

	#Generate random values for position and orientation
	# disk_rad=0.25; segment_no = 36
	
	# viz.startLayer(viz.POLYGON)
	# viz.pointSize(1)
	# for i in range(segment_no):
	# 	pt_z = disk_rad * math.cos(2*math.pi*i/segment_no)
	# 	pt_x = disk_rad * math.sin(2*math.pi*i/segment_no)
	# 	viz.vertex([pt_x, 0, pt_z])
	# disk = viz.endLayer()
	# disk.zoffset(-1)
	# disk.color(targetColor)

	return Target #, disk

