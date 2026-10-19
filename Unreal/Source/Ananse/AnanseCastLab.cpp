#include "AnanseCastLab.h"
#include "Camera/CameraComponent.h"
#include "AnanseAsoLedger.h"
#include "AnanseAsoSurfaceProbe.h"
#include "AnanseMission.h"
#include "AnanseCinematic.h"
#include "AnanseCatalogue.h"
#include "AnanseLeopardContact.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimInstanceProxy.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/InputComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HighResScreenshot.h"
#include "Misc/Paths.h"
void UAnanseCastAnimInstance::NativePostEvaluateAnimation()
{
 Super::NativePostEvaluateAnimation();++Evaluations;EvaluatedClip=nullptr;EvaluatedTime=-1;
 for(const auto& Player:GetProxyOnGameThread<FAnimInstanceProxy>().GetUngroupedActivePlayersRead())
  if(auto* Sequence=Cast<UAnimSequence>(Player.SourceAsset.Get())){EvaluatedClip=Sequence;EvaluatedTime=Player.TimeAccumulator?*Player.TimeAccumulator:-1;}
}
AAnanseCastLabPlayer::AAnanseCastLabPlayer()
{
 bLabSelectionPawn=true;AutoPossessAI=EAutoPossessAI::Disabled;
 GetCharacterMovement()->MaxWalkSpeed=45;GetCharacterMovement()->RotationRate=FRotator(0,120,0);
 GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
 LedgerVisual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LedgerPresentation"));LedgerVisual->SetupAttachment(GetMesh());LedgerVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);LedgerVisual->SetGenerateOverlapEvents(false);LedgerVisual->SetVisibility(false);
}
void AAnanseCastLabPlayer::BeginPlay()
{
 bLabSelectionPawn=!(bStoryCampaignPresentation && DesignId==TEXT("kwaku-human-v1") && CharacterId==TEXT("kwaku"));
 const bool AcceptedEpisode=bStoryCampaignPresentation && !bLabSelectionPawn && CharacterId==TEXT("kwaku") && FParse::Param(FCommandLine::Get(),TEXT("AnanseAcceptedVisuals")) && AuthoredMesh && AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku");
 const bool VisualMesh=AcceptedEpisode || (FParse::Param(FCommandLine::Get(),TEXT("AnanseVisualReview"))&&bLabSelectionPawn&&AuthoredMesh&&(AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Visual_v001/Kwaku.Kwaku")||AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Visual_v002/Kwaku.Kwaku")||AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Visual_v003/Kwaku.Kwaku")||AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku")));
 if(bRefinedFace&&DesignId==TEXT("kwaku-human-v1")&&!VisualMesh)
 {
  const auto* Catalogue=GetGameInstance()->GetSubsystem<UAnanseCatalogue>();
  if(!FParse::Param(FCommandLine::Get(),TEXT("AnanseArtRefinement"))||!Catalogue||!Catalogue->bLoaded||(Catalogue->KwakuVisualRevision!=2&&Catalogue->KwakuVisualRevision!=3&&Catalogue->KwakuVisualRevision!=4&&Catalogue->KwakuVisualRevision!=5)){AuthoredMesh=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/Story_v001/Kwaku.Kwaku"));bRefinedFace=false;}
  else AuthoredMesh=LoadObject<USkeletalMesh>(nullptr,Catalogue->KwakuVisualRevision==5?TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v005/Kwaku.Kwaku"):Catalogue->KwakuVisualRevision==4?TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v003/Kwaku.Kwaku"):Catalogue->KwakuVisualRevision==3?TEXT("/Game/Ananse/Characters/Kwaku/Refined_v002/Kwaku.Kwaku"):TEXT("/Game/Ananse/Characters/Kwaku/Refined_v001/Kwaku.Kwaku"));
 }
 // Blueprint height changes capsule before parent initialization; root movement is gameplay-owned.
 GetCapsuleComponent()->SetCapsuleSize(DesignId==TEXT("kojo-tortoise-v1")?36:30,AuthoringHeight*.5f+3,true);
 GetMesh()->SetRelativeLocation(FVector(0,0,-GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()));
 Super::BeginPlay();
 if(!bLabSelectionPawn){GetCharacterMovement()->MaxWalkSpeed=GetDefault<AAnansePlayer>()->GetCharacterMovement()->MaxWalkSpeed;GetCharacterMovement()->RotationRate=GetDefault<AAnansePlayer>()->GetCharacterMovement()->RotationRate;}
 // Catalogue appearance is historical campaign data, not this isolated design binding.
 GetMesh()->SetRelativeLocation(FVector(0,0,-GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()));GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);GetMesh()->SetRelativeScale3D(FVector::OneVector);
 if(DesignId==TEXT("aso-yaa-human-v1")&&AuthoredMesh&&(AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v001/AsoYaa.AsoYaa")||AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v002/AsoYaa.AsoYaa")||AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v001/AsoYaa.AsoYaa")||AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa")))GetMesh()->SetRelativeRotation(FRotator(0,AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa")?0:AuthoredMesh->GetPathName()!=TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v001/AsoYaa.AsoYaa")?90:-90,0));
 Body->SetVisibility(false);Head->SetVisibility(false);
 bFamilyReady=AuthoredMesh && AuthoredMesh->GetSkeleton() && AnimationClass && AuthoredClips.Num()>=8;
 if(bLedgerPresentation)bFamilyReady &= AuthoredMesh==GetClass()->GetDefaultObject<AAnanseCastLabPlayer>()->AuthoredMesh;
 for(UAnimSequence* Clip:AuthoredClips)bFamilyReady &= Clip && AuthoredMesh && Clip->GetSkeleton()==AuthoredMesh->GetSkeleton();
 if(bRefinedFace)bFamilyReady &= AuthoredMesh && AuthoredMesh->FindMorphTarget(TEXT("Blink_L")) && AuthoredMesh->FindMorphTarget(TEXT("Blink_R"));
 if(!bFamilyReady){GetMesh()->SetVisibility(false);GetCharacterMovement()->DisableMovement();Mission->Message(TEXT("Authored design missing/incompatible; no primitive substitution."));return;}
 GetCharacterMovement()->bForceNextFloorCheck=true;GetCharacterMovement()->SetMovementMode(MOVE_Falling);
 const bool RefinedLighting=FParse::Param(FCommandLine::Get(),TEXT("AnanseArtRefinement"));
 GetMesh()->SetLightingChannels(RefinedLighting||!bLabSelectionPawn,!RefinedLighting&&bLabSelectionPawn,false);
 CameraBoom->TargetArmLength=AuthoringHeight*1.6f;CameraBoom->SocketOffset=FVector(0,0,AuthoringHeight*.15f);
 GetMesh()->SetSkeletalMesh(AuthoredMesh);GetMesh()->SetAnimInstanceClass(AnimationClass);GetMesh()->SetVisibility(true);PlayAuthoredClip(0);
 if(bAsoLedgerPresentation&&FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoContact"))&&!FParse::Param(FCommandLine::Get(),TEXT("AnanseNeutralLabLighting")))
 {
  // Moving neutral-review fills: expose surfaces, never hide geometry with darkness.
  for(int32 I=0;I<2;++I){auto* Fill=NewObject<UPointLightComponent>(this);AddInstanceComponent(Fill);Fill->SetupAttachment(GetRootComponent());Fill->SetMobility(EComponentMobility::Movable);Fill->IntensityUnits=ELightUnits::Candelas;Fill->SetIntensity(I?160.f:350.f);Fill->SetAttenuationRadius(450.f);Fill->SetSourceRadius(45.f);Fill->SetCastShadows(false);Fill->SetLightColor(I?FLinearColor(.80f,.9f,1.f):FLinearColor(1.f,.94f,.86f));Fill->SetRelativeLocation(FVector(140.f,I?150.f:-130.f,I?65.f:130.f));Fill->RegisterComponent();}
 }
 if(bAsoLedgerPresentation&&(AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa")||AuthoredMesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa")))
 {
  GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);
  // The lab now has the same visible support as the authored evidence action.
  auto* Stand=NewObject<UStaticMeshComponent>(this,TEXT("AsoLedgerSupport"));AddInstanceComponent(Stand);Stand->SetupAttachment(GetMesh());Stand->SetStaticMesh(LedgerSupportMesh);Stand->SetCollisionEnabled(ECollisionEnabled::NoCollision);Stand->SetGenerateOverlapEvents(false);Stand->SetRelativeLocation(FVector(30,0,0));Stand->RegisterComponent();bFamilyReady &= Stand->GetStaticMesh()!=nullptr;
 }
 if(bAsoLedgerPresentation){bFamilyReady &= LedgerMesh!=nullptr;LedgerVisual->SetStaticMesh(LedgerMesh);GetMesh()->RegisterOnBoneTransformsFinalizedDelegate(FOnBoneTransformsFinalizedMultiCast::FDelegate::CreateUObject(this,&AAnanseCastLabPlayer::UpdateAsoLedger));}
 if(bLedgerPresentation){LedgerVisual->SetStaticMesh(LedgerMesh);bFamilyReady &= LedgerMesh!=nullptr;}
 if(DesignId!=TEXT("esi-moth-v1")){LiveContacts=NewObject<UAnanseLeopardContact>(this,TEXT("SupportingLegContacts"));LiveContacts->RegisterComponent();}
 if(bLabSelectionPawn)Mission->Message(TEXT("Authored cast WIP: 0 auto,1-9 clips. Mapped contacts active on grounded designs; art pending. Lab only; no new powers."));
}
bool AAnanseCastLabPlayer::PlayAuthoredClip(int32 Index)
{
 if(!bFamilyReady || !AuthoredClips.IsValidIndex(Index))return false;
 auto* Anim=Cast<UAnanseCastAnimInstance>(GetMesh()->GetAnimInstance());if(!Anim)return false;
 const bool ResetInspection=(bLedgerPresentation&&(Index==8||ActiveClip==8))||(bAsoLedgerPresentation&&(Index==4||ActiveClip==4));ActiveClip=Index;Anim->Clip=AuthoredClips[Index];if(ResetInspection)Anim->RestartPresentationGraph();LedgerAge=0;bLedgerLatched=false;LedgerVisual->SetVisibility(false);++AsoSurfaceEpoch;return true;
}
void AAnanseCastLabPlayer::UpdateAsoLedger()
{
 if(!bAsoLedgerPresentation)return;const auto* Anim=Cast<UAnanseCastAnimInstance>(GetMesh()->GetAnimInstance());
 AnanseAsoLedger::Update(GetMesh(),LedgerVisual,Anim?Anim->EvaluatedClip.Get():nullptr,Anim?Anim->EvaluatedTime:-1.f);
 CaptureAsoSurface(GetMesh(),Anim?Anim->EvaluatedClip.Get():nullptr,Anim?Anim->EvaluatedTime:-1.f,AsoSurfaceCaptures,AsoSurfaceEpoch);
 if(Anim&&Anim->EvaluatedClip&&Anim->EvaluatedClip->GetName().Contains(TEXT("InspectEvidence"))&&LedgerVisual->IsVisible())
 {
  const float T=Anim->EvaluatedTime;
  if(T>=1.6f&&T<6.f){++AsoLedgerSamples;AsoLedgerMaxBindingErrorCm=FMath::Max(AsoLedgerMaxBindingErrorCm,float(FVector::Dist(LedgerVisual->GetComponentLocation(),GetMesh()->GetSocketLocation(TEXT("socket_ledger_R")))));}
  const float Times[]={1.61f,2.4f,3.6f,4.8f,6.81f};const TCHAR* Names[]={TEXT("ledger_contact_start"),TEXT("ledger_stable_hold"),TEXT("ledger_inspection_closeup"),TEXT("ledger_gesture_closeup"),TEXT("ledger_release")};
  for(int32 I=0;I<5;++I)if(T>=Times[I]&&!(AsoLedgerPhaseMask&(1u<<I)))
  {
   AsoLedgerPhaseMask|=1u<<I;FString Report;if(FParse::Value(FCommandLine::Get(),TEXT("AnanseStoryCastVerify="),Report))FScreenshotRequest::RequestScreenshot(FPaths::GetPath(Report)/(FString(Names[I])+TEXT(".png")),true,false);
  }
 }

}
void AAnanseCastLabPlayer::PresentLedgerInteraction(){if(bLedgerPresentation&&bFamilyReady){bManual=true;bEpisodeLedger=!bLabSelectionPawn;PlayAuthoredClip(8);}}
void AAnanseCastLabPlayer::Tick(float Delta)
{
 Super::Tick(Delta);
 const bool InCinematic=Mission&&Mission->Cinematic&&Mission->Cinematic->bActive;
 if(bEpisodeLedger&&!InCinematic&&(GetVelocity().SizeSquared2D()>25||IsWebFlying()||GetCharacterMovement()->IsFalling())){bEpisodeLedger=false;bManual=false;PlayAuthoredClip(0);}
 if(bFamilyReady&&bLedgerPresentation&&ActiveClip==8&&LedgerMesh)
 {
  LedgerAge+=Delta;const float Length=AuthoredClips[8]->GetPlayLength();const auto* Presentation=Cast<UAnanseCastAnimInstance>(GetMesh()->GetAnimInstance());const float Phase=Presentation&&Presentation->EvaluatedClip==AuthoredClips[8]?Presentation->EvaluatedTime:-1.f;
  if(Phase>=.70f&&Phase<=2.65f)
  {
   if(!bLedgerLatched)
   {
    // Latch once against the evaluated held pose, then remain relative to the hand.
    // The authored prop frame is component-space centimetres, Blender -Y -> native +X.
    FTransform Frame=GetMesh()->GetComponentTransform();Frame.SetLocation(Frame.TransformPosition(FVector(24.8f,0,104.5f+(LiveContacts?LiveContacts->Snapshot.BodyZ:0.f))));LedgerVisual->DetachFromComponent(FDetachmentTransformRules::KeepWorldTransform);LedgerVisual->SetWorldTransform(Frame);LedgerVisual->AttachToComponent(GetMesh(),FAttachmentTransformRules::KeepWorldTransform,TEXT("hand_R"));bLedgerLatched=true;
   }
   LedgerVisual->SetVisibility(true);
  }
  else{LedgerVisual->SetVisibility(false);bLedgerLatched=false;}
  if(bEpisodeLedger&&LedgerAge>=Length){bEpisodeLedger=false;bManual=false;PlayAuthoredClip(0);}
 }
 else if(LedgerVisual){LedgerVisual->SetVisibility(false);bLedgerLatched=false;}
 if(bAsoLedgerPresentation&&FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoDiagnosticCamera")))
 {
  // Review framing only; no root, skeleton, input or collision changes.
  if(auto* PC=Cast<APlayerController>(GetController()))PC->SetControlRotation(FRotator(-5,180,0));
  const bool Close=FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoLedgerClose"));CameraBoom->TargetArmLength=Close?130.f:AuthoringHeight*1.65f;CameraBoom->SocketOffset=FVector(0,0,Close?25.f:AuthoringHeight*.15f);Camera->SetFieldOfView(Close?55.f:70.f);
 }
 // Explicit comparison camera only; no saved asset or gameplay camera changes.
 FString ComparisonView;
 if(bAsoLedgerPresentation&&FParse::Value(FCommandLine::Get(),TEXT("AnanseAsoComparisonCamera="),ComparisonView))
 {
  const bool Grip=ComparisonView.StartsWith(TEXT("grip"));const float Yaw=ComparisonView==TEXT("profile")?90.f:ComparisonView==TEXT("threequarter")||ComparisonView==TEXT("gripoblique")?135.f:180.f;
  const FVector Target=Grip&&LedgerVisual?LedgerVisual->GetComponentLocation()+FVector(0,0,3):GetMesh()->Bounds.Origin;
  CameraBoom->TargetArmLength=Grip?110.f:450.f;CameraBoom->SocketOffset=FVector(0,0,Target.Z-CameraBoom->GetComponentLocation().Z);Camera->SetFieldOfView(Grip?40.f:45.f);
  if(auto* PC=Cast<APlayerController>(GetController()))PC->SetControlRotation(FRotator(Grip?-12.f:0.f,Yaw,0));
 }
 if(bFamilyReady&&bRefinedFace)
 {
  FaceAge+=Delta;const float Phase=FMath::Fmod(FaceAge,4.f);
  AppliedBlink=bHoldBlink?1.f:FMath::Clamp(1.f-FMath::Abs(Phase-3.85f)/.12f,0.f,1.f);
  GetMesh()->SetMorphTarget(TEXT("Blink_L"),AppliedBlink);GetMesh()->SetMorphTarget(TEXT("Blink_R"),AppliedBlink);
  if(DesignId==TEXT("aso-yaa-human-v1"))
  {
   const FName Names[]={TEXT("Concern"),TEXT("Suspicion"),TEXT("Disapproval"),TEXT("Consideration"),TEXT("Resolve"),TEXT("Agreement"),TEXT("Refusal"),TEXT("QuietWarning"),TEXT("ControlledAnger")};
   const int32 Face=ActiveClip==13?0:ActiveClip==11?8:ActiveClip==7?1:ActiveClip==3?3:ActiveClip==5?3:ActiveClip==14?4:ActiveClip==8?5:ActiveClip==9?6:ActiveClip==10?7:-1;
   for(int32 I=0;I<UE_ARRAY_COUNT(Names);++I)GetMesh()->SetMorphTarget(Names[I],Face==I?.65f:0.f);
  }
 }
 if(bFamilyReady && DesignId==TEXT("esi-moth-v1"))GetMesh()->SetRelativeLocation(FVector(0,0,-GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()+12.f+3.f*FMath::Sin(GetWorld()->GetTimeSeconds()*2.f)));
 if(LiveContacts)LiveContacts->bEnabled=GetVelocity().Size2D()<=65.f && !IsWebFlying();
 if(bFamilyReady && !bManual){int32 Desired=GetVelocity().SizeSquared2D()>25?1:0;if(!bLabSelectionPawn && GetVelocity().Size2D()>160)Desired=2;if(!bLabSelectionPawn && IsWebFlying() && AuthoredClips.Num()>5)Desired=5;if(Desired!=ActiveClip)PlayAuthoredClip(Desired);}
}
void AAnanseCastLabPlayer::ResetTransientMotion(){Super::ResetTransientMotion();FaceAge=0;bHoldBlink=false;AppliedBlink=0;LedgerAge=0;bLedgerLatched=false;bEpisodeLedger=false;if(LedgerVisual)LedgerVisual->SetVisibility(false);if(bRefinedFace){GetMesh()->SetMorphTarget(TEXT("Blink_L"),0);GetMesh()->SetMorphTarget(TEXT("Blink_R"),0);}if(LiveContacts)LiveContacts->ResetContacts();bManual=false;if(bFamilyReady)PlayAuthoredClip(0);}
void AAnanseCastLabPlayer::SetupPlayerInputComponent(UInputComponent* Input)
{
 Super::SetupPlayerInputComponent(Input);
 if(!bLabSelectionPawn)return;
 if(bRefinedFace)Input->BindKey(EKeys::B,IE_Pressed,this,&AAnanseCastLabPlayer::ToggleBlink);
 Input->BindKey(EKeys::RightBracket,IE_Pressed,this,&AAnanseCastLabPlayer::NextClip);
 Input->BindKey(EKeys::LeftBracket,IE_Pressed,this,&AAnanseCastLabPlayer::PreviousClip);
 Input->BindKey(EKeys::Zero,IE_Pressed,this,&AAnanseCastLabPlayer::Clip0);
 Input->BindKey(EKeys::One,IE_Pressed,this,&AAnanseCastLabPlayer::Clip1);Input->BindKey(EKeys::Two,IE_Pressed,this,&AAnanseCastLabPlayer::Clip2);
 Input->BindKey(EKeys::Three,IE_Pressed,this,&AAnanseCastLabPlayer::Clip3);Input->BindKey(EKeys::Four,IE_Pressed,this,&AAnanseCastLabPlayer::Clip4);
 Input->BindKey(EKeys::Five,IE_Pressed,this,&AAnanseCastLabPlayer::Clip5);Input->BindKey(EKeys::Six,IE_Pressed,this,&AAnanseCastLabPlayer::Clip6);
 Input->BindKey(EKeys::Seven,IE_Pressed,this,&AAnanseCastLabPlayer::Clip7);Input->BindKey(EKeys::Eight,IE_Pressed,this,&AAnanseCastLabPlayer::Clip8);Input->BindKey(EKeys::Nine,IE_Pressed,this,&AAnanseCastLabPlayer::Clip9);
}
