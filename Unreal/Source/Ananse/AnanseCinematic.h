#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "TimerManager.h"
#include "AnanseDialogue.h"
#include "AnanseCinematic.generated.h"
class UAnanseMission;
class ULevelSequence;
class ULevelSequencePlayer;
class ALevelSequenceActor;
class APlayerController;
class APawn;

/** Presentation only. Mission state owns durable events; cancelling never awards them. */
UCLASS(ClassGroup=(Ananse),meta=(BlueprintSpawnableComponent))
class ANANSE_API UAnanseCinematic : public UActorComponent
{
    GENERATED_BODY()
public:
    UAnanseCinematic();
    virtual void TickComponent(float Delta,ELevelTick TickType,FActorComponentTickFunction* TickFunction) override;
    bool Start(UAnanseMission* Mission,ULevelSequence* Sequence,FName EventId,bool bVisualOnly=false);
    UFUNCTION(BlueprintCallable) void Skip();
    UFUNCTION(BlueprintCallable) void Cancel();
    UFUNCTION(BlueprintPure) bool HasPendingStop() const { return PendingStop.IsValid(); }
    double PlaybackSeconds() const;
    bool IsNegotiationPresentation()const{return bActive&&bNegotiationDialogue;}
    UPROPERTY(BlueprintReadOnly) bool bActive=false;
    UPROPERTY(BlueprintReadOnly) FName ActiveEvent;
protected:
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UFUNCTION() void Finished();
    UFUNCTION() void Stopped();
    void CompleteExternalStop();
    FTimerHandle PendingStop;
    void Release(bool bComplete);
    UPROPERTY(Transient) TObjectPtr<ULevelSequencePlayer> Player;
    UPROPERTY(Transient) TObjectPtr<ALevelSequenceActor> SequenceActor;
    UPROPERTY(Transient) TObjectPtr<UAnanseMission> MissionOwner;
    TWeakObjectPtr<APlayerController> Controller;
    TWeakObjectPtr<APawn> OriginalPawn;
    TWeakObjectPtr<AActor> OriginalView;
    FRotator OriginalRotation;
    TEnumAsByte<EMovementMode> OriginalMode=MOVE_None;
    uint8 OriginalCustomMode=0;
    TMap<FName,FAnanseDialogueLine> DraftLines;
    bool bOpeningDialogue=false;
    bool bPursuitDialogue=false;
    bool bNegotiationDialogue=false;
    bool bTransientPresentation=false;
};
