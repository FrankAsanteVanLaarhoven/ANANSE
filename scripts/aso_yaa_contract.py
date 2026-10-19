"""Validate the native socket-object schema without accepting empty named assets."""
import math
REQUIRED={'socket_voice':'jaw','socket_ledger_L':'hand_L','socket_ledger_R':'hand_R'}
def validate_native_sockets(report):
 rows=report.get('socket_objects')
 if not isinstance(rows,list)or not rows:raise ValueError('Nonempty native socket_objects report required')
 names=[row.get('name')for row in rows]
 if len(set(names))!=len(names):raise ValueError('Duplicate socket identity')
 mapped={row['name']:row for row in rows}
 for name,bone in REQUIRED.items():
  row=mapped.get(name)
  if not row or row.get('bone')!=bone:raise ValueError('Missing or incompatible socket bone: '+name)
  for field in ['relative_location_cm','relative_rotation_pitch_yaw_roll','scale']:
   vector=row.get(field)
   if not isinstance(vector,list)or len(vector)!=3 or any(not isinstance(v,(int,float))or not math.isfinite(v)for v in vector):raise ValueError('Invalid socket transform: '+name)
  if any(v<=0 for v in row['scale']):raise ValueError('Invalid socket scale')
 return True

def validate_ledger_observation(row):
 count=row.get('aso_ledger_samples');mask=row.get('aso_ledger_phase_mask');error=row.get('aso_ledger_max_binding_error_cm')
 return isinstance(count,int)and not isinstance(count,bool)and count>=30 and mask==31 and isinstance(error,(int,float))and not isinstance(error,bool)and math.isfinite(error)and 0<=error<=.1
