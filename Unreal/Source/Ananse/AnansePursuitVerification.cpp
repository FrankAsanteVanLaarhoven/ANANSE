#include "AnansePursuitVerification.h"
#if !UE_BUILD_SHIPPING
#include "AnansePlayer.h"
#include "AnanseCastLab.h"
#include "AnanseMission.h"
#include "AnanseWorld.h"
#include "AnansePursuit.h"
#include "AnanseCinematic.h"
#include "AnanseSpiderLab.h"
#include "AnanseGroundContact.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Animation/AnimInstance.h"
#include "Components/StaticMeshComponent.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "EngineUtils.h"
#include "Dom/JsonObject.h"
#include "InputCoreTypes.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "GenericPlatform/GenericPlatformInputDeviceMapper.h"
#include "UObject/StrongObjectPtr.h"
namespace
{
struct FRun
{
    int32 Phase=0,Captures=0,Detour=0,EscapeWaypoint=0,EscapeLoopWaypoint=0,DialogueLines=0,RouteInputPhase=0;double Active=0,PhaseStart=0,KeyStart=0;bool KeyHeld=false,Done=false,EscapeMirror=false,ReloadVerified=false,PostOutcomeWalkStarted=false,DialogueVerified=false,EscapeGateVerified=false;
    FKey HeldKey;FString Failure;TArray<TSharedPtr<FJsonValue>> Checks;
    TWeakObjectPtr<AActor> Obstacle;FVector Knowledge,BeforeOcclusion,OcclusionDestination;
    TWeakObjectPtr<AAnanseSpiderLabPlayer> Companion;int32 CompanionWaypoint=0,MixedPlayerWaypoint=0,MixedMetricsSamples=0,MixedProgressChecks=0;
    double CompanionSpawnTime=0,MixedWalkDistance=0,CompanionWalkDistance=0,CompanionProgressStart=0,LastMixedMetrics=0;
    FVector PreviousMixedPlayer,PreviousCompanion,CompanionProgressPosition;
    double OcclusionWithinCaptureSeconds=0;float OcclusionMinimumRange=TNumericLimits<float>::Max();
    TStrongObjectPtr<UAnanseSave> Expected;
    bool TravelRequested=false,TravelArrived=false,BeforeChoiceSaved=false;int32 EpilogueLines=0;
    FAnanseMissionState BeforeTravel;
};
FRun R;
uint32 AsoObserved=0;
void Key(APlayerController* PC,FKey K,bool Press){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Press?IE_Pressed:IE_Released,Press?1.f:0.f,-1,IPlatformInputDeviceMapper::Get().GetDefaultInputDevice()));}
void StopWalk(APlayerController* PC){Key(PC,EKeys::W,false);}
bool Press(APlayerController* PC,FKey K)
{
    if(!R.KeyHeld){R.HeldKey=K;R.KeyHeld=true;R.KeyStart=R.Active;Key(PC,K,true);return false;}
    if(R.Active-R.KeyStart<.25)return false;
    Key(PC,R.HeldKey,false);R.KeyHeld=false;return true;
}
bool Walk(AAnansePlayer* P,APlayerController* PC,FVector Destination,float Radius=20)
{
    const FVector Delta=Destination-P->GetActorLocation();
    if(Delta.SizeSquared2D()<FMath::Square(Radius)){StopWalk(PC);return true;}
    PC->SetControlRotation(FRotator(0,FMath::RadiansToDegrees(FMath::Atan2(Delta.Y,Delta.X)),0));Key(PC,EKeys::W,true);return false;
}
void Next(){R.Phase++;R.PhaseStart=R.Active;}
bool Check(bool Pass,const FString& Label)
{
    if(!Pass){R.Failure=Label;R.Done=true;return false;}
    R.Checks.Add(MakeShared<FJsonValueString>(Label));return true;
}
int32 PursuerCount(UWorld* World){int32 Count=0;for(TActorIterator<AAnansePursuit> It(World);It;++It)if(IsValid(*It))Count++;return Count;}
void Cleanup(APlayerController* PC)
{
    StopWalk(PC);if(R.KeyHeld){Key(PC,R.HeldKey,false);R.KeyHeld=false;}
    if(R.Obstacle.IsValid())R.Obstacle->Destroy();R.Obstacle.Reset();
    if(R.Companion.IsValid())R.Companion->Destroy();R.Companion.Reset();
}
}
bool IsExpectedEpisodeTravelPawn(AAnansePlayer* P)
{
    return R.TravelRequested && !R.TravelArrived && P && P->CharacterId==TEXT("kwaku") && P->IsNativePlayReady() &&
        UWorld::RemovePIEPrefix(P->GetWorld()->GetOutermost()->GetName())==UAnanseMission::SanctuaryMap();
}
void TickPursuitVerification(AAnansePlayer* P,float DeltaSeconds,double RequiredSeconds,bool& Finished,FString& Error,TSharedPtr<FJsonObject> Report,FString Out,FString Slot,bool Reload,bool EpisodeReload)
{
    Finished=false;Error.Reset();if(!P || !P->Mission)return;
    APlayerController* PC=Cast<APlayerController>(P->GetController());if(!PC)return;
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAcceptedVisuals")))
    {
        auto* Hero=Cast<AAnanseCastLabPlayer>(P);
        const bool Bound=Hero && Hero->CharacterId==TEXT("kwaku") && !Hero->bLabSelectionPawn && Hero->bStoryCampaignPresentation && Hero->GetMesh()->GetSkeletalMeshAsset() && Hero->GetMesh()->GetSkeletalMeshAsset()->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku") && Hero->GetMesh()->GetAnimInstance();
        Report->SetBoolField(TEXT("accepted_campaign_appearance"),Bound);
        Report->SetStringField(TEXT("accepted_campaign_mesh"),P->GetMesh()->GetSkeletalMeshAsset()?P->GetMesh()->GetSkeletalMeshAsset()->GetPathName():TEXT("None"));
        Report->SetStringField(TEXT("accepted_campaign_pawn"),P->GetClass()->GetPathName());
        if(!Bound){Finished=true;Error=TEXT("Accepted campaign appearance missing; old mesh or lab-only pawn cannot satisfy this run");return;}
    }
    UAnanseMission* M=P->Mission;R.Active+=DeltaSeconds;
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoReview")))
    {
        for(TActorIterator<AAnanseInteractable> It(P->GetWorld());It;++It)if(It->bNegotiationPresentation&&It->CharacterId==TEXT("aso-yaa"))
        {
            const auto* Skin=It->CharacterVisual->GetSkeletalMeshAsset();
            if(Skin&&(Skin->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v001/AsoYaa.AsoYaa")||Skin->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v002/AsoYaa.AsoYaa")||Skin->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v001/AsoYaa.AsoYaa")||Skin->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa"))&&It->CharacterVisual->IsPlaying()&&It->NegotiationPose>=0&&It->NegotiationPose<16)AsoObserved|=(1u<<It->NegotiationPose);
        }
        Report->SetNumberField(TEXT("aso_observed_pose_mask"),AsoObserved);
    }
    Report->SetNumberField(TEXT("pursuit_phase"),R.Phase);Report->SetNumberField(TEXT("pursuit_capture_retry_cycles"),R.Captures);Report->SetArrayField(TEXT("pursuit_checks"),R.Checks);
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseFormsScenery")) && !EpisodeReload && !Report->HasField(TEXT("authored_interactable_count")))
    {
        int32 Count=0,Ready=0,Characters=0;TArray<TSharedPtr<FJsonValue>> Bindings;
        for(TActorIterator<AAnanseInteractable> It(P->GetWorld());It;++It)
        {
            ++Count;const auto* A=*It;const bool Prop=A->PropVisual->GetStaticMesh()!=nullptr;
            const bool Character=A->CharacterVisual->GetSkeletalMeshAsset() && A->CharacterVisual->IsVisible() && A->CharacterVisual->IsPlaying();
            if(Character)++Characters;
            if((Prop||Character) && !A->Mesh->IsVisible() && A->Mesh->GetCollisionEnabled()!=ECollisionEnabled::NoCollision && A->PropVisual->GetCollisionEnabled()==ECollisionEnabled::NoCollision && A->CharacterVisual->GetCollisionEnabled()==ECollisionEnabled::NoCollision)++Ready;
            auto B=MakeShared<FJsonObject>();B->SetStringField(TEXT("action"),A->Action.ToString());B->SetStringField(TEXT("identity"),A->CharacterId.ToString());B->SetStringField(TEXT("visual"),Character?A->CharacterVisual->GetSkeletalMeshAsset()->GetPathName():Prop?A->PropVisual->GetStaticMesh()->GetPathName():TEXT("missing"));Bindings.Add(MakeShared<FJsonValueObject>(B));
        }
        Report->SetNumberField(TEXT("authored_interactable_count"),Count);Report->SetNumberField(TEXT("authored_interactable_ready"),Ready);Report->SetNumberField(TEXT("authored_npc_idle_playing"),Characters);Report->SetArrayField(TEXT("authored_interactable_bindings"),Bindings);
        if(!Check(Count==8 && Ready==8 && Characters==2,TEXT("Actual authored props/two human idle bindings; Osebo exists only as the pursuer replace eight markers; original collision roots retained")))return;
    }
    if(M->Pursuer){Report->SetStringField(TEXT("pursuit_behaviour"),M->Pursuer->Behaviour.ToString());Report->SetBoolField(TEXT("pursuit_nav_available"),M->Pursuer->bNavigationAvailable);Report->SetStringField(TEXT("pursuer_position"),M->Pursuer->GetActorLocation().ToString());Report->SetStringField(TEXT("pursuer_last_known"),M->Pursuer->LastKnownLocation.ToString());}
    if(R.Active>FMath::Max(600.0,RequiredSeconds+60.0) || (R.Active-R.PhaseStart>50 && (EpisodeReload?R.Phase<2:(Reload && !R.ReloadVerified?R.Phase<2:R.Phase<18)))){R.Failure=FString::Printf(TEXT("Bounded pursuit readiness timeout phase %d; feedback %s"),R.Phase,*M->LatestMessage);R.Done=true;}
    if(R.Done){if(R.Failure.IsEmpty()&&!Reload&&!EpisodeReload&&FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoReview"))&&M->State.Route==TEXT("negotiation")){const uint32 Required=(1u<<4)|(1u<<8)|(1u<<(M->State.Outcome==TEXT("truth-exposed")?11:10));if((AsoObserved&Required)!=Required)R.Failure=TEXT("Aso actual evidence/agreement/consequence presentation not observed");}Cleanup(PC);Finished=true;Error=R.Failure;return;}
    if(EpisodeReload)
    {
        if(R.Phase==0)
        {
            UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));
            if(!Check(Save && Save->SchemaVersion==4 && Save->State.bEpisodeSession && Save->MapIdentity==UWorld::RemovePIEPrefix(P->GetWorld()->GetOutermost()->GetName()),TEXT("Separate process opens the recorded episode checkpoint map")))return;
            R.Expected.Reset(Save);Next();return;
        }
        if(R.Phase==1)
        {
            if(!Report->HasField(TEXT("episode_reload_input_dispatched")))
            {
                if(R.Active-R.PhaseStart<2.f || !P->GetCharacterMovement()->IsMovingOnGround())return;
                if(!Press(PC,EKeys::F9))return;
                Report->SetBoolField(TEXT("episode_reload_input_dispatched"),true);return;
            }
            const FAnanseMissionState& S=R.Expected->State;
            Report->SetStringField(TEXT("episode_reload_feedback"),M->LatestMessage);
            Report->SetStringField(TEXT("episode_expected_position"),R.Expected->Position.ToString());
            FHitResult SavedHit;FCollisionQueryParams SavedQuery(SCENE_QUERY_STAT(AnanseSavedPoseAudit),false,P);
            const auto* Capsule=P->GetCapsuleComponent();Report->SetNumberField("episode_capsule_half_height",Capsule->GetScaledCapsuleHalfHeight());Report->SetNumberField("episode_capsule_radius",Capsule->GetScaledCapsuleRadius());
            const bool SavedBlocked=P->GetWorld()->SweepSingleByChannel(SavedHit,R.Expected->Position,R.Expected->Position+FVector(0,0,.01),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()),SavedQuery);
            Report->SetStringField("episode_root_bound_offset",(Capsule->Bounds.Origin-P->GetActorLocation()).ToString());
            Report->SetStringField("episode_updated_primitive",GetNameSafe(P->GetCharacterMovement()->UpdatedPrimitive));
            FVector Proposed;Report->SetBoolField("episode_encroaching",P->GetWorld()->EncroachingBlockingGeometry(P,R.Expected->Position,R.Expected->Rotation,&Proposed));Report->SetStringField("episode_encroachment_adjustment",Proposed.ToString());
            TArray<FOverlapResult> Overlaps;FCollisionResponseParams Response;FCollisionQueryParams Query(SCENE_QUERY_STAT(AnanseSavedOverlapAudit),false,P);Capsule->InitSweepCollisionParams(Query,Response);
            P->GetWorld()->OverlapMultiByChannel(Overlaps,R.Expected->Position,R.Expected->Rotation.Quaternion(),Capsule->GetCollisionObjectType(),Capsule->GetCollisionShape(),Query,Response);
            TArray<TSharedPtr<FJsonValue>> Blockers;for(const auto& Hit:Overlaps)if(Hit.bBlockingHit)Blockers.Add(MakeShared<FJsonValueString>(GetNameSafe(Hit.GetActor())+TEXT("/")+GetNameSafe(Hit.GetComponent())));Report->SetArrayField("episode_overlap_blockers",Blockers);
            Report->SetBoolField(TEXT("episode_saved_pose_blocked"),SavedBlocked);Report->SetStringField(TEXT("episode_saved_pose_blocker"),GetNameSafe(SavedHit.GetActor()));
            if(auto* Static=Cast<AStaticMeshActor>(SavedHit.GetActor()))if(UStaticMesh* Mesh=Static->GetStaticMeshComponent()->GetStaticMesh())Report->SetStringField(TEXT("episode_saved_pose_blocker_mesh"),Mesh->GetPathName());
            Report->SetStringField(TEXT("episode_expected_route"),S.Route.ToString());
            Report->SetStringField(TEXT("episode_actual_route"),M->State.Route.ToString());
            if((M->State.Route!=S.Route || M->State.Outcome!=S.Outcome || M->State.ProductionBeat!=S.ProductionBeat) && R.Active-R.PhaseStart<3.f)return;
            if(!Check(M->State.bEpisodeSession && M->State.Route==S.Route && M->State.Outcome==S.Outcome && M->State.ProductionBeat==S.ProductionBeat && M->State.CompletedPresentationEvents==S.CompletedPresentationEvents && M->State.Thread==S.Thread && M->State.MarketTrust==S.MarketTrust && M->State.CourtTrust==S.CourtTrust && M->State.bLedger==S.bLedger && M->State.bEvidence==S.bEvidence && M->State.bPermit==S.bPermit && M->State.bPursuitEscaped==S.bPursuitEscaped,TEXT("Cross-process F9 restores declared episode fields and consumed dialogue IDs")))return;
            if(!Check(FVector::Dist(P->GetActorLocation(),R.Expected->Position)<5 && !M->Pursuer && !M->State.bCaptured && !PC->IsMoveInputIgnored(),TEXT("Restart preserves checkpoint position, control and absence of transient chase actor")))return;
            Report->SetStringField(TEXT("episode_reload_beat"),S.ProductionBeat.ToString());
            Report->SetStringField(TEXT("episode_reload_outcome"),S.Outcome.ToString());Next();return;
        }
        if(R.Active>=RequiredSeconds)
        {
            if(Check(M->State.CompletedPresentationEvents==R.Expected->State.CompletedPresentationEvents && M->State.Outcome==R.Expected->State.Outcome,TEXT("Idle restart does not repeat durable dialogue or consequences")))R.Done=true;
        }
        return;
    }
    if(Reload && !R.ReloadVerified)
    {
        if(R.Phase==0)
        {
            UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));if(!Check(Save && Save->SchemaVersion==3 && Save->State.bPursuitStarted && !Save->State.bCaptured,TEXT("Actual schema3 active-chase checkpoint exists")))return;
            R.Expected.Reset(Save);Key(PC,EKeys::F9,true);
            // InputKey dispatch can apply during the following player-input tick; compare on readiness,
            // with declared bounded timer tolerance rather than calling LoadLocal directly.
            Next();return;
        }
        if(R.Phase==1)
        {
            if(!M->State.bPursuitStarted)return;
            Key(PC,EKeys::F9,false);const UAnanseSave* Save=R.Expected.Get();
            if(!Check(M->State.Route==Save->State.Route && M->State.bLedger==Save->State.bLedger && M->State.Thread==Save->State.Thread && M->State.Outcome==Save->State.Outcome && M->State.ProductionBeat==Save->State.ProductionBeat && M->State.CompletedPresentationEvents==Save->State.CompletedPresentationEvents,TEXT("Restart restores documented chase mission fields and presentation IDs")))return;
            if(!Check(M->bHasPursuitRecovery && M->PursuitRecoveryPosition.Equals(Save->PursuitRecoveryPosition,.05) && M->PursuitRecoveryState.Route==Save->PursuitRecoveryState.Route && M->PursuitRecoveryState.bLedger==Save->PursuitRecoveryState.bLedger,TEXT("Restart restores pre-chase retry checkpoint")))return;
            if(!Check(P->GetActorLocation().Equals(Save->Position,2.0) && FMath::Abs(M->State.PursuitSeconds-Save->State.PursuitSeconds)<.35 && M->Pursuer && PursuerCount(P->GetWorld())==1,TEXT("Restart restores position elapsed chase time and one real pursuer")))return;
            const float Voice=FMath::Max(0.f,M->VoiceUntil-M->Clock()),Mirror=FMath::Max(0.f,M->MirrorUntil-M->Clock());
            bool Timers=FMath::Abs(Voice-Save->VoiceRemaining)<.35 && FMath::Abs(Mirror-Save->MirrorRemaining)<.35;
            for(const auto& Pair:Save->CooldownRemaining)Timers=Timers && FMath::Abs(FMath::Max(0.f,M->Cooldowns.FindRef(Pair.Key)-M->Clock())-Pair.Value)<.35;
            if(!Check(Timers && M->RecoveryVoiceRemaining==Save->RecoveryVoiceRemaining && M->RecoveryMirrorRemaining==Save->RecoveryMirrorRemaining && M->RecoveryCooldownRemaining.OrderIndependentCompareEqual(Save->RecoveryCooldownRemaining),TEXT("Restart restores relative ability and pre-chase recovery timers (0.35s live-tick tolerance)")))return;
            if(!Check(M->Pursuer->LastKnownLocation.Equals(Save->State.PursuerLastKnown,.05) && FMath::Abs(M->State.PursuitLostSightSeconds-Save->State.PursuitLostSightSeconds)<.35,TEXT("Restart restores cached knowledge and bounded search elapsed state")))return;
            Report->SetStringField(TEXT("pursuit_reload_slot"),Slot);
            // After field comparison, play capture/retry/escape in this new process.
            // An idle loaded scene alone does not establish recovered controls.
            R.ReloadVerified=true;R.Phase=11;R.PhaseStart=R.Active;return;
        }
        return;
    }
    Report->SetStringField(TEXT("pursuit_player_position"),P->GetActorLocation().ToString());
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseStoryPresentation")) && M->Pursuer && !Report->HasField(TEXT("staging_human_pursuer_checked")))
    {
        auto* Mesh=M->Pursuer->GetMesh()->GetSkeletalMeshAsset();auto* Anim=M->Pursuer->GetMesh()->GetAnimInstance();
        const bool Bound=Mesh && Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboHuman/Story_v001/OseboHuman.OseboHuman") && Anim && Anim->GetClass()->GetPathName()==TEXT("/Game/Ananse/Characters/OseboHuman/Story_v001/ABP_OseboHuman.ABP_OseboHuman_C") && M->Pursuer->GetMesh()->IsVisible() && !M->Pursuer->ProxyBody->IsVisible();
        Report->SetBoolField(TEXT("staging_human_pursuer_checked"),true);Report->SetBoolField(TEXT("staging_human_pursuer_bound"),Bound);
        Report->SetStringField(TEXT("staging_pursuer_mesh"),Mesh?Mesh->GetPathName():TEXT("missing"));Report->SetStringField(TEXT("staging_pursuer_animation"),Anim?Anim->GetClass()->GetPathName():TEXT("missing"));
        if(!Check(Bound,TEXT("Existing Osebo pursuit owns actual human mesh/independent graph; primitive hidden")))return;
    }
    switch(R.Phase)
    {
    case 0:if(!Check(!UGameplayStatics::DoesSaveGameExist(Slot,0),TEXT("Dedicated chase slot absent before save; prior checkpoints protected")))return;
        if(!Check(M->State.bProductionPursuit || M->EnableProductionPursuit(),TEXT("Production pursuit explicitly enabled")))return;Next();return;
    case 1:if(Walk(P,PC,FVector(-800,-350,P->GetActorLocation().Z)))Next();return;
    case 2:if(Press(PC,EKeys::E)){if(Check(M->State.bEvidence,TEXT("Actual E interaction obtains evidence")))Next();}return;
    case 3:
        {
            FString Route=TEXT("negotiation");FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyRoute="),Route);
            const FVector Target=Route==TEXT("social")?FVector(-500,0,P->GetActorLocation().Z):Route==TEXT("rooftop")?FVector(-150,50,P->GetActorLocation().Z):FVector(-100,-200,P->GetActorLocation().Z);
            if(Walk(P,PC,Target))Next();return;
        }
    case 4:
        {
            FString Route=TEXT("negotiation");FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyRoute="),Route);
            if(Route==TEXT("social"))
            {
                if(R.RouteInputPhase==0){if(Press(PC,EKeys::E)){if(Check(M->State.bLearnedVoice,TEXT("Actual captain interaction learns authorized call")))R.RouteInputPhase++;}return;}
                if(Press(PC,EKeys::Two)){if(Check(M->VoiceActive() && M->State.Thread==2,TEXT("Permitted actual Borrowed Voice activates and charges thread")))Next();}return;
            }
            if(Route==TEXT("rooftop"))
            {
                if(R.RouteInputPhase==0){if(Press(PC,EKeys::One)){if(Check(P->IsWebFlying() && M->State.Thread==2,TEXT("Permitted actual Web Step starts validated roof traversal")))R.RouteInputPhase++;}return;}
                if(P->IsWebFlying() || !P->GetCharacterMovement()->IsMovingOnGround())return;
                if(!Check(M->State.bOnRooftop && P->GetActorLocation().Z>300,TEXT("Actual Web Step lands on the roof")))return;
                if(Press(PC,EKeys::Three)){if(Check(M->MirrorActive() && M->State.Thread==1,TEXT("Actual Mirror distracts roof watcher with remaining thread")))Next();}return;
            }
            if(Press(PC,EKeys::E)){if(Check(M->State.bPermit,TEXT("Actual E interaction negotiates permit")))Next();}return;
        }
    case 5:
        {
            FString Route=TEXT("negotiation");FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyRoute="),Route);
            if(Walk(P,PC,Route==TEXT("rooftop")?FVector(100,650,P->GetActorLocation().Z):FVector(500,250,P->GetActorLocation().Z)))Next();return;
        }
    case 6:
        {
            FString Route=TEXT("negotiation");FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyRoute="),Route);
            if(Press(PC,EKeys::E)){if(Check(M->State.bArchive && M->State.Route==FName(*Route),TEXT("Actual route prerequisites and archive interaction grant requested infiltration")))Next();}return;
        }
    case 7:
        {
        FString Route=TEXT("negotiation");FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyRoute="),Route);
        if(Route==TEXT("rooftop") && R.Detour<3)
        {
            const FVector2D RoofDetour[]={FVector2D(500,650),FVector2D(500,100),FVector2D(850,100)};
            const FVector2D D=RoofDetour[R.Detour];if(Walk(P,PC,FVector(D.X,D.Y,P->GetActorLocation().Z)))R.Detour++;return;
        }
        if(R.Detour<2){const FVector2D D[2]={FVector2D(500,100),FVector2D(850,100)};if(Walk(P,PC,FVector(D[R.Detour].X,D[R.Detour].Y,P->GetActorLocation().Z)))R.Detour++;return;}
        if(Walk(P,PC,FVector(850,250,P->GetActorLocation().Z)))Next();return;
        }
    case 8:if(Press(PC,EKeys::E)){if(Check(M->State.bLedger && M->Cinematic && M->Cinematic->bActive,TEXT("Ledger starts bound real technical pursuit intro")))Next();}return;
    case 9:if(Press(PC,EKeys::Escape)){if(Check(M->State.bPursuitStarted && M->Pursuer && !M->Cinematic->bActive && !PC->IsMoveInputIgnored(),TEXT("Actual Escape skip hands control to played pursuit")))Next();}return;
    case 10:if(Press(PC,EKeys::F5))
        {
            UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));
            if(!Check(Save && Save->State.bPursuitStarted && Save->bHasPursuitRecovery,TEXT("F5 creates dedicated actual active-chase checkpoint")))return;
            R.Expected.Reset(Save);Report->SetStringField(TEXT("pursuit_saved_slot"),Slot);Next();
        }return;
    case 11:
        {
            if(!Check(!M->StartPursuit() && PursuerCount(P->GetWorld())==1,TEXT("Repeated chase entry cannot duplicate Osebo")))return;
            const FVector A=M->Pursuer->GetActorLocation(),B=P->GetActorLocation();
            FActorSpawnParameters Spawn;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
            AActor* Wall=P->GetWorld()->SpawnActor<AActor>(AActor::StaticClass(),(A+B)*.5,FRotator::ZeroRotator,Spawn);
            UBoxComponent* Box=NewObject<UBoxComponent>(Wall);Wall->SetRootComponent(Box);Box->SetBoxExtent(FVector(1,650,220));Box->SetCollisionProfileName(TEXT("BlockAll"));Box->RegisterComponent();Wall->SetActorLocation((A+B)*.5);Wall->SetActorRotation((B-A).Rotation());
            R.Obstacle=Wall;R.Knowledge=M->Pursuer->LastKnownLocation;R.BeforeOcclusion=P->GetActorLocation();
            const FVector Normal=(B-A).GetSafeNormal2D();
            R.OcclusionDestination=(A+B)*.5+Normal*(P->GetCapsuleComponent()->GetScaledCapsuleRadius()+3.f)+Normal.RotateAngleAxis(90,FVector::UpVector)*40.f;
            R.OcclusionDestination.Z=P->GetActorLocation().Z;R.OcclusionWithinCaptureSeconds=0;Next();return;
        }
    case 12:
        {
            if(M->State.bCaptured){Check(false,TEXT("Occluding collision fixture must block capture"));return;}
            Walk(P,PC,R.OcclusionDestination,3);
            const float Range=FVector::Dist(P->GetActorLocation(),M->Pursuer->GetActorLocation());
            FHitResult Sight;FCollisionQueryParams Query(SCENE_QUERY_STAT(AnanseVerifyOccludedCapture),false,M->Pursuer);
            const bool Hit=P->GetWorld()->LineTraceSingleByChannel(Sight,M->Pursuer->GetActorLocation()+FVector(0,0,65),P->GetActorLocation()+FVector(0,0,35),ECC_Visibility,Query);
            const bool BlockedByFixture=Hit && Sight.GetActor()==R.Obstacle.Get();
            if(BlockedByFixture)R.OcclusionMinimumRange=FMath::Min(R.OcclusionMinimumRange,Range);
            const bool Eligible=Range<100.f && BlockedByFixture && !M->Pursuer->HasVisibleTarget() && M->Pursuer->LastKnownLocation.Equals(R.Knowledge,2.0);
            R.OcclusionWithinCaptureSeconds=Eligible?R.OcclusionWithinCaptureSeconds+DeltaSeconds:0;
            Report->SetNumberField(TEXT("occluded_capture_minimum_center_range_cm"),R.OcclusionMinimumRange);
            Report->SetNumberField(TEXT("occluded_capture_current_center_range_cm"),Range);
            Report->SetNumberField(TEXT("occluded_capture_continuous_duration_seconds"),R.OcclusionWithinCaptureSeconds);
            Report->SetBoolField(TEXT("occluded_capture_fixture_blocks_actual_sight_ray"),BlockedByFixture);
            if(R.OcclusionWithinCaptureSeconds<.35)
            {
                if(R.Active-R.PhaseStart>10)Check(false,TEXT("Could not establish real occluded capture range <100cm continuously for >=0.35s"));
                return;
            }
            StopWalk(PC);
            if(!Check(!M->State.bCaptured && FVector::Dist2D(P->GetActorLocation(),R.BeforeOcclusion)>30,TEXT("Actual fixture blocks sight/capture below100cm for>=0.35s without hidden-target updates")))return;
            R.Obstacle->Destroy();R.Obstacle.Reset();Next();return;
        }
    case 13:
        if(M->State.bCaptured){StopWalk(PC);if(Check(M->State.Outcome.IsNone() && P->GetCharacterMovement()->MovementMode==MOVE_None,TEXT("Visible proximity causes real capture without consequence")))Next();return;}
        if(M->Pursuer)Walk(P,PC,M->Pursuer->GetActorLocation(),90);return;
    case 14:
        if(Press(PC,EKeys::E))
        {
            if(!Check(!M->State.bCaptured && M->State.bPursuitStarted && M->Pursuer && PursuerCount(P->GetWorld())==1 && P->GetCharacterMovement()->MovementMode==MOVE_Walking && !PC->IsMoveInputIgnored() && M->State.Outcome.IsNone(),TEXT("Actual retry interaction restores control state and one pursuer")))return;
            R.Captures++;Report->SetNumberField(TEXT("pursuit_capture_retry_cycles"),R.Captures);
            if(R.Captures<10){R.Phase=13;R.PhaseStart=R.Active;}else Next();
        }return;
    case 15:
        if(!R.EscapeMirror)
        {
            if(!Press(PC,EKeys::Three))return;
            if(!Check(M->MirrorActive() && IsValid(P->MirrorActor),TEXT("Actual permitted Mirror input produces the escape distraction")))return;
            R.EscapeMirror=true;
        }
        {
            if(M->State.bCaptured){Check(false,TEXT("Final played escape unexpectedly captured"));return;}
            const FVector2D Route[]={FVector2D(850,100),FVector2D(1300,100),FVector2D(1300,250),FVector2D(1300,350)};
            if(R.EscapeWaypoint<4)
            {
                const FVector2D Destination=Route[R.EscapeWaypoint];
                if(Walk(P,PC,FVector(Destination.X,Destination.Y,P->GetActorLocation().Z)))R.EscapeWaypoint++;
                return;
            }
            Next();return;
        }
    case 16:
        {
            if(M->State.bCaptured){Check(false,TEXT("Final played escape unexpectedly captured"));return;}
            if(!M->Pursuer){Check(false,TEXT("Played escape lost its actual pursuer"));return;}
            const FVector Gate(1300,350,P->GetActorLocation().Z);
            if(FVector::Dist2D(P->GetActorLocation(),Gate)<25 && M->Pursuer->CanEscape())
            {StopWalk(PC);Next();return;}
            // Keep moving through the escape lane while the real chase clock and
            // physical separation become eligible; never advance time or move actors directly.
            if(M->State.PursuitSeconds>=6.f && FVector::Dist2D(P->GetActorLocation(),M->Pursuer->GetActorLocation())>=450.f)
            {Walk(P,PC,Gate);return;}
            const FVector2D Loop[]={FVector2D(1300,250),FVector2D(1300,450),FVector2D(1450,450),FVector2D(1450,250)};
            const FVector2D Destination=Loop[R.EscapeLoopWaypoint%4];
            if(Walk(P,PC,FVector(Destination.X,Destination.Y,P->GetActorLocation().Z)))R.EscapeLoopWaypoint++;
            return;
        }
    case 17:
        {
            if(!R.EscapeGateVerified)
            {
                if(Press(PC,EKeys::E))R.EscapeGateVerified=Check(M->State.bPursuitEscaped && M->State.Outcome.IsNone(),TEXT("Separate played escape interaction grants no consequence"));
                return;
            }
            const bool Expose=FParse::Param(FCommandLine::Get(),TEXT("AnanseVerifyExpose"));
            if(!R.BeforeChoiceSaved && FParse::Param(FCommandLine::Get(),TEXT("AnanseVerifyEpisode")))
            {
                if(!Check(M->SaveLocal(Slot+TEXT("_BeforeChoice")),TEXT("Native save service preserves actual pre-consequence played checkpoint")))return;
                R.BeforeChoiceSaved=true;Report->SetStringField(TEXT("episode_before_choice_slot"),Slot+TEXT("_BeforeChoice"));
            }
            const FVector Choice(1300,Expose?-150:350,P->GetActorLocation().Z);
            if(!Walk(P,PC,Choice))return;
            if(Press(PC,EKeys::E))
                if(Check(M->State.Outcome==(Expose?TEXT("truth-exposed"):TEXT("witnesses-protected")),TEXT("Actual separate choice interaction awards selected consequence")))Next();
            return;
        }
    case 18:
        {
            if(M->Cinematic&&M->Cinematic->bActive)return; // A real reaction shot temporarily owns input; wait rather than count blocked E presses.
            if(!R.DialogueVerified && FParse::Param(FCommandLine::Get(),TEXT("AnanseVerifyConsequenceDialogue")))
            {
                const bool Expose=FParse::Param(FCommandLine::Get(),TEXT("AnanseVerifyExpose"));
                const int32 Expected=Expose?(M->State.bPermit?4:3):3;
                Report->SetNumberField(TEXT("consequence_dialogue_lines_observed"),R.DialogueLines);
                if(R.DialogueLines<Expected)
                {
                    if(Press(PC,EKeys::E))
                    {
                        if(!Check(!M->ActiveDialogueId.IsNone() && !M->ActiveDialogueText.IsEmpty(),TEXT("Actual E resolves authored subtitle with stable ID")))return;
                        R.DialogueLines++;Report->SetStringField(TEXT("consequence_last_line"),M->ActiveDialogueId.ToString());
                    }
                    return;
                }
                if(!Check(M->State.ProductionBeat==TEXT("sanctuary_pending"),TEXT("Dialogue consumption awaits real sanctuary integration")))return;
                R.DialogueVerified=true;
            }
            if(FParse::Param(FCommandLine::Get(),TEXT("AnanseVerifyEpisode"))){Next();return;}
            if(RequiredSeconds>=600)
            {
                if(!R.Companion.IsValid())
                {
                    FActorSpawnParameters Spawn;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButDontSpawnIfColliding;
                    AAnanseSpiderLabPlayer* Companion=P->GetWorld()->SpawnActor<AAnanseSpiderLabPlayer>(AAnanseSpiderLabPlayer::StaticClass(),FVector(-1900,-1200,P->GetActorLocation().Z),FRotator::ZeroRotator,Spawn);
                    R.Companion=Companion;
                    if(!Check(Companion && Companion->GetMesh()->GetSkeletalMeshAsset() && Companion->GroundContact,TEXT("Mixed stability fixture spawned real imported eight-appendage proxy without campaign swap")))return;
                    Companion->Mission->Deactivate();
                    Companion->GetCharacterMovement()->bRunPhysicsWithNoController=true;Companion->GetCharacterMovement()->MaxWalkSpeed=35;
                    Companion->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
                    Companion->bUseControllerRotationYaw=false;Companion->GetCharacterMovement()->bOrientRotationToMovement=true;
                    Companion->PlayProxyClip(2);
                    const FVector2D Corners[]={FVector2D(-1900,-1200),FVector2D(-1700,-1200),FVector2D(-1700,-1000),FVector2D(-1900,-1000)};
                    FCollisionQueryParams PatrolQuery(SCENE_QUERY_STAT(AnanseMixedPatrolQualification),false,Companion);
                    for(int32 I=0;I<4;I++)
                    {
                        const FVector2D A=Corners[I],B=Corners[(I+1)%4];FHitResult Obstruction;
                        const float Z=Companion->GetActorLocation().Z;
                        const bool Blocked=P->GetWorld()->SweepSingleByChannel(Obstruction,FVector(A.X,A.Y,Z),FVector(B.X,B.Y,Z),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(Companion->GetCapsuleComponent()->GetScaledCapsuleRadius(),Companion->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()),PatrolQuery);
                        if(!Check(!Blocked,FString::Printf(TEXT("Mixed patrol actual capsule segment %d is clear; blocker=%s"),I,*GetNameSafe(Obstruction.GetActor()))))return;
                    }
                    Report->SetBoolField(TEXT("mixed_patrol_initial_capsule_sweeps_clear"),true);

                    R.CompanionSpawnTime=R.Active;R.CompanionProgressStart=R.Active;R.LastMixedMetrics=R.Active;
                    R.PreviousCompanion=Companion->GetActorLocation();R.CompanionProgressPosition=R.PreviousCompanion;R.PreviousMixedPlayer=P->GetActorLocation();
                    Report->SetStringField(TEXT("mixed_stability_scope"),TEXT("Development-only moving spider fixture and Kwaku controlled player; no second campaign progression, physical input or final art claim."));
                    Report->SetNumberField(TEXT("mixed_companion_spawn_active_seconds"),R.CompanionSpawnTime);
                }
                AAnanseSpiderLabPlayer* Companion=R.Companion.Get();
                R.MixedWalkDistance+=FVector::Dist2D(P->GetActorLocation(),R.PreviousMixedPlayer);R.PreviousMixedPlayer=P->GetActorLocation();
                R.CompanionWalkDistance+=FVector::Dist2D(Companion->GetActorLocation(),R.PreviousCompanion);R.PreviousCompanion=Companion->GetActorLocation();
                const FVector2D PlayerLoop[]={FVector2D(1300,250),FVector2D(1300,450)};
                const FVector2D PlayerTarget=PlayerLoop[R.MixedPlayerWaypoint%2];
                if(Walk(P,PC,FVector(PlayerTarget.X,PlayerTarget.Y,P->GetActorLocation().Z)))R.MixedPlayerWaypoint++;
                const FVector2D SpiderLoop[]={FVector2D(-1700,-1200),FVector2D(-1700,-1000),FVector2D(-1900,-1000),FVector2D(-1900,-1200)};
                const FVector2D SpiderTarget=SpiderLoop[R.CompanionWaypoint%4];
                const FVector Destination(SpiderTarget.X,SpiderTarget.Y,Companion->GetActorLocation().Z);
                if(FVector::DistSquared2D(Destination,Companion->GetActorLocation())<FMath::Square(20.f))R.CompanionWaypoint++;
                else Companion->AddMovementInput((Destination-Companion->GetActorLocation()).GetSafeNormal2D(),1,true);
                if(R.Active-R.CompanionProgressStart>=5)
                {
                    if(FVector::Dist2D(Companion->GetActorLocation(),R.CompanionProgressPosition)<=30){Check(false,TEXT("Mixed spider fixture stalled in real collision movement"));return;}
                    R.MixedProgressChecks++;Report->SetNumberField(TEXT("mixed_spider_progress_windows_passed"),R.MixedProgressChecks);
                    R.CompanionProgressPosition=Companion->GetActorLocation();R.CompanionProgressStart=R.Active;
                }
                Report->SetNumberField(TEXT("mixed_player_actual_walk_distance_cm"),R.MixedWalkDistance);
                Report->SetNumberField(TEXT("mixed_spider_actual_walk_distance_cm"),R.CompanionWalkDistance);
                Report->SetNumberField(TEXT("mixed_spider_active_duration_seconds"),R.Active-R.CompanionSpawnTime);
                if(R.Active-R.LastMixedMetrics>=1 || R.Active>=RequiredSeconds)
                {
                    TSharedPtr<FJsonObject> Metrics;const auto Reader=TJsonReaderFactory<>::Create(Companion->GroundContact->MetricsJson());
                    if(!FJsonSerializer::Deserialize(Reader,Metrics) || !Metrics.IsValid()){Check(false,TEXT("Mixed spider live contact metrics malformed"));return;}
                    R.MixedMetricsSamples++;Report->SetNumberField(TEXT("mixed_spider_contact_metric_samples"),R.MixedMetricsSamples);
                    Report->SetObjectField(TEXT("mixed_spider_contact_metrics"),Metrics);R.LastMixedMetrics=R.Active;
                }
            }
            if(RequiredSeconds<600 && R.Active<RequiredSeconds)
            {
                if(!R.PostOutcomeWalkStarted){R.PreviousMixedPlayer=P->GetActorLocation();R.PostOutcomeWalkStarted=true;}
                R.MixedWalkDistance+=FVector::Dist2D(P->GetActorLocation(),R.PreviousMixedPlayer);R.PreviousMixedPlayer=P->GetActorLocation();
                const FVector2D Loop[]={FVector2D(1300,250),FVector2D(1300,450)};
                const auto Destination=Loop[R.MixedPlayerWaypoint%2];if(Walk(P,PC,FVector(Destination.X,Destination.Y,P->GetActorLocation().Z)))R.MixedPlayerWaypoint++;
                Report->SetNumberField(TEXT("post_outcome_actual_walk_distance_cm"),R.MixedWalkDistance);return;
            }
            if(R.Active<RequiredSeconds)return;
            if(RequiredSeconds<600 && !Check(R.MixedWalkDistance>100,TEXT("Actual input permits walking after consequence without clearing mission outcome")))return;
            if(RequiredSeconds>=600 && !Check(R.MixedWalkDistance>1000 && R.CompanionWalkDistance>1000,TEXT("Mixed stability player and eight-appendage proxy both actually traversed")))return;
            const FName ExpectedOutcome=FParse::Param(FCommandLine::Get(),TEXT("AnanseVerifyExpose"))?FName(TEXT("truth-exposed")):FName(TEXT("witnesses-protected"));
            if(Check(R.Captures==10 && M->State.bPursuitEscaped && M->State.Outcome==ExpectedOutcome,TEXT("Ten real capture/retry cycles and one played escape complete")))R.Done=true;return;
        }
    case 19:
        // The authored dock adds real piles at the former greybox approach.
        // Walk around them through the open dock lane; do not bypass interaction sight checks.
        if(Walk(P,PC,FParse::Param(FCommandLine::Get(),TEXT("AnanseStoryPresentation"))?FVector(1800,580,P->GetActorLocation().Z):FVector(1650,700,P->GetActorLocation().Z)))Next();return;
    case 20:
        {
            if(!Check(M->SanctuaryGate!=nullptr,TEXT("Actual Story Road gate exists after the consumed consequence")))return;
            FHitResult Obstruction;FCollisionQueryParams Sight(SCENE_QUERY_STAT(AnanseStoryGateVerify),false,P);
            const bool Blocked=P->GetWorld()->LineTraceSingleByChannel(Obstruction,P->GetActorLocation(),M->SanctuaryGate->GetActorLocation(),ECC_Visibility,Sight);
            Report->SetStringField(TEXT("sanctuary_approach_obstruction"),GetNameSafe(Obstruction.GetActor()));
            Report->SetStringField(TEXT("sanctuary_approach_player"),P->GetActorLocation().ToString());
            Report->SetStringField(TEXT("sanctuary_approach_gate"),M->SanctuaryGate->GetActorLocation().ToString());
            if(!Check(!Blocked || Obstruction.GetActor()==M->SanctuaryGate,TEXT("Real walk reaches an unobstructed gate interaction approach")))return;
        }
        R.BeforeTravel=M->State;R.TravelRequested=true;
        Key(PC,EKeys::E,true);Next();return;
    case 21:
        {
            if(UWorld::RemovePIEPrefix(P->GetWorld()->GetOutermost()->GetName())!=UAnanseMission::SanctuaryMap() || M->State.ProductionBeat!=TEXT("sanctuary"))
            {if(R.Active-R.PhaseStart>30)Check(false,TEXT("Actual sanctuary travel/load timed out"));return;}
            if(R.Active-R.PhaseStart<1.0)return; // Let real movement settle on the destination floor before saving.
            R.TravelArrived=true;
            if(!Check(M->State.bEpisodeSession && M->State.Route==R.BeforeTravel.Route && M->State.Outcome==R.BeforeTravel.Outcome && M->State.CompletedPresentationEvents==R.BeforeTravel.CompletedPresentationEvents && M->State.MarketTrust==R.BeforeTravel.MarketTrust && M->State.CourtTrust==R.BeforeTravel.CourtTrust,TEXT("Actual map travel preserves outcome, trust and consumed narrative IDs")))return;
            int32 Spiders=0;for(TActorIterator<AAnanseSpiderLabPlayer> It(P->GetWorld());It;++It)if(It->CharacterId==TEXT("ananse") && It->GetMesh()->GetSkeletalMeshAsset())Spiders++;
            if(!Check(P->CharacterId==TEXT("kwaku") && PC->GetPawn()==P && Spiders==1 && !M->Pursuer,TEXT("Sanctuary contains a separate imported spider while Kwaku stays possessed")))return;
            if(!Check(M->SaveLocal(Slot+TEXT("_Sanctuary")),TEXT("Native save service preserves sanctuary arrival before epilogue")))return;
            Report->SetStringField(TEXT("episode_sanctuary_slot"),Slot+TEXT("_Sanctuary"));Next();return;
        }
    case 22:
        if(Walk(P,PC,FVector(-100,-50,P->GetActorLocation().Z)))Next();return;
    case 23:
        if(R.EpilogueLines<3)
        {
            if(Press(PC,EKeys::E))
            {
                const FName Expected[]={TEXT("MSN_FOREST_010"),TEXT("MSN_FOREST_020"),TEXT("MSN_FOREST_030")};
                if(!Check(M->ActiveDialogueId==Expected[R.EpilogueLines],TEXT("Actual speaker interaction advances authored epilogue line")))return;
                R.EpilogueLines++;
            }
            return;
        }
        if(!Check(M->State.ProductionBeat==TEXT("episode_complete"),TEXT("Third epilogue interaction reaches canonical episode completion")))return;
        Next();return;
    case 24:
        if(Press(PC,EKeys::F5))
        {
            UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));
            if(!Check(Save && Save->SchemaVersion==4 && Save->State.ProductionBeat==TEXT("episode_complete") && Save->MapIdentity==UAnanseMission::SanctuaryMap(),TEXT("F5 saves actual completed episode in destination map")))return;
            Report->SetBoolField(TEXT("episode_completed_and_saved"),true);Next();
        }return;
    case 25:
        StopWalk(PC);
        if(R.Active>=RequiredSeconds)
            if(Check(R.Captures==10 && M->State.Outcome==R.BeforeTravel.Outcome && M->State.ProductionBeat==TEXT("episode_complete"),TEXT("Played route, pursuit, consequence and technical epilogue complete without campaign swap")))R.Done=true;
        return;
    default:Check(false,TEXT("Unexpected pursuit verifier phase"));return;
    }
}
#else
void TickPursuitVerification(AAnansePlayer*,float,double,bool& Finished,FString& Error,TSharedPtr<FJsonObject>,FString,FString,bool,bool){Finished=false;Error.Reset();}
bool IsExpectedEpisodeTravelPawn(AAnansePlayer*){return false;}
#endif
