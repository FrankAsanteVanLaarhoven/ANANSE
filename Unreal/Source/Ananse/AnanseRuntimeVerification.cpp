#include "AnanseRuntimeVerification.h"
#include "AnanseMotionReview.h"
#include "Materials/Material.h"
#include "Engine/PointLight.h"
#include "Components/PointLightComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
static FString DefaultAnanseCheckpointSlot(FName CharacterId)
{
 if(CharacterId==TEXT("kwaku") && FParse::Param(FCommandLine::Get(),TEXT("AnanseEnvironmentRoute")))return TEXT("AnanseEnvironmentRoute_v1");
 if(CharacterId==TEXT("kwaku") && FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoReview")))return TEXT("AnanseAsoEpisode_v1");
 if(CharacterId==TEXT("kwaku") && FParse::Param(FCommandLine::Get(),TEXT("AnanseAcceptedVisuals")))return TEXT("AnanseAcceptedEpisode_v1");
 return CharacterId==TEXT("kwaku")?FString(TEXT("AnansePrototype")):FString(TEXT("AnanseCharacter_"))+CharacterId.ToString();
}
#if !UE_BUILD_SHIPPING
#include "AnansePlayer.h"
#include "Containers/Ticker.h"
#include "Camera/PlayerCameraManager.h"
#include "AnanseCastLab.h"
#include "Engine/SkeletalMesh.h"
#include "AnanseCinematic.h"
#include "AnanseSpiderLab.h"
#include "AnanseGroundContact.h"
#include "AnansePursuitVerification.h"
#include "LevelSequence.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "AnanseMission.h"
#include "AnanseCatalogue.h"
#include "AnansePowers.h"
#include "AbilitySystemComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameModeBase.h"
#include "UnrealClient.h"
#include "DynamicRHI.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "ProfilingDebugging/TraceAuxiliary.h"
#include "Trace/Trace.h"
#include "Engine/Engine.h"
#include "InputKeyEventArgs.h"
#include "GameFramework/PlayerInput.h"
#include "EnhancedPlayerInput.h"
#include "Components/InputComponent.h"
#include "GenericPlatform/GenericPlatformInputDeviceMapper.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/EngineVersion.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "Containers/Ticker.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"
#include "RHI.h"
#include "RHIGlobals.h"
#include "RHIStats.h"
#include "EngineUtils.h"
#include "AnanseEnvironmentCluster.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "HAL/PlatformMemory.h"
#if WITH_EDITOR
#include "Editor.h"
#endif
namespace
{
struct FVerification
{
    bool Initialized=false,Enabled=false,Done=false,Failed=false,Pressed=false;
    uint32 OwnerId=0;int32 Phase=0,WalkPoint=0,BeforeCount=0;double Created=0,Started=0,ActiveSeconds=0,ReadyAt=0,LastReport=0;
    FString Mode,Out,ExpectedHash,ExpectedColour,Slot;int32 ExpectedMirror=0;float RequiredSeconds=60;int32 ContactBeforeReset=0;double FixtureWaitStarted=0;
    TWeakObjectPtr<AActor> CinematicView;TWeakObjectPtr<APawn> CinematicPawn;uint8 CinematicMoveMode=0;double CinematicStarted=0;
    TSharedPtr<FJsonObject> Report=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Checks;
    TMap<FName,int32> Actions;
    TSet<FName> ObservedDialogue;
    TSet<FName> AsoCapturedDialogue;bool bAsoInsertCaptured=false;double LastAsoVideo=-1;TArray<TSharedPtr<FJsonValue>> AsoVideoFrames;
    bool bCinematicPauseStarted=false,bCinematicPauseResumed=false,bCinematicPauseFrozen=false;
    bool bAppearanceCaptureStarted=false;
    double LastEnvironmentSample=-1;TArray<TSharedPtr<FJsonValue>> EnvironmentSamples;
    TArray<FTransform> ClipPose;double ClipRotationDelta=0,ClipTranslationDelta=0;
    void Write()
    {
        Report->SetArrayField(TEXT("checks"),Checks);Report->SetNumberField(TEXT("phase"),Phase);
        Report->SetNumberField(TEXT("active_play_seconds"),ActiveSeconds);
        FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Report.ToSharedRef(),Writer);
        IFileManager::Get().MakeDirectory(*FPaths::GetPath(Out),true);
        FFileHelper::SaveStringToFile(Text,*Out,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    }
} V;
void Key(APlayerController* PC,FKey KeyName,bool Down)
{
    bool Delivered=PC->InputKey(FInputKeyEventArgs::CreateSimulated(KeyName,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,IPlatformInputDeviceMapper::Get().GetDefaultInputDevice()));
    V.Report->SetBoolField(TEXT("last_input_accepted"),Delivered);
}
TSharedRef<FJsonObject> MissionState(const FAnanseMissionState& S)
{
    auto J=MakeShared<FJsonObject>();
    J->SetBoolField(TEXT("evidence"),S.bEvidence);J->SetBoolField(TEXT("learned_voice"),S.bLearnedVoice);
    J->SetBoolField(TEXT("permit"),S.bPermit);J->SetBoolField(TEXT("archive"),S.bArchive);J->SetBoolField(TEXT("ledger"),S.bLedger);J->SetBoolField(TEXT("on_rooftop"),S.bOnRooftop);
    J->SetNumberField(TEXT("thread"),S.Thread);J->SetNumberField(TEXT("suspicion"),S.Suspicion);J->SetNumberField(TEXT("market_trust"),S.MarketTrust);J->SetNumberField(TEXT("court_trust"),S.CourtTrust);
    J->SetStringField(TEXT("route"),S.Route.ToString());J->SetStringField(TEXT("outcome"),S.Outcome.ToString());return J;
}
void End(AAnansePlayer* P,const FString& Error=FString())
{
    if(V.Done)return;
    const UGameViewportClient* Viewport=P->GetWorld()->GetGameViewport();
    const bool Lit=Viewport && Viewport->ViewModeIndex==VMI_Lit && Viewport->EngineShowFlags.Lighting && !Viewport->EngineShowFlags.Wireframe && !Viewport->EngineShowFlags.ShaderComplexity;
    const FString Failure=Error.IsEmpty() && !Lit?TEXT("Acceptance requires normal lit gameplay; a gameplay key changed the debug view mode."):Error;
    V.Report->SetNumberField(TEXT("view_mode_index"),Viewport?Viewport->ViewModeIndex:-1);V.Report->SetBoolField(TEXT("normal_lit_rendering"),Lit);
    V.Done=true;V.Failed=!Failure.IsEmpty();
    if(APlayerController* PC=Cast<APlayerController>(P->GetController()))Key(PC,EKeys::W,false);
    V.Report->SetStringField(TEXT("status"),V.Failed?TEXT("failed"):TEXT("assertions_passed"));
    if(V.Failed){V.Report->SetStringField(TEXT("error"),Failure);UE_LOG(LogTemp,Error,TEXT("ANANSE verification: %s"),*Failure);}
    V.Report->SetObjectField(TEXT("mission_state"),MissionState(P->Mission->State));
    if(auto* Lab=Cast<AAnanseSpiderLabPlayer>(P))if(Lab->GroundContact)V.Report->SetStringField(TEXT("ground_contact_metrics"),Lab->GroundContact->MetricsJson());
    V.Write();
    FScreenshotRequest::RequestScreenshot(FPaths::GetPath(V.Out)/TEXT("native-game.png"),true,false);
    const double Finish=FPlatformTime::Seconds()+2;bool PIE=P->GetWorld()->WorldType==EWorldType::PIE;
    FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Finish,PIE,StopSeenAt=0.0](float) mutable
    {
        if(FPlatformTime::Seconds()<Finish)return true;
#if WITH_EDITOR
        if(PIE && GEditor && GEditor->PlayWorld){GEditor->RequestEndPlayMap();return true;}
        if(PIE)
        {
            if(StopSeenAt==0){StopSeenAt=FPlatformTime::Seconds();return true;}
            if(FPlatformTime::Seconds()-StopSeenAt<2)return true;
        }
#endif
        // Capture stays active through gameplay and the final framebuffer. Close
        // the owned trace session before static page allocators are destroyed.
#if UE_TRACE_ENABLED
        FTraceAuxiliary::Pause();FTraceAuxiliary::Stop();UE::Trace::Shutdown();
        V.Report->SetBoolField(TEXT("profile_trace_closed_before_exit"),true);
#endif
        V.Report->SetBoolField(TEXT("play_stopped"),true);V.Write();
        FPlatformMisc::RequestExitWithStatus(false,V.Failed?2:0,TEXT("ANANSE native verification completed"));return false;
    }));
}
bool Check(AAnansePlayer* P,bool Good,const FString& Name)
{
    if(!Good){End(P,Name+TEXT("; feedback: ")+P->Mission->LatestMessage);return false;}
    V.Checks.Add(MakeShared<FJsonValueString>(Name));return true;
}
bool Walk(AAnansePlayer* P,APlayerController* PC,float X,float Y)
{
    FVector D=FVector(X,Y,P->GetActorLocation().Z)-P->GetActorLocation();
    if(D.Size2D()<20){Key(PC,EKeys::W,false);return true;}
    PC->SetControlRotation(FRotator(0,FMath::RadiansToDegrees(FMath::Atan2(D.Y,D.X)),0));
    Key(PC,EKeys::W,true);return false;
}
void Next(){V.Phase++;V.Pressed=false;V.ReadyAt=FPlatformTime::Seconds()+.35;}
bool Action(AAnansePlayer* P,APlayerController* PC,FKey K,FName Name)
{
    if(!V.Pressed){V.BeforeCount=V.Actions.FindRef(Name);Key(PC,K,true);V.Pressed=true;V.ReadyAt=FPlatformTime::Seconds();return false;}
    if(V.Actions.FindRef(Name)<=V.BeforeCount && FPlatformTime::Seconds()-V.ReadyAt<1)return false;
    Key(PC,K,false);return Check(P,V.Actions.FindRef(Name)>V.BeforeCount,TEXT("simulated input reached native ")+Name.ToString());
}
}
FString AnanseVerificationSaveSlot(FName CharacterId)
{
 if(V.Enabled && !V.Slot.IsEmpty())return V.Slot;
 FString Slot;if(FParse::Value(FCommandLine::Get(),TEXT("AnanseCheckpointSlot="),Slot))return Slot;
 return DefaultAnanseCheckpointSlot(CharacterId);
}
bool AnanseUsesDiagnosticCheckpoint()
{
 return V.Enabled && (V.Mode==TEXT("contact") || V.Mode==TEXT("spider")) && V.Slot.StartsWith(TEXT("AnanseVerify_"));
}
void NotifyAnanseVerificationAction(AAnansePlayer*,FName Action)
{
    if(V.Enabled && !V.Done)V.Actions.FindOrAdd(Action)++;
}
void TickAnanseRuntimeVerification(AAnansePlayer* P,float Delta)
{
    if(TickAnanseMotionReview(P,Delta))return;
    if(!V.Initialized)
    {
        V.Created=FPlatformTime::Seconds();V.Initialized=true;V.Enabled=FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyMode="),V.Mode);
        if(!V.Enabled)return;
        FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyReport="),V.Out);FParse::Value(FCommandLine::Get(),TEXT("AnanseExpectedHash="),V.ExpectedHash);
        FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifySeconds="),V.RequiredSeconds);V.RequiredSeconds=FMath::Clamp(V.RequiredSeconds,60.f,600.f);
        FParse::Value(FCommandLine::Get(),TEXT("AnanseExpectedColour="),V.ExpectedColour);FParse::Value(FCommandLine::Get(),TEXT("AnanseExpectedMirror="),V.ExpectedMirror);
        FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifySlot="),V.Slot);
        if(V.Out.IsEmpty() || V.Slot.IsEmpty()){V.Enabled=false;UE_LOG(LogTemp,Error,TEXT("Verification requires explicit report path and dedicated save slot."));return;}
        V.Report->SetStringField(TEXT("mode"),V.Mode);V.Report->SetStringField(TEXT("slot"),V.Slot);V.Report->SetStringField(TEXT("status"),TEXT("starting"));
        V.Report->SetStringField(TEXT("scope"),TEXT("Native development verification; simulated controller input events, not physical hardware."));
        V.Report->SetStringField(TEXT("engine"),FEngineVersion::Current().ToString());
    }
    if(!V.Enabled || V.Done)return;
    if(V.OwnerId!=0 && V.OwnerId!=P->GetUniqueID())
    {
        if(!IsExpectedEpisodeTravelPawn(P))return;
        V.OwnerId=P->GetUniqueID();V.Report->SetStringField(TEXT("episode_destination_world"),P->GetWorld()->GetPathName());
    }
    if(!P->IsNativePlayReady())
    {
        if(FPlatformTime::Seconds()-V.LastReport>5){V.LastReport=FPlatformTime::Seconds();V.Report->SetBoolField(TEXT("actor_begun_play"),P->HasActorBegunPlay());V.Report->SetBoolField(TEXT("has_controller"),P->GetController()!=nullptr);V.Report->SetBoolField(TEXT("world_begun_play"),P->GetWorld()->HasBegunPlay());V.Write();}
        if(FPlatformTime::Seconds()-V.Created>30)End(P,TEXT("BeginPlay/possession readiness expired"));return;
    }
    V.ActiveSeconds+=Delta;
    APlayerController* PC=Cast<APlayerController>(P->GetController());if(!PC)return;
    double Now=FPlatformTime::Seconds();
    // Read-only development observations. RHI counters describe the last completed
    // render frame sampled on the game thread, not synchronized GPU timing.
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseEnvironmentRoute")) && (V.LastEnvironmentSample<0 || V.ActiveSeconds-V.LastEnvironmentSample>=1.))
    {
        V.LastEnvironmentSample=V.ActiveSeconds;auto Sample=MakeShared<FJsonObject>();
        Sample->SetNumberField(TEXT("active_seconds"),V.ActiveSeconds);Sample->SetNumberField(TEXT("game_delta_ms"),Delta*1000.);
        Sample->SetNumberField(TEXT("last_frame_rhi_draw_calls"),GNumDrawCallsRHI[0]);Sample->SetNumberField(TEXT("last_frame_rhi_primitives"),GNumPrimitivesDrawnRHI[0]);
        FTextureMemoryStats TextureMemory;RHIGetTextureMemoryStats(TextureMemory);
        Sample->SetNumberField(TEXT("rhi_streaming_texture_bytes"),double(TextureMemory.StreamingMemorySize));Sample->SetNumberField(TEXT("rhi_nonstreaming_texture_bytes"),double(TextureMemory.NonStreamingMemorySize));
        int32 MeshComponents=0,RecentlyRendered=0,Instances=0,MaterialSlots=0;
        for(TActorIterator<AActor> It(P->GetWorld());It;++It){TArray<UStaticMeshComponent*> Components;It->GetComponents(Components);for(auto* Component:Components)if(Component->IsVisible() && !It->IsHidden()){MeshComponents++;MaterialSlots+=Component->GetNumMaterials();if(Component->WasRecentlyRendered(.2f))RecentlyRendered++;if(auto* Cluster=Cast<UHierarchicalInstancedStaticMeshComponent>(Component))Instances+=Cluster->GetInstanceCount();}}
        Sample->SetNumberField(TEXT("visible_flag_static_mesh_components"),MeshComponents);Sample->SetNumberField(TEXT("recently_rendered_components"),RecentlyRendered);Sample->SetNumberField(TEXT("loaded_visible_instances"),Instances);Sample->SetNumberField(TEXT("visible_component_material_slots"),MaterialSlots);
        if(P->GetWorld()->GetOutermost()->GetName().Contains(TEXT("L_StoryForest_Route")) && !V.Report->HasField(TEXT("static_bridge_checked")))
        {
            bool Visible=false;for(TActorIterator<AAnanseEnvironmentCluster> It(P->GetWorld());It;++It)if(It->Instances->GetStaticMesh() && It->Instances->GetStaticMesh()->GetPathName().Contains(TEXT("GoldenWebCrossing")))Visible=It->Instances->IsVisible() && !It->IsHidden() && It->Instances->GetInstanceCount()==1;
            FHitResult Ground;FCollisionQueryParams Params(SCENE_QUERY_STAT(EnvironmentBridge),false,P);
            const bool Hit=P->GetWorld()->LineTraceSingleByChannel(Ground,FVector(350,-200,200),FVector(350,-200,-100),ECC_Visibility,Params);
            FHitResult Sweep;const bool Blocked=P->GetWorld()->SweepSingleByChannel(Sweep,FVector(240,-200,107),FVector(460,-200,107),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(42,88),Params);
            V.Report->SetBoolField(TEXT("static_bridge_checked"),true);V.Report->SetNumberField(TEXT("static_bridge_deck_hit_z_cm"),Hit?Ground.ImpactPoint.Z:-999.);V.Report->SetBoolField(TEXT("static_bridge_capsule_clear"),!Blocked);
            if(!Check(P,Visible && Hit && FMath::Abs(Ground.ImpactPoint.Z-16.)<.1 && !Blocked,TEXT("Static sanctuary web crossing visible with matching16cm deck and clear42x88cm capsule sweep")))return;
        }
        const auto Memory=FPlatformMemory::GetStats();Sample->SetNumberField(TEXT("process_physical_bytes"),double(Memory.UsedPhysical));Sample->SetStringField(TEXT("map"),P->GetWorld()->GetOutermost()->GetName());Sample->SetStringField(TEXT("player_position"),P->GetActorLocation().ToString());
        const FString Dir=FPaths::GetPath(V.Out)/TEXT("environment_frames");IFileManager::Get().MakeDirectory(*Dir,true);
        const FString Frame=Dir/FString::Printf(TEXT("route_%04d.png"),V.EnvironmentSamples.Num());FScreenshotRequest::RequestScreenshot(Frame,true,false);Sample->SetStringField(TEXT("frame"),Frame);
        TArray<TSharedPtr<FJsonValue>> MotionRows;for(TActorIterator<AAnanseEnvironmentCluster> It(P->GetWorld());It;++It)if(It->bMotionVariantLoaded){auto M=MakeShared<FJsonObject>();M->SetStringField(TEXT("source_mesh"),It->MotionSourcePath);M->SetStringField(TEXT("motion_mesh"),It->Instances->GetStaticMesh()->GetPathName());M->SetNumberField(TEXT("instances"),It->Instances->GetInstanceCount());M->SetBoolField(TEXT("actor_tick"),It->IsActorTickEnabled());M->SetBoolField(TEXT("collision"),It->GetActorEnableCollision());MotionRows.Add(MakeShared<FJsonValueObject>(M));}Sample->SetArrayField(TEXT("secondary_motion_clusters"),MotionRows);
        V.EnvironmentSamples.Add(MakeShared<FJsonValueObject>(Sample));V.Report->SetArrayField(TEXT("environment_samples"),V.EnvironmentSamples);
    }
    if(V.Started==0)
    {
        V.Started=Now;V.OwnerId=P->GetUniqueID();V.ReadyAt=Now+1;
        V.Report->SetStringField(TEXT("world_type"),P->GetNativeWorldType());V.Report->SetStringField(TEXT("world"),P->GetWorld()->GetPathName());
        V.Report->SetStringField(TEXT("pawn"),P->GetClass()->GetName());V.Report->SetStringField(TEXT("controller"),PC->GetClass()->GetName());
        V.Report->SetStringField(TEXT("game_mode"),P->GetWorld()->GetAuthGameMode()->GetClass()->GetName());
        V.Report->SetStringField(TEXT("player_input_class"),PC->PlayerInput?PC->PlayerInput->GetClass()->GetName():TEXT("None"));
        V.Report->SetStringField(TEXT("input_component_class"),P->InputComponent?P->InputComponent->GetClass()->GetName():TEXT("None"));
        if(UEnhancedPlayerInput* Input=Cast<UEnhancedPlayerInput>(PC->PlayerInput))V.Report->SetNumberField(TEXT("enhanced_mapping_count"),Input->GetEnhancedActionMappingsView().Num());
        V.Report->SetStringField(TEXT("rhi"),GDynamicRHI?GDynamicRHI->GetName():TEXT("None"));V.Report->SetStringField(TEXT("adapter"),GRHIAdapterName);
        V.Report->SetStringField(TEXT("status"),TEXT("running"));V.Write();return;
    }
    if(P->GetUniqueID()!=V.OwnerId){End(P,TEXT("Unexpected pawn replacement/world travel during verification"));return;}
    if(Now-V.Started>V.RequiredSeconds+90){End(P,TEXT("Native scenario timed out"));return;}
    if(Now-V.LastReport>10){V.LastReport=Now;V.Report->SetNumberField(TEXT("walk_point"),V.WalkPoint);V.Report->SetStringField(TEXT("player_position"),P->GetActorLocation().ToString());if(auto* Lab=Cast<AAnanseSpiderLabPlayer>(P))V.Report->SetStringField(TEXT("ground_contact_metrics"),Lab->GroundContact->MetricsJson());V.Write();}
    // Observe evaluated component-space bones after the input has started the clip.
    // This measures live animation, separately from imported-track/headless tests.
    if((V.Mode==TEXT("spider") || V.Mode==TEXT("contact")) && V.Phase>=1 && V.Phase<=4 && V.Pressed && Now>V.ReadyAt-4)
    {
        const TArray<FTransform>& Pose=P->GetMesh()->GetComponentSpaceTransforms();
        if(V.ClipPose.IsEmpty())V.ClipPose=Pose;
        else if(Pose.Num()==V.ClipPose.Num())for(int32 I=0;I<Pose.Num();I++)
        {
            V.ClipRotationDelta=FMath::Max(V.ClipRotationDelta,Pose[I].GetRotation().AngularDistance(V.ClipPose[I].GetRotation()));
            V.ClipTranslationDelta=FMath::Max(V.ClipTranslationDelta,FVector::Distance(Pose[I].GetLocation(),V.ClipPose[I].GetLocation()));
        }
    }
    if(Now<V.ReadyAt)return;
    UAnanseMission* M=P->Mission;UAnanseCatalogue* C=P->GetCatalogue();
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAcceptedVisuals")))
    {
        const auto* Hero=Cast<AAnanseCastLabPlayer>(P);const auto* Skin=P->GetMesh()->GetSkeletalMeshAsset();
        const bool Bound=Hero&&Hero->CharacterId==TEXT("kwaku")&&!Hero->bLabSelectionPawn&&Hero->bStoryCampaignPresentation&&Skin&&Skin->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku")&&P->GetMesh()->GetAnimInstance();
        const bool FirstAcceptedCheck=!V.Report->HasField(TEXT("accepted_campaign_appearance"));
        V.Report->SetBoolField(TEXT("accepted_campaign_appearance"),Bound);V.Report->SetStringField(TEXT("accepted_campaign_mesh"),Skin?Skin->GetPathName():TEXT("None"));
        if((FirstAcceptedCheck||!Bound)&&!Check(P,Bound,TEXT("Exact accepted campaign mesh and non-lab ownership")))return;
    }

    if(V.Mode==TEXT("spider") && FParse::Param(FCommandLine::Get(),TEXT("AnanseAppearanceCapture")) && V.ActiveSeconds>=V.RequiredSeconds-4)
    {
        Key(PC,EKeys::W,false);P->GetCharacterMovement()->StopMovementImmediately();
        if(!V.bAppearanceCaptureStarted)
        {
            if(!Check(P,V.Phase>=5 && V.WalkPoint>=4,TEXT("Original four-clip and movement gates complete before appearance inspection")))return;
            V.bAppearanceCaptureStarted=true;PC->SetControlRotation(FRotator(-5,P->GetActorRotation().Yaw+180,0));P->CameraBoom->TargetArmLength=300;
            if(auto* Lab=Cast<AAnanseSpiderLabPlayer>(P))Lab->PlayProxyClip(0);
            APointLight* Fill=P->GetWorld()->SpawnActor<APointLight>(P->GetActorLocation()+P->GetActorForwardVector()*180-P->GetActorRightVector()*100+FVector(0,0,130),FRotator::ZeroRotator);
            if(!Check(P,Fill!=nullptr,TEXT("Declared diagnostic appearance fill spawned")))return;
            UPointLightComponent* Light=Cast<UPointLightComponent>(Fill->GetLightComponent());
            if(!Check(P,Light!=nullptr,TEXT("Actual installed point-light component resolved")))return;
            Light->SetMobility(EComponentMobility::Movable);Light->SetIntensity(2500);Light->SetAttenuationRadius(1000);Light->SetCastShadows(false);
            V.Report->SetStringField(TEXT("appearance_capture_scope"),TEXT("Ordinary front gameplay camera; transient 2500-intensity/1000cm-radius shadowless point fill. Inspection fixture, not production lighting acceptance."));
        }
        if(V.ActiveSeconds>=V.RequiredSeconds)End(P);
        return;
    }
    if(M->Cinematic&&M->Cinematic->bActive&&M->Cinematic->ActiveEvent==TEXT("aso_negotiation_finished_or_skipped")&&FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoReview")))
    {
        const double At=M->Cinematic->PlaybackSeconds();const bool Insert=!V.bAsoInsertCaptured&&At>=2.6&&At<3.2;
        const bool Dialogue=!M->ActiveDialogueId.IsNone()&&!V.AsoCapturedDialogue.Contains(M->ActiveDialogueId)&&FMath::Fmod(At,3.6)>.25;
        if(Insert||Dialogue)
        {
            const FString Name=Insert?TEXT("aso-evidence-insert"):TEXT("aso-dialogue-")+M->ActiveDialogueId.ToString();FScreenshotRequest::RequestScreenshot(FPaths::GetPath(V.Out)/(Name+TEXT(".png")),true,false);
            if(Insert)V.bAsoInsertCaptured=true;else V.AsoCapturedDialogue.Add(M->ActiveDialogueId);
            if(PC->PlayerCameraManager){auto Camera=MakeShared<FJsonObject>();Camera->SetNumberField(TEXT("timeline_seconds"),At);Camera->SetStringField(TEXT("location_cm"),PC->PlayerCameraManager->GetCameraLocation().ToString());Camera->SetStringField(TEXT("rotation"),PC->PlayerCameraManager->GetCameraRotation().ToString());Camera->SetNumberField(TEXT("horizontal_fov_degrees"),PC->PlayerCameraManager->GetFOVAngle());V.Report->SetObjectField(Name,Camera);}
        }
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoContact")))
    {
        if(M->State.CompletedPresentationEvents.Contains(TEXT("aso_broken_promise_visual_only"))){Check(P,false,TEXT("Visual reaction must not create a durable mission event"));return;}
        if(M->Cinematic&&M->Cinematic->bActive&&(M->Cinematic->IsNegotiationPresentation()||M->Cinematic->ActiveEvent==TEXT("aso_broken_promise_visual_only")))
        {
            const double T=M->Cinematic->PlaybackSeconds();
            if(V.ActiveSeconds-V.LastAsoVideo>=.1)
            {
                const FString Folder=FPaths::GetPath(V.Out)/TEXT("negotiation_frames");IFileManager::Get().MakeDirectory(*Folder,true);const FString Name=FString::Printf(TEXT("negotiation_%05d.png"),V.AsoVideoFrames.Num());FScreenshotRequest::RequestScreenshot(Folder/Name,true,false);
                auto Frame=MakeShared<FJsonObject>();Frame->SetStringField(TEXT("png"),Name);Frame->SetStringField(TEXT("event"),M->Cinematic->ActiveEvent.ToString());Frame->SetNumberField(TEXT("active_seconds"),V.ActiveSeconds);Frame->SetNumberField(TEXT("sequence_seconds"),T);V.AsoVideoFrames.Add(MakeShared<FJsonValueObject>(Frame));V.LastAsoVideo=V.ActiveSeconds;V.Report->SetArrayField(TEXT("aso_video_frames"),V.AsoVideoFrames);
            }
            if(M->Cinematic->ActiveEvent==TEXT("aso_broken_promise_visual_only")&&T>.5&&!V.AsoCapturedDialogue.Contains(TEXT("aso_broken_promise_visual_only")))
            {FScreenshotRequest::RequestScreenshot(FPaths::GetPath(V.Out)/TEXT("cinematic_broken_promise.png"),true,false);V.AsoCapturedDialogue.Add(TEXT("aso_broken_promise_visual_only"));}
        }
    }
    if(!M->ActiveDialogueId.IsNone())
    {
        const bool Seen=V.ObservedDialogue.Contains(M->ActiveDialogueId);V.ObservedDialogue.Add(M->ActiveDialogueId);
        if(!Seen && V.Mode==TEXT("cinematic"))FScreenshotRequest::RequestScreenshot(FPaths::GetPath(V.Out)/TEXT("subtitle-")+M->ActiveDialogueId.ToString()+TEXT(".png"),true,false);
    }
    if(V.Mode==TEXT("spider") || V.Mode==TEXT("contact"))
    {
        AAnanseSpiderLabPlayer* Lab=Cast<AAnanseSpiderLabPlayer>(P);
        if(!Lab){End(P,TEXT("Spider verification requires the isolated lab pawn"));return;}
        if(V.Phase==0)
        {
            if(!Check(P,C && C->bLoaded && C->ContentHash==V.ExpectedHash,TEXT("live publication hash loaded")))return;
            V.Report->SetStringField(TEXT("loaded_hash"),C->ContentHash);
            if(!Check(P,P->CharacterId==TEXT("ananse") && PC->GetPawn()==P,TEXT("separate Ananse identity possessed")))return;
            if(!Check(P,P->GetMesh()->GetRelativeRotation().Equals(FRotator::ZeroRotator,.0001f) && FVector::DotProduct(P->GetMesh()->GetForwardVector(),P->GetActorForwardVector())>.9999f,TEXT("Published custom spider binding preserves verified +X basis; no inherited mannequin yaw")))return;
            const FAnanseCharacterSpec* SpiderSpec=C->Find(TEXT("ananse"));
            if(!Check(P,SpiderSpec && !SpiderSpec->Variants.IsEmpty() && Lab->PublishedClothMaterial && Lab->PublishedClothSlot!=INDEX_NONE,TEXT("Actual named proxy cloth material consumes published Ananse variant")))return;
            if(!Check(P,Lab->PublishedClothMaterial->GetMaterial()->GetUsageByFlag(MATUSAGE_SkeletalMesh),TEXT("Actual parent material has cooked skeletal-mesh usage; parameter storage alone is insufficient")))return;
            const FLinearColor ActualCloth=Lab->PublishedClothMaterial->K2_GetVectorParameterValue(TEXT("ClothColor"));
            if(!Check(P,ActualCloth.Equals(SpiderSpec->Variants[0].Cloth,.0001f) && P->GetMesh()->GetMaterial(Lab->PublishedClothSlot)==Lab->PublishedClothMaterial,TEXT("Live skeletal cloth slot matches published linear colour at tolerance 0.0001")))return;
            V.Report->SetStringField(TEXT("actual_spider_cloth_linear"),ActualCloth.ToString());V.Report->SetNumberField(TEXT("actual_spider_cloth_slot"),Lab->PublishedClothSlot);
            if(!Check(P,GDynamicRHI && FString(GDynamicRHI->GetName())==TEXT("Vulkan"),TEXT("real Vulkan rendering backend")))return;
            TArray<TSharedPtr<FJsonValue>> Bones;for(FName Name:Lab->GetImportedBoneNames())Bones.Add(MakeShared<FJsonValueString>(Name.ToString()));V.Report->SetArrayField(TEXT("imported_bones"),Bones);
            if(!Check(P,Bones.Num()>=102,TEXT("imported custom skeleton retains at least 102 joints")))return;
            for(const TCHAR* Side:{TEXT("upper_l"),TEXT("upper_r"),TEXT("lower_l"),TEXT("lower_r")})
                if(!Check(P,P->GetMesh()->DoesSocketExist(FName(*(FString(TEXT("socket_thread_"))+Side))),TEXT("four hand marker bindings retained")))return;
            if(V.Mode==TEXT("spider"))Lab->GroundContact->bEnabled=false; // Original baked-clip qualification remains distinct from live IK.
            if(!Check(P,Lab->ProxyClips.Num()==4 && !Lab->ProxyClips.Contains(nullptr),TEXT("four imported skeletal clips available")))return;
            V.Report->SetBoolField(TEXT("engineering_proxy"),true);V.Report->SetStringField(TEXT("unsupported"),TEXT("Live terrain foot-locking, production deformation, cloth, final art, rig controls and physical hardware input unqualified."));Next();return;
        }
        if(V.Mode==TEXT("contact") && V.Phase==4)
        {
            if(!V.Pressed){V.BeforeCount=Lab->GroundContact->ResetCount;Key(PC,EKeys::SpaceBar,true);V.Pressed=true;V.ReadyAt=Now+1.5;return;}
            Key(PC,EKeys::SpaceBar,false);
            if(!P->GetCharacterMovement()->IsMovingOnGround()){if(Now-V.ReadyAt>3)End(P,TEXT("Jump landing readiness expired"));return;}
            if(!Check(P,Lab->GroundContact->ResetCount>V.BeforeCount,TEXT("Actual jump releases and reacquires transient contacts")))return;
            Lab->PlayProxyClip(2);Next();return;
        }
        if(V.Phase>=1 && V.Phase<=4)
        {
            int32 Index=V.Phase-1;FKey Keys[]={EKeys::F1,EKeys::F2,EKeys::F3,EKeys::F4};
            if(!V.Pressed){V.ClipPose.Reset();V.ClipRotationDelta=0;V.ClipTranslationDelta=0;Key(PC,Keys[Index],true);V.Pressed=true;V.ReadyAt=Now+5;return;}
            Key(PC,Keys[Index],false);
            if(!Check(P,Lab->ActiveProxyClip==Index,TEXT("actual clip-selector input reached skeletal player")))return;
            if(!Check(P,V.ClipPose.Num()>=102 && (V.ClipRotationDelta>.0001 || V.ClipTranslationDelta>.1),TEXT("live evaluated bones move during selected clip")))return;
            V.Report->SetNumberField(FString::Printf(TEXT("clip_%d_max_rotation_radians"),Index),V.ClipRotationDelta);
            V.Report->SetNumberField(FString::Printf(TEXT("clip_%d_max_translation_cm"),Index),V.ClipTranslationDelta);
            FScreenshotRequest::RequestScreenshot(FPaths::GetPath(V.Out)/FString::Printf(TEXT("spider-clip-%d.png"),Index),true,false);
            Next();return;
        }
        if(V.Mode==TEXT("contact") && V.Phase>=6)
        {
            Key(PC,EKeys::W,false);
            if(V.Phase==6){if(!P->GetCharacterMovement()->IsMovingOnGround())return;if(!Action(P,PC,EKeys::F5,TEXT("save")))return;if(!Check(P,UGameplayStatics::DoesSaveGameExist(V.Slot,0),TEXT("Dedicated spider checkpoint created through F5")))return;V.ContactBeforeReset=Lab->GroundContact->ResetCount;Next();return;}
            if(V.Phase==7){if(!Action(P,PC,EKeys::F9,TEXT("load")))return;if(!Check(P,Lab->GroundContact->ResetCount>V.ContactBeforeReset,TEXT("F9 checkpoint load rebuilds transient contacts")))return;Next();return;}
            if(V.Phase==8){if(!Walk(P,PC,0,0))return;V.ContactBeforeReset=Lab->GroundContact->ResetCount;if(!Check(P,P->StartWebFlight(P->GetActorLocation()+FVector(150,0,40)),TEXT("Direct native flight-transition fixture starts; no ability permission granted")))return;Next();V.ReadyAt=Now+2;return;}
            if(V.Phase==9){if(P->IsWebFlying() || !P->GetCharacterMovement()->IsMovingOnGround())return;if(!Check(P,Lab->GroundContact->ResetCount>V.ContactBeforeReset,TEXT("Flight/landing rebuilds contacts")))return;Next();return;}
            if(V.ActiveSeconds<V.RequiredSeconds)return;
        }
        FVector2D Points[]={FVector2D(0,200),FVector2D(200,200),FVector2D(200,0),FVector2D(0,0)};
        FVector2D Fixtures[]={FVector2D(0,0),FVector2D(450,0),FVector2D(800,0),FVector2D(0,0),FVector2D(0,500),FVector2D(0,900),FVector2D(-500,700),FVector2D(-500,0),FVector2D(-900,0),FVector2D(-900,400),FVector2D(-900,800),FVector2D(0,0)};
        if(V.Mode!=TEXT("contact") || V.Phase==5)
        {auto Point=V.Mode==TEXT("contact")?Fixtures[V.WalkPoint%12]:Points[V.WalkPoint%4];if(Walk(P,PC,Point.X,Point.Y))
         {if(V.Mode==TEXT("contact") && V.WalkPoint%12==10){if(V.FixtureWaitStarted==0)V.FixtureWaitStarted=Now;if(Now-V.FixtureWaitStarted<6)return;V.FixtureWaitStarted=0;}V.WalkPoint++;}}
        if(V.Mode==TEXT("contact") && V.Phase==5 && V.WalkPoint>=12){Next();return;}
        if(V.ActiveSeconds>=V.RequiredSeconds)
        {
            if(V.Mode==TEXT("contact"))
            {
                for(const auto& L:Lab->GroundContact->Legs)
                {
                    auto D=L.Drift;D.Sort();auto N=L.Penetration;N.Sort();
                    for(const TCHAR* Role:{TEXT("flat"),TEXT("ramp"),TEXT("steps"),TEXT("uneven"),TEXT("moving"),TEXT("disappearing")})
                        if(!Check(P,L.SupportSamples.FindRef(FName(*(FString(TEXT("AnanseFixture:"))+Role)))>=10,TEXT("per-leg actual fixture support coverage: ")+FString(Role)))return;
                    if(!Check(P,L.MaxStretchError<=.05 && Lab->GroundContact->InvalidTransforms==0,TEXT("post-solve finite transforms and segment-length preservation")))return;
                    if(!Check(P,L.JointLimitViolations==0,TEXT("evaluated supporting-leg knee flex stays within declared 5..155 degree engineering limits")))return;
                    if(!Check(P,D.Num()>100 && D[FMath::Min(D.Num()-1,FMath::FloorToInt(D.Num()*.95))]<=2 && N.Last()<=.5,TEXT("actual post-solve stance drift and penetration gate")))return;
                }
                if(!Check(P,V.WalkPoint>=12,TEXT("declared fixture route traversed")))return;
            }
            if(Check(P,V.WalkPoint>=4,TEXT("possessed spider uses existing movement input")))End(P);
        }return;
    }
    if(V.Phase==0)
    {
        if(!Check(P,C && C->bLoaded && C->ContentHash==V.ExpectedHash,TEXT("live publication hash loaded")))return;
        V.Report->SetStringField(TEXT("loaded_hash"),C->ContentHash);
        if(!Check(P,GDynamicRHI && FString(GDynamicRHI->GetName())==TEXT("Vulkan"),TEXT("real Vulkan rendering backend")))return;
        V.Report->SetBoolField(TEXT("primitive_placeholder"),P->Body->IsVisible());
        FLinearColor Actual;bool HasColour=P->Body->GetMaterial(0) && P->Body->GetMaterial(0)->GetVectorParameterValue(FMaterialParameterInfo(TEXT("ClothColor")),Actual);
        FLinearColor Wanted=FLinearColor::FromSRGBColor(FColor::FromHex(V.ExpectedColour));
        if(!Check(P,HasColour && Actual.Equals(Wanted,.0001f),TEXT("primitive material matches expected sRGB-to-linear colour (tolerance 0.0001)")))return;
        V.Report->SetStringField(TEXT("actual_linear_colour"),Actual.ToString());
        bool Mirror=P->Abilities->FindAbilitySpecFromClass(UAnanseMirrorAbility::StaticClass())!=nullptr;
        if(!Check(P,Mirror==(V.ExpectedMirror!=0),TEXT("permitted mirror ability grant matches publication")))return;
        if(!Check(P,PC->GetPawn()==P && (P->GetWorld()->WorldType==EWorldType::Game || P->GetWorld()->WorldType==EWorldType::PIE),TEXT("possessed native game pawn")))return;
        Next();return;
    }
    if(V.Mode==TEXT("pursuit") || V.Mode==TEXT("pursuit-reload") || V.Mode==TEXT("episode-reload"))
    {
        bool Finished=false;FString Error;
        TickPursuitVerification(P,Delta,V.RequiredSeconds,Finished,Error,V.Report,V.Out,V.Slot,V.Mode==TEXT("pursuit-reload"),V.Mode==TEXT("episode-reload"));
        if(Finished)End(P,Error);return;
    }
    if(V.Mode==TEXT("cinematic"))
    {
        const bool Aso=FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoReview"));
        const FName Completion=Aso?FName(TEXT("aso_negotiation_finished_or_skipped")):FName(TEXT("opening_finished_or_skipped"));
        ULevelSequence* Sequence=LoadObject<ULevelSequence>(nullptr,Aso?(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoContact"))?TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/Cinematics_v001/LS_AsoNegotiation_v002.LS_AsoNegotiation_v002"):TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v002/Cinematics_v004/LS_AsoNegotiation_v002.LS_AsoNegotiation_v002")):TEXT("/Game/Production/Market/Technical_v001/LS_MarketOpening_Technical.LS_MarketOpening_Technical"));
        if(!Sequence){End(P,TEXT("Missing actual opening sequence asset"));return;}
        auto Restored=[&](){return PC->GetPawn()==V.CinematicPawn.Get() && PC->GetViewTarget()==V.CinematicView.Get() && !PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored() && P->GetCharacterMovement()->MovementMode==V.CinematicMoveMode;};
        if(V.Phase==1)
        {
            V.CinematicView=PC->GetViewTarget();V.CinematicPawn=PC->GetPawn();V.CinematicMoveMode=P->GetCharacterMovement()->MovementMode;
            if(!Check(P,M->BeginCinematic(Sequence,Completion),TEXT("real opening LevelSequence started")))return;Next();V.ReadyAt=Now+1;return;
        }
        if(V.Phase==2)
        {
            if(!V.Pressed && !Check(P,M->Cinematic && M->Cinematic->bActive && PC->IsMoveInputIgnored() && PC->IsLookInputIgnored() && PC->GetViewTarget()!=V.CinematicView.Get(),TEXT("sequence camera cut and cinematic input locks active")))return;
            FScreenshotRequest::RequestScreenshot(FPaths::GetPath(V.Out)/TEXT("opening-active.png"),true,false);
            if(!Action(P,PC,EKeys::Escape,TEXT("skip")))return;
            if(!Check(P,Restored() && !M->Cinematic->HasPendingStop() && !M->Cinematic->bActive && M->State.CompletedPresentationEvents.Contains(Completion) && (Aso?M->State.Outcome.IsNone():M->State.ProductionBeat==TEXT("investigation")),TEXT("skip restores possession camera movement input and advances opening once")))return;
            if(!Check(P,!M->BeginCinematic(Sequence,Completion),TEXT("completed opening cannot replay or award twice")))return;Next();return;
        }
        if(V.Phase==3){if(!Check(P,M->BeginCinematic(Sequence,TEXT("opening_cancel_probe")),TEXT("cancellation sequence started")))return;Next();V.ReadyAt=Now+1;return;}
        if(V.Phase==4)
        {
            if(Aso&&M->State.bEpisodeSession&&!V.bCinematicPauseResumed)
            {
                if(V.bCinematicPauseStarted)return;
                V.bCinematicPauseStarted=true;Key(PC,EKeys::P,true);Key(PC,EKeys::P,false);
                const double Deadline=FPlatformTime::Seconds()+1.;const TWeakObjectPtr<AAnansePlayer> Weak=P;
                FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Weak,Deadline,Observed=false,PausedAt=0.,ResumeAt=0.](float)mutable{
                    auto* Hero=Weak.Get();if(!Hero)return false;
                    if(!Observed){if(!UGameplayStatics::IsGamePaused(Hero)){if(FPlatformTime::Seconds()<Deadline)return true;V.bCinematicPauseResumed=true;return false;}Observed=true;PausedAt=Hero->Mission->Cinematic->PlaybackSeconds();ResumeAt=FPlatformTime::Seconds()+.5;V.Report->SetBoolField(TEXT("aso_input_pause_observed"),true);}
                    if(FPlatformTime::Seconds()<ResumeAt)return true;
                    const double Drift=FMath::Abs(Hero->Mission->Cinematic->PlaybackSeconds()-PausedAt);V.Report->SetNumberField(TEXT("aso_pause_clock_drift_seconds"),Drift);V.bCinematicPauseFrozen=Drift<=.05;
                    if(auto* Controller=Cast<APlayerController>(Hero->GetController())){Key(Controller,EKeys::P,true);Key(Controller,EKeys::P,false);}V.bCinematicPauseResumed=true;return false;}));return;
            }
            if(Aso&&M->State.bEpisodeSession)if(!Check(P,V.bCinematicPauseFrozen&&!UGameplayStatics::IsGamePaused(P),TEXT("Negotiation clock held within .05 seconds and resumed through actual input")))return;
            M->CancelCinematic();if(!Check(P,Restored() && !M->Cinematic->HasPendingStop() && !M->State.CompletedPresentationEvents.Contains(TEXT("opening_cancel_probe")),TEXT("cancellation restores control without durable award")))return;
            if(Aso){if(!Check(P,M->BeginCinematic(Sequence,TEXT("opening_cancel_probe")),TEXT("Cancelled negotiation can retry same unconsumed event")))return;M->CancelCinematic();if(!Check(P,Restored()&&!M->State.CompletedPresentationEvents.Contains(TEXT("opening_cancel_probe")),TEXT("Retried cancellation remains non-durable")))return;}
            Next();return;
        }
        if(V.Phase==5){if(!Check(P,M->BeginCinematic(Sequence,TEXT("opening_finish_probe")),TEXT("natural-finish sequence started")))return;V.CinematicStarted=Now;Next();return;}
        if(V.Phase==6)
        {
            if(M->Cinematic->bActive){if(Now-V.CinematicStarted>40)End(P,TEXT("natural sequence finish expired"));return;}
            if(!Check(P,Restored() && !M->Cinematic->HasPendingStop() && M->State.CompletedPresentationEvents.Contains(TEXT("opening_finish_probe")),TEXT("natural finish restores control and durable event")))return;
            const FName ExpectedAso[]={TEXT("MSN_NEG_010"),TEXT("MSN_NEG_020"),TEXT("MSN_NEG_030"),TEXT("MSN_NEG_040"),TEXT("MSN_NEG_050")};
            const FName ExpectedOpening[]={TEXT("MSN_OPEN_010"),TEXT("MSN_OPEN_020"),TEXT("MSN_OPEN_030"),TEXT("MSN_OPEN_040"),TEXT("MSN_OPEN_050")};
            for(int32 I=0;I<5;++I)if(!Check(P,V.ObservedDialogue.Contains(Aso?ExpectedAso[I]:ExpectedOpening[I]),TEXT("Actual timeline exposed each expected authored subtitle")))return;
            if(!Check(P,M->ActiveDialogueId.IsNone(),TEXT("Finish clears presentation-only subtitle state")))return;
            Next();return;
        }
        if(V.Phase==7)
        {
            if(!Action(P,PC,EKeys::F5,TEXT("save")))return;
            if(!Check(P,UGameplayStatics::DoesSaveGameExist(V.Slot,0),TEXT("cinematic semantic checkpoint saved through input")))return;Next();return;
        }
        FVector2D Points[]={FVector2D(-900,-150),FVector2D(-700,-150),FVector2D(-700,-350),FVector2D(-900,-350)};
        auto Point=Points[V.WalkPoint%4];if(Walk(P,PC,Point.X,Point.Y))V.WalkPoint++;
        if(V.ActiveSeconds>=V.RequiredSeconds){if(Check(P,V.WalkPoint>=4,TEXT("movement works after cinematic finish skip and cancel")))End(P);}return;
    }
    if(V.Mode==TEXT("r2"))
    {
        if(V.Phase==1 || V.Phase==2)
        {
            if(!Action(P,PC,V.Phase==1?EKeys::Three:EKeys::Gamepad_FaceButton_Top,TEXT("mirror")))return;
            if(!Check(P,M->State.Thread==3 && !M->MirrorActive(),TEXT("absent mirror blocked through simulated keyboard/gamepad path")))return;Next();return;
        }
        if(V.Phase==3)
        {
            int32 W,H;PC->GetViewportSize(W,H);
            if(!V.Pressed){V.BeforeCount=V.Actions.FindRef(TEXT("mirror"));PC->InputTouch(FTouchId(FInputDeviceId::CreateFromInternalId(0),ETouchIndex::Touch1),ETouchType::Began,FVector2D(W-50,159),1,FPlatformTime::Cycles64());V.Pressed=true;V.ReadyAt=Now+.3;return;}
            PC->InputTouch(FTouchId(FInputDeviceId::CreateFromInternalId(0),ETouchIndex::Touch1),ETouchType::Ended,FVector2D(W-50,159),0,FPlatformTime::Cycles64());
            if(!Check(P,V.Actions.FindRef(TEXT("mirror"))>V.BeforeCount && M->State.Thread==3 && !M->MirrorActive(),TEXT("absent mirror blocked through simulated touch input path")))return;Next();return;
        }
        FVector2D Points[]={FVector2D(-900,-150),FVector2D(-700,-150),FVector2D(-700,-350),FVector2D(-900,-350)};
        auto Point=Points[V.WalkPoint%4];if(Walk(P,PC,Point.X,Point.Y))V.WalkPoint++;
        if(V.ActiveSeconds>=V.RequiredSeconds){if(Check(P,V.WalkPoint>=4,TEXT("WASD binding drives collision-aware native movement")))End(P);}return;
    }
    if(V.Mode==TEXT("reload"))
    {
        if(V.Phase==1)
        {
            UAnanseSave* S=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(V.Slot,0));
            if(!Check(P,S!=nullptr,TEXT("dedicated native checkpoint exists after process restart")))return;
            if(!Action(P,PC,EKeys::F9,TEXT("load")))return;
            bool Same=FAnanseMissionState::StaticStruct()->CompareScriptStruct(&S->State,&M->State,0);
            if(!Check(P,Same && P->GetActorLocation().Equals(S->Position,.05f) && P->GetActorRotation().Equals(S->Rotation,.01f),TEXT("all mission fields and transform restored")))return;
            float Clock=P->GetWorld()->GetTimeSeconds();
            if(!Check(P,FMath::IsNearlyEqual(FMath::Max(0.f,M->VoiceUntil-Clock),S->VoiceRemaining,.03f) && FMath::IsNearlyEqual(FMath::Max(0.f,M->MirrorUntil-Clock),S->MirrorRemaining,.03f),TEXT("saved relative power timers restored")))return;
            for(const auto& Entry:S->CooldownRemaining)if(!Check(P,FMath::IsNearlyEqual(FMath::Max(0.f,M->Cooldowns.FindRef(Entry.Key)-Clock),Entry.Value,.03f),TEXT("saved cooldown restored: ")+Entry.Key.ToString()))return;
            Next();return;
        }
        if(V.ActiveSeconds>=V.RequiredSeconds)End(P);return;
    }
    if(V.Mode!=TEXT("baseline")){End(P,TEXT("Unknown native verification mode"));return;}
    if(V.Phase==1)
    {
        if(!Walk(P,PC,-650,150))return;
        if(!Action(P,PC,EKeys::E,TEXT("interact")))return;
        if(Check(P,M->State.bLearnedVoice,TEXT("learned captain call via native spatial interaction")))Next();return;
    }
    if(V.Phase==2)
    {
        if(!Action(P,PC,EKeys::Two,TEXT("voice")))return;
        if(Check(P,M->VoiceActive() && M->State.Thread==2,TEXT("Borrowed Voice activated through input binding")))Next();return;
    }
    if(V.Phase==3)
    {
        if(!Action(P,PC,EKeys::Three,TEXT("mirror")))return;
        if(Check(P,M->MirrorActive() && M->State.Thread==1,TEXT("Trick Mirror activated through input binding")))Next();return;
    }
    if(V.Phase==4)
    {
        if(!V.Pressed && !Walk(P,PC,-400,300))return;
        if(!Action(P,PC,EKeys::One,TEXT("web")))return;
        if(Check(P,P->IsWebFlying() && M->State.Thread==0,TEXT("Web Step starts collision-checked native traversal"))){Next();V.ReadyAt=Now+1;}return;
    }
    if(V.Phase==5){if(Check(P,!P->IsWebFlying(),TEXT("Web Step completes native flight")))Next();return;}
    FVector2D Route[]={FVector2D(-800,-350),FVector2D(-100,-200),FVector2D(500,250),FVector2D(850,250),FVector2D(1300,350)};
    if(V.Phase>=6 && V.Phase<=10)
    {
        // Walk around the solid archive marker instead of driving through it.
        if(V.Phase==9 && V.WalkPoint<2)
        {
            const FVector2D Detour[2]={FVector2D(500,100),FVector2D(850,100)};
            auto Point=Detour[V.WalkPoint];if(Walk(P,PC,Point.X,Point.Y))V.WalkPoint++;return;
        }
        if(V.Phase==10 && V.WalkPoint<5)
        {
            const FVector2D Detour[3]={FVector2D(850,100),FVector2D(1300,100),FVector2D(1300,250)};
            auto Point=Detour[V.WalkPoint-2];if(Walk(P,PC,Point.X,Point.Y))V.WalkPoint++;return;
        }
        auto Point=Route[V.Phase-6];if(!Walk(P,PC,Point.X,Point.Y))return;
        if(!Action(P,PC,EKeys::E,TEXT("interact")))return;
        bool Good=V.Phase==6?M->State.bEvidence:V.Phase==7?M->State.bPermit:V.Phase==8?M->State.bArchive:V.Phase==9?M->State.bLedger:M->State.Outcome==TEXT("witnesses-protected");
        if(Check(P,Good,FString::Printf(TEXT("native mission spatial step %d"),V.Phase-5)))Next();return;
    }
    if(V.Phase==11)
    {
        if(!V.Pressed && !Check(P,M->State.Route==TEXT("negotiation") && !UGameplayStatics::DoesSaveGameExist(V.Slot,0),TEXT("completed route and unused dedicated save slot")))return;
        if(!Action(P,PC,EKeys::F5,TEXT("save")))return;
        if(!Check(P,UGameplayStatics::DoesSaveGameExist(V.Slot,0),TEXT("native checkpoint written through F5 input path")))return;
        V.Report->SetStringField(TEXT("save_path"),FPaths::ProjectSavedDir()/TEXT("SaveGames")/(V.Slot+TEXT(".sav")));Next();return;
    }
    if(V.ActiveSeconds>=V.RequiredSeconds)End(P);
}
#else
bool AnanseUsesDiagnosticCheckpoint(){return false;}
void TickAnanseRuntimeVerification(AAnansePlayer*,float){}
void NotifyAnanseVerificationAction(AAnansePlayer*,FName){}
FString AnanseVerificationSaveSlot(FName CharacterId){return DefaultAnanseCheckpointSlot(CharacterId);}
#endif
