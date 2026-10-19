#include "AnanseMission.h"
#include "AnanseDialogue.h"
#include "AnanseRuntimeVerification.h"
#include "AnanseCinematic.h"
#include "AnanseCatalogue.h"
#include "AnansePlayer.h"
#include "AnansePursuit.h"
#include "LevelSequence.h"
#include "AnanseWorld.h"
#include "Components/StaticMeshComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/PackageName.h"
#include "TimerManager.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
static FName CheckpointCharacter(const AActor* Owner);

UAnanseMission::UAnanseMission(){ PrimaryComponentTick.bCanEverTick=false; }
FString UAnanseMission::SanctuaryMap(){if(FParse::Param(FCommandLine::Get(),TEXT("AnanseEnvironmentRoute")))return TEXT("/Game/Ananse/Maps/EnvironmentRoute_v002/L_StoryForest_Route");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAcceptedVisuals")))return TEXT("/Game/Ananse/Maps/EpisodeAccepted_v001/L_Sanctuary_AcceptedVisuals");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseInteractionRefinement")))return TEXT("/Game/Ananse/Maps/Interactions_v003/L_Sanctuary_EpisodeInteractions");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseFormsScenery")))return TEXT("/Game/Ananse/Maps/Refinement_v007/L_Sanctuary_EpisodeForms");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtRefinement")))return TEXT("/Game/Ananse/Maps/Refinement_v003/L_Sanctuary_EpisodeRefined");return FParse::Param(FCommandLine::Get(),TEXT("AnanseStoryPresentation"))?TEXT("/Game/Ananse/Maps/Story_v001/L_Sanctuary_EpisodeStaging"):TEXT("/Game/Production/Sanctuary/Technical_v001/L_StorySanctuary_Technical");}
FString UAnanseMission::MarketMap(){if(FParse::Param(FCommandLine::Get(),TEXT("AnanseEnvironmentRoute")))return TEXT("/Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoContact")))return TEXT("/Game/Ananse/Maps/Contact_v002/L_Market_AsoNegotiation");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoReview")))return TEXT("/Game/Ananse/Maps/Negotiation_v002/L_Market_AsoNegotiation");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAcceptedVisuals")))return TEXT("/Game/Ananse/Maps/EpisodeAccepted_v001/L_Market_AcceptedVisuals");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseInteractionRefinement")))return TEXT("/Game/Ananse/Maps/Interactions_v003/L_Market_EpisodeInteractions");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseFormsScenery")))return TEXT("/Game/Ananse/Maps/Refinement_v007/L_Market_EpisodeForms");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtRefinement")))return TEXT("/Game/Ananse/Maps/Refinement_v003/L_Market_EpisodeRefined");return FParse::Param(FCommandLine::Get(),TEXT("AnanseStoryPresentation"))?TEXT("/Game/Ananse/Maps/Story_v001/L_Market_EpisodeStaging"):TEXT("/Game/Maps/L_Market_Greybox");}
void UAnanseMission::BeginPlay()
{
    Super::BeginPlay();
    const AAnansePlayer* Player=Cast<AAnansePlayer>(GetOwner());
    const bool Episode=Player && Player->CharacterId==TEXT("kwaku") && FParse::Param(FCommandLine::Get(),TEXT("AnanseEpisode"));
    State.bEpisodeSession=Episode;
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseProductionPursuit")) || Episode)
    {
        EnableProductionPursuit();
        if(!PursuitIntroSequence)PursuitIntroSequence=LoadObject<ULevelSequence>(nullptr,TEXT("/Game/Production/Market/Technical_v002/LS_PursuitIntro_Technical.LS_PursuitIntro_Technical"));
        if(!PursuitIntroSequence)Message(TEXT("Production pursuit enabled but technical intro asset is missing; ledger progression remains blocked."));
    }
    if(GetWorld())
    {
        const FString Continue=GetWorld()->URL.GetOption(TEXT("AnanseContinueSlot="),TEXT(""));
        if(!Continue.IsEmpty())
            GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Continue](){LoadLocal(Continue);}));
    }
}
float UAnanseMission::Clock() const { return GetWorld()?GetWorld()->GetTimeSeconds():0.f; }
void UAnanseMission::Message(const FString& Text){ LatestMessage=Text;Changed.Broadcast(); }
void UAnanseMission::AddSuspicion(float Amount)
{
    if(!State.Outcome.IsNone()) return;
    // Once the played chase starts, Osebo capture owns failure. A checkpoint watcher
    // must not race an unrelated detained outcome against capture/retry.
    if(State.bProductionPursuit && State.bPursuitStarted && !State.bPursuitEscaped)return;
    State.Suspicion=FMath::Clamp(State.Suspicion+FMath::Max(0.f,Amount),0.f,100.f);
    if(State.Suspicion>=100.f){State.Outcome=TEXT("detained");Message(TEXT("Detained. Your cover failed. Load a prior local save or restart the level."));}
    Changed.Broadcast();
}
bool UAnanseMission::Act(FName Action)
{
    if(Action==TEXT("consequence_response"))return PresentConsequenceLine();
    if(Action==TEXT("sanctuary"))return TravelToSanctuary(AnanseVerificationSaveSlot(CheckpointCharacter(GetOwner())));
    if(Action==TEXT("epilogue"))return PresentEpilogueLine();
    if(Action==TEXT("retry"))return RetryPursuit();
    if(State.bCaptured){Message(TEXT("Captured by Osebo. Interact with retry to restore the preserved chase checkpoint."));return false;}
    if(Action==TEXT("escape"))
    {
        if(State.bPursuitEscaped)return false;
        if(!State.bProductionPursuit || !Pursuer || !Pursuer->CanEscape()){Message(TEXT("Reach the escape gate after at least six seconds of played pursuit with Osebo safely behind."));return false;}
        State.bPursuitEscaped=true;State.ProductionBeat=TEXT("decision");Pursuer->Halt();
        if(EscapeMarker){EscapeMarker->Destroy();EscapeMarker=nullptr;}
        Message(TEXT("You escaped Osebo. Choose the ledger consequence."));return true;
    }
    if(!State.Outcome.IsNone()){Message(TEXT("This run is complete. Restart the level to explore another outcome."));return false;}
    if(Action==TEXT("evidence"))
    {
        if(State.bEvidence){Message(TEXT("The evidence is already recorded; it cannot be farmed."));return false;}
        State.bEvidence=true;Message(TEXT("The edict's seal was altered. This is evidence, not merely a rumour."));return true;
    }
    if(Action==TEXT("listen")){State.bLearnedVoice=true;Message(TEXT("You learned the captain's call. Borrowed Voice now has a specific identity to imitate."));return true;}
    if(Action==TEXT("negotiate"))
    {
        if(!State.bEvidence){Message(TEXT("Aso Yaa needs evidence before she will negotiate access."));return false;}
        if(State.bPermit){Message(TEXT("You already promised to protect the named witnesses."));return false;}
        State.bPermit=true;State.MarketTrust++;Message(TEXT("Aso Yaa grants a permit. You have promised to protect the witnesses."));return true;
    }
    if(Action==TEXT("archive"))
    {
        if(State.bPermit)State.Route=TEXT("negotiation");
        else if(VoiceActive())State.Route=TEXT("social");
        else if(State.bOnRooftop && MirrorActive())State.Route=TEXT("rooftop");
        else{AddSuspicion(25.f);if(State.Outcome.IsNone())Message(TEXT("Access denied: obtain a permit, borrow the authorised voice, or distract the watcher from the rooftop."));return false;}
        State.bArchive=true;Message(FString::Printf(TEXT("Archive access obtained by %s. Recover the ledger."),*State.Route.ToString()));return true;
    }
    if(Action==TEXT("ledger"))
    {
        if(!State.bArchive){Message(TEXT("The sealed ledger requires archive access, even if you physically bypass a wall."));return false;}
        if(State.bLedger){Message(TEXT("Ledger already recovered."));return false;}
        State.bLedger=true;
        if(State.bProductionPursuit)State.ProductionBeat=TEXT("discovery");
        Message(TEXT("The ledger proves the forgery but names vulnerable witnesses. Choose exposure or protection."));return true;
    }
    if(Action==TEXT("expose") || Action==TEXT("protect"))
    {
        if(!State.bLedger){Message(TEXT("Recover the ledger before choosing its fate."));return false;}
        if(State.bProductionPursuit && !State.bPursuitEscaped){Message(TEXT("Escape the played pursuit before choosing the consequence."));return false;}
        if(Action==TEXT("expose"))
        {
            if(!State.bEvidence){Message(TEXT("Public exposure needs corroborating evidence from the altered edict."));return false;}
            State.Outcome=TEXT("truth-exposed");State.CourtTrust-=2;State.MarketTrust+=State.bPermit?-2:1;
            Message(State.bPermit?TEXT("The forgery is exposed, but you broke your promise and endangered the witnesses."):TEXT("The forgery is exposed. Its witnesses are now vulnerable to retaliation."));
        }
        else {State.Outcome=TEXT("witnesses-protected");State.MarketTrust+=2;Message(TEXT("The witnesses are protected. The court's authorised history remains uncorrected."));}
        if(State.bProductionPursuit)State.ProductionBeat=TEXT("consequence");
        return true;
    }
    Message(TEXT("Unknown interaction."));return false;
}
bool UAnanseMission::PresentConsequenceLine()
{
    if(State.Outcome!=TEXT("truth-exposed") && State.Outcome!=TEXT("witnesses-protected"))return false;
    if(State.bProductionPursuit && !State.bPursuitEscaped)return false;
    TArray<FName> Ids;
    if(State.Outcome==TEXT("truth-exposed"))
    {
        if(State.bPermit)Ids.Add(TEXT("MSN_BROKEN_010"));
        Ids.Append({TEXT("MSN_EXPOSE_010"),TEXT("MSN_EXPOSE_020"),TEXT("MSN_EXPOSE_030")});
    }
    else Ids.Append({TEXT("MSN_PROTECT_010"),TEXT("MSN_PROTECT_020"),TEXT("MSN_PROTECT_030")});
    TMap<FName,FAnanseDialogueLine> Lines;FString Error;
    if(!AnanseDialogue::Load(Lines,Error)){Message(Error);return false;}
    // Check the whole required branch before consuming any durable presentation event.
    for(FName Id:Ids)if(!Lines.Contains(Id)){Message(TEXT("Required consequence dialogue is missing; no presentation progress consumed."));return false;}
    for(FName Id:Ids)
    {
        if(State.CompletedPresentationEvents.Contains(Id))continue;
        const FAnanseDialogueLine& Line=Lines.FindChecked(Id);
        ActiveDialogueId=Id;ActiveDialogueSpeaker=Line.Speaker;ActiveDialogueText=Line.Text;
        State.CompletedPresentationEvents.Add(Id);
        bool bComplete=true;for(FName Required:Ids)bComplete &= State.CompletedPresentationEvents.Contains(Required);
        if(bComplete && State.bProductionPursuit){State.ProductionBeat=TEXT("sanctuary_pending");RestoreEpisodePresentation();}
        Message(Line.Speaker+TEXT(": ")+Line.Text);
        return true;
    }
    Message(State.bEpisodeSession?TEXT("Consequence dialogue complete. Follow the Story Road gate to Ananse."):TEXT("Consequence dialogue complete. Sanctuary map/presentation integration is still required."));
    return false;
}
bool UAnanseMission::CommitPower(FName Power)
{
    if(State.bCaptured || !State.Outcome.IsNone() || State.Thread<1){Message(TEXT("No story-thread remains, or the run has ended."));return false;}
    if(Cooldowns.FindRef(Power)>Clock()){Message(TEXT("That power is cooling down."));return false;}
    if(Power==TEXT("borrowed-voice") && !State.bLearnedVoice){Message(TEXT("First listen to the captain's authorised call."));return false;}
    if(Power!=TEXT("web-step") && Power!=TEXT("borrowed-voice") && Power!=TEXT("trick-mirror")){Message(TEXT("Unknown power."));return false;}
    State.Thread--;Cooldowns.Add(Power,Clock()+4.f);
    if(Power==TEXT("borrowed-voice")){VoiceUntil=Clock()+12.f;AddSuspicion(8.f);Message(TEXT("This checkpoint accepts the voice for 12 seconds; this is not global disguise immunity."));}
    if(Power==TEXT("trick-mirror")){MirrorUntil=Clock()+8.f;Message(TEXT("The archive watcher is distracted for eight seconds."));}
    if(Power==TEXT("web-step")){State.bOnRooftop=true;AddSuspicion(10.f);Message(TEXT("Web Step consumed one thread. The archive watcher still needs distracting."));}
    Changed.Broadcast();return true;
}
bool UAnanseMission::ValidCheckpointSlot(const FString& SlotName)
{
    if(SlotName.IsEmpty() || SlotName.Len()>64)return false;
    for(TCHAR C:SlotName)if(!FChar::IsAlnum(C) && C!=TEXT('_') && C!=TEXT('-'))return false;
    return true;
}
static FName CheckpointCharacter(const AActor* Owner)
{
    if(const AAnansePlayer* Player=Cast<AAnansePlayer>(Owner))return Player->CharacterId;
    return NAME_None;
}
static FString CheckpointMap(const UWorld* World)
{
    return World?UWorld::RemovePIEPrefix(World->GetOutermost()->GetName()):FString();
}
bool UAnanseMission::CheckpointCompatible(const UAnanseSave* Save,const FString& Hash,FName Character,const FString& Map,FString& Reason)
{
    Reason.Reset();
    if(!Save || (Save->SchemaVersion!=1 && Save->SchemaVersion!=2 && Save->SchemaVersion!=3 && Save->SchemaVersion!=4)){Reason=TEXT("Unsupported checkpoint schema; existing bytes retained.");return false;}
    if(Save->SchemaVersion==4 && (Save->EpisodeId!=TEXT("market-of-stolen-names-v1") || !Save->State.bEpisodeSession || (Save->MapIdentity!=MarketMap() && Save->MapIdentity!=SanctuaryMap())))
    {Reason=TEXT("Invalid episode checkpoint binding; existing bytes retained.");return false;}
    if(Hash.IsEmpty() || Save->ContentHash!=Hash){Reason=TEXT("Checkpoint content revision differs; explicit migration required and existing bytes retained.");return false;}
    if(Character.IsNone() || Map.IsEmpty()){Reason=TEXT("Active character/map binding is missing.");return false;}
    // Historical schema-1 checkpoints had only the campaign Kwaku greybox binding.
    // Absence of fields is not permission to restore into a new character or map.
    const FName SavedCharacter=Save->SchemaVersion==1?FName(TEXT("kwaku")):Save->CharacterId;
    const FString SavedMap=Save->SchemaVersion==1?TEXT("/Game/Maps/L_Market_Greybox"):Save->MapIdentity;
    if(SavedCharacter!=Character || SavedMap!=Map){Reason=TEXT("Checkpoint belongs to another character/map; existing bytes retained.");return false;}
    return true;
}
bool UAnanseMission::SaveLocal(const FString& SlotName)
{
    if(Cinematic && Cinematic->bActive){Message(TEXT("Finish or skip the active presentation before checkpoint changes."));return false;}
    if(!ValidCheckpointSlot(SlotName))
    {Message(TEXT("Invalid local checkpoint slot."));return false;}
    if(!GetWorld() || !GetOwner())return false;
    UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::CreateSaveGameObject(UAnanseSave::StaticClass()));
    if(!Save)return false;
    if(State.bEpisodeSession){Save->SchemaVersion=4;Save->EpisodeId=TEXT("market-of-stolen-names-v1");Save->State=State;}
    if(!GetWorld()->GetGameInstance())return false;
    if(const UAnanseCatalogue* C=GetWorld()->GetGameInstance()->GetSubsystem<UAnanseCatalogue>())Save->ContentHash=C->ContentHash;
    Save->CharacterId=CheckpointCharacter(GetOwner());Save->MapIdentity=CheckpointMap(GetWorld());
    FString Reason;
    if(!CheckpointCompatible(Save,Save->ContentHash,Save->CharacterId,Save->MapIdentity,Reason)){Message(Reason);return false;}
    if(UGameplayStatics::DoesSaveGameExist(SlotName,0))
    {
        const UAnanseSave* Existing=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(SlotName,0));
        if(!CheckpointCompatible(Existing,Save->ContentHash,Save->CharacterId,Save->MapIdentity,Reason)){Message(Reason+TEXT(" Use a new checkpoint slot."));return false;}
    }
    Save->bHasPursuitRecovery=bHasPursuitRecovery;Save->PursuitRecoveryState=PursuitRecoveryState;
    Save->PursuitRecoveryPosition=PursuitRecoveryPosition;Save->PursuitRecoveryRotation=PursuitRecoveryRotation;
    Save->RecoveryVoiceRemaining=RecoveryVoiceRemaining;Save->RecoveryMirrorRemaining=RecoveryMirrorRemaining;Save->RecoveryCooldownRemaining=RecoveryCooldownRemaining;
    Save->State=State;Save->Position=GetOwner()->GetActorLocation();Save->Rotation=GetOwner()->GetActorRotation();
    Save->VoiceRemaining=FMath::Max(0.f,VoiceUntil-Clock());Save->MirrorRemaining=FMath::Max(0.f,MirrorUntil-Clock());
    for(const auto& C:Cooldowns)Save->CooldownRemaining.Add(C.Key,FMath::Max(0.f,C.Value-Clock()));
    const bool bSaved=UGameplayStatics::SaveGameToSlot(Save,SlotName,0);Message(bSaved?TEXT("Local prototype checkpoint saved."):TEXT("Local save failed."));return bSaved;
}
bool UAnanseMission::LoadLocal(const FString& SlotName)
{
    if(Cinematic && Cinematic->bActive){Message(TEXT("Finish or skip the active presentation before checkpoint changes."));return false;}
    if(!ValidCheckpointSlot(SlotName))
    {Message(TEXT("Invalid local checkpoint slot."));return false;}
    if(!GetWorld() || !GetOwner())return false;
    const UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(SlotName,0));
    if(!GetWorld()->GetGameInstance())return false;
    const UAnanseCatalogue* C=GetWorld()->GetGameInstance()->GetSubsystem<UAnanseCatalogue>();
    FString Reason;
    if(!CheckpointCompatible(Save,C?C->ContentHash:FString(),CheckpointCharacter(GetOwner()),CheckpointMap(GetWorld()),Reason)){Message(Reason);return false;}
    CancelCinematic();
    // MoveComponent may report no movement when already at the exact checkpoint.
    // Treat that as a no-op only after checking the existing pose is unblocked.
    const bool AlreadyAtCheckpoint=GetOwner()->GetActorLocation().Equals(Save->Position,UE_KINDA_SMALL_NUMBER)
        && GetOwner()->GetActorRotation().Equals(Save->Rotation,UE_KINDA_SMALL_NUMBER);
    const bool PlacementSucceeded=AlreadyAtCheckpoint
        ? !GetWorld()->EncroachingBlockingGeometry(GetOwner(),Save->Position,Save->Rotation)
        : GetOwner()->TeleportTo(Save->Position,Save->Rotation,false,false);
    if(!PlacementSucceeded){Message(TEXT("Checkpoint location is blocked; load cancelled."));return false;}
    if(AAnansePlayer* Player=Cast<AAnansePlayer>(GetOwner()))Player->ResetTransientMotion();
    State=Save->State;VoiceUntil=Save->VoiceRemaining>0.f?Clock()+Save->VoiceRemaining:-1.f;MirrorUntil=Save->MirrorRemaining>0.f?Clock()+Save->MirrorRemaining:-1.f;
    ActiveDialogueId=NAME_None;ActiveDialogueSpeaker.Empty();ActiveDialogueText.Empty();
    Cooldowns.Empty();for(const auto& Pair:Save->CooldownRemaining)Cooldowns.Add(Pair.Key,Clock()+Pair.Value);
    if(ACharacter* Character=Cast<ACharacter>(GetOwner())){Character->GetCharacterMovement()->StopMovementImmediately();Character->GetCharacterMovement()->SetMovementMode(MOVE_Walking);}
    bHasPursuitRecovery=Save->bHasPursuitRecovery;PursuitRecoveryState=Save->PursuitRecoveryState;
    PursuitRecoveryPosition=Save->PursuitRecoveryPosition;PursuitRecoveryRotation=Save->PursuitRecoveryRotation;
    RecoveryVoiceRemaining=Save->RecoveryVoiceRemaining;RecoveryMirrorRemaining=Save->RecoveryMirrorRemaining;RecoveryCooldownRemaining=Save->RecoveryCooldownRemaining;RestorePursuitActor();
    if(State.bCaptured){EnsureRetryMarker();if(ACharacter* Character=Cast<ACharacter>(GetOwner()))Character->GetCharacterMovement()->DisableMovement();}
    RestoreEpisodePresentation();
    Message(TEXT("Local checkpoint restored. This is not a cloud or authoritative multiplayer save."));return true;
}

bool UAnanseMission::CompletePresentationEvent(FName EventId)
{
    if(EventId.IsNone() || State.CompletedPresentationEvents.Contains(EventId))return false;
    State.CompletedPresentationEvents.Add(EventId);
    if(EventId==TEXT("opening_finished_or_skipped") && State.ProductionBeat==TEXT("arrival"))State.ProductionBeat=TEXT("investigation");
    if(EventId==TEXT("pursuit_intro_finished_or_skipped") && State.bProductionPursuit && State.bLedger && !State.bPursuitStarted)StartPursuit();
    Changed.Broadcast();return true;
}
bool UAnanseMission::BeginCinematic(ULevelSequence* Sequence,FName EventId)
{
    if(!GetOwner() || EventId.IsNone() || State.CompletedPresentationEvents.Contains(EventId))return false;
    if(!Cinematic){Cinematic=NewObject<UAnanseCinematic>(GetOwner());Cinematic->RegisterComponent();}
    return Cinematic->Start(this,Sequence,EventId);
}
void UAnanseMission::SkipCinematic(){if(Cinematic)Cinematic->Skip();}
void UAnanseMission::CancelCinematic(){if(Cinematic)Cinematic->Cancel();}

bool UAnanseMission::EnableProductionPursuit()
{
    if(State.bLedger || !State.Outcome.IsNone())return false;
    State.bProductionPursuit=true;Changed.Broadcast();return true;
}
bool UAnanseMission::StartPursuit()
{
    if(!State.bProductionPursuit || !State.bLedger || State.bPursuitStarted || !GetOwner() || !GetWorld())return false;
    PursuitRecoveryState=State;PursuitRecoveryPosition=GetOwner()->GetActorLocation();PursuitRecoveryRotation=GetOwner()->GetActorRotation();bHasPursuitRecovery=true;
    RecoveryVoiceRemaining=FMath::Max(0.f,VoiceUntil-Clock());RecoveryMirrorRemaining=FMath::Max(0.f,MirrorUntil-Clock());RecoveryCooldownRemaining.Empty();
    for(const auto& Pair:Cooldowns)RecoveryCooldownRemaining.Add(Pair.Key,FMath::Max(0.f,Pair.Value-Clock()));
    State.bPursuitStarted=true;State.ProductionBeat=TEXT("pursuit");State.PursuerLastKnown=GetOwner()->GetActorLocation();
    RestorePursuitActor();
    if(!Pursuer){State=PursuitRecoveryState;Message(TEXT("Osebo spawn blocked; pursuit not started."));return false;}
    Message(TEXT("OSEBO PURSUIT / PROXY: reach the escape gate while keeping your distance."));return true;
}
void UAnanseMission::RestorePursuitActor()
{
    if(EscapeMarker){EscapeMarker->Destroy();EscapeMarker=nullptr;}
    if(Pursuer){Pursuer->Destroy();Pursuer=nullptr;}
    if(!State.bPursuitStarted || State.bPursuitEscaped || State.bCaptured || !GetWorld())return;
    FActorSpawnParameters Spawn;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButDontSpawnIfColliding;
    Pursuer=GetWorld()->SpawnActor<AAnansePursuit>(AAnansePursuit::StaticClass(),State.PursuerPosition,FRotator::ZeroRotator,Spawn);
    if(Pursuer){Pursuer->Start(this,Cast<ACharacter>(GetOwner()));EnsureEscapeMarker();}
}
void UAnanseMission::CapturePursuit()
{
    if(!State.bProductionPursuit || !State.bPursuitStarted || State.bPursuitEscaped || State.bCaptured)return;
    CancelCinematic();if(AAnansePlayer* Player=Cast<AAnansePlayer>(GetOwner()))Player->ResetTransientMotion();State.bCaptured=true;State.ProductionBeat=TEXT("captured");
    if(ACharacter* Character=Cast<ACharacter>(GetOwner())){Character->GetCharacterMovement()->StopMovementImmediately();Character->GetCharacterMovement()->DisableMovement();}
    EnsureRetryMarker();
    Message(TEXT("Osebo captured you. Retry restores the preserved pre-pursuit checkpoint; no consequence has been awarded."));
}
bool UAnanseMission::RetryPursuit()
{
    if(!State.bCaptured || !bHasPursuitRecovery || !GetOwner())return false;
    if(!GetOwner()->TeleportTo(PursuitRecoveryPosition,PursuitRecoveryRotation,false,false)){Message(TEXT("Retry location blocked; checkpoint retained."));return false;}
    if(RetryMarker){RetryMarker->Destroy();RetryMarker=nullptr;}
    State=PursuitRecoveryState;VoiceUntil=RecoveryVoiceRemaining>0?Clock()+RecoveryVoiceRemaining:-1;MirrorUntil=RecoveryMirrorRemaining>0?Clock()+RecoveryMirrorRemaining:-1;
    Cooldowns.Empty();for(const auto& Pair:RecoveryCooldownRemaining)Cooldowns.Add(Pair.Key,Clock()+Pair.Value);
    if(AAnansePlayer* Player=Cast<AAnansePlayer>(GetOwner()))Player->ResetTransientMotion();
    if(ACharacter* Character=Cast<ACharacter>(GetOwner())){Character->GetCharacterMovement()->StopMovementImmediately();Character->GetCharacterMovement()->SetMovementMode(MOVE_Walking);}
    // The technical intro has already presented; restarting the played chase does not award it twice.
    return StartPursuit();
}
void UAnanseMission::EndPlay(const EEndPlayReason::Type Reason)
{
    if(EscapeMarker){EscapeMarker->Destroy();EscapeMarker=nullptr;}
    if(SanctuaryGate){SanctuaryGate->Destroy();SanctuaryGate=nullptr;}
    CancelCinematic();if(Pursuer){Pursuer->Destroy();Pursuer=nullptr;}if(RetryMarker){RetryMarker->Destroy();RetryMarker=nullptr;}Super::EndPlay(Reason);
}

void UAnanseMission::RestoreEpisodePresentation()
{
    if(SanctuaryGate){SanctuaryGate->Destroy();SanctuaryGate=nullptr;}
    if(!State.bEpisodeSession || State.ProductionBeat!=TEXT("sanctuary_pending") || !GetWorld() || CheckpointMap(GetWorld())!=MarketMap())return;
    FActorSpawnParameters Spawn;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    SanctuaryGate=GetWorld()->SpawnActor<AAnanseInteractable>(AAnanseInteractable::StaticClass(),FVector(1800,700,60),FRotator::ZeroRotator,Spawn);
    if(SanctuaryGate){SanctuaryGate->Configure(TEXT("sanctuary"),TEXT("E: follow the Story Road to Ananse / technical epilogue"));SanctuaryGate->Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
}

bool UAnanseMission::TravelToSanctuary(const FString& SlotName)
{
    if(!State.bEpisodeSession || State.ProductionBeat!=TEXT("sanctuary_pending") || !GetWorld() || CheckpointMap(GetWorld())!=MarketMap())return false;
    if(!FPackageName::DoesPackageExist(SanctuaryMap())){Message(TEXT("Sanctuary map is not available in this build; checkpoint retained."));return false;}
    if(!SaveLocal(SlotName))return false;
    UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(SlotName,0));
    if(!Save || Save->SchemaVersion!=4)return false;
    // The saved destination is durable before travel. Continue can recover after
    // a process interruption; no actor pointers or planted-foot targets cross maps.
    Save->MapIdentity=SanctuaryMap();Save->Position=FVector(-400,-350,110);Save->Rotation=FRotator::ZeroRotator;
    Save->State.ProductionBeat=TEXT("sanctuary");Save->bHasPursuitRecovery=false;
    Save->VoiceRemaining=0;Save->MirrorRemaining=0;Save->CooldownRemaining.Empty();
    if(!UGameplayStatics::SaveGameToSlot(Save,SlotName,0)){Message(TEXT("Destination checkpoint failed; travel cancelled."));return false;}
    CancelCinematic();UGameplayStatics::OpenLevel(this,FName(*SanctuaryMap()),true,TEXT("AnanseContinueSlot=")+SlotName);return true;
}

bool UAnanseMission::PresentEpilogueLine()
{
    if(!State.bEpisodeSession || !GetWorld() || CheckpointMap(GetWorld())!=SanctuaryMap() || State.ProductionBeat!=TEXT("sanctuary"))return false;
    const FName Ids[]={TEXT("MSN_FOREST_010"),TEXT("MSN_FOREST_020"),TEXT("MSN_FOREST_030")};
    TMap<FName,FAnanseDialogueLine> Lines;FString Error;
    if(!AnanseDialogue::Load(Lines,Error)){Message(Error);return false;}
    for(FName Id:Ids)if(!Lines.Contains(Id)){Message(TEXT("Epilogue dialogue missing; no event consumed."));return false;}
    for(FName Id:Ids)
    {
        if(State.CompletedPresentationEvents.Contains(Id))continue;
        const FAnanseDialogueLine& Line=Lines.FindChecked(Id);
        ActiveDialogueId=Id;ActiveDialogueSpeaker=Line.Speaker;ActiveDialogueText=Line.Text;
        State.CompletedPresentationEvents.Add(Id);
        if(Id==TEXT("MSN_FOREST_030"))State.ProductionBeat=TEXT("episode_complete");
        Message(Line.Speaker+TEXT(": ")+Line.Text);
        return true;
    }
    return false;
}

void UAnanseMission::EnsureEscapeMarker()
{
    if(!GetWorld() || IsValid(EscapeMarker))return;
    FActorSpawnParameters Spawn;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    EscapeMarker=GetWorld()->SpawnActor<AAnanseInteractable>(AAnanseInteractable::StaticClass(),FVector(1300,350,60),FRotator::ZeroRotator,Spawn);
    if(EscapeMarker)
    {
        EscapeMarker->Configure(TEXT("escape"),TEXT("E: leave pursuit, then choose the ledger's fate"));
        EscapeMarker->Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }
}

void UAnanseMission::EnsureRetryMarker()
{
    if(!GetWorld() || !GetOwner())return;
    if(IsValid(RetryMarker))RetryMarker->Destroy();RetryMarker=nullptr;
    FActorSpawnParameters Spawn;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    RetryMarker=GetWorld()->SpawnActor<AAnanseInteractable>(AAnanseInteractable::StaticClass(),GetOwner()->GetActorLocation()+FVector(100,0,0),FRotator::ZeroRotator,Spawn);
    if(RetryMarker){RetryMarker->Configure(TEXT("retry"),TEXT("E: retry Osebo pursuit"));RetryMarker->Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
}
