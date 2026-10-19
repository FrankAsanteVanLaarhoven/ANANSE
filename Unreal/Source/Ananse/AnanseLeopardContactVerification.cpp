#include "AnanseLeopardLab.h"
#include "AnanseLeopardContact.h"
#include "AnanseAuthoredAnimation.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/World.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/GameViewportClient.h"
#include "RHI.h"
#include "Json.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Containers/Ticker.h"
#include "ProfilingDebugging/TraceAuxiliary.h"
#include "Trace/Trace.h"

void AAnanseLeopardLabPlayer::TickContactQualification(float Dt)
{
#if !UE_BUILD_SHIPPING
 if(ContactQualificationFile.IsEmpty()||bContactQualificationDone||!LiveContacts||!LiveContacts->bReady)return;
 ContactQualificationSeconds+=Dt;const int32 Phase=FMath::Min(7,int32(ContactQualificationSeconds/20));
 const float Age=ContactQualificationSeconds-Phase*20;
 if(Phase!=ContactFixture)
 {
  ContactFixture=Phase;GetCharacterMovement()->StopMovementImmediately();
  // Explicit fixture relocation, not pose-driven collision correction. Transient
  // contacts are released before relocation and rebuilt after authoritative landing.
  ResetTransientMotion();SetActorLocation(FVector(-140,Phase<6?Phase*400:0,300),false,nullptr,ETeleportType::TeleportPhysics);
  if(Phase==4||Phase==5)SetActorLocation(FVector(0,Phase*400,200),false,nullptr,ETeleportType::TeleportPhysics);
  HoldLeopardClip(7);
 }
 if(Phase<4 && Age>2)
 {
  const float Target=FMath::Fmod(Age-2,14.f)<7?150.f:-140.f;
  if(FMath::Abs(Target-GetActorLocation().X)>6)AddMovementInput(FVector(Target>GetActorLocation().X?1:-1,0,0),1);
 }
 if(Phase==6 && Age>3 && !bContactJumped){Jump();bContactJumped=true;}
 if(Phase==7 && Age>3 && !bContactFlew)bContactFlew=StartWebFlight(GetActorLocation()+FVector(100,0,40));
 if(ContactQualificationSeconds<160)return;
 bContactQualificationDone=true;
 TSharedPtr<FJsonObject> M;auto Reader=TJsonReaderFactory<>::Create(LiveContacts->MetricsJson());FJsonSerializer::Deserialize(Reader,M);
 const bool ArtPass2=FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2"));
 const bool Visual=FParse::Param(FCommandLine::Get(),TEXT("AnanseVisualReview"));
 const bool Interaction=FParse::Param(FCommandLine::Get(),TEXT("AnanseInteractionRefinement"));
 const FString ExpectedMap=ArtPass2?TEXT("/Game/Ananse/Maps/ArtPass2_v003/L_LeopardArtContact"):Visual?TEXT("/Game/Ananse/Maps/Visual_v003/L_LeopardVisualContact"):Interaction?TEXT("/Game/Ananse/Maps/Interactions_v003/L_LeopardContactInteractions"):TEXT("/Game/Ananse/Maps/CharacterLabs/LeopardContact_v001/L_LeopardContactLab");
 const FString ExpectedMesh=ArtPass2?TEXT("/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/OseboLeopard.OseboLeopard"):Visual?TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v003/OseboLeopard.OseboLeopard"):Interaction?TEXT("/Game/Ananse/Characters/OseboLeopard/Interactions_v003/OseboLeopard.OseboLeopard"):TEXT("/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard");
 const bool FixtureBinding=GetWorld()->GetOutermost()->GetName()==ExpectedMap && GetMesh()->GetSkeletalMeshAsset() && GetMesh()->GetSkeletalMeshAsset()->GetPathName()==ExpectedMesh;
 bool Passed=M.IsValid() && FixtureBinding && bContactJumped && bContactFlew;
 if(M.IsValid())
 {
  Passed &= M->GetNumberField(TEXT("invalid_transforms"))==0 && M->GetNumberField(TEXT("solved_chains"))==2;
  for(const auto& Item:M->GetArrayField(TEXT("legs")))
  {
   const auto& L=Item->AsObject();Passed &= L->GetNumberField(TEXT("samples"))>100 && L->GetNumberField(TEXT("p95_stance_drift_cm"))<=2 && L->GetNumberField(TEXT("max_penetration_cm"))<=.5 && L->GetNumberField(TEXT("max_segment_length_error_cm"))<=.1;
   const auto& Coverage=L->GetObjectField(TEXT("support_sample_coverage"));
   for(const TCHAR* Name:{TEXT("flat"),TEXT("ramp"),TEXT("steps"),TEXT("uneven"),TEXT("moving"),TEXT("disappearing")})
   {double Count=0;Passed &= Coverage->TryGetNumberField(TEXT("AnanseFixture:")+FString(Name),Count)&&Count>100;}
  }
 }
 auto* Anim=Cast<UAnanseLeopardAnimInstance>(GetMesh()->GetAnimInstance());
 Passed &= Anim && Anim->EvaluatedGraphClip==LeopardClips[7] && Anim->GraphEvaluations>100;
 auto* View=GetWorld()->GetGameViewport();const bool Rendered=View && GDynamicRHI && FString(GDynamicRHI->GetName())==TEXT("Vulkan") && View->ViewModeIndex==VMI_Lit;Passed &= Rendered;
 auto R=MakeShared<FJsonObject>();R->SetBoolField(TEXT("passed"),Passed);R->SetBoolField(TEXT("fixture_binding_valid"),FixtureBinding);R->SetStringField(TEXT("expected_fixture_map"),ExpectedMap);R->SetStringField(TEXT("expected_fixture_mesh"),ExpectedMesh);R->SetNumberField(TEXT("seconds"),ContactQualificationSeconds);R->SetBoolField(TEXT("normal_lit_rendering"),Rendered);R->SetBoolField(TEXT("jump_started"),bContactJumped);R->SetBoolField(TEXT("web_transition_started"),bContactFlew);R->SetBoolField(TEXT("upper_body_graph_active"),Anim&&Anim->EvaluatedGraphClip==LeopardClips[7]);R->SetObjectField(TEXT("metrics"),M);R->SetStringField(TEXT("world"),GetWorld()->GetOutermost()->GetName());R->SetStringField(TEXT("mesh"),GetMesh()->GetSkeletalMeshAsset()->GetPathName());R->SetStringField(TEXT("fixture_protocol"),TEXT("8x20s; explicit relocations across flat,15deg ramp,10cm steps,5/10/15cm uneven,moving,disappearing,jump,WebStep transition. Controlled45cm/s walking. Source sole-plane markers; no full mesh collision acceptance."));
 R->SetNumberField(TEXT("evaluated_lod"),GetMesh()->GetPredictedLODLevel());R->SetNumberField(TEXT("available_lods"),GetMesh()->GetSkeletalMeshAsset()->GetLODNum());
 FString Text;auto W=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(R,W);FFileHelper::SaveStringToFile(Text,*ContactQualificationFile);
 FScreenshotRequest::RequestScreenshot(FPaths::ChangeExtension(ContactQualificationFile,TEXT("png")),true,false);
 const double Finish=FPlatformTime::Seconds()+2;
 FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Finish,Passed](float){if(FPlatformTime::Seconds()<Finish)return true;
#if UE_TRACE_ENABLED
 FTraceAuxiliary::Pause();FTraceAuxiliary::Stop();UE::Trace::Shutdown();
#endif
 FPlatformMisc::RequestExitWithStatus(false,Passed?0:2,TEXT("Feline contact fixture qualification complete"));return false;}));
#endif
}
