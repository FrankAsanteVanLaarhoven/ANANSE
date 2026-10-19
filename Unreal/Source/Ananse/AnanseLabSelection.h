#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SaveGame.h"
#include "AnanseLabSelection.generated.h"
class UPointLightComponent;class AAnansePlayer;class USkeletalMesh;class USkeletalMeshComponent;class UMaterialInterface;class UAnimInstance;class UAnimSequence;class UInputMappingContext;struct FStreamableHandle;class FJsonValue;

/** Allowlisted project content, not a metadata-supplied executable class path. */
UCLASS(BlueprintType)
class ANANSE_API UAnanseCharacterDefinition:public UPrimaryDataAsset
{
 GENERATED_BODY()
public:
 UPROPERTY(EditAnywhere,BlueprintReadOnly) FName DesignId;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) FName CharacterIdentity;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) FName SkeletonKey;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) int32 Revision=1;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TSoftClassPtr<AAnansePlayer> PawnClass;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TSoftObjectPtr<USkeletalMesh> Mesh;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TArray<TSoftObjectPtr<UAnimSequence>> Clips;
 // Technical fixture readiness never grants art approval or campaign permission.
 UPROPERTY(EditAnywhere,BlueprintReadOnly) bool bEngineeringFixture=false;
 bool ValidateLoaded(FString& Error)const;
};
UCLASS()
class ANANSE_API UAnanseLabSelectionSave:public USaveGame
{
 GENERATED_BODY()
public:
 UPROPERTY(SaveGame) int32 SchemaVersion=1;
 UPROPERTY(SaveGame) FName DesignId;
 UPROPERTY(SaveGame) FName CharacterIdentity;
 UPROPERTY(SaveGame) FName SkeletonKey;
 UPROPERTY(SaveGame) FName CosmeticVariant=TEXT("base");
 UPROPERTY(SaveGame) int32 AssetRevision=1;
 UPROPERTY(SaveGame) FString ContentHash;
};
/** Exists only in the authorised lab GameMode. Fixed allowlist; no campaign swap. */
UCLASS()
class ANANSE_API AAnanseLabController:public APlayerController
{
 GENERATED_BODY()
public:
 // One policy for initial lab lighting and subsequent possession changes.
 static void ConfigurePreviewLight(UPointLightComponent* Light,bool bStory);
 virtual void SetupInputComponent()override;
 virtual void BeginPlay()override;
 virtual void OnPossess(APawn* InPawn)override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
 UFUNCTION(BlueprintCallable) bool SelectDesign(FName Design);
 UFUNCTION(BlueprintCallable) void CancelSelection();
 UFUNCTION(BlueprintCallable) bool SaveSelection();
 UFUNCTION(BlueprintCallable) bool LoadSelection();
 UPROPERTY(BlueprintReadOnly) FName SelectedDesign=TEXT("ananse-spider-existing");
 UPROPERTY(BlueprintReadOnly) FString SelectionStatus=TEXT("Development lab: Home spider / End leopard / Backspace cancel / F6 save / F8 load");
 bool IsSelectionPending()const{return Pending.IsValid();}
 uint64 Generation=0;
private:
 int32 KwakuPresentationRevision()const;
 TArray<TWeakObjectPtr<AActor>> PreviewLights;
 TWeakObjectPtr<AActor> PreviewFog;
 TSharedPtr<FStreamableHandle> Pending;
 UPROPERTY(Transient) TArray<TObjectPtr<UMaterialInterface>> PreviewMaterials;
 TWeakObjectPtr<USkeletalMeshComponent> PreviewMesh;
 void ToggleWireframe();void RestorePreview();void ToggleLabPause();
 void FinishSelection(uint64 Request,FName Design);
 void NextStoryDesign();
 void SelectSpider(){SelectDesign(TEXT("ananse-spider-existing"));}
 void SelectBaseline(){SelectDesign(TEXT("kwaku-development"));}
 void SelectLeopard(){SelectDesign(TEXT("osebo-leopard-v1"));}
 void SaveLab(){SaveSelection();}void LoadLab(){LoadSelection();}
 float VerifySeconds=0,NextVerifyAction=0;
 int32 VerifyStage=0,SwapCount=0;
 bool bVerifyFailed=false,bVerifyDone=false;
 bool bRestoredProfile=false;
 uint64 RestoreGeneration=0;
 UPROPERTY(Transient) TObjectPtr<UAnanseCharacterDefinition> LoadedDefinition;
 FString VerifyFile;
 TArray<TWeakObjectPtr<UInputMappingContext>> VerifyMappings;
 void TickCrossFamily(float DeltaSeconds);
 void TickStoryCast(float DeltaSeconds);
 bool bArtOpenCaptured=false,bArtClosedCaptured=false;
 float StoryAge=0,StoryPhaseAge=0,StoryMaxBlink=0;bool bStoryLedgerObserved=false,bStoryLedgerCaptured=false,bStoryLedgerResetTested=false;
 int32 StoryStage=0,StoryIndex=0,StoryRoundTrips=0,StoryClipIndex=0;
 bool bStoryFailed=false,bStoryDone=false,bStoryClipMotion=false;
 FVector StoryStart;
 TArray<FTransform> StoryPose;
 TArray<TSharedPtr<FJsonValue>> StoryRecords,StoryClipChecks;

 int32 CrossStage=0,CrossCommitted=0;
 float CrossAge=0,CrossPhaseStart=0;
 uint32 CrossOldPawn=0;
 FName CrossExpected;
 bool bCrossFailed=false,bCrossDone=false,bCrossPoseReady=false,bCrossPhoto=false;
 FVector CrossPosition;
 TArray<FTransform> CrossPose;
 TArray<TSharedPtr<FJsonValue>> CrossTransitions;
 TArray<TSharedPtr<FJsonValue>> CrossNegativeChecks;
 FName CrossRestoredDesign;
 int32 TestSelectionFault=0,RejectedStaleCompletions=0,CrossStaleBefore=0;
 TWeakObjectPtr<AActor> TestSpawnBlocker;
 bool bTestLateCompletionFired=false;
};
