#pragma once
#include "CoreMinimal.h"
#include "AnanseGroundContact.h"
#include "AnanseLeopardContact.generated.h"

struct FAnanseFelinePose
{
 FVector Target[2],Normal[2],SoleOffset[2];
 bool Valid[2]={false,false};
 bool Enabled=false;
 float BodyZ=0;
};

/** Two supporting-chain contact state; each owner validates its own skeleton. All traces/support transforms belong to the game thread. */
UCLASS(ClassGroup=Animation)
class ANANSE_API UAnanseLeopardContact:public UActorComponent
{
 GENERATED_BODY()
public:
 UAnanseLeopardContact();
 virtual void BeginPlay()override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
 virtual void TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Tick)override;
 void ResetContacts();
 void SampleFinalPose();
 FString MetricsJson()const;
 FAnanseFelinePose Snapshot;
 FAnanseLegContact Legs[2];
 FVector Nominal[2],Hip[2];float Upper[2],Lower[2];
 int32 Resets=0,InvalidTransforms=0,SolvedChains=0;
 float QueryUs=0,SolveUs=0;
 bool bEnabled=true,bReady=false;
private:
 bool bCollect=false;
 bool Ground(const FVector& Point,FHitResult& Hit)const;
 void Plant(int32 Leg,const FHitResult& Hit);
 FVector PreviousPosition=FVector::ZeroVector;
 int32 NextLeg=0;
 FDelegateHandle PoseDelegate;
 TArray<float> Queries,Solves,Frames;
 double LastFrame=0;
 float MaxPenetration[2]={0,0};FString PenetrationContext[2];
};
