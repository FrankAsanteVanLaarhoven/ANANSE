"""Evaluate saved source meshes/actions and render their real topology/rig views."""
import bpy,bmesh,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];report=Path(sys.argv[sys.argv.index('--')+1]);assert not report.exists();records=[]
for key,revision,oldrev in [('Kwaku','Authored_v015','Authored_v008'),('OseboLeopard','Authored_v005','Authored_v002')]:
 folder=R/'SourceArt/Characters'/key/revision;source=folder/(key+'.blend');digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(R/'SourceArt/Characters'/key/oldrev/(key+'.blend')));original_rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
 def rest(rig):return [(b.name,b.parent.name if b.parent else None,[v for row in b.matrix_local for v in row])for b in rig.data.bones]
 original=rest(original_rig);original_actions=sorted(a.name for a in bpy.data.actions);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');assert rest(rig)==original;assert sorted(a.name for a in bpy.data.actions)==original_actions;rig.animation_data.action=None
 def neutral():
  for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
  s.frame_set(0);bpy.context.view_layer.update()
 neutral();meshes=[o for o in s.objects if o.type=='MESH'and not o.hide_render];weighted=0;maximum=0
 for o in meshes:
  for v in o.data.vertices:
   weights=[a.weight for a in v.groups if o.vertex_groups[a.group].name in rig.data.bones];assert weights and all(math.isfinite(w)and w>=0 for w in weights)and abs(sum(weights)-1)<1e-5,(o.name,v.index,weights);maximum=max(maximum,len([w for w in weights if w>0]));weighted+=1
 assert maximum<=4
 clips=[]
 for action in bpy.data.actions:
  neutral();rig.animation_data.action=action;start,end=action.frame_range;poses=[]
  for t in [0,.25,.5,.75,1]:s.frame_set(round(start+(end-start)*t));poses.append([tuple(b.matrix.translation)for b in rig.pose.bones])
  motion=max((Vector(a)-Vector(b)).length for pose in poses[1:]for a,b in zip(poses[0],pose));assert motion>1e-6,(key,action.name,motion);clips.append({'action':action.name,'evaluated_max_joint_displacement_m':motion})
 rig.animation_data.action=None;neutral();out=folder/('Technical_v001'if key=='Kwaku'else'Technical_v002');assert not out.exists();out.mkdir();s.render.resolution_x=800;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.eevee.taa_render_samples=24;views={}
 for name in ['front','left','right','back','beauty']:
  s.camera=bpy.data.objects[('Camera_'if key=='OseboLeopard'else'')+name];s.render.filepath=str(out/(name+'_solid.png'));bpy.ops.render.render(write_still=True);views[name]={'camera':[list(row)for row in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale}
 for name in ['front','left','back']:
  mods=[]
  for o in meshes:
   m=o.modifiers.new('ActualTopology','WIREFRAME');m.thickness=.0005;m.use_replace=True;mods.append((o,m))
  s.camera=bpy.data.objects[('Camera_'if key=='OseboLeopard'else'')+name];s.render.filepath=str(out/(name+'_topology.png'));bpy.ops.render.render(write_still=True)
  for o,m in mods:o.modifiers.remove(m)
 # Evaluation and volumes use actual saved part meshes, independent of the export join.
 arm_names=['ContinuousArmHand_L','ContinuousArmHand_R']if key=='Kwaku'else['ContinuousArmPaw_L','ContinuousArmPaw_R'];volumes={}
 def volume(o):
  o.hide_set(False);bpy.context.view_layer.update()
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();bm=bmesh.new();bm.from_mesh(m);value=abs(bm.calc_volume(signed=True));bm.free();e.to_mesh_clear();return value
 for n in arm_names:volumes[n]={'neutral_m3':volume(bpy.data.objects[n])}
 if key=='Kwaku':rig.animation_data.action=bpy.data.actions['InspectLedger'];s.frame_set(35)
 else:
  for side in ['L','R']:rig.pose.bones['lowerarm_'+side].rotation_euler.x=1.15;rig.pose.bones['upperarm_'+side].rotation_euler.x=-.6
 bpy.context.view_layer.update()
 for n in arm_names:
  v=volume(bpy.data.objects[n]);volumes[n].update(bent_m3=v,bent_to_neutral_ratio=v/volumes[n]['neutral_m3'])
 s.camera=bpy.data.objects['Camera_beauty'if key=='OseboLeopard'else'beauty'];s.render.filepath=str(out/'evaluated_arm_pose.png');bpy.ops.render.render(write_still=True);rig.animation_data.action=None;neutral()
 eye_hits=[]
 if key=='Kwaku':
  mesh=bpy.data.objects['SK_Kwaku']
  for side in ['L','R']:mesh.data.shape_keys.key_blocks['Blink_'+side].value=1
  bpy.context.view_layer.update();e=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
  for sign,side in [(-1,'L'),(1,'R')]:
   for dx in [-.006,0,.006]:
    for dz in [-.003,0,.003]:
     hit,p,n,i=e.ray_cast(Vector((sign*.041+dx,-2,1.3795+dz)),Vector((0,1,0)));material=e.data.materials[e.data.polygons[i].material_index].name if hit else'NONE';eye_hits.append({'side':side,'dx':dx,'dz':dz,'material':material});assert material=='Skin',(side,dx,dz,material)
  s.camera=bpy.data.objects['front'];s.render.filepath=str(out/'evaluated_closed_lids.png');bpy.ops.render.render(write_still=True)
  for side in ['L','R']:mesh.data.shape_keys.key_blocks['Blink_'+side].value=0
 rods=[]
 for o in meshes:o.hide_render=True
 for b in rig.data.bones:
  a=rig.matrix_world@b.head_local;c=rig.matrix_world@b.tail_local;d=c-a
  if d.length<1e-6:continue
  bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.0025,depth=d.length,location=(a+c)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();rods.append(o)
 s.camera=bpy.data.objects['Camera_front'if key=='OseboLeopard'else'front'];s.render.filepath=str(out/'actual_skeleton.png');bpy.ops.render.render(write_still=True)
 for o in rods:bpy.data.objects.remove(o,do_unlink=True)
 for o in meshes:o.hide_render=False
 assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
 record={'character':key,'revision':revision,'scene_sha256':digest,'rest_bones_unchanged':True,'bone_count':len(original),'weighted_visible_vertices':weighted,'max_influences':maximum,'evaluated_actions':clips,'arm_volumes':volumes,'closed_lid_evaluated_samples':eye_hits,'views':views,'creative_approved':False,'limitations':['Volume ratios and surface proximity do not establish natural deformation or likeness','Hand and cloth full penetration/contact review remains open','Technical sheets are visual model inspections, not manufacturing CAD']};(out/'model-derived-evidence.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
report.write_text(json.dumps({'source_checks_passed':True,'characters':records,'creative_approved':False},indent=2)+'\n')
