"""Editor orchestration only; all acceptance assertions run in native C++."""
import unreal
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
