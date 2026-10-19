#pragma once
#include "CoreMinimal.h"
#include "AnansePlayer.h"
#include "AnanseAuthoredAnimation.h"
#include "AnanseCastLab.generated.h"
class UAnimSequence;class UAnanseLeopardContact;
class UStaticMeshComponent;class UStaticMesh;
UCLASS(Transient,Blueprintable)
class ANANSE_API UAnanseCastAnimInstance:public UAnanseLeopardAnimInstance
{
 GENERATED_BODY()
public:
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) int32 Evaluations=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) TObjectPtr<UAnimSequence> EvaluatedClip;
 UPROPERTY(Transient,BlueprintReadOnly,Category=Animation) float EvaluatedTime=-1;
 virtual void NativePostEvaluateAnimation()override;
};
/** Shared input interface only. Each design binds a distinct mesh, skeleton and graph. */
UCLASS()
class ANANSE_API AAnanseCastLabPlayer:public AAnansePlayer
{
 GENERATED_BODY()
public:
 AAnanseCastLabPlayer();
 virtual void BeginPlay()override;
 virtual void Tick(float Delta)override;
 virtual void SetupPlayerInputComponent(UInputComponent* Input)override;
 virtual void ResetTransientMotion()override;
 UPROPERTY(EditDefaultsOnly) bool bStoryCampaignPresentation=false;
 UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) bool bRefinedFace=false;
 UPROPERTY(EditDefaultsOnly) bool bLedgerPresentation=false;
 UPROPERTY(EditDefaultsOnly) bool bAsoLedgerPresentation=false;
 void UpdateAsoLedger();
 int32 AsoLedgerSamples=0;
 float AsoLedgerMaxBindingErrorCm=0;
 uint32 AsoLedgerPhaseMask=0;
 TSet<FString> AsoSurfaceCaptures;
 uint32 AsoSurfaceEpoch=0;
 UPROPERTY(EditDefaultsOnly) TObjectPtr<UStaticMesh> LedgerMesh;
 UPROPERTY(EditDefaultsOnly) TObjectPtr<UStaticMesh> LedgerSupportMesh;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> LedgerVisual;
 UPROPERTY(Transient,BlueprintReadOnly) bool bLedgerLatched=false;
 UFUNCTION(BlueprintCallable) void PresentLedgerInteraction();
 UPROPERTY(Transient,BlueprintReadOnly) float AppliedBlink=0;
 UFUNCTION(BlueprintCallable) void HoldBlinkPreview(bool Closed){bHoldBlink=Closed;}
 UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) FName DesignId;
 UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) FName FamilyKey;
 UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TObjectPtr<USkeletalMesh> AuthoredMesh;
 UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TArray<TObjectPtr<UAnimSequence>> AuthoredClips;
 UPROPERTY(EditDefaultsOnly) TSubclassOf<UAnanseCastAnimInstance> AnimationClass;
 UPROPERTY(EditDefaultsOnly) float AuthoringHeight=170;
 UPROPERTY(BlueprintReadOnly) bool bFamilyReady=false;
 UFUNCTION(BlueprintCallable) bool PlayAuthoredClip(int32 Index);
 UFUNCTION(BlueprintCallable) bool HoldAuthoredClip(int32 Index){bManual=true;return PlayAuthoredClip(Index);}
 UPROPERTY(Transient) TObjectPtr<UAnanseLeopardContact> LiveContacts;
 int32 ActiveClip=0;
private:
 bool bManual=false;bool bHoldBlink=false;float FaceAge=0;float LedgerAge=0;bool bEpisodeLedger=false;
 void NextClip(){bManual=true;if(!AuthoredClips.IsEmpty())PlayAuthoredClip((ActiveClip+1)%AuthoredClips.Num());}
 void PreviousClip(){bManual=true;if(!AuthoredClips.IsEmpty())PlayAuthoredClip((ActiveClip+AuthoredClips.Num()-1)%AuthoredClips.Num());}
 void ToggleBlink(){bHoldBlink=!bHoldBlink;}
 void Clip0(){bManual=false;PlayAuthoredClip(0);}void Clip1(){bManual=true;PlayAuthoredClip(0);}
 void Clip2(){bManual=true;PlayAuthoredClip(1);}void Clip3(){bManual=true;PlayAuthoredClip(2);}
 void Clip4(){bManual=true;PlayAuthoredClip(3);}void Clip5(){bManual=true;PlayAuthoredClip(4);}
 void Clip6(){bManual=true;PlayAuthoredClip(5);}void Clip7(){bManual=true;PlayAuthoredClip(6);}
 void Clip8(){bManual=true;PlayAuthoredClip(7);}void Clip9(){bManual=true;PlayAuthoredClip(8);}
};
