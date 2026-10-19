#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "AnanseWorld.generated.h"
struct FAnanseMissionState;
class ULevelSequence;
class UStaticMeshComponent;class USkeletalMeshComponent;class UAnimSequence;class UTextRenderComponent;class AAnansePlayer;
UCLASS()
class ANANSE_API AAnanseInteractable : public AActor
{
    GENERATED_BODY()
public:
    AAnanseInteractable();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    static int32 NegotiationPoseFor(const FAnanseMissionState& State);
    UPROPERTY(EditAnywhere) bool bNegotiationPresentation=false;
    UPROPERTY(EditAnywhere) TObjectPtr<ULevelSequence> NegotiationSequence;
    UPROPERTY(EditAnywhere) TArray<TObjectPtr<UAnimSequence>> NegotiationClips;
    UPROPERTY(Transient,BlueprintReadOnly) int32 NegotiationPose=0;
    void PlayNegotiation(int32 Index);
    void UpdateNegotiationLedger();
    UPROPERTY(EditAnywhere) bool bNegotiationLedger=false;
    UPROPERTY(EditAnywhere) TObjectPtr<ULevelSequence> BrokenPromiseReaction;
    FName LastReactionDialogue;
    bool bWasNegotiationShot=false;
    double LastNegotiationPlayback=-1;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> NegotiationLedgerVisual;
    int32 LastNegotiationState=-1;
    float NegotiationAge=0;
    float NegotiationClock=0;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UTextRenderComponent> Label;
    // Optional authored presentation; the original root owns interaction/collision.
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> PropVisual;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<USkeletalMeshComponent> CharacterVisual;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<UAnimSequence> PresentationIdle;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) FName Action=TEXT("evidence");
    UPROPERTY(EditAnywhere,BlueprintReadWrite) FName CharacterId;
    void Configure(FName InAction,const FString& Text,FName InCharacterId=NAME_None);
    void Use(AAnansePlayer* Player);
};
UCLASS()
class ANANSE_API AAnanseWatchman : public AActor
{
    GENERATED_BODY()
public:
    AAnanseWatchman();
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Mesh;
};
UCLASS()
class ANANSE_API AAnanseGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AAnanseGameMode();
};
UCLASS()
class ANANSE_API AAnanseHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
