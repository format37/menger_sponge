import pymesh
import numpy as np
import math
import datetime

depth = 4

def mesh_trans(mesh, x, y, z):
    return pymesh.form_mesh(mesh.vertices + [[x, y, z]], mesh.faces)

def mesh_rotate(mesh, x, y, z, angle):
    rot = pymesh.Quaternion.fromAxisAngle(np.array([x, y, z]), math.pi*2*angle/360)
    return pymesh.form_mesh(np.dot(rot.to_matrix(), mesh.vertices.T).T, mesh.faces)

def menger_sponge(depth):
    sponge = None
    z = [-1,2]
    side = 1
    for d in range(1, depth+1):
        log(str(d)+' / '+str(depth)+' sponge holes iteration')
        side /= 3
        for x in range(1,3**d,3):
            for y in range(1,3**d,3):
                if sponge is None:
                    sponge = pymesh.generate_box_mesh([side*x,side*y,z[0]], [side*x+side,side*y+side,z[1]])
                else:
                    sponge = pymesh.boolean(
                        sponge, 
                        pymesh.generate_box_mesh([side*x,side*y,z[0]], [side*x+side,side*y+side,z[1]]), 
                        operation="union", 
                        engine="igl"
                        )
    return sponge

def log(message):
    print(datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'), message)

# solid box
log('0 / '+str(depth)+' iteration')
mesh_fractal = pymesh.generate_box_mesh([0,0,0], [1,1,1])

# sponge holes generation
sponge_a = menger_sponge(depth)
log('rotate b')
sponge_b = mesh_rotate(mesh = sponge_a, x = 1, y = 0, z = 0, angle = 90)
log('trans b')
sponge_b = mesh_trans(mesh = sponge_b, x = 0, y = 1, z = 0)
log('rotate c')
sponge_c = mesh_rotate(mesh = sponge_a, x = 0, y = 1, z = 0, angle = 90)
log('trans c')
sponge_c = mesh_trans(mesh = sponge_c, x = 0, y = 0, z = 1)

# sponge holes union into single mesh model
operation = 'union'
log('union u = a + b')
sponge_u = pymesh.boolean(sponge_a, sponge_b, operation=operation, engine="igl")
log('union u = u + c')
sponge_u = pymesh.boolean(sponge_u, sponge_c, operation=operation, engine="igl")

# boolean difference
operation = 'difference'
log(operation+' fractal - u')
mesh_fractal = pymesh.boolean(mesh_fractal, sponge_u, operation=operation, engine="igl")

# save
log('saving..')
pymesh.save_mesh("menger_sponge_"+depth+".stl", mesh_fractal, ascii=False)
log('job complete')
