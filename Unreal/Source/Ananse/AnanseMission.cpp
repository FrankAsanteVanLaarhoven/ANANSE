#include "AnanseMission.h"
#include "AnanseCatalogue.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"

UAnanseMission::UAnanseMission(){ PrimaryComponentTick.bCanEverTick=false; }
float UAnanseMission::Clock() const { return GetWorld()?GetWorld()->GetTimeSeconds():0.f; }
void UAnanseMission::Message(const FString& Text){ LatestMessage=Text;Changed.Broadcast(); }
void UAnanseMission::AddSuspicion(float Amount)
{
    if(!State.Outcome.IsNone()) return;
    State.Suspicion=FMath::Clamp(State.Suspicion+FMath::Max(0.f,Amount),0.f,100.f);
    if(State.Suspicion>=100.f){State.Outcome=TEXT("detained");Message(TEXT("Detained. Your cover failed. Load a prior local save or restart the level."));}
    Changed.Broadcast();
}
bool UAnanseMission::Act(FName Action)
{
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
        State.bLedger=true;Message(TEXT("The ledger proves the forgery but names vulnerable witnesses. Choose exposure or protection."));return true;
    }
    if(Action==TEXT("expose") || Action==TEXT("protect"))
    {
        if(!State.bLedger){Message(TEXT("Recover the ledger before choosing its fate."));return false;}
        if(Action==TEXT("expose"))
        {
            if(!State.bEvidence){Message(TEXT("Public exposure needs corroborating evidence from the altered edict."));return false;}
            State.Outcome=TEXT("truth-exposed");State.CourtTrust-=2;State.MarketTrust+=State.bPermit?-2:1;
            Message(State.bPermit?TEXT("The forgery is exposed, but you broke your promise and endangered the witnesses."):TEXT("The forgery is exposed. Its witnesses are now vulnerable to retaliation."));
        }
        else {State.Outcome=TEXT("witnesses-protected");State.MarketTrust+=2;Message(TEXT("The witnesses are protected. The court's authorised history remains uncorrected."));}
        return true;
    }
    Message(TEXT("Unknown interaction."));return false;
}
bool UAnanseMission::CommitPower(FName Power)
{
    if(!State.Outcome.IsNone() || State.Thread<1){Message(TEXT("No story-thread remains, or the run has ended."));return false;}
    if(Cooldowns.FindRef(Power)>Clock()){Message(TEXT("That power is cooling down."));return false;}
    if(Power==TEXT("borrowed-voice") && !State.bLearnedVoice){Message(TEXT("First listen to the captain's authorised call."));return false;}
    if(Power!=TEXT("web-step") && Power!=TEXT("borrowed-voice") && Power!=TEXT("trick-mirror")){Message(TEXT("Unknown power."));return false;}
    State.Thread--;Cooldowns.Add(Power,Clock()+4.f);
    if(Power==TEXT("borrowed-voice")){VoiceUntil=Clock()+12.f;AddSuspicion(8.f);Message(TEXT("This checkpoint accepts the voice for 12 seconds; this is not global disguise immunity."));}
    if(Power==TEXT("trick-mirror")){MirrorUntil=Clock()+8.f;Message(TEXT("The archive watcher is distracted for eight seconds."));}
    if(Power==TEXT("web-step")){State.bOnRooftop=true;AddSuspicion(10.f);Message(TEXT("Web Step consumed one thread. The archive watcher still needs distracting."));}
    Changed.Broadcast();return true;
}
bool UAnanseMission::SaveLocal()
{
    if(!GetWorld() || !GetOwner())return false;
    UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::CreateSaveGameObject(UAnanseSave::StaticClass()));
    if(!Save)return false;
    if(const UAnanseCatalogue* C=GetWorld()->GetGameInstance()->GetSubsystem<UAnanseCatalogue>())Save->ContentHash=C->ContentHash;
    Save->State=State;Save->Position=GetOwner()->GetActorLocation();Save->Rotation=GetOwner()->GetActorRotation();
    Save->VoiceRemaining=FMath::Max(0.f,VoiceUntil-Clock());Save->MirrorRemaining=FMath::Max(0.f,MirrorUntil-Clock());
    for(const auto& C:Cooldowns)Save->CooldownRemaining.Add(C.Key,FMath::Max(0.f,C.Value-Clock()));
    const bool bSaved=UGameplayStatics::SaveGameToSlot(Save,TEXT("AnansePrototype"),0);Message(bSaved?TEXT("Local prototype checkpoint saved."):TEXT("Local save failed."));return bSaved;
}
bool UAnanseMission::LoadLocal()
{
    if(!GetWorld() || !GetOwner())return false;
    const UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(TEXT("AnansePrototype"),0));
    if(!Save || Save->SchemaVersion!=1){Message(TEXT("No compatible local checkpoint exists."));return false;}
    const UAnanseCatalogue* C=GetWorld()->GetGameInstance()->GetSubsystem<UAnanseCatalogue>();
    if(!C || C->ContentHash.IsEmpty() || C->ContentHash!=Save->ContentHash){Message(TEXT("Checkpoint uses another content revision. Migration is required; the save was not overwritten."));return false;}
    if(!GetOwner()->TeleportTo(Save->Position,Save->Rotation,false,false)){Message(TEXT("Checkpoint location is blocked; load cancelled."));return false;}
    State=Save->State;VoiceUntil=Save->VoiceRemaining>0.f?Clock()+Save->VoiceRemaining:-1.f;MirrorUntil=Save->MirrorRemaining>0.f?Clock()+Save->MirrorRemaining:-1.f;
    Cooldowns.Empty();for(const auto& Pair:Save->CooldownRemaining)Cooldowns.Add(Pair.Key,Clock()+Pair.Value);
    if(ACharacter* Character=Cast<ACharacter>(GetOwner())){Character->GetCharacterMovement()->StopMovementImmediately();Character->GetCharacterMovement()->SetMovementMode(MOVE_Walking);}
    Message(TEXT("Local checkpoint restored. This is not a cloud or authoritative multiplayer save."));return true;
}
