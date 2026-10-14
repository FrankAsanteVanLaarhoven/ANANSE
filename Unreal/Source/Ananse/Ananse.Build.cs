using UnrealBuildTool;
public class Ananse : ModuleRules
{
    public Ananse(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "CoreUObject", "Engine", "RHI", "ApplicationCore", "InputCore", "EnhancedInput",
            "GameplayAbilities", "GameplayTags", "GameplayTasks", "Json", "JsonUtilities"
        });
        if(Target.Type==TargetType.Editor)PrivateDependencyModuleNames.Add("UnrealEd");
    }
}
