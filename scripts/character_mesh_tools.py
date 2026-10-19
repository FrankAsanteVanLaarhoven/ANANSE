"""Shared project-owned mesh construction from the qualified leopard authoring path."""
import bpy,bmesh,math
import numpy as np
from mathutils import Vector
parts=[];binds={};joints={}
scene=None
def material(name, color, metal=0, rough=.55):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metal; p.inputs['Roughness'].default_value = rough
    return m

def mesh(name, verts, faces, mat, bone=None, weights=None, uv=None):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);parts.append(obj)
    obj.data.materials.append(mat)
    for p in data.polygons:p.use_smooth=True
    layer=data.uv_layers.new(name='UVMap')
    for p in data.polygons:
        polygon_u=[uv[data.loops[li].vertex_index][0] for li in p.loop_indices] if uv else []
        for li in p.loop_indices:
            vi=data.loops[li].vertex_index
            u,v=uv[vi] if uv else (.5+verts[vi][0]*.2, verts[vi][2]*.45)
            if polygon_u and max(polygon_u)-min(polygon_u)>.5 and u==0:u=1
            layer.data[li].uv=(u,v)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    binds[obj.name]=weights if weights else [{bone:1.0} for _ in verts]
    return obj

def loft(name,rings,mat,bone=None,chain=None,segments=24):
    # Each ring is center xyz + transverse horizontal/depth radii; authored quads.
    verts=[];uv=[];weights=[]
    for i,(x,y,z,rx,ry) in enumerate(rings):
        for j in range(segments):
            a=2*math.pi*j/segments
            verts.append((x+rx*math.cos(a),y+ry*math.sin(a),z));uv.append((j/segments,i/(len(rings)-1)))
            if chain:
                t=i/(len(rings)-1)*(len(chain)-1);lo=min(int(t),len(chain)-2);alpha=t-lo
                weights.append({chain[lo]:1-alpha,chain[lo+1]:alpha})
    faces=[]
    for i in range(len(rings)-1):
        for j in range(segments):
            a=i*segments+j;b=i*segments+(j+1)%segments
            faces.append((a,b,b+segments,a+segments))
    faces.extend([tuple(reversed(range(segments))),tuple(range((len(rings)-1)*segments,len(verts)))])
    return mesh(name,verts,faces,mat,bone,weights if chain else None,uv)

def tube(name,points,radii,mat,bones=None,bone=None,segments=12):
    verts=[];uv=[];weights=[]
    for i,p in enumerate(points):
        p=Vector(p);tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        axis=tangent.normalized();ref=Vector((0,1,0))
        if abs(axis.dot(ref))>.95:ref=Vector((1,0,0))
        u=axis.cross(ref).normalized();v=axis.cross(u).normalized()
        for j in range(segments):
            a=j*2*math.pi/segments;pos=p+radii[i]*(math.cos(a)*u+math.sin(a)*v)
            verts.append(tuple(pos));uv.append((j/segments,i/(len(points)-1)))
            if bones:
                t=i/(len(points)-1)*(len(bones)-1);lo=min(int(t),len(bones)-2);f=t-lo
                weights.append({bones[lo]:1-f,bones[lo+1]:f})
    faces=[]
    for i in range(len(points)-1):
        for j in range(segments):
            a=i*segments+j;b=i*segments+(j+1)%segments;faces.append((a,b,b+segments,a+segments))
    faces.extend([tuple(reversed(range(segments))),tuple(range((len(points)-1)*segments,len(verts)))])
    return mesh(name,verts,faces,mat,bone,weights if bones else None,uv)

def oval(name,center,scale,mat,bone):
    # Quad latitude surface; poles are small capped rings, no stock body primitive.
    return loft(name,[(center[0],center[1],center[2]+scale[2]*math.cos(a),
       max(.0004,scale[0]*math.sin(a)),max(.0004,scale[1]*math.sin(a)))
       for a in np.linspace(.015,math.pi-.015,16)],mat,bone,segments=28)

def panel(name, coords, mat, bone):
    # Leather panels have actual side walls and a bevel, not painted poster planes.
    verts=coords+[(x,y+.012,z) for x,y,z in coords];n=len(coords)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    obj=mesh(name,verts,faces,mat,bone)
    return obj

def bone(name,head,tail,parent=None):joints[name]=(head,tail,parent)

def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
