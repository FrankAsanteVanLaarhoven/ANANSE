#include "AnanseLabSelection.h"
#include "AnanseSpiderLab.h"
#include "AnanseLeopardLab.h"
#include "AnanseCastLab.h"
#include "AnanseLeopardContact.h"
#include "HAL/PlatformMemory.h"
#include "AnanseGroundContact.h"
#include "AnanseCatalogue.h"
#include "AnanseAuthoredAnimation.h"
#include "AbilitySystemComponent.h"
#include "AIController.h"
#include "Animation/AnimInstance.h"
#include "Animation/Skeleton.h"
#include "Components/BoxComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/LocalPlayer.h"
#include "Engine/SkeletalMesh.h"
#include "EngineUtils.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Json.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "TimerManager.h"
#include "Containers/Ticker.h"
#include "RHI.h"
#include "Trace/Trace.h"
#include "ProfilingDebugging/TraceAuxiliary.h"

void AAnanseLabController::TickCrossFamily(float DeltaSeconds)
{
#if !UE_BUILD_SHIPPING
 FString File;if(bCrossDone || !FParse::Value(FCommandLine::Get(),TEXT("AnanseCrossFamilyVerify="),File))return;
 const bool Aso=FParse::Param(FCommandLine::Get(),TEXT("AnanseCrossAso"));const FName Other=Aso?FName(TEXT("aso-yaa-human-v1")):FName(TEXT("osebo-leopard-v1"));
 CrossAge+=DeltaSeconds;
 auto Negative=[&](const TCHAR* Name,bool Passed)
 {auto Check=MakeShared<FJsonObject>();Check->SetStringField(TEXT("check"),Name);Check->SetBoolField(TEXT("passed"),Passed);CrossNegativeChecks.Add(MakeShared<FJsonValueObject>(Check));bCrossFailed|=!Passed;};
 auto SelectNext=[&]()
 {
  auto* Current=Cast<AAnansePlayer>(GetPawn());
  if(!Current){bCrossFailed=true;CrossStage=4;return;}
  CrossExpected=(CrossCommitted%2==0)?Other:FName(TEXT("ananse-spider-existing"));
  CrossOldPawn=Current->GetUniqueID();CrossPhaseStart=CrossAge;
  if(!SelectDesign(CrossExpected)){bCrossFailed=true;CrossStage=4;}else CrossStage=2;
 };
 if(CrossAge>110){bCrossFailed=true;CrossStage=4;}
 if(CrossStage==0)
 {
  if(GetWorld()->GetPathName()!=TEXT("/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab.L_AnanseCharacterLab"))
  {bCrossFailed=true;CrossStage=4;}
  else
  {
   const APawn* Prior=GetPawn();Negative(TEXT("unknown_design_retained"),!SelectDesign(TEXT("not-allowlisted")) && GetPawn()==Prior);
   CrossPhaseStart=CrossAge;
   if(FParse::Param(FCommandLine::Get(),TEXT("AnanseCrossRestoreCheck")))
   {if(!LoadSelection())bCrossFailed=true;CrossStage=10;}
   else {if(!SelectDesign(TEXT("ananse-spider-existing")))bCrossFailed=true;CrossStage=1;}
  }
 }
 else if(CrossStage==10 && !Pending)
 {
  FString Expected=TEXT("osebo-leopard-v1");FParse::Value(FCommandLine::Get(),TEXT("AnanseCrossExpectedRestore="),Expected);
  if(!bRestoredProfile || SelectedDesign!=FName(*Expected))bCrossFailed=true;
  CrossRestoredDesign=SelectedDesign;
  if(!SelectDesign(TEXT("ananse-spider-existing")))bCrossFailed=true;
  CrossStage=1;CrossPhaseStart=CrossAge;
 }
 else if(CrossStage==1 && !Pending)
 {
  auto* Player=Cast<AAnanseSpiderLabPlayer>(GetPawn());
  if(!Player || SelectedDesign!=TEXT("ananse-spider-existing")){bCrossFailed=true;CrossStage=4;}
  else
  {
   CrossOldPawn=Player->GetUniqueID();TestSelectionFault=1;
   SelectDesign(Other);CrossStage=20;CrossPhaseStart=CrossAge;
  }
 }
 else if(CrossStage>=20 && CrossStage<=22 && !Pending)
 {
  APawn* Current=GetPawn();const bool Retained=Current && Current->GetUniqueID()==CrossOldPawn && SelectedDesign==TEXT("ananse-spider-existing");
  if(!Current){bCrossFailed=true;CrossStage=4;return;}
  if(CrossStage==20)
  {Negative(TEXT("missing_asset_retained"),Retained);TestSelectionFault=2;SelectDesign(Other);CrossStage=21;}
  else if(CrossStage==21)
  {
   Negative(TEXT("incompatible_rig_retained"),Retained);
   AActor* Blocker=GetWorld()->SpawnActor<AActor>();TestSpawnBlocker=Blocker;
   auto* Box=NewObject<UBoxComponent>(Blocker);Box->SetBoxExtent(FVector(1000));
   Box->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);Box->SetCollisionResponseToAllChannels(ECR_Block);
   Blocker->SetRootComponent(Box);Box->RegisterComponent();Blocker->SetActorLocation(Current->GetActorLocation()+FVector(5000,0,1000));
   TestSelectionFault=3;SelectDesign(Other);CrossStage=22;
  }
  else
  {
   Negative(TEXT("blocked_spawn_retained"),Retained);if(TestSpawnBlocker.IsValid())TestSpawnBlocker->Destroy();TestSpawnBlocker.Reset();TestSelectionFault=0;
   SelectDesign(Other);const uint64 Stale=Generation;CancelSelection();
   Negative(TEXT("cancel_retained"),GetPawn()==Current && !Pending);
   CrossStaleBefore=RejectedStaleCompletions;
   bTestLateCompletionFired=false;
   FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,FTimerDelegate::CreateWeakLambda(this,[this,Stale,Other](){bTestLateCompletionFired=true;FinishSelection(Stale,Other);}),.1f,false);
   SelectDesign(Other);SelectDesign(TEXT("ananse-spider-existing"));CrossStage=23;
  }
  CrossPhaseStart=CrossAge;
 }
 else if(CrossStage==23 && !Pending && CrossAge-CrossPhaseStart>.3f)
 {
  Negative(TEXT("latest_request_won"),SelectedDesign==TEXT("ananse-spider-existing") && Cast<AAnanseSpiderLabPlayer>(GetPawn()));
  Negative(TEXT("late_completion_rejected"),bTestLateCompletionFired && RejectedStaleCompletions>CrossStaleBefore);
  SelectNext();
 }
 else if(CrossStage==2 && !Pending)
 {
  auto* Player=Cast<AAnansePlayer>(GetPawn());
  if(!Player || Player->GetUniqueID()==CrossOldPawn || SelectedDesign!=CrossExpected)
  {bCrossFailed=true;CrossStage=4;}
  else
  {
   if(auto* Spider=Cast<AAnanseSpiderLabPlayer>(Player))Spider->PlayProxyClip(1);
   else if(auto* Leopard=Cast<AAnanseLeopardLabPlayer>(Player))Leopard->HoldLeopardClip(7);
   else if(auto* CastPawn=Cast<AAnanseCastLabPlayer>(Player))CastPawn->HoldAuthoredClip(6);
   else bCrossFailed=true;
   CrossPosition=Player->GetActorLocation();CrossPhaseStart=CrossAge;bCrossPoseReady=false;bCrossPhoto=false;CrossStage=3;
  }
 }
 else if(CrossStage==3)
 {
  auto* Player=Cast<AAnansePlayer>(GetPawn());
  if(!Player){bCrossFailed=true;CrossStage=4;}
  else
  {
   const float Age=CrossAge-CrossPhaseStart;
   if(Age>.2f && !bCrossPoseReady){CrossPose=Player->GetMesh()->GetComponentSpaceTransforms();bCrossPoseReady=true;}
   // Keep selection stress on its declared clear flat fixture. Terrain traversal
   // and the intentionally obstructed-spawn case have separate assertions.
   if(Age>.2f && Age<.6f)Player->AddMovementInput(FVector::ForwardVector,CrossPosition.X>30?-1.f:1.f);
   if(Age>.7f && CrossCommitted==38 && !bCrossPhoto)
   {bCrossPhoto=true;SetControlRotation(FRotator(-8,180,0));FScreenshotRequest::RequestScreenshot(FPaths::GetPath(File)/(Aso?TEXT("aso.png"):TEXT("leopard.png")),true,false);}
   if(Age>=1.f)
   {
    auto* Mesh=Player->GetMesh();bool Motion=false,Finite=true;
    const auto& Pose=Mesh->GetComponentSpaceTransforms();
    for(const auto& Transform:Pose)if(Transform.ContainsNaN() || !Transform.IsRotationNormalized())Finite=false;
    if(bCrossPoseReady && Pose.Num()==CrossPose.Num())for(int32 I=1;I<Pose.Num();++I)
     if(Pose[I].GetRotation().AngularDistance(CrossPose[I].GetRotation())>.0001f)Motion=true;
    const float Moved=FVector::Dist2D(CrossPosition,Player->GetActorLocation());
    int32 Pawns=0,AIs=0;for(TActorIterator<AAnansePlayer> It(GetWorld());It;++It)if(!It->IsActorBeingDestroyed())++Pawns;
    for(TActorIterator<AAIController> It(GetWorld());It;++It)if(!It->IsActorBeingDestroyed())++AIs;
    auto* Sub=GetLocalPlayer()?ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()):nullptr;
    bool Valid=Player->GetController()==this && GetViewTarget()==Player && Pawns==1 && AIs==0 && Motion && Finite && Moved>.5f && Sub && Sub->HasMappingContext(Player->GetOwnedInputMapping()) && Player->Abilities->GetActivatableAbilities().Num()==0;
    if(Sub)for(const auto& Old:VerifyMappings)if(Old.IsValid() && Old.Get()!=Player->GetOwnedInputMapping() && Sub->HasMappingContext(Old.Get()))Valid=false;
    VerifyMappings.AddUnique(Player->GetOwnedInputMapping());
    auto* Spider=Cast<AAnanseSpiderLabPlayer>(Player);auto* Leopard=Cast<AAnanseLeopardLabPlayer>(Player);auto* CastPawn=Cast<AAnanseCastLabPlayer>(Player);
    const bool AsoContacts=CastPawn&&CastPawn->LiveContacts&&CastPawn->LiveContacts->bReady&&CastPawn->LiveContacts->SolvedChains==2;
    const bool FelineContacts=Leopard && Leopard->LiveContacts && Leopard->LiveContacts->bReady && Leopard->LiveContacts->SolvedChains==2;
    if(Leopard)Valid &= FelineContacts;if(Aso&&CastPawn)Valid &= AsoContacts;
    const bool IsSpider=CrossExpected==TEXT("ananse-spider-existing");
    int32 GraphEvaluations=0;bool GraphClip=false;
    if(const auto* Anim=Cast<UAnanseContactAnimInstance>(Mesh->GetAnimInstance()))
    {GraphEvaluations=Anim->GraphEvaluations;GraphClip=Anim->bUseAuthoredGraph && Anim->EvaluatedGraphClip==Anim->Clip;}
    if(const auto* Anim=Cast<UAnanseLeopardAnimInstance>(Mesh->GetAnimInstance()))
    {GraphEvaluations=Anim->GraphEvaluations;GraphClip=Anim->EvaluatedGraphClip==Anim->Clip;}
    Valid &= GraphEvaluations>0 && GraphClip;
    Valid &= IsSpider?(Spider && Spider->GroundContact && Spider->GroundContact->ResetCount>0 && Spider->GroundContact->LastSolvedChains==4):(Aso?(CastPawn&&CastPawn->bFamilyReady&&CastPawn->DesignId==Other&&!CastPawn->FindComponentByClass<UAnanseGroundContact>()):(Leopard && Leopard->bFamilyReady && !Leopard->FindComponentByClass<UAnanseGroundContact>()));
    Valid &= Mesh->GetSkeletalMeshAsset() && Mesh->GetAnimInstance() && Mesh->GetSkeletalMeshAsset()->GetRefSkeleton().GetNum()==(IsSpider?102:Aso?48:64);
    auto Entry=MakeShared<FJsonObject>();Entry->SetNumberField(TEXT("transition"),CrossCommitted+1);Entry->SetBoolField(TEXT("passed"),Valid);
    Entry->SetStringField(TEXT("requested_design"),CrossExpected.ToString());Entry->SetStringField(TEXT("committed_design"),SelectedDesign.ToString());
    Entry->SetStringField(TEXT("pawn_class"),Player->GetClass()->GetPathName());Entry->SetNumberField(TEXT("possessed_pawn_id"),Player->GetUniqueID());
    Entry->SetStringField(TEXT("mesh"),Mesh->GetSkeletalMeshAsset()->GetPathName());Entry->SetStringField(TEXT("skeleton"),Mesh->GetSkeletalMeshAsset()->GetSkeleton()->GetPathName());
    Entry->SetStringField(TEXT("animation_instance"),Mesh->GetAnimInstance()->GetClass()->GetPathName());
    Entry->SetStringField(TEXT("physics"),Mesh->GetPhysicsAsset()?Mesh->GetPhysicsAsset()->GetPathName():TEXT("missing"));
    Entry->SetBoolField(TEXT("input_mapping_active"),Sub && Sub->HasMappingContext(Player->GetOwnedInputMapping()));
    Entry->SetBoolField(TEXT("camera_bound"),GetViewTarget()==Player);Entry->SetBoolField(TEXT("evaluated_gesture_motion"),Motion);Entry->SetNumberField(TEXT("movement_cm"),Moved);
    if(const auto* A=Cast<UAnanseContactAnimInstance>(Mesh->GetAnimInstance())){Entry->SetNumberField(TEXT("secondary_bones"),A->SecondaryBoneCount);Entry->SetNumberField(TEXT("secondary_evaluations"),A->SecondaryEvaluations);Entry->SetNumberField(TEXT("secondary_peak_degrees"),A->SecondaryPeakDegrees);Entry->SetNumberField(TEXT("secondary_resets"),A->SecondaryResets);}
    if(const auto* A=Cast<UAnanseLeopardAnimInstance>(Mesh->GetAnimInstance())){Entry->SetNumberField(TEXT("secondary_bones"),A->SecondaryBoneCount);Entry->SetNumberField(TEXT("secondary_evaluations"),A->SecondaryEvaluations);Entry->SetNumberField(TEXT("secondary_peak_degrees"),A->SecondaryPeakDegrees);Entry->SetNumberField(TEXT("secondary_resets"),A->SecondaryResets);}
    Entry->SetNumberField(TEXT("graph_evaluations"),GraphEvaluations);Entry->SetBoolField(TEXT("graph_clip_observed"),GraphClip);
    Entry->SetNumberField(TEXT("resident_memory_bytes"),double(FPlatformMemory::GetStats().UsedPhysical));
    Entry->SetBoolField(TEXT("aso_contacts_rebuilt"),AsoContacts);Entry->SetBoolField(TEXT("feline_contacts_rebuilt"),FelineContacts);
    if(Leopard)Entry->SetStringField(TEXT("feline_contact_metrics"),Leopard->LiveContacts->MetricsJson());
    Entry->SetBoolField(TEXT("finite_pose"),Finite);
    Entry->SetBoolField(TEXT("spider_contacts_rebuilt"),IsSpider && Spider && Spider->GroundContact->ResetCount>0);
    CrossTransitions.Add(MakeShared<FJsonValueObject>(Entry));bCrossFailed|=!Valid;++CrossCommitted;
    Player->GetCharacterMovement()->StopMovementImmediately();
    if(CrossCommitted<40)SelectNext();
    else {if(!SaveSelection())bCrossFailed=true;if(Spider)Spider->PlayProxyClip(0);CrossStage=4;}
   }
  }
 }
 if(CrossStage!=4 && CrossAge-CrossPhaseStart>15){bCrossFailed=true;CrossStage=4;}
 if(CrossStage==4 && CrossAge>=60)
 {
  bCrossDone=true;TestSelectionFault=0;
  const auto* View=GetWorld()->GetGameViewport();const bool Rendered=View && GDynamicRHI && FString(GDynamicRHI->GetName())==TEXT("Vulkan") && View->ViewModeIndex==VMI_Lit && View->EngineShowFlags.Lighting && !View->EngineShowFlags.Wireframe && !View->EngineShowFlags.ShaderComplexity && !PreviewMesh.IsValid();
  bCrossFailed |= !Rendered || CrossCommitted!=40 || CrossNegativeChecks.Num()!=7;
  auto Report=MakeShared<FJsonObject>();Report->SetStringField(TEXT("other_design"),Other.ToString());Report->SetBoolField(TEXT("passed"),!bCrossFailed);Report->SetNumberField(TEXT("seconds"),CrossAge);
  Report->SetStringField(TEXT("selection_status"),SelectionStatus);
  Report->SetStringField(TEXT("stress_fixture"),TEXT("Bounded flat-floor walk; ramp/step locomotion is a separate terrain gate"));
  Report->SetStringField(TEXT("world"),GetWorld()->GetPathName());
  if(const auto* Catalogue=GetGameInstance()->GetSubsystem<UAnanseCatalogue>())Report->SetStringField(TEXT("loaded_publication_hash"),Catalogue->ContentHash);
  Report->SetNumberField(TEXT("committed_cross_family_transitions"),CrossCommitted);Report->SetNumberField(TEXT("complete_round_trips"),CrossCommitted/2);
  Report->SetArrayField(TEXT("transitions"),CrossTransitions);Report->SetArrayField(TEXT("negative_checks"),CrossNegativeChecks);
  Report->SetBoolField(TEXT("normal_lit_rendering"),Rendered);Report->SetStringField(TEXT("restored_design"),CrossRestoredDesign.ToString());
  Report->SetBoolField(TEXT("restored_profile_committed"),bRestoredProfile);Report->SetNumberField(TEXT("rejected_stale_completions"),RejectedStaleCompletions);
  if(auto* Spider=Cast<AAnanseSpiderLabPlayer>(GetPawn()))Report->SetStringField(TEXT("post_return_contact_metrics"),Spider->GroundContact->MetricsJson());
  Report->SetStringField(TEXT("input_scope"),TEXT("Native requests and simulated movement; late callback is an adversarial timed production-handler completion. No physical controller/touch claim."));
  Report->SetBoolField(TEXT("full_character_acceptance"),false);Report->SetStringField(TEXT("open_gates"),Aso?TEXT("Aso creative/prop contact, broader terrain, long memory and physical devices"):TEXT("Feline contact accuracy, Control Rig authoring qualification, publication and creative approval"));
  FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(Report,Writer);FFileHelper::SaveStringToFile(Json,*File);
  SetControlRotation(FRotator(-8,180,0));FScreenshotRequest::RequestScreenshot(FPaths::ChangeExtension(File,TEXT("png")),true,false);
  const double Finish=FPlatformTime::Seconds()+2;
  FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Finish,Failed=bCrossFailed](float)
  {
   if(FPlatformTime::Seconds()<Finish)return true;
#if UE_TRACE_ENABLED
   FTraceAuxiliary::Pause();FTraceAuxiliary::Stop();UE::Trace::Shutdown();
#endif
   FPlatformMisc::RequestExitWithStatus(false,Failed?2:0,TEXT("Cross-family selection verification complete"));return false;
  }));
 }
#endif
}
