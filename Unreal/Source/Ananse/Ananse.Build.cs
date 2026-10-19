using UnrealBuildTool;
public class Ananse : ModuleRules
{
    public Ananse(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "TraceLog", "CoreUObject", "Engine", "RHI", "ApplicationCore", "InputCore", "EnhancedInput",
            "GameplayAbilities", "GameplayTags", "GameplayTasks", "Json", "JsonUtilities", "LevelSequence", "MovieScene", "AnimationCore", "AnimGraphRuntime", "AIModule", "NavigationSystem"
        });
        if(Target.Type==TargetType.Editor)PrivateDependencyModuleNames.AddRange(new string[]{"UnrealEd","AnimGraph","BlueprintGraph","KismetCompiler","MeshDescription","StaticMeshDescription","SkeletalMeshDescription"});
    }
}
