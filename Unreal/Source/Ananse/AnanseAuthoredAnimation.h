#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AnanseAuthoredAnimation.generated.h"
class UAnimSequence;class UAnimBlueprint;class USkeletalMesh;

/** Feline-only graph variables. No world/component reads on animation workers. */
UCLASS(Transient,Blueprintable)
class ANANSE_API UAnanseLeopardAnimInstance : public UAnimInstance
{
 GENERATED_BODY()
public:
 UPROPERTY(Transient,BlueprintReadWrite,Category=Animation) TObjectPtr<UAnimSequence> Clip;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) int32 GraphEvaluations=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) TObjectPtr<UAnimSequence> EvaluatedGraphClip;
 bool bResetSecondaryMotion=false;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) int32 SecondaryBoneCount=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) int32 SecondaryEvaluations=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) int32 SecondaryResets=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) float SecondaryPeakDegrees=0;
 virtual void NativePostEvaluateAnimation() override;
 virtual FAnimInstanceProxy* CreateAnimInstanceProxy()override;
 virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy)override;
 void RestartPresentationGraph();
};

/** Editor authoring of a real sequence graph; unavailable as a runtime operation. */
UCLASS()
class ANANSE_API UAnanseAnimationAuthoring : public UBlueprintFunctionLibrary
{
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static bool PopulateClipGraph(UAnimBlueprint* Blueprint,UAnimSequence* DefaultClip,FString& Error);
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static bool AddLeopardSockets(USkeletalMesh* Mesh,FString& Error);
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static bool AddStorySockets(USkeletalMesh* Mesh,FString& Error);
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static FString DescribeRig(USkeletalMesh* Mesh);
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static FString AuthorAsoLedgerGrip(USkeletalMesh* Mesh,UAnimSequence* Clip);
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static FString DescribeAuthoredBonePose(USkeletalMesh* Mesh,UAnimSequence* Clip,float Time);
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static bool PrepareLeopardQuality(USkeletalMesh* Mesh,FString& Error);
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static FString PrepareInteractionSurface(USkeletalMesh* Mesh);
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static FString DescribeSkinProbe(USkeletalMesh* Mesh,UAnimSequence* Clip,FVector RestPoint,float Time);
 UFUNCTION(BlueprintCallable,Category="Character Authoring")
 static FString CorrectInteractionImportFrame(USkeletalMesh* Mesh);
};
