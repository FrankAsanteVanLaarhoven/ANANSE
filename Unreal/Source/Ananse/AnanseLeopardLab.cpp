#include "AnanseLeopardLab.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/Controller.h"
#include "AnanseLeopardContact.h"
#include "AnanseCatalogue.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/Material.h"
#include "Engine/GameInstance.h"
#include "AnanseAuthoredAnimation.h"
#include "AnanseLabSelection.h"
#include "AnanseMission.h"
#include "AnanseWorld.h"
#include "Animation/AnimSequence.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "AbilitySystemComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Animation/Skeleton.h"
#include "RHI.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Containers/Ticker.h"
#include "ProfilingDebugging/TraceAuxiliary.h"
#include "Trace/Trace.h"

AAnanseLeopardLabPlayer::AAnanseLeopardLabPlayer()
{
 CharacterId=TEXT("osebo");bLabSelectionPawn=true;
 AutoPossessAI=EAutoPossessAI::Disabled;
 GetCapsuleComponent()->InitCapsuleSize(38,104);
 GetCharacterMovement()->MaxWalkSpeed=45;
 GetCharacterMovement()->RotationRate=FRotator(0,100,0);
 GetMesh()->SetRelativeLocation(FVector(0,0,-104));
 GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);
 GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
}
void AAnanseLeopardLabPlayer::BeginPlay()
{
 Super::BeginPlay();
 Body->SetVisibility(false);Head->SetVisibility(false);
 if(LeopardMesh)GetMesh()->SetSkeletalMesh(LeopardMesh);
 USkeletalMesh* Mesh=GetMesh()->GetSkeletalMeshAsset();
 bFamilyReady=Mesh && Mesh->GetSkeleton() && LeopardClips.Num()==9;
 if(bFamilyReady)
 {
  const FReferenceSkeleton& Ref=Mesh->GetRefSkeleton();
  for(const TCHAR* Bone:{TEXT("root"),TEXT("pelvis"),TEXT("head"),TEXT("hand_L"),TEXT("hand_R"),TEXT("foot_L"),TEXT("foot_R"),TEXT("tail_06"),TEXT("ear_L"),TEXT("ear_R")})
   bFamilyReady &= Ref.FindBoneIndex(Bone)!=INDEX_NONE;
  for(UAnimSequence* Clip:LeopardClips)bFamilyReady &= Clip && Clip->GetSkeleton()==Mesh->GetSkeleton();
 }
 if(!bFamilyReady)
 {
  GetMesh()->SetVisibility(false);GetCharacterMovement()->DisableMovement();
  Mission->Message(TEXT("OseboLeopard unavailable: actual feline mesh/skeleton/nine clips required. No primitive fallback."));return;
 }
 GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);
 UClass* AnimClass=LoadClass<UAnanseLeopardAnimInstance>(nullptr,TEXT("/Game/Ananse/Characters/OseboLeopard/Animations/ABP_OseboLeopard.ABP_OseboLeopard_C"));
 if(!AnimClass){bFamilyReady=false;GetMesh()->SetVisibility(false);GetCharacterMovement()->DisableMovement();Mission->Message(TEXT("Missing compiled feline Animation Blueprint; no substitute animation family."));return;}
 GetMesh()->SetAnimInstanceClass(AnimClass);GetMesh()->SetVisibility(true);PlayLeopardClip(0);
 int32 ForcedLod=-1;if(FParse::Value(FCommandLine::Get(),TEXT("AnanseLeopardForcedLOD="),ForcedLod) && ForcedLod>=0 && ForcedLod<Mesh->GetLODNum())
 {InspectionLod=ForcedLod;GetMesh()->SetForcedLOD(ForcedLod+1);}
 LiveContacts=NewObject<UAnanseLeopardContact>(this,TEXT("FelineLiveContacts"));LiveContacts->RegisterComponent();
 if(const auto* Catalogue=GetGameInstance()->GetSubsystem<UAnanseCatalogue>())
 {
  UMaterial* Parent=LoadObject<UMaterial>(nullptr,TEXT("/Game/Ananse/Characters/OseboLeopard/Presentation_v002/M_LeopardCosmetic.M_LeopardCosmetic"));
  const int32 CapeSlot=GetMesh()->GetMaterialIndex(TEXT("Cape_Burgundy")),AccentSlot=GetMesh()->GetMaterialIndex(TEXT("Cape_WovenGold_Trim"));
  if(Parent && CapeSlot>=0 && AccentSlot>=0)
  {
   CapeMaterial=GetMesh()->CreateDynamicMaterialInstance(CapeSlot,Parent);AccentMaterial=GetMesh()->CreateDynamicMaterialInstance(AccentSlot,Parent);
   CapeMaterial->SetVectorParameterValue(TEXT("BaseColour"),Catalogue->LeopardCape);CapeMaterial->SetScalarParameterValue(TEXT("Metallic"),0);CapeMaterial->SetScalarParameterValue(TEXT("Roughness"),.84);
   AccentMaterial->SetVectorParameterValue(TEXT("BaseColour"),Catalogue->LeopardAccent);AccentMaterial->SetScalarParameterValue(TEXT("Metallic"),.55);AccentMaterial->SetScalarParameterValue(TEXT("Roughness"),.4);
   PublishedVisualRevision=Catalogue->LeopardVisualRevision;
  }
  else if(Catalogue->bLeopardVisualPublished)
  {bFamilyReady=false;GetCharacterMovement()->DisableMovement();Mission->Message(TEXT("Published leopard cosmetic dependencies missing; no silent binding substitution."));return;}
 }
 Mission->Message(TEXT("OSEBO LEOPARD authored revision: live contacts active; final art pending. 1-9 motion categories; 0 automatic; F10 LOD inspection. Campaign mapping unapproved."));
#if !UE_BUILD_SHIPPING
 FParse::Value(FCommandLine::Get(),TEXT("AnanseLeopardVerify="),QualificationFile);
 FParse::Value(FCommandLine::Get(),TEXT("AnanseLeopardContactVerify="),ContactQualificationFile);
 QualificationStart=GetActorLocation();
#endif
}
bool AAnanseLeopardLabPlayer::PlayLeopardClip(int32 Index)
{
 if(!bFamilyReady || !LeopardClips.IsValidIndex(Index) || !LeopardClips[Index])return false;
 auto* Anim=Cast<UAnanseLeopardAnimInstance>(GetMesh()->GetAnimInstance());if(!Anim)return false;
 ActiveLeopardClip=Index;Anim->Clip=LeopardClips[Index];
 UE_LOG(LogTemp,Display,TEXT("ANANSE leopard clip=%d asset=%s"),Index,*LeopardClips[Index]->GetPathName());return true;
}
void AAnanseLeopardLabPlayer::Tick(float DeltaSeconds)
{
 Super::Tick(DeltaSeconds);
 TickQualification(DeltaSeconds);
 TickContactQualification(DeltaSeconds);
 if(bFamilyReady && !bManualPresentation)
 {
  const int32 Desired=GetVelocity().SizeSquared2D()>25?1:0;
  if(Desired!=ActiveLeopardClip)PlayLeopardClip(Desired);
 }
}
void AAnanseLeopardLabPlayer::TickQualification(float DeltaSeconds)
{
#if !UE_BUILD_SHIPPING
 if(QualificationFile.IsEmpty() || bQualificationDone || !bFamilyReady)return;
 QualificationSeconds+=DeltaSeconds;bManualPresentation=true;
 const int32 Stage=FMath::Min(8,int32(QualificationSeconds/5));
 if(Stage!=QualificationStage){QualificationStage=Stage;bPoseBaseline=false;PlayLeopardClip(Stage);}
 const float Within=QualificationSeconds-Stage*5;
 if(FParse::Param(FCommandLine::Get(),TEXT("AnanseVisualReview")))
 {
  // Inspection only: fixed camera and real morph targets; no root, input or mission authority changes.
  const float ReviewHeight=GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()*2.f;const bool Close=Stage==0||Stage==3||Stage==7;CameraBoom->TargetArmLength=Close?55.f:ReviewHeight*1.7f;CameraBoom->SocketOffset=FVector(0,0,Close?ReviewHeight*.43f:ReviewHeight*.12f);if(GetController())GetController()->SetControlRotation(FRotator(0,180,0));
  if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2")))
  {
   Camera->SetFieldOfView(Close?40.f:60.f);CameraBoom->TargetArmLength=Close?105.f:ReviewHeight*1.75f;
   const FVector EyeLine=GetMesh()->GetSocketLocation(TEXT("head"))+FVector(0,0,7.f);
   const float FootZ=FMath::Min(GetMesh()->GetSocketLocation(TEXT("foot_L")).Z,GetMesh()->GetSocketLocation(TEXT("foot_R")).Z);CameraBoom->SocketOffset=FVector(0,0,(Close?EyeLine.Z:(EyeLine.Z+FootZ)*.5f)-GetActorLocation().Z);
  }
  const TCHAR* Shapes[]={TEXT("BrowUp"),TEXT("BrowDown"),TEXT("Concern"),TEXT("Suspicion"),TEXT("Determination")};
  for(int32 I=0;I<5;++I)GetMesh()->SetMorphTarget(Shapes[I],Stage==I+1?1.f:0.f);
  const float Blink=Stage==0&&Within>2.7f&&Within<3.4f?1.f:0.f;GetMesh()->SetMorphTarget(TEXT("Blink_L"),Blink);GetMesh()->SetMorphTarget(TEXT("Blink_R"),Blink);
  const float ReviewShotAt=Stage==5?1.2f:2.f;
  if(Within>=ReviewShotAt&&Within-DeltaSeconds<ReviewShotAt)
  {
   FScreenshotRequest::RequestScreenshot(FPaths::GetPath(QualificationFile)/FString::Printf(TEXT("leopard-stage-%d.png"),Stage),true,false);
   if(FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2")))
   {
    auto View=MakeShared<FJsonObject>();View->SetNumberField(TEXT("horizontal_fov_degrees"),Camera->FieldOfView);View->SetNumberField(TEXT("equivalent_36mm_focal_length_mm"),18.f/FMath::Tan(FMath::DegreesToRadians(Camera->FieldOfView*.5f)));View->SetStringField(TEXT("actual_camera_world_cm"),Camera->GetComponentLocation().ToString());View->SetStringField(TEXT("evaluated_head_world_cm"),GetMesh()->GetSocketLocation(TEXT("head")).ToString());View->SetNumberField(TEXT("actual_camera_to_head_cm"),FVector::Dist(Camera->GetComponentLocation(),GetMesh()->GetSocketLocation(TEXT("head"))));for(TActorIterator<APostProcessVolume> Volume(GetWorld());Volume;++Volume)if(Volume->Priority>=100.f&&Volume->bUnbound){View->SetNumberField(TEXT("exposure_compensation_stops"),Volume->Settings.AutoExposureBias);View->SetNumberField(TEXT("exposure_method"),int32(Volume->Settings.AutoExposureMethod));View->SetBoolField(TEXT("physical_camera_exposure"),Volume->Settings.AutoExposureApplyPhysicalCameraExposure);View->SetNumberField(TEXT("motion_blur_amount"),Volume->Settings.MotionBlurAmount);break;}FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(View,Writer);FFileHelper::SaveStringToFile(Text,*(FPaths::GetPath(QualificationFile)/FString::Printf(TEXT("camera-stage-%d.json"),Stage)));
   }
  }
  if(Stage==0&&Within>=3.f&&Within-DeltaSeconds<3.f)FScreenshotRequest::RequestScreenshot(FPaths::GetPath(QualificationFile)/TEXT("leopard-blink.png"),true,false);
 }

 if(Within>.4f)
 {
  if(const auto* Anim=Cast<UAnanseLeopardAnimInstance>(GetMesh()->GetAnimInstance()))
   if(Anim->GraphEvaluations>0 && Anim->EvaluatedGraphClip==LeopardClips[Stage])GraphClipObserved[Stage]=true;
  const auto& Current=GetMesh()->GetComponentSpaceTransforms();
  if(!bPoseBaseline){PoseBaseline=Current;bPoseBaseline=true;}
  else if(Within<4.8f && Current.Num()==PoseBaseline.Num())
   for(int32 I=1;I<Current.Num();++I)
    if(Current[I].GetRotation().AngularDistance(PoseBaseline[I].GetRotation())>.001f || FVector::Distance(Current[I].GetTranslation(),PoseBaseline[I].GetTranslation())>.01f)MotionObserved[Stage]=true;
 }
 if(QualificationSeconds>46 && QualificationSeconds<50)AddMovementInput(FVector::ForwardVector,1);
 if(QualificationSeconds<60)return;
 bQualificationDone=true;
 APlayerController* PC=Cast<APlayerController>(GetController());
 auto* Sub=PC && PC->GetLocalPlayer()?ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()):nullptr;
 auto* View=GetWorld()->GetGameViewport();
 const bool Rendered=View && GDynamicRHI && FString(GDynamicRHI->GetName())==TEXT("Vulkan") && View->ViewModeIndex==VMI_Lit && View->EngineShowFlags.Lighting && !View->EngineShowFlags.Wireframe;
 const float Distance=FVector::Dist2D(GetActorLocation(),QualificationStart);
 FVector Face=GetMesh()->GetSocketLocation(TEXT("jaw"))-GetMesh()->GetSocketLocation(TEXT("head"));Face.Z=0;Face.Normalize();
 const float ForwardAlignment=FVector::DotProduct(Face,GetActorForwardVector());
 bool Passed=Rendered && PC && PC->GetPawn()==this && Sub && Sub->HasMappingContext(GetOwnedInputMapping()) && Abilities->GetActivatableAbilities().Num()==0 && Distance>100;
 Passed &= ForwardAlignment>.95f;
 if(FParse::Param(FCommandLine::Get(),TEXT("AnanseLeopardSaveProfile")))
 {auto* Lab=Cast<AAnanseLabController>(PC);Passed &= Lab && Lab->SelectedDesign==TEXT("osebo-leopard-v1") && Lab->SaveSelection();}
 for(int32 I=0;I<9;++I)Passed &= MotionObserved[I] && GraphClipObserved[I];
 auto Report=MakeShared<FJsonObject>();Report->SetBoolField(TEXT("passed"),Passed);Report->SetNumberField(TEXT("seconds"),QualificationSeconds);
 Report->SetStringField(TEXT("world"),GetWorld()->GetPathName());Report->SetStringField(TEXT("pawn_class"),GetClass()->GetPathName());
 Report->SetStringField(TEXT("mesh"),LeopardMesh->GetPathName());Report->SetStringField(TEXT("skeleton"),LeopardMesh->GetSkeleton()->GetPathName());
 Report->SetStringField(TEXT("animation_instance"),GetMesh()->GetAnimInstance()->GetClass()->GetPathName());
 Report->SetNumberField(TEXT("bones"),LeopardMesh->GetRefSkeleton().GetNum());Report->SetNumberField(TEXT("movement_cm"),Distance);
 Report->SetNumberField(TEXT("face_forward_alignment"),ForwardAlignment);
 Report->SetStringField(TEXT("face_world_direction"),Face.ToString());Report->SetStringField(TEXT("actor_rotation"),GetActorRotation().ToString());
 Report->SetStringField(TEXT("mesh_relative_rotation"),GetMesh()->GetRelativeRotation().ToString());
 Report->SetBoolField(TEXT("normal_lit_rendering"),Rendered);Report->SetNumberField(TEXT("ability_grants"),Abilities->GetActivatableAbilities().Num());
 TArray<TSharedPtr<FJsonValue>> Motion;
 for(int32 I=0;I<9;++I){auto Entry=MakeShared<FJsonObject>();Entry->SetStringField(TEXT("clip"),LeopardClips[I]->GetPathName());Entry->SetBoolField(TEXT("evaluated_bone_motion"),MotionObserved[I]);Entry->SetBoolField(TEXT("graph_clip_observed"),GraphClipObserved[I]);Motion.Add(MakeShared<FJsonValueObject>(Entry));}
 Report->SetArrayField(TEXT("clips"),Motion);Report->SetStringField(TEXT("input_scope"),TEXT("native simulated movement; no physical controller claim"));
 Report->SetBoolField(TEXT("contact_qualified"),false);Report->SetBoolField(TEXT("creative_approved"),false);
 Report->SetBoolField(TEXT("live_contacts_enabled"),LiveContacts && LiveContacts->bReady && LiveContacts->bEnabled);
 if(LiveContacts)Report->SetStringField(TEXT("ground_contact_metrics"),LiveContacts->MetricsJson());
 Report->SetNumberField(TEXT("published_visual_revision"),PublishedVisualRevision);
 Report->SetNumberField(TEXT("evaluated_lod"),GetMesh()->GetPredictedLODLevel());
 Report->SetNumberField(TEXT("available_lods"),LeopardMesh->GetLODNum());
 Report->SetStringField(TEXT("actual_cape_linear"),CapeMaterial?CapeMaterial->K2_GetVectorParameterValue(TEXT("BaseColour")).ToString():TEXT("unbound"));
 Report->SetStringField(TEXT("actual_accent_linear"),AccentMaterial?AccentMaterial->K2_GetVectorParameterValue(TEXT("BaseColour")).ToString():TEXT("unbound"));
 FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(Report,Writer);FFileHelper::SaveStringToFile(Json,*QualificationFile);
 FScreenshotRequest::RequestScreenshot(FPaths::ChangeExtension(QualificationFile,TEXT("png")),true,false);
 const double Finish=FPlatformTime::Seconds()+2;
 FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Finish,Passed](float)
 {
  if(FPlatformTime::Seconds()<Finish)return true;
#if UE_TRACE_ENABLED
  FTraceAuxiliary::Pause();FTraceAuxiliary::Stop();UE::Trace::Shutdown();
#endif
  FPlatformMisc::RequestExitWithStatus(false,Passed?0:2,TEXT("Leopard isolated playback qualification complete"));return false;
 }));
#endif
}
void AAnanseLeopardLabPlayer::ResetTransientMotion()
{
 Super::ResetTransientMotion();bManualPresentation=false;
 if(LiveContacts)LiveContacts->ResetContacts();
 if(bFamilyReady)PlayLeopardClip(0);
}
void AAnanseLeopardLabPlayer::SetupPlayerInputComponent(UInputComponent* Input)
{
 Super::SetupPlayerInputComponent(Input);
 Input->BindKey(EKeys::One,IE_Pressed,this,&AAnanseLeopardLabPlayer::Idle);
 Input->BindKey(EKeys::Two,IE_Pressed,this,&AAnanseLeopardLabPlayer::Patrol);
 Input->BindKey(EKeys::Three,IE_Pressed,this,&AAnanseLeopardLabPlayer::Run);
 Input->BindKey(EKeys::Four,IE_Pressed,this,&AAnanseLeopardLabPlayer::Turn);
 Input->BindKey(EKeys::Five,IE_Pressed,this,&AAnanseLeopardLabPlayer::Investigate);
 Input->BindKey(EKeys::Six,IE_Pressed,this,&AAnanseLeopardLabPlayer::Capture);
 Input->BindKey(EKeys::Seven,IE_Pressed,this,&AAnanseLeopardLabPlayer::Recover);
 Input->BindKey(EKeys::Eight,IE_Pressed,this,&AAnanseLeopardLabPlayer::Command);
 Input->BindKey(EKeys::Nine,IE_Pressed,this,&AAnanseLeopardLabPlayer::Isolation);
 Input->BindKey(EKeys::Zero,IE_Pressed,this,&AAnanseLeopardLabPlayer::Automatic);
 Input->BindKey(EKeys::F10,IE_Pressed,this,&AAnanseLeopardLabPlayer::CycleInspectionLod);
}
void AAnanseLeopardLabPlayer::CycleInspectionLod()
{if(!bFamilyReady)return;InspectionLod++;if(InspectionLod>=LeopardMesh->GetLODNum())InspectionLod=-1;GetMesh()->SetForcedLOD(InspectionLod+1);Mission->Message(FString::Printf(TEXT("Leopard inspection LOD %d (-1 automatic); deformation review remains separate."),InspectionLod));}
AAnanseLeopardLabMode::AAnanseLeopardLabMode()
{
 DefaultPawnClass=AAnanseLeopardLabPlayer::StaticClass();
 HUDClass=AAnanseHUD::StaticClass();PlayerControllerClass=AAnanseLabController::StaticClass();
}
