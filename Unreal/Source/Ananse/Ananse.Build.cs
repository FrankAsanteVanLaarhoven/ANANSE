using UnrealBuildTool;
public class Ananse : ModuleRules
{
    public Ananse(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput",
            "GameplayAbilities", "GameplayTags", "GameplayTasks", "Json", "JsonUtilities"
        });
    }
}
