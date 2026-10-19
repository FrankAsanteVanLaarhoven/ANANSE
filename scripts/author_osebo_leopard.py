"""Author the first editable leopard revision in the approved local Blender.

Original surface geometry, UVs, texture, armature and distinct keyed actions.
This revision requires deformation, runtime and human resemblance review.
"""
import bpy, bmesh
from mathutils import Vector
import math, json, hashlib, sys, random, struct
from pathlib import Path
import numpy as np

args = sys.argv[sys.argv.index('--') + 1:]
OUT = Path(args[0]).resolve()
if OUT.exists(): raise RuntimeError('A source revision already exists; never overwrite it')
OUT.mkdir(parents=True)
(OUT/'authoring-source.py').write_bytes(Path(__file__).read_bytes())
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 900; scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.fps = 30
scene.world = bpy.data.worlds.new('NeutralWorld')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.11,.13,.17,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .35
scene.view_settings.view_transform = 'AgX'
parts = []; binds = {}; joints = {}; actions = []

def material(name, color, metal=0, rough=.55):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metal; p.inputs['Roughness'].default_value = rough
    return m

fur = material('Fur_Gold_Rosettes',(.68,.37,.10))
cream = material('Muzzle_Chest_Cream',(.73,.65,.46))
dark = material('Nose_Lips_Claws',(.027,.016,.013),rough=.38)
iris = material('Iris_Amber',(.65,.42,.07),rough=.25)
white = material('Eye_Sclera',(.68,.62,.39),rough=.23)
leather = material('Armour_Brown_Leather',(.065,.022,.008),rough=.65)
edge = material('Leather_Edge',(.17,.065,.022),rough=.59)
brass = material('Clasp_Brass',(.56,.32,.085),metal=.72,rough=.33)
cape = material('Cape_Burgundy',(.17,.013,.025),rough=.87)
lining = material('Cape_Inner',(.075,.009,.017),rough=.95)

# A saved original raster texture, exported through supported glTF material nodes.
rng = random.Random(71249); size = 1024
yy,xx=np.mgrid[0:size,0:size]; base=np.zeros((size,size,4),dtype=np.float32)
grain=np.random.default_rng(71249).normal(0,.012,(size,size))
base[:,:,0]=.72+grain; base[:,:,1]=.43+grain; base[:,:,2]=.14+grain; base[:,:,3]=1
for _ in range(64):
    cx,cy=rng.uniform(0,size),rng.uniform(0,size);rx,ry=rng.uniform(22,39),rng.uniform(25,44)
    dx=((xx-cx+size/2)%size-size/2)/rx
    dy=((yy-cy+size/2)%size-size/2)/ry
    a=np.arctan2(dy,dx); d=np.sqrt(dx*dx+dy*dy)*(1+.11*np.sin(5*a+cx))
    ring=(d>.64)&(d<1.02)&(np.sin(a*3+cy)>-.75)
    inside=d<.60
    base[inside,:3]*=np.array([.85,.72,.59]); base[ring,:3]=(.055,.028,.014)
image=bpy.data.images.new('Osebo_Original_Rosettes',width=size,height=size,alpha=True)
image.pixels.foreach_set(np.clip(base,0,1).ravel()); image.filepath_raw=str(OUT/'Osebo_Fur_BaseColor.png');image.file_format='PNG';image.save();image.pack()
n=fur.node_tree.nodes.new('ShaderNodeTexImage');n.image=image
fur.node_tree.links.new(n.outputs['Color'],fur.node_tree.nodes['Principled BSDF'].inputs['Base Color'])

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
bone('root',(0,0,0),(0,0,.15))
bone('pelvis',(0,0,.96),(0,0,1.12),'root')
bone('spine_01',(0,0,1.12),(0,0,1.30),'pelvis')
bone('spine_02',(0,0,1.30),(0,0,1.48),'spine_01')
bone('chest',(0,0,1.48),(0,0,1.62),'spine_02')
bone('neck',(0,0,1.62),(0,-.015,1.78),'chest')
bone('head',(0,-.015,1.78),(0,-.035,1.99),'neck')
bone('jaw',(0,-.075,1.83),(0,-.19,1.80),'head')
loft('Body_FelineTorso',[(0,.015,.93,.15,.12),(0,.01,1.02,.20,.13),(0,0,1.13,.165,.105),
 (0,0,1.25,.18,.115),(0,.005,1.40,.245,.15),(0,.01,1.52,.27,.14),(0,0,1.61,.17,.11)],fur,chain=['pelvis','spine_01','spine_02','chest'])
loft('Neck_Fur',[(0,0,1.59,.12,.10),(0,0,1.68,.105,.10),(0,-.015,1.78,.10,.085)],fur,'neck')
loft('Head_Cheeks_Brow',[(0,-.04,1.76,.081,.085),(0,-.055,1.80,.12,.116),
 (0,-.042,1.85,.145,.125),(0,-.025,1.92,.15,.117),(0,-.01,1.98,.115,.093),(0,0,2.01,.055,.042)],fur,'head',segments=32)
oval('Throat_Cream',(0,-.092,1.69),(.068,.015,.115),cream,'neck')
oval('LowerJaw',(0,-.107,1.805),(.082,.075,.033),cream,'jaw')
for sign,side in [(-1,'L'),(1,'R')]:
    bone('ear_'+side,(sign*.102,0,1.967),(sign*.14,0,2.075),'head')
    oval('Ear_'+side,(sign*.135,0,2.007),(.043,.026,.047),fur,'ear_'+side)
    oval('EarInner_'+side,(sign*.135,-.024,2.010),(.027,.005,.031),dark,'ear_'+side)
    bone('eye_'+side,(sign*.062,-.117,1.924),(sign*.062,-.16,1.924),'head')
    oval('EyeLid_'+side,(sign*.070,-.121,1.926),(.041,.017,.025),dark,'head')
    oval('Eye_'+side,(sign*.070,-.135,1.927),(.034,.010,.018),white,'eye_'+side)
    oval('Iris_'+side,(sign*.070,-.145,1.927),(.019,.004,.017),iris,'eye_'+side)
    oval('Pupil_'+side,(sign*.070,-.149,1.927),(.004,.002,.014),dark,'eye_'+side)
    oval('Muzzle_'+side,(sign*.041,-.145,1.838),(.054,.063,.040),cream,'head')
    for i in range(3):oval('WhiskerDot_'+side+str(i),(sign*(.038+i*.013),-.201+i*.006,1.837),(.003,.002,.003),dark,'head')
    tube('Brow_'+side,[(sign*.025,-.115,1.962),(sign*.06,-.132,1.966),(sign*.097,-.105,1.956)],[.008,.009,.005],fur,bone='head')
    # Purposefully modelled biped limb contours, joints and separate digits.
    shoulder=(sign*.235,0,1.54);elbow=(sign*.36,-.012,1.29);wrist=(sign*.40,-.025,1.06)
    bone('clavicle_'+side,(0,0,1.53),shoulder,'chest')
    bone('upperarm_'+side,shoulder,elbow,'clavicle_'+side)
    bone('lowerarm_'+side,elbow,wrist,'upperarm_'+side)
    bone('hand_'+side,wrist,(sign*.405,-.035,.955),'lowerarm_'+side)
    loft('Arm_'+side,[(sign*.235,0,1.57,.092,.088),(sign*.285,0,1.48,.085,.080),
        (sign*.335,0,1.36,.069,.065),(sign*.36,-.012,1.29,.052,.051),
        (sign*.378,-.02,1.18,.065,.054),(sign*.40,-.025,1.06,.038,.033)],fur,
        chain=['clavicle_'+side,'upperarm_'+side,'lowerarm_'+side,'hand_'+side])
    oval('PawPalm_'+side,(sign*.405,-.029,1.012),(.052,.035,.073),fur,'hand_'+side)
    for d in range(4):
        x=sign*(.369+d*.024);z=.986;endz=.927+abs(1.5-d)*.007
        a='digit_%s_%d_01'%(side,d);b='digit_%s_%d_02'%(side,d)
        bone(a,(x,-.038,z),(x,-.045,(z+endz)/2),'hand_'+side)
        bone(b,(x,-.045,(z+endz)/2),(x,-.052,endz),a)
        tube('PawDigit_'+side+str(d),[(x,-.032,z),(x,-.041,(z+endz)/2),(x,-.052,endz)],[.014,.014,.009],fur,bones=[a,b])
    hip=(sign*.127,0,1.00);knee=(sign*.143,-.048,.58);ankle=(sign*.148,.018,.16)
    bone('thigh_'+side,hip,knee,'pelvis');bone('shin_'+side,knee,ankle,'thigh_'+side)
    bone('foot_'+side,ankle,(sign*.148,-.13,.055),'shin_'+side)
    bone('ball_'+side,(sign*.148,-.13,.055),(sign*.148,-.205,.05),'foot_'+side)
    loft('Leg_'+side,[(sign*.127,0,1.00,.105,.105),(sign*.13,-.013,.88,.108,.10),
       (sign*.14,-.041,.71,.085,.081),(sign*.143,-.048,.58,.062,.064),
       (sign*.146,-.013,.46,.080,.074),(sign*.148,.019,.29,.055,.052),
       (sign*.148,.018,.14,.042,.041)],fur,chain=['thigh_'+side,'shin_'+side,'foot_'+side])
    oval('PawFoot_'+side,(sign*.148,-.070,.075),(.078,.134,.065),fur,'foot_'+side)
    for d in range(4):
        x=sign*.148+(d-1.5)*.035
        name='toe_'+side+str(d);bone(name,(x,-.135,.06),(x,-.222,.048),'ball_'+side)
        oval('Toe_'+side+str(d),(x,-.166,.054),(.023,.053,.035),fur,name)
        tube('Claw_'+side+str(d),[(x,-.205,.052),(x,-.227,.04),(x,-.237,.042)],[.009,.007,.0005],dark,bone=name,segments=8)
    # Shaped shin guard with strap and raised edge.
    panel('ShinGuard_'+side,[(sign*.148-.065,-.083,.48),(sign*.148+.065,-.083,.48),
       (sign*.148+.038,-.071,.20),(sign*.148-.038,-.071,.20)],leather,'shin_'+side)
    panel('Bracer_'+side,[(sign*.40-.05,-.073,1.20),(sign*.40+.05,-.073,1.20),
       (sign*.40+.04,-.068,1.08),(sign*.40-.04,-.068,1.08)],leather,'lowerarm_'+side)

panel('Nose_Triangular',[(-.024,-.207,1.857),(.024,-.207,1.857),(0,-.216,1.837)],dark,'head')
tube('MouthSeam',[(-.065,-.177,1.812),(0,-.200,1.805),(.065,-.177,1.812)],[.0025]*3,dark,bone='jaw',segments=8)
# Curved cuirass quads conform to the authored torso; a real volume with side walls.
rows=[(1.10,.164,.139),(1.20,.177,.141),(1.35,.231,.163),(1.50,.267,.155),(1.59,.194,.129)]
v=[];f=[];uv=[];cols=25
for layer in range(2):
    for i,(z,rx,ry) in enumerate(rows):
        for j in range(cols):
            a=math.pi*j/(cols-1)
            v.append((rx*math.cos(a),-ry*math.sin(a)-.008+layer*.009,z-.035*abs(math.cos(a)) if i==4 else z))
            uv.append((j/(cols-1),i/(len(rows)-1)))
count=len(rows)*cols
for layer in range(2):
    for i in range(len(rows)-1):
        for j in range(cols-1):
            a=layer*count+i*cols+j;quad=(a,a+1,a+cols+1,a+cols)
            f.append(quad if layer==0 else tuple(reversed(quad)))
edgeids=list(range(cols))+[i*cols+cols-1 for i in range(1,len(rows))]+list(reversed(range((len(rows)-1)*cols,(len(rows)-1)*cols+cols-1)))+[i*cols for i in reversed(range(1,len(rows)-1))]
for a,b in zip(edgeids,edgeids[1:]+edgeids[:1]):f.append((a,b,b+count,a+count))
mesh('Armour_CurvedCuirass',v,f,leather,'chest',uv=uv)
for sign in (-1,1):
    panel('Chest_Inlay_'+str(sign),[(sign*.03,-.177,1.52),(sign*.11,-.174,1.51),
       (sign*.14,-.16,1.25),(sign*.065,-.161,1.21)],edge,'chest')
tube('DiagonalHarness',[(-.18,-.135,1.57),(-.09,-.177,1.43),(.04,-.165,1.28),(.13,-.105,1.13)],[.017]*4,edge,bone='chest',segments=8)
for i in range(14):
    x=-.21+i*.032;z=1.51
    y=-.155*math.sqrt(max(0,1-(x/.267)**2))-.013
    oval('Armour_Rivet_'+str(i),(x,y,z),(.004,.003,.004),brass,'chest')
loft('Belt',[(0,0,1.11,.172,.132),(0,0,1.06,.177,.135)],leather,'pelvis',segments=48)
oval('BeltMedallion',(0,-.147,1.085),(.053,.015,.053),brass,'pelvis')
oval('BeltMedallionInset',(0,-.162,1.085),(.039,.004,.039),edge,'pelvis')
panel('FrontArmourFlap',[(-.15,-.132,1.05),(.15,-.132,1.05),(.105,-.16,.86),(0,-.18,.81),(-.105,-.16,.86)],leather,'pelvis')
for sign in (-1,1):
    tube('FlapBinding_'+str(sign),[(sign*.148,-.148,1.045),(sign*.104,-.176,.86),(0,-.195,.81)],[.003]*3,brass,bone='pelvis',segments=6)

tailpoints=[]
for i in range(25):
    t=i/24;tailpoints.append((.08+ .43*math.sin(t*2.2),.10+.42*t,1.00-.66*t+.24*t*t))
for i in range(6):
    bone('tail_%02d'%(i+1),tailpoints[i*4],tailpoints[min(24,(i+1)*4)],'pelvis' if i==0 else 'tail_%02d'%i)
tube('Tail_Articulated',tailpoints,[.045*(1-i/38) for i in range(25)],fur,bones=['tail_%02d'%(i+1) for i in range(6)],segments=16)
for side,sign in [('L',-1),('R',1)]:
    bone('cape_'+side+'_01',(sign*.17,.02,1.59),(sign*.23,.16,1.32),'chest')
    bone('cape_'+side+'_02',(sign*.23,.16,1.32),(sign*.29,.22,1.05),'cape_'+side+'_01')
    bone('cape_'+side+'_03',(sign*.29,.22,1.05),(sign*.33,.25,.84),'cape_'+side+'_02')
# Continuous cape grid with scalloped lower edge, modelled folds and two surfaces.
verts=[];faces=[];uv=[];weights=[];rows=24;cols=32
for i in range(rows):
    t=i/(rows-1)
    for j in range(cols):
        u=j/(cols-1);theta=(u-.5)*math.pi*1.30
        width=.23+.14*t
        x=math.sin(theta)*width;y=.025+math.cos(theta)*(.115+.16*t)+.014*math.sin(u*math.pi*12)*(t+.2)
        z=1.60-.73*t+.04*t*t*math.cos(u*math.pi*4)
        verts.append((x,y,z));uv.append((u,t));side='L' if x<0 else 'R'
        b=min(1,int(t*2));f=t*2-b
        weights.append({'cape_'+side+'_%02d'%(b+1):1-f,'cape_'+side+'_%02d'%(b+2):f})
for i in range(rows-1):
    for j in range(cols-1):
        a=i*cols+j;faces.append((a,a+1,a+cols+1,a+cols))
cloth=mesh('Cape_TailoredPleats',verts,faces,cape,weights=weights,uv=uv)
trim=material('Cape_WovenGold_Trim',(.40,.23,.075),rough=.9)
hem=[tuple(Vector(p)+Vector((0,.004,0))) for p in verts[-cols:]]
tube('Cape_WovenHem',hem,[.006]*cols,trim,bones=['cape_L_03','cape_R_03'],segments=6)
for side,j in [('L',0),('R',cols-1)]:
    points=[tuple(Vector(verts[i*cols+j])+Vector((0,.004,0))) for i in range(rows)]
    tube('Cape_Edge_'+side,points,[.005]*len(points),trim,bones=['cape_'+side+'_01','cape_'+side+'_02','cape_'+side+'_03'],segments=6)
# A deliberately single-surface game cloth; native material must be two-sided.
# Thickness/lining remains an explicit art task rather than an export-only change.
oval('CapeClasp',(-.11,-.138,1.58),(.044,.017,.044),brass,'chest')
for j in range(15):
    a=j*2*math.pi/15;oval('ClaspRivet'+str(j),(-.11+.032*math.cos(a),-.154,1.58+.032*math.sin(a)),(.003,.003,.003),edge,'chest')

# A single root hierarchy; no copied mannequin or spider topology/bones.
arm=bpy.data.armatures.new('SKEL_OseboLeopard');rig=bpy.data.objects.new('SKEL_OseboLeopard',arm)
scene.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for name,(head,tail,parent) in joints.items():
    b=arm.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=arm.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
for obj in parts:
    for name in {n for row in binds[obj.name] for n,w in row.items() if w>0}:obj.vertex_groups.new(name=name)
    for i,row in enumerate(binds[obj.name]):
        total=sum(w for w in row.values() if w>0)
        for name,w in row.items():
            if w>0:obj.vertex_groups[name].add([i],w/total,'REPLACE')
    mod=obj.modifiers.new('Skin','ARMATURE');mod.object=rig;obj.parent=rig
rig['design_id']='osebo-leopard-v1';rig['art_approval']='PENDING';rig['campaign_mapping']='UNAPPROVED'
rig['anatomy_decisions']='PROPOSED four paw digits, four toes, moderately raised hock; hidden rear armour and cape construction authored for review'

def action(name,duration,pose):
    act=bpy.data.actions.new(name);rig.animation_data_create();rig.animation_data.action=act
    frames=int(duration*30)
    for frame in range(0,frames+1,2):
        t=frame/30
        for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0)
        pose(t,duration)
        for b in rig.pose.bones:
            b.keyframe_insert(data_path='rotation_euler',frame=frame)
    act.use_fake_user=True;actions.append(dict(name=name,seconds=duration,frames=frames+1))

def rot(name,x=0,y=0,z=0):rig.pose.bones[name].rotation_euler=(x,y,z)
def idle(t,d):
    rot('chest',.015*math.sin(t*2));rot('head',0,.025*math.sin(t),.02*math.sin(t*.8))
    for i in range(6):rot('tail_%02d'%(i+1),.02*math.sin(t*1.5-i*.25),0,.03*math.sin(t-i*.2))
def gait(t,d,run=False):
    idle(t,d);freq=2*math.pi*(1.65 if run else .85);amp=.65 if run else .30
    for side,phase in [('L',0),('R',math.pi)]:
        s=math.sin(t*freq+phase);rot('thigh_'+side,amp*s);rot('shin_'+side,-.14-max(0,-s)*amp*1.2)
        rot('foot_'+side,-amp*s*.4);rot('upperarm_'+side,-amp*s*.65);rot('lowerarm_'+side,-.15-amp*.25)
    if run:rot('spine_01',.1)
action('IdleGuard',3,idle)
action('Patrol',2.4,lambda t,d:gait(t,d))
action('RunPursuit',2.4,lambda t,d:gait(t,d,True))
def turn(t,d):
    gait(t,d);rot('pelvis',0,0,.20*math.sin(t*math.pi/d));rot('head',0,0,-.3*math.sin(t*math.pi/d))
action('TurnStop',3,turn)
def investigate(t,d):idle(t,d);rot('neck',.08,0,.30*math.sin(t*2*math.pi/d));rot('ear_L',.2*math.sin(t*3));rot('ear_R',-.15*math.sin(t*2))
action('Investigate',4,investigate)
def capture(t,d):
    idle(t,d);a=max(0,math.sin(t*math.pi/d));rot('spine_01',a*.12)
    for side in ['L','R']:
        rot('upperarm_'+side,-a*1.10);rot('lowerarm_'+side,-a*.35)
        for i in range(4):rot('digit_%s_%d_02'%(side,i),a*.55)
action('CaptureReach',2,capture)
action('StaggerRecover',2.5,lambda t,d:(idle(t,d),rot('spine_01',-.25*math.sin(t*math.pi/d)*math.exp(-t))))
def command(t,d):idle(t,d);a=math.sin(t*math.pi/d);rot('upperarm_R',-.85*a,0,-.25*a);rot('lowerarm_R',-.50*a);rot('head',0,0,-.12*a)
action('Command',3,command)
def isolation(t,d):
    names=['upperarm_L','upperarm_R','hand_L','hand_R','foot_L','foot_R','ear_L','ear_R','jaw']+['tail_%02d'%i for i in range(1,7)]
    slot=min(len(names)-1,int(t/d*len(names)));a=.30*math.sin((t/d*len(names)-slot)*math.pi)
    rot(names[slot],a)
action('LimbIsolation',10,isolation)
rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0)
scene.frame_set(0)

def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size_ in [('Key',(-3,-4,5),650,4),('Fill',(3,-2,3),400,3),('Rim',(1,3,4),900,3)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size_
    o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,1.2))
cameras={}
for name,loc in [('front',(0,-5,1.10)),('left',(-5,0,1.10)),('right',(5,0,1.10)),('back',(0,5,1.10)),('beauty',(3,-5,2.5))]:
    data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=2.55
    o=bpy.data.objects.new('Camera_'+name,data);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,1.06));cameras[name]=o
scene.camera=cameras['beauty']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'OseboLeopard.blend'))

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
geometry=hashlib.sha256()
for obj in parts:
    geometry.update(obj.name.encode())
    for v in obj.data.vertices:geometry.update(np.asarray(v.co,dtype='<f4').tobytes())
    for poly in obj.data.polygons:geometry.update(np.asarray(poly.vertices,dtype='<i4').tobytes())
rigmap=dict(design_id='osebo-leopard-v1',units='metres',forward='Blender -Y; glTF +Z',up='Blender +Z; glTF +Y',
    source_scene_sha256=digest(OUT/'OseboLeopard.blend'),geometry_sha256=geometry.hexdigest(),
    bone_count=len(joints),bones=[dict(name=n,parent_index=list(joints).index(p) if p else -1,
       head=list(h),tail=list(t),rest_matrix=[list(row) for row in arm.bones[n].matrix_local]) for n,(h,t,p) in joints.items()],
    anatomy_status='PROPOSED hidden anatomy; creative approval pending',
    sockets_proposed={'socket_capture_L':'hand_L','socket_capture_R':'hand_R','socket_cape':'chest','socket_voice':'jaw'},
    parts=[dict(name=o.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),material=o.data.materials[0].name) for o in parts],
    actions=actions,cameras={n:dict(matrix_world=[list(row) for row in o.matrix_world],ortho_scale=o.data.ortho_scale) for n,o in cameras.items()},
    limitations=['First authored revision, not final approved art','Foot contact, joint clearance and runtime acceptance not yet measured','LOD reduction not yet authored','Socket bindings require actual native sockets'])
(OUT/'rig-map.json').write_text(json.dumps(rigmap,indent=2)+'\n')
bpy.ops.object.select_all(action='DESELECT')
for o in parts+[rig]:o.select_set(True)
bpy.context.view_layer.objects.active=rig
# Preserve named editable parts in the saved scene; one joined export copy avoids
# an importer silently making one SkeletalMesh per accessory. No source overwrite.
bpy.ops.wm.obj_export(filepath=str(OUT/'OseboLeopard_Inspection.obj'),export_selected_objects=True)
copies=[]
for o in parts:
    copy=o.copy();copy.data=o.data.copy();scene.collection.objects.link(copy);copies.append(copy)
    o.select_set(False);o.hide_render=True;o.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
for o in copies:o.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join()
joined=bpy.context.object;joined.name='SK_OseboLeopard'
rig.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'OseboLeopard.glb'),use_selection=True,export_format='GLB',
    export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,
    export_all_influences=False,export_def_bones=True,export_yup=True)
# Remove exporter credit metadata from the new authored artifact; retain format
# identifiers and all actual geometry/animation bytes. No third-party art is used.
path=OUT/'OseboLeopard.glb';raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0]
document=json.loads(raw[20:20+length]);document['asset'].pop('generator',None)
payload=json.dumps(document,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4)
tail=raw[20+length:]
path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
for path in [OUT/'OseboLeopard_Inspection.obj',OUT/'OseboLeopard_Inspection.mtl']:
    text=path.read_text();path.write_text(''.join(line for line in text.splitlines(True) if not line.startswith('# Blender')))
bpy.data.objects.remove(joined,do_unlink=True)
for o in parts:o.hide_render=False;o.hide_set(False)
for name,cam in cameras.items():
    scene.camera=cam;scene.render.filepath=str(OUT/(name+'_solid.png'));bpy.ops.render.render(write_still=True)
(OUT/'source-status.json').write_text(json.dumps(dict(scene_sha256=digest(OUT/'OseboLeopard.blend'),
    glb_sha256=digest(OUT/'OseboLeopard.glb'),geometry_sha256=geometry.hexdigest(),
    dcc_version=bpy.app.version_string,status='AUTHORED_REQUIRES_REVIEW_AND_NATIVE_QUALIFICATION',
    creative_approval=False,native_import_executed=False),indent=2)+'\n')
