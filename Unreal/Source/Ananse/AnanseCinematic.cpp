#include "AnanseCinematic.h"
#include "AnanseMission.h"
#include "AnanseWorld.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "LevelSequence.h"
#include "LevelSequencePlayer.h"
#include "LevelSequenceActor.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Character.h"
#include "MovieSceneSequencePlaybackSettings.h"
#include "Engine/World.h"

UAnanseCinematic::UAnanseCinematic()
{
    PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.bStartWithTickEnabled=false;PrimaryComponentTick.TickInterval=.1f;
}
double UAnanseCinematic::PlaybackSeconds() const{return Player?Player->GetCurrentTime().AsSeconds():0;}
void UAnanseCinematic::TickComponent(float Delta,ELevelTick TickType,FActorComponentTickFunction* TickFunction)
{
    Super::TickComponent(Delta,TickType,TickFunction);
    if(!bActive || !Player || !MissionOwner)return;
    // Game-thread presentation query. Sequencer owns actor transforms; only this
    // path controls speaker camera-component orientation. No pawn/root writes.
    if(bNegotiationDialogue || bTransientPresentation)
    {
        const auto* Hero=Cast<ACharacter>(OriginalPawn.Get());FVector HeroHead=Hero?Hero->GetMesh()->GetSocketLocation(TEXT("head"))+FVector(0,0,5):FVector::ZeroVector;
        AAnanseInteractable* Strategist=nullptr;for(TActorIterator<AAnanseInteractable> It(GetWorld());It;++It)if(It->bNegotiationPresentation&&It->CharacterId==TEXT("aso-yaa")){Strategist=*It;break;}
        if(Strategist)
        {
            const FVector AsoHead=Strategist->CharacterVisual->GetSocketLocation(TEXT("head"))+FVector(0,0,5);
            for(TActorIterator<ACameraActor> It(GetWorld());It;++It)
            {
                FVector Target;if(It->ActorHasTag(TEXT("AsoShot:Kwaku")))Target=HeroHead;
                else if(It->ActorHasTag(TEXT("AsoShot:Both")))Target=(HeroHead+AsoHead)*.5f;
                else if(It->ActorHasTag(TEXT("AsoShot:Ledger")))Target=Strategist->NegotiationLedgerVisual->GetComponentLocation();
                else if(It->ActorHasTag(TEXT("AsoShot:Aso")))Target=AsoHead;else continue;
                if(auto* Camera=It->GetCameraComponent())Camera->SetWorldRotation((Target-Camera->GetComponentLocation()).Rotation());
            }
        }
    }
    const double Seconds=Player->GetCurrentTime().AsSeconds();FName Id;
    if(bOpeningDialogue)
    {
        const double At[]={6,13,19,22,25};
        const FName Names[]={TEXT("MSN_OPEN_010"),TEXT("MSN_OPEN_020"),TEXT("MSN_OPEN_030"),TEXT("MSN_OPEN_040"),TEXT("MSN_OPEN_050")};
        for(int32 I=0;I<5;++I)if(Seconds>=At[I])Id=Names[I];
    }
    if(bPursuitDialogue)Id=TEXT("MSN_CHASE_010");
    if(bNegotiationDialogue){const FName Names[]={TEXT("MSN_NEG_010"),TEXT("MSN_NEG_020"),TEXT("MSN_NEG_030"),TEXT("MSN_NEG_040"),TEXT("MSN_NEG_050")};Id=Names[FMath::Clamp(int32(Seconds/3.6),0,4)];}
    if(const FAnanseDialogueLine* Line=DraftLines.Find(Id))
    {MissionOwner->ActiveDialogueId=Id;MissionOwner->ActiveDialogueSpeaker=Line->Speaker;MissionOwner->ActiveDialogueText=Line->Text;}
}

bool UAnanseCinematic::Start(UAnanseMission* Mission,ULevelSequence* Sequence,FName EventId,bool bVisualOnly)
{
    if(bActive || !Mission || !Sequence || EventId.IsNone() || Mission->State.CompletedPresentationEvents.Contains(EventId))return false;
    APawn* Pawn=Cast<APawn>(Mission->GetOwner());
    APlayerController* PC=Pawn?Cast<APlayerController>(Pawn->GetController()):nullptr;
    if(!PC || !GetWorld())return false;
    bOpeningDialogue=Sequence->GetName()==TEXT("LS_MarketOpening_Technical");
    bPursuitDialogue=Sequence->GetName()==TEXT("LS_PursuitIntro_Technical");
    bNegotiationDialogue=Sequence->GetName()==TEXT("LS_AsoNegotiation_v001")||Sequence->GetName()==TEXT("LS_AsoNegotiation_v002");
    DraftLines.Empty();
    if(bOpeningDialogue || bPursuitDialogue || bNegotiationDialogue)
    {
        FString Error;
        if(!AnanseDialogue::Load(DraftLines,Error)){Mission->Message(Error);return false;}
        if(bNegotiationDialogue)for(const TCHAR* Id:{TEXT("MSN_NEG_010"),TEXT("MSN_NEG_020"),TEXT("MSN_NEG_030"),TEXT("MSN_NEG_040"),TEXT("MSN_NEG_050")})if(!DraftLines.Contains(FName(Id))){Mission->Message(TEXT("Negotiation subtitle binding incomplete."));return false;}
        if(bOpeningDialogue)for(const TCHAR* Id:{TEXT("MSN_OPEN_010"),TEXT("MSN_OPEN_020"),TEXT("MSN_OPEN_030"),TEXT("MSN_OPEN_040"),TEXT("MSN_OPEN_050")})
            if(!DraftLines.Contains(FName(Id))){Mission->Message(TEXT("Opening draft subtitle binding is incomplete."));return false;}
        if(bPursuitDialogue && !DraftLines.Contains(TEXT("MSN_CHASE_010"))){Mission->Message(TEXT("Pursuit draft subtitle binding is incomplete."));return false;}
    }
    FMovieSceneSequencePlaybackSettings Settings;
    Settings.FinishCompletionStateOverride=EMovieSceneCompletionModeOverride::ForceRestoreState;
    Settings.bAutoPlay=false;
    ALevelSequenceActor* CreatedActor=nullptr;
    Player=ULevelSequencePlayer::CreateLevelSequencePlayer(GetWorld(),Sequence,Settings,CreatedActor);
    SequenceActor=CreatedActor;
    if(!Player)return false;
    Controller=PC;OriginalPawn=Pawn;OriginalView=PC->GetViewTarget();OriginalRotation=PC->GetControlRotation();
    bTransientPresentation=bVisualOnly;
    MissionOwner=Mission;ActiveEvent=EventId;bActive=true;
    PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);
    if(ACharacter* Character=Cast<ACharacter>(Pawn))
    {
        UCharacterMovementComponent* Movement=Character->GetCharacterMovement();
        OriginalMode=Movement->MovementMode;OriginalCustomMode=Movement->CustomMovementMode;
        Movement->StopMovementImmediately();Movement->DisableMovement();
    }
    Player->OnFinished.AddDynamic(this,&UAnanseCinematic::Finished);
    Player->OnStop.AddDynamic(this,&UAnanseCinematic::Stopped);
    SetComponentTickEnabled(true);Player->Play();return true;
}
void UAnanseCinematic::Finished(){Release(true);}
void UAnanseCinematic::Stopped()
{
    if(!bActive)return;
    // UE natural completion broadcasts OnStop before OnFinished. Do not consume
    // the lifecycle until the same-frame finish event has had its chance.
    if(GetWorld())
    {
        GetWorld()->GetTimerManager().ClearTimer(PendingStop);
        PendingStop=GetWorld()->GetTimerManager().SetTimerForNextTick(this,&UAnanseCinematic::CompleteExternalStop);
    }
    else Release(false);
}
void UAnanseCinematic::CompleteExternalStop(){Release(false);}
void UAnanseCinematic::Skip(){if(bActive)Release(true);}
void UAnanseCinematic::Cancel(){Release(false);}
void UAnanseCinematic::EndPlay(const EEndPlayReason::Type Reason){Release(false);Super::EndPlay(Reason);}
void UAnanseCinematic::Release(bool bComplete)
{
    if(GetWorld())GetWorld()->GetTimerManager().ClearTimer(PendingStop);
    if(!bActive)return;
    bActive=false;
    SetComponentTickEnabled(false);
    if(Player)
    {
        Player->OnFinished.RemoveDynamic(this,&UAnanseCinematic::Finished);
        Player->OnStop.RemoveDynamic(this,&UAnanseCinematic::Stopped);
        Player->Stop();
    }
    if(APlayerController* PC=Controller.Get())
    {
        // Balance only this component's input locks; do not clear another system's locks.
        PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);
        if(APawn* Pawn=OriginalPawn.Get())if(PC->GetPawn()!=Pawn)PC->Possess(Pawn);
        if(AActor* View=OriginalView.Get())PC->SetViewTarget(View);
        PC->SetControlRotation(OriginalRotation);
    }
    if(ACharacter* Character=Cast<ACharacter>(OriginalPawn.Get()))
        Character->GetCharacterMovement()->SetMovementMode(OriginalMode,OriginalCustomMode);
    if(MissionOwner && !bTransientPresentation){MissionOwner->ActiveDialogueId=NAME_None;MissionOwner->ActiveDialogueSpeaker.Empty();MissionOwner->ActiveDialogueText.Empty();}
    if(bComplete && MissionOwner && !bTransientPresentation)MissionOwner->CompletePresentationEvent(ActiveEvent);
    if(SequenceActor)SequenceActor->Destroy();
    Player=nullptr;SequenceActor=nullptr;MissionOwner=nullptr;ActiveEvent=NAME_None;
}
