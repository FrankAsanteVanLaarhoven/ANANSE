#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameFramework/SaveGame.h"
class ULevelSequence;
class UAnanseCinematic;
class AAnansePursuit;
class AAnanseInteractable;
#include "AnanseMission.generated.h"

USTRUCT(BlueprintType)
struct FAnanseMissionState
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly,SaveGame) bool bEpisodeSession=false;
    UPROPERTY(BlueprintReadOnly,SaveGame) bool bProductionPursuit=false;
    UPROPERTY(BlueprintReadOnly,SaveGame) bool bPursuitStarted=false;
    UPROPERTY(BlueprintReadOnly,SaveGame) bool bPursuitEscaped=false;
    UPROPERTY(BlueprintReadOnly,SaveGame) bool bCaptured=false;
    UPROPERTY(BlueprintReadOnly,SaveGame) float PursuitSeconds=0;
    UPROPERTY(BlueprintReadOnly,SaveGame) float PursuitLostSightSeconds=0;
    UPROPERTY(BlueprintReadOnly,SaveGame) FVector PursuerPosition=FVector(500,550,96);
    UPROPERTY(BlueprintReadOnly,SaveGame) FVector PursuerLastKnown=FVector::ZeroVector;
    UPROPERTY(BlueprintReadOnly,SaveGame) FName ProductionBeat=TEXT("arrival");
    UPROPERTY(BlueprintReadOnly,SaveGame) TArray<FName> CompletedPresentationEvents;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bEvidence=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bLearnedVoice=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bPermit=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bArchive=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bLedger=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bOnRooftop=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 Thread=3;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float Suspicion=0.f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 MarketTrust=0;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 CourtTrust=0;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FName Route;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FName Outcome;
};
UCLASS()
class ANANSE_API UAnanseSave : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY(SaveGame) int32 SchemaVersion=3;
    UPROPERTY(SaveGame) FName EpisodeId;
    UPROPERTY(SaveGame) bool bHasPursuitRecovery=false;
    UPROPERTY(SaveGame) FAnanseMissionState PursuitRecoveryState;
    UPROPERTY(SaveGame) FVector PursuitRecoveryPosition=FVector::ZeroVector;
    UPROPERTY(SaveGame) FRotator PursuitRecoveryRotation=FRotator::ZeroRotator;
    UPROPERTY(SaveGame) float RecoveryVoiceRemaining=0;
    UPROPERTY(SaveGame) float RecoveryMirrorRemaining=0;
    UPROPERTY(SaveGame) TMap<FName,float> RecoveryCooldownRemaining;
    UPROPERTY(SaveGame) FName CharacterId;
    UPROPERTY(SaveGame) FString MapIdentity;
    UPROPERTY(SaveGame) FString ContentHash;
    UPROPERTY(SaveGame) FAnanseMissionState State;
    UPROPERTY(SaveGame) FVector Position=FVector::ZeroVector;
    UPROPERTY(SaveGame) FRotator Rotation=FRotator::ZeroRotator;
    UPROPERTY(SaveGame) float VoiceRemaining=0;
    UPROPERTY(SaveGame) float MirrorRemaining=0;
    UPROPERTY(SaveGame) TMap<FName,float> CooldownRemaining;
};
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FAnanseMissionChanged);
UCLASS(ClassGroup=(Ananse),meta=(BlueprintSpawnableComponent))
class ANANSE_API UAnanseMission : public UActorComponent
{
    GENERATED_BODY()
public:
    UAnanseMission();
    virtual void BeginPlay() override;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<ULevelSequence> PursuitIntroSequence;
    UPROPERTY(BlueprintReadOnly) FAnanseMissionState State;
    UPROPERTY(BlueprintReadOnly) FString LatestMessage=TEXT("Find the altered edict. Movement: WASD / stick. Interact: E. Powers: 1, 2, 3.");
    UPROPERTY(BlueprintAssignable) FAnanseMissionChanged Changed;
    UPROPERTY(BlueprintReadOnly) float VoiceUntil=-1.f;
    UPROPERTY(BlueprintReadOnly) float MirrorUntil=-1.f;
    UPROPERTY(BlueprintReadOnly) TMap<FName,float> Cooldowns;
    UFUNCTION(BlueprintCallable) bool Act(FName Action);
    UFUNCTION(BlueprintCallable) bool PresentConsequenceLine();
    UFUNCTION(BlueprintCallable) bool PresentEpilogueLine();
    UFUNCTION(BlueprintCallable) bool TravelToSanctuary(const FString& SlotName);
    static FString SanctuaryMap();
    static FString MarketMap();
    static bool ValidCheckpointSlot(const FString& SlotName);
    UPROPERTY(BlueprintReadOnly) FName ActiveDialogueId;
    UPROPERTY(BlueprintReadOnly) FString ActiveDialogueSpeaker;
    UPROPERTY(BlueprintReadOnly) FString ActiveDialogueText;
    UFUNCTION(BlueprintCallable) bool CommitPower(FName Power);
    UFUNCTION(BlueprintCallable) void AddSuspicion(float Amount);
    UFUNCTION(BlueprintCallable) void Message(const FString& Text);
    UFUNCTION(BlueprintCallable) bool SaveLocal(const FString& SlotName=TEXT("AnansePrototype"));
    UFUNCTION(BlueprintCallable) bool LoadLocal(const FString& SlotName=TEXT("AnansePrototype"));
    UFUNCTION(BlueprintCallable) bool BeginCinematic(ULevelSequence* Sequence,FName EventId);
    UFUNCTION(BlueprintCallable) void SkipCinematic();
    UFUNCTION(BlueprintCallable) void CancelCinematic();
    UFUNCTION(BlueprintCallable) bool CompletePresentationEvent(FName EventId);
    UPROPERTY(Transient,BlueprintReadOnly) TObjectPtr<UAnanseCinematic> Cinematic;
    static bool CheckpointCompatible(const UAnanseSave* Save,const FString& ContentHash,FName CharacterId,const FString& MapIdentity,FString& Reason);
    UFUNCTION(BlueprintCallable) bool EnableProductionPursuit();
    UFUNCTION(BlueprintCallable) bool StartPursuit();
    UFUNCTION(BlueprintCallable) void CapturePursuit();
    UFUNCTION(BlueprintCallable) bool RetryPursuit();
    UPROPERTY(Transient,BlueprintReadOnly) TObjectPtr<AAnansePursuit> Pursuer;
    void RestorePursuitActor();
    void EnsureRetryMarker();
    UPROPERTY(Transient) TObjectPtr<AAnanseInteractable> RetryMarker;
    UPROPERTY(Transient) TObjectPtr<AAnanseInteractable> EscapeMarker;
    void EnsureEscapeMarker();
    UPROPERTY(Transient) TObjectPtr<AAnanseInteractable> SanctuaryGate;
    void RestoreEpisodePresentation();
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    UPROPERTY(Transient) bool bHasPursuitRecovery=false;
    UPROPERTY(Transient) FAnanseMissionState PursuitRecoveryState;
    UPROPERTY(Transient) FVector PursuitRecoveryPosition=FVector::ZeroVector;
    UPROPERTY(Transient) FRotator PursuitRecoveryRotation=FRotator::ZeroRotator;
    UPROPERTY(Transient) float RecoveryVoiceRemaining=0;
    UPROPERTY(Transient) float RecoveryMirrorRemaining=0;
    UPROPERTY(Transient) TMap<FName,float> RecoveryCooldownRemaining;
    float Clock() const;
    UFUNCTION(BlueprintPure) bool VoiceActive() const { return Clock()<=VoiceUntil; }
    UFUNCTION(BlueprintPure) bool MirrorActive() const { return Clock()<=MirrorUntil; }
};
