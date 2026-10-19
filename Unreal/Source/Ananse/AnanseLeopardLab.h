#pragma once
#include "CoreMinimal.h"
#include "AnansePlayer.h"
#include "GameFramework/GameModeBase.h"
#include "AnanseLeopardLab.generated.h"
class UAnimSequence;class USkeletalMesh;class UAnanseLeopardContact;class UMaterialInstanceDynamic;

/** Isolated feline design. Does not replace the campaign Osebo pursuer. */
UCLASS()
class ANANSE_API AAnanseLeopardLabPlayer : public AAnansePlayer
{
 GENERATED_BODY()
public:
 AAnanseLeopardLabPlayer();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
 virtual void ResetTransientMotion() override;
 UFUNCTION(BlueprintCallable) bool PlayLeopardClip(int32 Index);
 UFUNCTION(BlueprintCallable) bool HoldLeopardClip(int32 Index){bManualPresentation=true;return PlayLeopardClip(Index);}
 UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TObjectPtr<USkeletalMesh> LeopardMesh;
 UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TArray<TObjectPtr<UAnimSequence>> LeopardClips;
 UPROPERTY(BlueprintReadOnly) int32 ActiveLeopardClip=0;
 UPROPERTY(BlueprintReadOnly) bool bFamilyReady=false;
 UPROPERTY(Transient,BlueprintReadOnly) TObjectPtr<UAnanseLeopardContact> LiveContacts;
 UPROPERTY(Transient,BlueprintReadOnly) TObjectPtr<UMaterialInstanceDynamic> CapeMaterial;
 UPROPERTY(Transient,BlueprintReadOnly) TObjectPtr<UMaterialInstanceDynamic> AccentMaterial;
 UPROPERTY(BlueprintReadOnly) int32 PublishedVisualRevision=0;
private:
 bool bManualPresentation=false;
 int32 InspectionLod=-1;
 void CycleInspectionLod();
 void Idle(){bManualPresentation=true;PlayLeopardClip(0);}
 void Patrol(){bManualPresentation=true;PlayLeopardClip(1);}
 void Run(){bManualPresentation=true;PlayLeopardClip(2);}
 void Turn(){bManualPresentation=true;PlayLeopardClip(3);}
 void Investigate(){bManualPresentation=true;PlayLeopardClip(4);}
 void Capture(){bManualPresentation=true;PlayLeopardClip(5);}
 void Recover(){bManualPresentation=true;PlayLeopardClip(6);}
 void Command(){bManualPresentation=true;PlayLeopardClip(7);}
 void Isolation(){bManualPresentation=true;PlayLeopardClip(8);}
 void Automatic(){bManualPresentation=false;}
 void TickQualification(float DeltaSeconds);
 void TickContactQualification(float DeltaSeconds);
 FString ContactQualificationFile;
 float ContactQualificationSeconds=0;
 int32 ContactFixture=-1;
 bool bContactQualificationDone=false,bContactJumped=false,bContactFlew=false;
 FString QualificationFile;
 float QualificationSeconds=0;
 int32 QualificationStage=-1;
 bool bQualificationDone=false,bPoseBaseline=false;
 bool MotionObserved[9]={false,false,false,false,false,false,false,false,false};
 bool GraphClipObserved[9]={false,false,false,false,false,false,false,false,false};
 TArray<FTransform> PoseBaseline;
 FVector QualificationStart=FVector::ZeroVector;
};

UCLASS()
class ANANSE_API AAnanseLeopardLabMode : public AGameModeBase
{
 GENERATED_BODY()
public:AAnanseLeopardLabMode();
};
