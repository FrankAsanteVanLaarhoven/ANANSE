#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnanseEnvironmentCluster.generated.h"
class UHierarchicalInstancedStaticMeshComponent;
// Scenery-only editor container: no tick, input, mission state or collision authority.
UCLASS()
class ANANSE_API AAnanseEnvironmentCluster : public AActor
{
    GENERATED_BODY()
public:
    AAnanseEnvironmentCluster();
 virtual void BeginPlay()override;
 bool bMotionVariantLoaded=false;
 FString MotionSourcePath;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Environment")
    TObjectPtr<UHierarchicalInstancedStaticMeshComponent> Instances;
};
