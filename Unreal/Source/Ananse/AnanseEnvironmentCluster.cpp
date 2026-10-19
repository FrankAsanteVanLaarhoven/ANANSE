#include "AnanseEnvironmentCluster.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
AAnanseEnvironmentCluster::AAnanseEnvironmentCluster()
{
    PrimaryActorTick.bCanEverTick=false;
    Instances=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("SceneryInstances"));
    SetRootComponent(Instances);
    Instances->SetMobility(EComponentMobility::Static);
    Instances->SetCollisionProfileName(TEXT("NoCollision"));
    SetActorEnableCollision(false);
}

#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
void AAnanseEnvironmentCluster::BeginPlay()
{
 Super::BeginPlay();
 if(FParse::Param(FCommandLine::Get(),TEXT("AnanseDisableSecondaryMotion"))||!FParse::Param(FCommandLine::Get(),TEXT("AnanseEnvironmentRoute"))||!Instances->GetStaticMesh())return;
 const TMap<FString,FString> Versions={{TEXT("CanopySwag"),TEXT("HeroCells_v001")},{TEXT("Understory"),TEXT("HeroCells_v001")},{TEXT("CrownGuardian"),TEXT("HeroCells_v003")},{TEXT("RiverFig"),TEXT("HeroCells_v003")},{TEXT("TwinnedElder"),TEXT("HeroCells_v003")},{TEXT("RiverReach"),TEXT("HeroCells_v004")},{TEXT("StreamPools"),TEXT("HeroCells_v004")},{TEXT("LayeredGrove0"),TEXT("HeroCells_v004")},{TEXT("LayeredGrove1"),TEXT("HeroCells_v004")},{TEXT("LayeredGrove2"),TEXT("HeroCells_v004")},{TEXT("EcologyIsland"),TEXT("HeroCells_v004")},{TEXT("VerandaCorner"),TEXT("HeroCells_v004")}};
 const FString Name=Instances->GetStaticMesh()->GetName();const FString* Version=Versions.Find(Name);if(!Version)return;
 const FString Expected=FString::Printf(TEXT("/Game/Ananse/Environments/%s/%s/%s.%s"),**Version,*Name,*Name,*Name);
 if(Instances->GetStaticMesh()->GetPathName()!=Expected)return;
 MotionSourcePath=Expected;
 const FString NewPath=FString::Printf(TEXT("/Game/Ananse/Environments/Motion_v001/%s/%s.%s"),*Name,*Name,*Name);
 auto* Mesh=LoadObject<UStaticMesh>(nullptr,*NewPath);
 if(!Mesh){UE_LOG(LogTemp,Error,TEXT("Secondary motion dependency missing: %s; previous scenery retained"),*NewPath);return;}
 // No actor tick, moving colliders, transforms or instance edits. Old map remains
 // unchanged; this isolated visual variant is disabled by the comparison switch.
 TArray<UMaterialInterface*> Previous;for(int32 I=0;I<Instances->GetNumMaterials();++I)Previous.Add(Instances->GetMaterial(I));
 Instances->SetStaticMesh(Mesh);
 for(int32 I=0;I<Previous.Num();++I)if(auto* Old=Previous[I])
 {
  const FString N=Old->GetName().ToLower();if(!N.Contains(TEXT("bark"))&&!N.Contains(TEXT("leaf"))&&!N.Contains(TEXT("water"))&&!N.Contains(TEXT("indigo"))&&!N.Contains(TEXT("jade")))continue;
  const FString MaterialPath=TEXT("/Game/Ananse/Environments/Motion_v001/Overrides/")+Old->GetPathName().Mid(6);
  if(auto* Variant=LoadObject<UMaterialInterface>(nullptr,*MaterialPath))Instances->SetMaterial(I,Variant);
  else UE_LOG(LogTemp,Error,TEXT("Secondary motion dependency missing: %s; exact material override not replaced"),*MaterialPath);
 }
 Instances->SetEvaluateWorldPositionOffset(true);bMotionVariantLoaded=true;
}
