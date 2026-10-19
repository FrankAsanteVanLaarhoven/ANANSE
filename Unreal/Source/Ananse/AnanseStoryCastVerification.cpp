#include "AnanseLabSelection.h"
#include "Engine/PointLight.h"
#include "Components/PointLightComponent.h"
#include "HAL/FileManager.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"
#include "AnanseCastLab.h"
#include "AnanseCatalogue.h"
#include "AnanseSpiderLab.h"
#include "AnanseLeopardLab.h"
#include "AnanseGroundContact.h"
#include "AnanseLeopardContact.h"
#include "AbilitySystemComponent.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Engine/Engine.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "Camera/CameraActor.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Components/StaticMeshComponent.h"
#include "Json.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Containers/Ticker.h"
#include "RHI.h"
#include "Trace/Trace.h"
#include "ProfilingDebugging/TraceAuxiliary.h"
void AAnanseLabController::TickStoryCast(float Delta)
{
#if !UE_BUILD_SHIPPING
 FString File;if(bStoryDone||!FParse::Value(FCommandLine::Get(),TEXT("AnanseStoryCastVerify="),File))return;
 TArray<FName> Designs={TEXT("kwaku-human-v1"),TEXT("aso-yaa-human-v1"),TEXT("esi-human-v1"),TEXT("osebo-human-v1"),TEXT("kojo-tortoise-v1"),TEXT("kofi-hornbill-v1"),TEXT("esi-moth-v1")};
 if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoOnly")))Designs={TEXT("aso-yaa-human-v1")};
 const FName Base=FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoWithKwaku"))?FName(TEXT("kwaku-human-v1")):FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoWithLeopard"))?FName(TEXT("osebo-leopard-v1")):FName(TEXT("ananse-spider-existing"));
 StoryAge+=Delta;StoryPhaseAge+=Delta;
 static bool ProfileSaved=false,ProfileRestoreStarted=false,ProfileRestored=false;
 static double LastFrame=-1;static TArray<TSharedPtr<FJsonValue>> CapturedFrames;
 if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoCapture"))&&StoryAge-LastFrame>=.5)
 {
  const FString Folder=FPaths::GetPath(File)/TEXT("frames");IFileManager::Get().MakeDirectory(*Folder,true);
  const FString Name=FString::Printf(TEXT("aso_frame_%04d.png"),CapturedFrames.Num());FScreenshotRequest::RequestScreenshot(Folder/Name,true,false);
  auto Frame=MakeShared<FJsonObject>();Frame->SetStringField(TEXT("png"),Name);Frame->SetNumberField(TEXT("elapsed_seconds"),StoryAge);CapturedFrames.Add(MakeShared<FJsonValueObject>(Frame));LastFrame=StoryAge;
 }

 auto Begin=[&](FName Id,int32 Stage){StoryPhaseAge=0;if(!SelectDesign(Id)){bStoryFailed=true;StoryStage=99;}else StoryStage=Stage;};
 auto CountControlled=[&](){int32 Count=0;for(TActorIterator<APawn> It(GetWorld());It;++It)if(It->GetController()==this)++Count;return Count;};
 const bool FullClips=FParse::Param(FCommandLine::Get(),TEXT("AnanseStoryFullClips"));
 if(StoryAge>(FullClips?600.f:200.f)){bStoryFailed=true;StoryStage=99;}
 if(StoryStage==0)
 {
  if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoRestoreProfile"))&&!ProfileRestored)
  {
   if(!ProfileRestoreStarted){ProfileRestoreStarted=true;LoadSelection();return;}
   if(Pending)return;
   if(SelectedDesign!=TEXT("aso-yaa-human-v1")){bStoryFailed=true;StoryStage=99;}
   else ProfileRestored=true;
  }
  if(StoryStage==0)Begin(Base,1);
 }
 else if(StoryStage==1&&!Pending){Begin(Designs[StoryIndex],2);}
 else if(StoryStage==2&&!Pending&&StoryPhaseAge>.2f)
 {
  auto* P=Cast<AAnanseCastLabPlayer>(GetPawn());
  if(!P||!P->bFamilyReady||P->DesignId!=Designs[StoryIndex]||SelectedDesign!=P->DesignId||CountControlled()!=1||P->Abilities->GetActivatableAbilities().Num()!=0)
  {bStoryFailed=true;StoryStage=99;}
  else
  {
   StoryStart=P->GetActorLocation();StoryClipIndex=0;StoryPhaseAge=0;StoryPose=P->GetMesh()->GetComponentSpaceTransforms();StoryClipChecks.Reset();StoryMaxBlink=0;bStoryLedgerObserved=false;bStoryLedgerCaptured=false;bStoryLedgerResetTested=false;bStoryClipMotion=false;P->HoldAuthoredClip(0);StoryStage=3;
   P->CameraBoom->TargetArmLength=P->AuthoringHeight*1.55f;P->CameraBoom->SocketOffset=FVector(0,0,P->AuthoringHeight*.20f);SetControlRotation(FRotator(-8,180,0));if(P->bRefinedFace&&FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPortrait"))){P->CameraBoom->TargetArmLength=45;if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2")))P->Camera->SetFieldOfView(40.f);P->CameraBoom->SocketOffset=FVector(0,0,58);SetControlRotation(FRotator(0,180,0));if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2"))){P->CameraBoom->TargetArmLength=85;P->CameraBoom->SocketOffset=FVector(0,0,P->GetMesh()->GetSocketLocation(TEXT("head")).Z+11.f-P->GetActorLocation().Z);}}
  }
 }
 else if(StoryStage==3)
 {
  auto* P=Cast<AAnanseCastLabPlayer>(GetPawn());if(!P){bStoryFailed=true;StoryStage=99;}
  else
  {
   auto* Anim=Cast<UAnanseCastAnimInstance>(P->GetMesh()->GetAnimInstance());StoryMaxBlink=FMath::Max(StoryMaxBlink,P->AppliedBlink);
   P->AddMovementInput(FVector(0,StoryIndex%2?-1:1,0),.6f);if(P->bRefinedFace&&FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPortrait")))
   {
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2"))&&!bStoryLedgerObserved)
    {
     P->Camera->SetFieldOfView(40.f);P->CameraBoom->TargetArmLength=85.f;
     P->CameraBoom->SocketOffset=FVector(0,0,P->GetMesh()->GetSocketLocation(TEXT("head")).Z+11.f-P->GetActorLocation().Z);
     SetControlRotation(FRotator(0,P->GetActorRotation().Yaw+180.f,0));
    }
    if(P->AppliedBlink<.01f&&!bArtOpenCaptured){FScreenshotRequest::RequestScreenshot(FPaths::GetPath(File)/TEXT("kwaku-eyes-open.png"),true,false);bArtOpenCaptured=true;}
    if(P->AppliedBlink>.97f&&!bArtClosedCaptured){FScreenshotRequest::RequestScreenshot(FPaths::GetPath(File)/TEXT("kwaku-eyelids-closed.png"),true,false);bArtClosedCaptured=true;}
   }
   if(P->bAsoLedgerPresentation&&StoryClipIndex==4&&P->LedgerVisual)
   {
    P->Camera->SetFieldOfView(45.f);P->CameraBoom->TargetArmLength=120.f;P->CameraBoom->SocketOffset=FVector(0,0,P->LedgerVisual->GetComponentLocation().Z+12.f-P->CameraBoom->GetComponentLocation().Z);SetControlRotation(FRotator(0,P->GetActorRotation().Yaw+180.f,0));
   }
   else if(P->bAsoLedgerPresentation){P->Camera->SetFieldOfView(70.f);P->CameraBoom->TargetArmLength=P->AuthoringHeight*1.55f;const float Mid=(P->GetMesh()->GetSocketLocation(TEXT("head")).Z+10.f+(P->GetMesh()->GetSocketLocation(TEXT("foot_L")).Z+P->GetMesh()->GetSocketLocation(TEXT("foot_R")).Z)*.5f)*.5f;P->CameraBoom->SocketOffset=FVector(0,0,Mid-P->CameraBoom->GetComponentLocation().Z);SetControlRotation(FRotator(0,P->GetActorRotation().Yaw+180.f,0));}
   const auto& Pose=P->GetMesh()->GetComponentSpaceTransforms();
   for(int32 I=0;I<Pose.Num();++I){if(Pose[I].ContainsNaN())bStoryFailed=true;if(StoryPose.IsValidIndex(I)&&!Pose[I].Equals(StoryPose[I],.001f))bStoryClipMotion=true;}
   const bool ObserveLedger=P->bLedgerPresentation&&StoryClipIndex==8;
   if(ObserveLedger&&P->bLedgerLatched&&P->LedgerVisual&&P->LedgerVisual->IsVisible()&&P->LedgerVisual->GetStaticMesh()&&P->LedgerVisual->GetAttachParent()==P->GetMesh()&&P->LedgerVisual->GetAttachSocketName()==TEXT("hand_R")&&P->LedgerVisual->GetCollisionEnabled()==ECollisionEnabled::NoCollision)
   {
    if(!bStoryLedgerObserved){if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2")))P->Camera->SetFieldOfView(60.f);P->CameraBoom->TargetArmLength=120;P->CameraBoom->SocketOffset=FVector(0,0,25);SetControlRotation(FRotator(-8,P->GetActorRotation().Yaw+180,0));}
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2")))
    {
     P->Camera->SetFieldOfView(55.f);P->CameraBoom->TargetArmLength=160.f;
     const float FramingZ=(P->GetMesh()->GetSocketLocation(TEXT("head")).Z+11.f+P->LedgerVisual->GetComponentLocation().Z)*.5f;
     P->CameraBoom->SocketOffset=FVector(0,0,FramingZ-P->GetActorLocation().Z);SetControlRotation(FRotator(0,P->GetActorRotation().Yaw+180.f,0));
    }
    if(StoryPhaseAge>1.2f&&!bStoryLedgerCaptured)
    {
     FScreenshotRequest::RequestScreenshot(FPaths::GetPath(File)/TEXT("kwaku-ledger.png"),true,false);bStoryLedgerCaptured=true;
     if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2")))
     {
      auto View=MakeShared<FJsonObject>();View->SetNumberField(TEXT("horizontal_fov_degrees"),P->Camera->FieldOfView);View->SetNumberField(TEXT("equivalent_36mm_focal_length_mm"),18.f/FMath::Tan(FMath::DegreesToRadians(P->Camera->FieldOfView*.5f)));View->SetStringField(TEXT("actual_camera_world_cm"),P->Camera->GetComponentLocation().ToString());View->SetStringField(TEXT("evaluated_head_world_cm"),P->GetMesh()->GetSocketLocation(TEXT("head")).ToString());View->SetNumberField(TEXT("actual_camera_to_head_cm"),FVector::Dist(P->Camera->GetComponentLocation(),P->GetMesh()->GetSocketLocation(TEXT("head"))));for(TActorIterator<APostProcessVolume> Volume(P->GetWorld());Volume;++Volume)if(Volume->Priority>=100.f&&Volume->bUnbound){View->SetNumberField(TEXT("exposure_compensation_stops"),Volume->Settings.AutoExposureBias);View->SetNumberField(TEXT("exposure_method"),int32(Volume->Settings.AutoExposureMethod));View->SetBoolField(TEXT("physical_camera_exposure"),Volume->Settings.AutoExposureApplyPhysicalCameraExposure);View->SetNumberField(TEXT("motion_blur_amount"),Volume->Settings.MotionBlurAmount);break;}FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(View,Writer);FFileHelper::SaveStringToFile(Text,*(FPaths::GetPath(File)/TEXT("kwaku-camera.json")));
     }
     auto Probe=MakeShared<FJsonObject>();Probe->SetNumberField(TEXT("animation_time"),Anim?Anim->EvaluatedTime:-1);Probe->SetNumberField(TEXT("body_z"),P->LiveContacts?P->LiveContacts->Snapshot.BodyZ:0);Probe->SetStringField(TEXT("prop_component_location"),P->GetMesh()->GetComponentTransform().InverseTransformPosition(P->LedgerVisual->GetComponentLocation()).ToString());
     for(const TCHAR* Name:{TEXT("upperarm_L"),TEXT("lowerarm_L"),TEXT("hand_L"),TEXT("upperarm_R"),TEXT("lowerarm_R"),TEXT("hand_R"),TEXT("digit_R_2_01"),TEXT("digit_R_2_02")}){const int32 Index=P->AuthoredMesh->GetRefSkeleton().FindBoneIndex(Name);if(Pose.IsValidIndex(Index))Probe->SetStringField(Name,Pose[Index].GetTranslation().ToString());}
     FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Probe,Writer);FFileHelper::SaveStringToFile(Text,*(FPaths::GetPath(File)/TEXT("ledger-evaluated-pose.json")));
    }
    bStoryLedgerObserved=true;
   }
   if(ObserveLedger&&bStoryLedgerCaptured&&StoryPhaseAge>1.35f&&!bStoryLedgerResetTested)
   {
    const bool WasVisible=P->LedgerVisual->IsVisible();P->ResetTransientMotion();const bool Cleared=WasVisible&&!P->bLedgerLatched&&!P->LedgerVisual->IsVisible()&&P->ActiveClip==0;bStoryFailed|=!Cleared;bStoryLedgerResetTested=true;P->HoldAuthoredClip(8);StoryPhaseAge=0;bStoryClipMotion=false;StoryPose=P->GetMesh()->GetComponentSpaceTransforms();
   }
   if(StoryPhaseAge>((FullClips||ObserveLedger)?P->AuthoredClips[StoryClipIndex]->GetPlayLength()+.15f:.40f))
   {
    const bool Passed=Anim&&Anim->Evaluations>2&&Anim->EvaluatedClip==P->AuthoredClips[StoryClipIndex]&&bStoryClipMotion&&(!ObserveLedger||bStoryLedgerObserved);
    auto C=MakeShared<FJsonObject>();C->SetStringField(TEXT("clip"),P->AuthoredClips[StoryClipIndex]->GetPathName());C->SetBoolField(TEXT("graph_and_pose_observed"),Passed);if(ObserveLedger){C->SetBoolField(TEXT("separate_ledger_attached_observed"),bStoryLedgerObserved);C->SetBoolField(TEXT("ledger_reset_cleared"),bStoryLedgerResetTested&&!bStoryFailed);}StoryClipChecks.Add(MakeShared<FJsonValueObject>(C));bStoryFailed|=!Passed;
    ++StoryClipIndex;StoryPhaseAge=0;bStoryClipMotion=false;StoryPose=Pose;
    if(StoryClipIndex<P->AuthoredClips.Num())P->HoldAuthoredClip(StoryClipIndex);
    else
    {
     auto R=MakeShared<FJsonObject>();if(Anim){R->SetNumberField(TEXT("secondary_bones"),Anim->SecondaryBoneCount);R->SetNumberField(TEXT("secondary_evaluations"),Anim->SecondaryEvaluations);R->SetNumberField(TEXT("secondary_peak_degrees"),Anim->SecondaryPeakDegrees);R->SetNumberField(TEXT("secondary_resets"),Anim->SecondaryResets);}TInlineComponentArray<UPointLightComponent*> CharacterReviewLights(P);R->SetNumberField(TEXT("character_review_light_components"),CharacterReviewLights.Num());if(P->bAsoLedgerPresentation){R->SetNumberField(TEXT("aso_ledger_samples"),P->AsoLedgerSamples);R->SetNumberField(TEXT("aso_ledger_phase_mask"),P->AsoLedgerPhaseMask);R->SetNumberField(TEXT("aso_ledger_max_binding_error_cm"),P->AsoLedgerMaxBindingErrorCm);bStoryFailed|=P->AsoLedgerSamples<30||P->AsoLedgerPhaseMask!=31||P->AsoLedgerMaxBindingErrorCm>.1f;}R->SetStringField(TEXT("design"),P->DesignId.ToString());if(P->bLedgerPresentation){R->SetBoolField(TEXT("separate_ledger_attached_observed"),bStoryLedgerObserved);R->SetBoolField(TEXT("ledger_reset_cleared"),bStoryLedgerResetTested&&!bStoryFailed);}R->SetStringField(TEXT("pawn_class"),P->GetClass()->GetPathName());R->SetStringField(TEXT("mesh"),P->AuthoredMesh->GetPathName());R->SetStringField(TEXT("skeleton"),P->AuthoredMesh->GetSkeleton()->GetPathName());R->SetStringField(TEXT("animation_instance"),Anim?Anim->GetClass()->GetPathName():TEXT("missing"));R->SetNumberField(TEXT("bones"),P->AuthoredMesh->GetRefSkeleton().GetNum());R->SetNumberField(TEXT("definition_revision"),LoadedDefinition?LoadedDefinition->Revision:0);if(P->bRefinedFace){const bool Bound=P->AuthoredMesh->FindMorphTarget(TEXT("Blink_L"))&&P->AuthoredMesh->FindMorphTarget(TEXT("Blink_R"));R->SetBoolField(TEXT("refined_face_bindings"),Bound);R->SetNumberField(TEXT("published_visual_revision"),P->DesignId==TEXT("aso-yaa-human-v1")?GetGameInstance()->GetSubsystem<UAnanseCatalogue>()->AsoVisualRevision:GetGameInstance()->GetSubsystem<UAnanseCatalogue>()->KwakuVisualRevision);if(P->bAsoLedgerPresentation)R->SetBoolField(TEXT("unpublished_development_review_override"),true);R->SetNumberField(TEXT("applied_blink_peak"),StoryMaxBlink);bStoryFailed|=!Bound||StoryMaxBlink<.75f;}R->SetStringField(TEXT("mesh_relative_transform"),P->GetMesh()->GetRelativeTransform().ToString());if(P->LiveContacts){R->SetNumberField(TEXT("body_height_offset_cm"),P->LiveContacts->Snapshot.BodyZ);R->SetStringField(TEXT("target_left"),P->LiveContacts->Snapshot.Target[0].ToString());R->SetStringField(TEXT("sole_offset_left"),P->LiveContacts->Snapshot.SoleOffset[0].ToString());}R->SetNumberField(TEXT("movement_cm"),FVector::Dist(P->GetActorLocation(),StoryStart));R->SetArrayField(TEXT("clips"),StoryClipChecks);if(P->LiveContacts){R->SetStringField(TEXT("flat_contact_metrics"),P->LiveContacts->MetricsJson());bStoryFailed|=!P->LiveContacts->bReady || P->LiveContacts->SolvedChains!=2;}StoryRecords.Add(MakeShared<FJsonValueObject>(R));
     bStoryFailed|=FVector::Dist(P->GetActorLocation(),StoryStart)<10;
     FScreenshotRequest::RequestScreenshot(FPaths::GetPath(File)/FString::Printf(TEXT("cast_%d.png"),StoryIndex),true,false);
     StoryRoundTrips=0;Begin(Base,4);
    }
   }
  }
 }
 else if(StoryStage==4&&!Pending&&StoryPhaseAge>.12f)
 {
  auto* P=Cast<AAnansePlayer>(GetPawn());bool Ready=false;
  if(Base==TEXT("ananse-spider-existing")){auto* Spider=Cast<AAnanseSpiderLabPlayer>(P);auto* Contacts=Spider?Spider->FindComponentByClass<UAnanseGroundContact>():nullptr;Ready=Contacts&&Contacts->LastSolvedChains==4;}
  else if(auto* CastPawn=Cast<AAnanseCastLabPlayer>(P))Ready=Base==TEXT("kwaku-human-v1")&&CastPawn->bFamilyReady&&CastPawn->DesignId==Base&&CastPawn->LiveContacts&&CastPawn->LiveContacts->SolvedChains==2;
  else if(auto* Leopard=Cast<AAnanseLeopardLabPlayer>(P))Ready=Base==TEXT("osebo-leopard-v1")&&Leopard->LiveContacts&&Leopard->LiveContacts->SolvedChains==2;
  if(P&&!Ready&&StoryPhaseAge<3.f)return;
  if(!P||SelectedDesign!=Base||!Ready||CountControlled()!=1){bStoryFailed=true;StoryStage=99;}
  else if(++StoryRoundTrips>=20)
  {
   StoryRecords.Last()->AsObject()->SetNumberField(TEXT("complete_round_trips"),StoryRoundTrips);
   if(++StoryIndex<Designs.Num())Begin(Designs[StoryIndex],2);else StoryStage=98;
  }
  else Begin(Designs[StoryIndex],5);
 }
 else if(StoryStage==5&&!Pending&&StoryPhaseAge>.12f)
 {
  auto* P=Cast<AAnanseCastLabPlayer>(GetPawn());
  if(!P||!P->bFamilyReady||P->DesignId!=Designs[StoryIndex]||CountControlled()!=1||!P->GetOwnedInputMapping()||P->Abilities->GetActivatableAbilities().Num()!=0){bStoryFailed=true;StoryStage=99;}
  else Begin(Base,4);
 }
 if(StoryStage==98&&FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoOnly"))&&!ProfileSaved)
 {
  if(Pending)return;
  if(SelectedDesign!=TEXT("aso-yaa-human-v1")){if(!SelectDesign(TEXT("aso-yaa-human-v1"))){bStoryFailed=true;StoryStage=99;}return;}
  SaveSelection();ProfileSaved=true;
 }
 if((StoryStage==98&&StoryAge>=60)||StoryStage==99)
 {
  bStoryDone=true;
  const FString WorldName=GetWorld()->GetPathName();int32 EnvironmentModules=0;
  for(TActorIterator<AStaticMeshActor> It(GetWorld());It;++It)if(UStaticMesh* Mesh=It->GetStaticMeshComponent()->GetStaticMesh())if(Mesh->GetPathName().StartsWith(TEXT("/Game/Ananse/Environments/Story_v001/")))++EnvironmentModules;
  const bool Environment=WorldName.Contains(TEXT("/Maps/Story_v001/"));
  if(Environment)
  {
   const bool Market=WorldName.Contains(TEXT("Market"));bStoryFailed|=EnvironmentModules!=(Market?4:3);
   if(auto* Overview=GetWorld()->SpawnActor<ACameraActor>())
   {const FVector Position=Market?FVector(2400,-3300,1800):FVector(900,-1100,700);Overview->SetActorLocation(Position);Overview->SetActorRotation((FVector(0,0,Market?150:200)-Position).Rotation());SetViewTarget(Overview);
    const FString Shot=FPaths::GetPath(File)/TEXT("environment_overview.png");const double At=FPlatformTime::Seconds()+.25;
    FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([At,Shot](float){if(FPlatformTime::Seconds()<At)return true;FScreenshotRequest::RequestScreenshot(Shot,true,false);return false;}));}
  }
  const bool Passed=!bStoryFailed&&StoryRecords.Num()==Designs.Num()&&!GUsingNullRHI;
  auto R=MakeShared<FJsonObject>();
  R->SetBoolField(TEXT("neutral_review_enabled"),FParse::Param(FCommandLine::Get(),TEXT("AnanseNeutralLabLighting")));
  TArray<TSharedPtr<FJsonValue>> ReviewLights;
  for(const auto& Actor:PreviewLights)if(auto* Fill=Cast<APointLight>(Actor.Get()))if(auto* Light=Cast<UPointLightComponent>(Fill->GetLightComponent()))
  {
   auto Row=MakeShared<FJsonObject>();Row->SetNumberField(TEXT("intensity_lumens"),Light->Intensity);
   Row->SetBoolField(TEXT("uses_lumens_units"),Light->IntensityUnits==ELightUnits::Lumens);
   Row->SetBoolField(TEXT("channel0"),Light->LightingChannels.bChannel0);
   Row->SetBoolField(TEXT("channel1"),Light->LightingChannels.bChannel1);
   ReviewLights.Add(MakeShared<FJsonValueObject>(Row));
  }
  R->SetArrayField(TEXT("neutral_review_lights"),ReviewLights);
  R->SetBoolField(TEXT("aso_profile_restored"),ProfileRestored);R->SetBoolField(TEXT("aso_profile_saved"),ProfileSaved);R->SetArrayField(TEXT("captured_frames"),CapturedFrames);R->SetStringField(TEXT("round_trip_base"),Base.ToString());R->SetBoolField(TEXT("passed"),Passed);R->SetStringField(TEXT("loaded_publication_hash"),GetGameInstance()->GetSubsystem<UAnanseCatalogue>()->ContentHash);R->SetNumberField(TEXT("published_kwaku_visual_revision"),GetGameInstance()->GetSubsystem<UAnanseCatalogue>()->KwakuVisualRevision);R->SetNumberField(TEXT("actual_environment_modules"),EnvironmentModules);R->SetStringField(TEXT("selection_status"),SelectionStatus);R->SetNumberField(TEXT("seconds"),StoryAge);R->SetArrayField(TEXT("designs"),StoryRecords);R->SetStringField(TEXT("world"),GetWorld()->GetPathName());R->SetBoolField(TEXT("creative_approved"),false);R->SetBoolField(TEXT("new_family_contact_qualified"),false);R->SetStringField(TEXT("input_scope"),TEXT("native simulated movement; no physical controller/touch claim"));R->SetBoolField(TEXT("complete_clip_cycles"),FullClips);FString Json;auto W=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(R,W);FFileHelper::SaveStringToFile(Json,*File);
  const double Finish=FPlatformTime::Seconds()+2;FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Finish,Passed](float){if(FPlatformTime::Seconds()<Finish)return true;
#if UE_TRACE_ENABLED
   FTraceAuxiliary::Pause();FTraceAuxiliary::Stop();UE::Trace::Shutdown();
#endif
   FPlatformMisc::RequestExitWithStatus(false,Passed?0:2,TEXT("Story cast qualification complete"));return false;}));
 }
#endif
}
