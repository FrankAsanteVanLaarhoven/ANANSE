#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Animation/AnimInstance.h"
#include "AnanseGroundContact.generated.h"
class UAnimSequence;class UStaticMeshComponent;
// Plain pose input copied on the game thread; animation workers never dereference support actors.
struct FAnanseContactPose
{
 FVector Target[4],Normal[4];bool Valid[4]={false,false,false,false};
 bool Enabled=true;FVector BodyOffset=FVector(0,0,-6);FQuat BodyTilt=FQuat::Identity;
};
struct FAnanseLegContact
{
 enum class EPhase:uint8{Released,Stance,Swing};EPhase Phase=EPhase::Released;
 TWeakObjectPtr<UPrimitiveComponent> Support;
 FVector LocalPoint=FVector::ZeroVector,LocalNormal=FVector::UpVector,Point=FVector::ZeroVector,Normal=FVector::UpVector;
 FVector SwingStart=FVector::ZeroVector,SwingEnd=FVector::ZeroVector;float Progress=0;
 bool Reachable=false;int32 Transitions=0,ReachFailures=0,MissingSupport=0,Excluded=0;
 TArray<float> Drift,Penetration;float MaxStretchError=0,MinKneeFlex=180,MaxKneeFlex=0;int32 JointLimitViolations=0;
 TMap<FName,int32> SupportSamples;
};
UCLASS(ClassGroup=Animation,meta=(BlueprintSpawnableComponent))
class ANANSE_API UAnanseGroundContact:public UActorComponent
{
 GENERATED_BODY()
public:
 UAnanseGroundContact();virtual void BeginPlay()override;virtual void EndPlay(const EEndPlayReason::Type Reason)override;
 virtual void TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Tick)override;
 void ResetContacts();void SampleFinalizedPose();
 FAnanseContactPose Snapshot;FAnanseLegContact Legs[4];FVector Nominal[4],TipOffsets[4],BindHip[4],BindPelvis;int32 LastSolvedChains=0;
 TArray<float> FrameTimes,QueryTimes,SolveTimes;double LastFrame=0;float BindUpper[4],BindLower[4];int32 InvalidTransforms=0;
 float LastQueryMicroseconds=0,LastSolveMicroseconds=0;int32 ResetCount=0;
 bool bEnabled=true;
 FString MetricsJson()const;
 static const TCHAR* Sides[4];
private:
 bool bCollectMetrics=false;mutable int32 RejectedInteriorProbeStarts=0;
 TUniquePtr<FArchive> Csv;FString CsvBuffer;
 bool Ground(const FVector& Desired,FHitResult& Hit)const;
 bool CanReach(int32 Index,const FVector& Point,const FVector& Normal)const;
 void Plant(int32 Index,const FHitResult& Hit);
 void BuildReleasedTargets();
 FVector PreviousPosition=FVector::ZeroVector;int32 NextLeg=0;FDelegateHandle PoseDelegate;
};
UCLASS(Transient)
class ANANSE_API UAnanseContactAnimInstance:public UAnimInstance
{
 GENERATED_BODY()
public:
 bool bResetSecondaryMotion=false;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) int32 SecondaryBoneCount=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) int32 SecondaryEvaluations=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) int32 SecondaryResets=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) float SecondaryPeakDegrees=0;
 virtual FAnimInstanceProxy* CreateAnimInstanceProxy()override;
 virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy)override;
 UPROPERTY(Transient) TObjectPtr<UAnanseGroundContact> Contact;
 UPROPERTY(Transient,BlueprintReadWrite,Category=Animation) TObjectPtr<UAnimSequence> Clip;
 UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,Category=Animation) bool bUseAuthoredGraph=false;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) int32 GraphEvaluations=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) TObjectPtr<UAnimSequence> EvaluatedGraphClip;
 float ClipTime=0;
};

UCLASS()
class ANANSE_API AAnanseContactSupport:public AActor
{
 GENERATED_BODY()
public:
 AAnanseContactSupport();virtual void BeginPlay()override;virtual void Tick(float Delta)override;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Surface;
 UPROPERTY(EditAnywhere) bool bDisappearing=false;
private:FVector Origin;float Elapsed=0,OccupiedSeconds=0;bool bDisabled=false;
};
