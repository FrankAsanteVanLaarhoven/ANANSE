#include "AnanseGroundContact.h"
#include "AnanseSecondaryMotion.h"
#include "AnansePlayer.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimationPoseData.h"
#include "BonePose.h"
#include "TwoBoneIK.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "EngineUtils.h"
#include "Engine/OverlapResult.h"
#include "Components/CapsuleComponent.h"
const TCHAR* UAnanseGroundContact::Sides[4]={TEXT("front_l"),TEXT("front_r"),TEXT("rear_l"),TEXT("rear_r")};
namespace
{
// Engineering hinge envelope; final deformation/art calibration remains separate.
constexpr float MinimumKneeFlex=5.f,MaximumKneeFlex=155.f;
float ReachForFlex(float Upper,float Lower,float Flex)
{return FMath::Sqrt(FMath::Max(0.f,Upper*Upper+Lower*Lower+2*Upper*Lower*FMath::Cos(FMath::DegreesToRadians(Flex))));}
FName Bone(const TCHAR* Prefix,int32 I){return FName(*(FString(Prefix)+UAnanseGroundContact::Sides[I]));}
struct FContactProxy:public FAnimInstanceProxy
{
 explicit FContactProxy(UAnimInstance* Instance):FAnimInstanceProxy(Instance){}
 FAnanseSecondaryMotion Secondary;
 FAnanseContactPose Input;UAnimSequence* Sequence=nullptr;float Time=0,SolveUs=0;int32 SolvedChains=0;bool bAuthoredGraph=false;
 virtual void PreUpdate(UAnimInstance* Instance,float Delta)override
 {
  FAnimInstanceProxy::PreUpdate(Instance,Delta);check(IsInGameThread());
  auto* Anim=CastChecked<UAnanseContactAnimInstance>(Instance);Input=Anim->Contact?Anim->Contact->Snapshot:FAnanseContactPose();Input.Enabled=Anim->Contact && Anim->Contact->bEnabled;if(!Input.Enabled){Input.BodyOffset=FVector::ZeroVector;Input.BodyTilt=FQuat::Identity;}Sequence=Anim->Clip;
  bAuthoredGraph=Anim->bUseAuthoredGraph;if(Anim->bResetSecondaryMotion){Secondary.Initialized=false;Anim->bResetSecondaryMotion=false;}Secondary.Gather(Instance,Delta);
  if(Sequence){Anim->ClipTime=FMath::Fmod(Anim->ClipTime+Delta,Sequence->GetPlayLength());Time=Anim->ClipTime;}
 }
 virtual bool Evaluate(FPoseContext& Output)override
 {
  SolvedChains=0;TRACE_CPUPROFILER_EVENT_SCOPE(AnanseFourLegPoseSolve);
  const double Start=FPlatformTime::Seconds();Output.ResetToRefPose();
  if(bAuthoredGraph)EvaluateAnimationNode(Output);
  else if(Sequence){FAnimationPoseData Data(Output);Sequence->GetAnimationPose(Data,FAnimExtractContext(Time,true));}
  Secondary.Apply(Output);
  const FBoneContainer& Bones=Output.Pose.GetBoneContainer();
  auto Index=[&](FName Name){return Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(Bones.GetReferenceSkeleton().FindBoneIndex(Name)));};
  // Gameplay owns root motion; live contact owns pelvis height/tilt. Imported
  // gesture body motion must not invalidate the reference-based reach calculation.
  if(Input.Enabled)for(const TCHAR* Name:{TEXT("root"),TEXT("pelvis")})
  {auto B=Index(FName(Name));if(B.IsValid())Output.Pose[B]=Bones.GetRefPoseTransform(B);}
  // Contact owns supporting-leg pose; imported upper/lower arm gestures remain untouched.
  for(int32 I=0;I<4;I++)if(Input.Enabled)for(const TCHAR* Prefix:{TEXT("coxa_"),TEXT("femur_"),TEXT("tibia_"),TEXT("tarsus_"),TEXT("foot_tip_")})
  {auto B=Index(Bone(Prefix,I));if(B.IsValid())Output.Pose[B]=Bones.GetRefPoseTransform(B);}
  FCSPose<FCompactPose> Pose;Pose.InitPose(Output.Pose);
  auto Pelvis=Index(TEXT("pelvis"));
  if(Pelvis.IsValid()){FTransform Body=Pose.GetComponentSpaceTransform(Pelvis);Body.AddToTranslation(Input.BodyOffset);Body.SetRotation((Input.BodyTilt*Body.GetRotation()).GetNormalized());Pose.SetComponentSpaceTransform(Pelvis,Body);}
  for(int32 I=0;I<4;I++)
  {
   if(!Input.Enabled)continue;
   auto Hip=Index(Bone(TEXT("femur_"),I)),Knee=Index(Bone(TEXT("tibia_"),I)),Ankle=Index(Bone(TEXT("tarsus_"),I)),Tip=Index(Bone(TEXT("foot_tip_"),I));
   if(!Hip.IsValid()||!Knee.IsValid()||!Ankle.IsValid())continue;
   FTransform H=Pose.GetComponentSpaceTransform(Hip),K=Pose.GetComponentSpaceTransform(Knee),A=Pose.GetComponentSpaceTransform(Ankle);
   const int32 TipRef=Bones.GetReferenceSkeleton().FindBoneIndex(Bone(TEXT("foot_tip_"),I));
   if(TipRef<0)continue;
   const FVector TipLocal=Bones.GetReferenceSkeleton().GetRefBonePose()[TipRef].GetTranslation();
   const FVector Axis=A.GetRotation().RotateVector(TipLocal).GetSafeNormal();
   const FVector Normal=Input.Valid[I]?Input.Normal[I]:FVector::UpVector;
   FQuat FootRotation=(FQuat::FindBetweenNormals(Axis,-Normal)*A.GetRotation()).GetNormalized();
   // Released legs tuck clear of unsupported terrain instead of retaining an
   // extended reference pose beneath the crouched body. Collision remains owned
   // by CharacterMovement; this only changes the evaluated supporting-leg pose.
   const FVector Target=Input.Valid[I]?Input.Target[I]:A.TransformPosition(TipLocal)+FVector(0,0,40);
   FVector End=Target-FootRotation.RotateVector(TipLocal);
   // Bend plane is derived from the actual current imported chain, not a mannequin axis.
   FVector Along=(A.GetLocation()-H.GetLocation()).GetSafeNormal();
   FVector Bend=K.GetLocation()-H.GetLocation();Bend-=Along*FVector::DotProduct(Bend,Along);
   if(Bend.IsNearlyZero())Bend=FVector::CrossProduct(Along,Normal);
   const FVector Pole=H.GetLocation()+Bend.GetSafeNormal()*100;
   const float Upper=FVector::Distance(H.GetLocation(),K.GetLocation()),Lower=FVector::Distance(K.GetLocation(),A.GetLocation());
   const FVector Delta=End-H.GetLocation();
   End=H.GetLocation()+Delta.GetSafeNormal(SMALL_NUMBER,FVector::UpVector)*FMath::Clamp(float(Delta.Size()),ReachForFlex(Upper,Lower,MaximumKneeFlex),ReachForFlex(Upper,Lower,MinimumKneeFlex));
   AnimationCore::SolveTwoBoneIK(H,K,A,Pole,End,false,1,1);
   A.SetRotation(FootRotation);H.SetScale3D(FVector::OneVector);K.SetScale3D(FVector::OneVector);A.SetScale3D(FVector::OneVector);
   SolvedChains++;Pose.SetComponentSpaceTransform(Hip,H);Pose.SetComponentSpaceTransform(Knee,K);Pose.SetComponentSpaceTransform(Ankle,A);
  }
  FCSPose<FCompactPose>::ConvertComponentPosesToLocalPosesSafe(Pose,Output.Pose);
  SolveUs=float((FPlatformTime::Seconds()-Start)*1e6);return true;
 }
 virtual void PostEvaluate(UAnimInstance* Instance)override
 {
  FAnimInstanceProxy::PostEvaluate(Instance);auto* Anim=CastChecked<UAnanseContactAnimInstance>(Instance);
  Anim->SecondaryBoneCount=Secondary.AppliedBones;Anim->SecondaryEvaluations=Secondary.Evaluations;Anim->SecondaryPeakDegrees=Secondary.PeakDegrees;Anim->SecondaryResets=Secondary.Resets;
  if(bAuthoredGraph)
  {
   ++Anim->GraphEvaluations;Anim->EvaluatedGraphClip=nullptr;
   for(const auto& Player:GetUngroupedActivePlayersRead())if(auto* Clip=Cast<UAnimSequence>(Player.SourceAsset.Get()))Anim->EvaluatedGraphClip=Clip;
  }
  if(Anim->Contact){Anim->Contact->LastSolveMicroseconds=SolveUs;Anim->Contact->LastSolvedChains=SolvedChains;}
 }
};
}
FAnimInstanceProxy* UAnanseContactAnimInstance::CreateAnimInstanceProxy(){return new FContactProxy(this);}
void UAnanseContactAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy){delete Proxy;}
UAnanseGroundContact::UAnanseGroundContact(){PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PrePhysics;}
void UAnanseGroundContact::BeginPlay()
{
 Super::BeginPlay();auto* P=CastChecked<AAnansePlayer>(GetOwner());
 const FReferenceSkeleton& Ref=P->GetMesh()->GetSkeletalMeshAsset()->GetRefSkeleton();TArray<FTransform> CS=Ref.GetRefBonePose();
 for(int32 B=0;B<CS.Num();B++)if(Ref.GetParentIndex(B)>=0)CS[B]=CS[B]*CS[Ref.GetParentIndex(B)];
 BindPelvis=CS[Ref.FindBoneIndex(TEXT("pelvis"))].GetLocation();
 for(int32 I=0;I<4;I++){BindHip[I]=CS[Ref.FindBoneIndex(Bone(TEXT("femur_"),I))].GetLocation();Nominal[I]=CS[Ref.FindBoneIndex(Bone(TEXT("foot_tip_"),I))].GetLocation();TipOffsets[I]=Ref.GetRefBonePose()[Ref.FindBoneIndex(Bone(TEXT("foot_tip_"),I))].GetTranslation();BindUpper[I]=Ref.GetRefBonePose()[Ref.FindBoneIndex(Bone(TEXT("tibia_"),I))].GetTranslation().Size();BindLower[I]=Ref.GetRefBonePose()[Ref.FindBoneIndex(Bone(TEXT("tarsus_"),I))].GetTranslation().Size();}
 PrimaryComponentTick.AddPrerequisite(P->GetCharacterMovement(),P->GetCharacterMovement()->PrimaryComponentTick);
 P->GetMesh()->AddTickPrerequisiteComponent(this);
 PoseDelegate=P->GetMesh()->RegisterOnBoneTransformsFinalizedDelegate(FOnBoneTransformsFinalizedMultiCast::FDelegate::CreateUObject(this,&UAnanseGroundContact::SampleFinalizedPose));
 PreviousPosition=P->GetActorLocation();
 FString Report;if(FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyReport="),Report))
 {
  bCollectMetrics=true;
  Csv.Reset(IFileManager::Get().CreateFileWriter(*(FPaths::GetPath(Report)/(P->GetName()+TEXT("-foot-contact.csv"))),FILEWRITE_NoReplaceExisting));
  CsvBuffer=TEXT("time_s,leg,actual_x,actual_y,actual_z,contact_x,contact_y,contact_z,drift_cm,penetration_cm,segment_error_cm,query_us,pose_us,frame_interval_ms\n");
 }

}
void UAnanseGroundContact::EndPlay(const EEndPlayReason::Type Reason)
{if(Csv){FTCHARToUTF8 Data(*CsvBuffer);Csv->Serialize((void*)Data.Get(),Data.Length());Csv->Close();Csv.Reset();CsvBuffer.Reset();}if(auto* P=Cast<AAnansePlayer>(GetOwner()))P->GetMesh()->UnregisterOnBoneTransformsFinalizedDelegate(PoseDelegate);Super::EndPlay(Reason);}
void UAnanseGroundContact::ResetContacts()
{for(auto& L:Legs){L.Phase=FAnanseLegContact::EPhase::Released;L.Support.Reset();L.Reachable=false;L.Transitions++;}Snapshot=FAnanseContactPose();Snapshot.BodyOffset=FVector::ZeroVector;ResetCount++;}
bool UAnanseGroundContact::Ground(const FVector& Desired,FHitResult& Hit)const
{
 FCollisionQueryParams Params(SCENE_QUERY_STAT(AnanseGroundContact),false,GetOwner());
 const bool Found=GetWorld()->LineTraceSingleByChannel(Hit,Desired+FVector(0,0,200),Desired-FVector(0,0,160),ECC_Visibility,Params);
 if(bCollectMetrics && Found && Hit.GetComponent() && Hit.GetComponent()->Bounds.GetBox().IsInsideOrOn(Desired+FVector(0,0,90)))
 {
  FHitResult Former;const bool FormerHit=GetWorld()->LineTraceSingleByChannel(Former,Desired+FVector(0,0,90),Desired-FVector(0,0,160),ECC_Visibility,Params);
  if(FormerHit && (Former.bStartPenetrating || Former.Distance<=KINDA_SMALL_NUMBER))
  {
   if(RejectedInteriorProbeStarts==0)UE_LOG(LogTemp,Display,TEXT("Ananse contact probe diagnostic: former start=%s impact=%s distance=%.6f initial_overlap=%d; elevated hit=%s component=%s"),*(Desired+FVector(0,0,90)).ToString(),*Former.ImpactPoint.ToString(),Former.Distance,int32(Former.bStartPenetrating),*Hit.ImpactPoint.ToString(),*Hit.GetComponent()->GetName());
   RejectedInteriorProbeStarts++;
  }
 }
 return Found && !Hit.bStartPenetrating && Hit.Distance>KINDA_SMALL_NUMBER && Hit.GetComponent() && Hit.ImpactNormal.Z>=.819f;
}
bool UAnanseGroundContact::CanReach(int32 I,const FVector& Point,const FVector& Normal)const
{
 const auto* P=CastChecked<AAnansePlayer>(GetOwner());
 const FVector ModelHip=BindPelvis+Snapshot.BodyTilt.RotateVector(BindHip[I]-BindPelvis)+Snapshot.BodyOffset;
 const FVector Hip=P->GetMesh()->GetComponentTransform().TransformPosition(ModelHip);
 const FVector End=Point+Normal*TipOffsets[I].Size();
 const float Reach=FVector::Distance(Hip,End);
 return Reach<BindUpper[I]+BindLower[I]-2 && Reach>=ReachForFlex(BindUpper[I],BindLower[I],MaximumKneeFlex);
}
void UAnanseGroundContact::Plant(int32 I,const FHitResult& H)
{
 auto& L=Legs[I];L.Support=H.GetComponent();L.Point=H.ImpactPoint;L.Normal=H.ImpactNormal;
 L.LocalPoint=H.GetComponent()->GetComponentTransform().InverseTransformPosition(L.Point);
 L.LocalNormal=H.GetComponent()->GetComponentTransform().InverseTransformVectorNoScale(L.Normal);
 L.Phase=FAnanseLegContact::EPhase::Stance;L.Progress=0;L.Reachable=true;L.Transitions++;
}
void UAnanseGroundContact::BuildReleasedTargets()
{
 // Revalidate after the current frame's body-height/tilt adjustment. A contact
 // reachable under the previous snapshot must not be sent to an unreachable solve.
 for(int32 I=0;I<4;I++)if(Legs[I].Phase!=FAnanseLegContact::EPhase::Released && !CanReach(I,Legs[I].Point,Legs[I].Normal))
 {Legs[I].Phase=FAnanseLegContact::EPhase::Released;Legs[I].Support.Reset();Legs[I].Reachable=false;Legs[I].ReachFailures++;Legs[I].Transitions++;}
 const auto* P=CastChecked<AAnansePlayer>(GetOwner());const FTransform Mesh=P->GetMesh()->GetComponentTransform();
 for(int32 I=0;I<4;I++)if(Legs[I].Phase==FAnanseLegContact::EPhase::Released)
 {
  const FVector Hip=Mesh.TransformPosition(BindPelvis+Snapshot.BodyTilt.RotateVector(BindHip[I]-BindPelvis)+Snapshot.BodyOffset);
  FVector Aim=Hip-FVector(0,0,35);FHitResult H;
  if(Ground(Aim,H))Aim.Z=FMath::Max(Aim.Z,H.ImpactPoint.Z+2);
  if(FVector::Distance(Hip,Aim+FVector(0,0,TipOffsets[I].Size()))<ReachForFlex(BindUpper[I],BindLower[I],MaximumKneeFlex))Aim.Z=Hip.Z+35;
  // A pose target is not a latched contact. Keep the released limb folded near
  // its own hip and above queried support, rather than sprawling over a ledge.
  Snapshot.Valid[I]=true;Snapshot.Target[I]=Mesh.InverseTransformPosition(Aim);Snapshot.Normal[I]=Mesh.InverseTransformVectorNoScale(FVector::UpVector);
 }
}
void UAnanseGroundContact::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Tick)
{
 TRACE_CPUPROFILER_EVENT_SCOPE(AnanseFourLegGroundQueries);
 Super::TickComponent(Delta,Type,Tick);check(IsInGameThread());const double Start=FPlatformTime::Seconds();
 if(bCollectMetrics && LastFrame>0)FrameTimes.Add(float((Start-LastFrame)*1000));LastFrame=Start;
 auto* P=CastChecked<AAnansePlayer>(GetOwner());const FVector Position=P->GetActorLocation();
 const bool Discontinuity=FVector::Distance(Position,PreviousPosition)>100;PreviousPosition=Position;
 if(!bEnabled||!P->GetCharacterMovement()->IsMovingOnGround()||P->IsWebFlying()||Discontinuity){ResetContacts();BuildReleasedTargets();LastQueryMicroseconds=float((FPlatformTime::Seconds()-Start)*1e6);return;}
 const FTransform Mesh=P->GetMesh()->GetComponentTransform();bool Swinging=false;FVector MeanNormal=FVector::ZeroVector;float Height=0;int32 ValidCount=0;
 for(int32 I=0;I<4;I++)
 {
  auto& L=Legs[I];const FVector Desired=Mesh.TransformPosition(Nominal[I]);
  if(L.Phase==FAnanseLegContact::EPhase::Stance)
  {
   if(!L.Support.IsValid()||L.Support->GetCollisionEnabled()==ECollisionEnabled::NoCollision){L.Phase=FAnanseLegContact::EPhase::Released;L.MissingSupport++;L.Transitions++;}
   else
   {
    L.Point=L.Support->GetComponentTransform().TransformPosition(L.LocalPoint);L.Normal=L.Support->GetComponentTransform().TransformVectorNoScale(L.LocalNormal).GetSafeNormal();
    FHitResult H;if(!Ground(L.Point,H)||H.GetComponent()!=L.Support.Get()||FVector::Distance(H.ImpactPoint,L.Point)>2){L.Phase=FAnanseLegContact::EPhase::Released;L.MissingSupport++;L.Transitions++;}
   }
  }
  if(L.Phase==FAnanseLegContact::EPhase::Stance && !CanReach(I,L.Point,L.Normal)){L.Phase=FAnanseLegContact::EPhase::Released;L.Reachable=false;L.ReachFailures++;L.Transitions++;}
  if(L.Phase==FAnanseLegContact::EPhase::Released){FHitResult H;if(Ground(Desired,H) && CanReach(I,H.ImpactPoint,H.ImpactNormal))Plant(I,H);else{L.Reachable=false;L.MissingSupport++;}}
  if(L.Phase==FAnanseLegContact::EPhase::Swing)
  {
   Swinging=true;L.Progress=FMath::Min(1.f,L.Progress+Delta/.18f);
   const float ClearZ=FMath::Max(L.SwingStart.Z,L.SwingEnd.Z)+14;
   if(L.Progress<.25){L.Point=L.SwingStart;L.Point.Z=FMath::Lerp(L.SwingStart.Z,ClearZ,FMath::SmoothStep(0.f,1.f,L.Progress*4));}
   else if(L.Progress<.75){L.Point=FMath::Lerp(L.SwingStart,L.SwingEnd,FMath::SmoothStep(0.f,1.f,(L.Progress-.25f)*2));L.Point.Z=ClearZ;}
   else{L.Point=L.SwingEnd;L.Point.Z=FMath::Lerp(ClearZ,L.SwingEnd.Z,FMath::SmoothStep(0.f,1.f,(L.Progress-.75f)*4));}
   if(L.Progress>=1){FHitResult H;if(Ground(L.SwingEnd,H))Plant(I,H);else{L.Phase=FAnanseLegContact::EPhase::Released;L.MissingSupport++;}}
  }
  Snapshot.Valid[I]=L.Phase!=FAnanseLegContact::EPhase::Released;
  Snapshot.Target[I]=Mesh.InverseTransformPosition(L.Point);Snapshot.Normal[I]=Mesh.InverseTransformVectorNoScale(L.Normal);
  if(L.Phase==FAnanseLegContact::EPhase::Stance){MeanNormal+=Snapshot.Normal[I];Height+=L.Point.Z-Desired.Z;ValidCount++;}
 }
 // Round-robin diagonal order, at most two swings and at least two retained stances.
 // An unsupported leg cannot deadlock the other three legs' stepping schedule.
 int32 Stances=0,Swings=0;for(const auto& L:Legs){if(L.Phase==FAnanseLegContact::EPhase::Stance)Stances++;if(L.Phase==FAnanseLegContact::EPhase::Swing)Swings++;}
 const int32 Order[4]={0,3,1,2};const int32 ScheduleStart=NextLeg;
 for(int32 N=0;N<4 && Swings<2 && Stances>2;N++)
 {
  const int32 O=(ScheduleStart+N)%4,I=Order[O];auto& L=Legs[I];
  const FVector Desired=Mesh.TransformPosition(Nominal[I])+P->GetVelocity()*.1f;
  if(L.Phase!=FAnanseLegContact::EPhase::Stance || FVector::Dist2D(Desired,L.Point)<=10)continue;
  FHitResult H;
  if(Ground(Desired,H) && CanReach(I,H.ImpactPoint,H.ImpactNormal) && FMath::Abs(H.ImpactPoint.Z-L.Point.Z)<=25)
  {L.SwingStart=L.Point;L.SwingEnd=H.ImpactPoint;L.Progress=0;L.Phase=FAnanseLegContact::EPhase::Swing;L.Transitions++;Stances--;Swings++;NextLeg=(O+1)%4;}
 }
 Snapshot.BodyOffset=FVector(0,0,ValidCount?FMath::Clamp(Height/ValidCount-6,-16.f,4.f):-6);
 FQuat Tilt=FQuat::FindBetweenNormals(FVector::UpVector,MeanNormal.GetSafeNormal(SMALL_NUMBER,FVector::UpVector));const double Angle=Tilt.GetAngle();if(Angle>FMath::DegreesToRadians(12.))Tilt=FQuat::Slerp(FQuat::Identity,Tilt,FMath::DegreesToRadians(12.)/Angle);Snapshot.BodyTilt=Tilt;
 BuildReleasedTargets();
 LastQueryMicroseconds=float((FPlatformTime::Seconds()-Start)*1e6);if(bCollectMetrics)QueryTimes.Add(LastQueryMicroseconds);
}
void UAnanseGroundContact::SampleFinalizedPose()
{
 check(IsInGameThread());if(!bCollectMetrics)return;SolveTimes.Add(LastSolveMicroseconds);auto* P=CastChecked<AAnansePlayer>(GetOwner());auto* Mesh=P->GetMesh();
 for(const FTransform& Transform:Mesh->GetComponentSpaceTransforms())if(!Transform.IsValid())InvalidTransforms++;
 for(int32 I=0;I<4;I++)
 {
  auto& L=Legs[I];
  const FTransform Evaluated=Mesh->GetSocketTransform(Bone(TEXT("tarsus_"),I),RTS_World);
  const FVector Actual=Evaluated.TransformPosition(TipOffsets[I]);
  if(Actual.ContainsNaN()){InvalidTransforms++;continue;}
  const FVector HipPoint=Mesh->GetBoneLocation(Bone(TEXT("femur_"),I)),KneePoint=Mesh->GetBoneLocation(Bone(TEXT("tibia_"),I)),AnklePoint=Mesh->GetBoneLocation(Bone(TEXT("tarsus_"),I));
  const float Flex=180-FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(FVector::DotProduct((HipPoint-KneePoint).GetSafeNormal(),(AnklePoint-KneePoint).GetSafeNormal()),-1.,1.)));
  L.MinKneeFlex=FMath::Min(L.MinKneeFlex,Flex);L.MaxKneeFlex=FMath::Max(L.MaxKneeFlex,Flex);
  if(bEnabled && (Flex<MinimumKneeFlex-.1f || Flex>MaximumKneeFlex+.1f))L.JointLimitViolations++;

  float Penetration=0;
  if(bEnabled)
  {
   // Query actual collision occupancy, including swing. An overhead bridge is not
   // penetration: only components overlapping the evaluated contact point qualify.
   TArray<FOverlapResult> Overlaps;FCollisionQueryParams Q(SCENE_QUERY_STAT(AnanseEvaluatedFootPenetration),false,P);
   GetWorld()->OverlapMultiByChannel(Overlaps,Actual,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(.01f),Q);
   for(const auto& O:Overlaps)if(UPrimitiveComponent* C=O.GetComponent())
   {
    FHitResult SurfaceHit;if(C->LineTraceComponent(SurfaceHit,Actual+FVector(0,0,250),Actual-FVector(0,0,300),Q) && SurfaceHit.ImpactNormal.Z>=.819)
   {
     const float Depth=float(FMath::Max(0.,-FVector::DotProduct(Actual-SurfaceHit.ImpactPoint,SurfaceHit.ImpactNormal)));
     if(Depth>.5f && (L.Penetration.IsEmpty() || Depth>L.Penetration.Last()))
      UE_LOG(LogTemp,Display,TEXT("Ananse contact penetration diagnostic t=%.4f leg=%s phase=%d actual=%s top=%s component=%s boundsOrigin=%s extent=%s depth=%.4f"),GetWorld()->GetTimeSeconds(),Sides[I],int32(L.Phase),*Actual.ToString(),*SurfaceHit.ImpactPoint.ToString(),*C->GetName(),*C->Bounds.Origin.ToString(),*C->Bounds.BoxExtent.ToString(),Depth);
     Penetration=FMath::Max(Penetration,Depth);
   }
   }
   L.Penetration.Add(Penetration);
  }
  if(!bEnabled||L.Phase!=FAnanseLegContact::EPhase::Stance||!L.Support.IsValid()){L.Excluded++;continue;}
  L.SupportSamples.FindOrAdd(L.Support->GetOwner()->GetFName())++;
  for(FName Tag:L.Support->GetOwner()->Tags)if(Tag.ToString().StartsWith(TEXT("AnanseFixture:")))L.SupportSamples.FindOrAdd(Tag)++;
  const float Upper=FVector::Distance(Mesh->GetBoneLocation(Bone(TEXT("femur_"),I)),Mesh->GetBoneLocation(Bone(TEXT("tibia_"),I)));
  const float Lower=FVector::Distance(Mesh->GetBoneLocation(Bone(TEXT("tibia_"),I)),Mesh->GetBoneLocation(Bone(TEXT("tarsus_"),I)));
  L.MaxStretchError=FMath::Max(L.MaxStretchError,FMath::Max(FMath::Abs(Upper-BindUpper[I]),FMath::Abs(Lower-BindLower[I])));
  const float Drift=FVector::Distance(Actual,L.Point);L.Drift.Add(Drift);
  L.Reachable=Drift<=2;if(!L.Reachable)L.ReachFailures++;
  if(Csv)CsvBuffer+=FString::Printf(TEXT("%.6f,%s,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n"),GetWorld()->GetTimeSeconds(),Sides[I],Actual.X,Actual.Y,Actual.Z,L.Point.X,L.Point.Y,L.Point.Z,Drift,L.Penetration.Last(),L.MaxStretchError,LastQueryMicroseconds,LastSolveMicroseconds,FrameTimes.IsEmpty()?0:FrameTimes.Last());
 }
 if(Csv && CsvBuffer.Len()>65536){FTCHARToUTF8 Data(*CsvBuffer);Csv->Serialize((void*)Data.Get(),Data.Length());CsvBuffer.Reset();}
}
FString UAnanseGroundContact::MetricsJson()const
{
 auto Root=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Array;
 for(int32 I=0;I<4;I++)
 {
  auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("leg"),Sides[I]);J->SetNumberField(TEXT("upper_length_cm"),BindUpper[I]);J->SetNumberField(TEXT("lower_length_cm"),BindLower[I]);J->SetNumberField(TEXT("samples"),Legs[I].Drift.Num());J->SetNumberField(TEXT("excluded_swing_airborne_invalid"),Legs[I].Excluded);
  auto D=Legs[I].Drift;D.Sort();auto N=Legs[I].Penetration;N.Sort();J->SetNumberField(TEXT("p95_stance_drift_cm"),D.Num()?D[FMath::Min(D.Num()-1,FMath::FloorToInt(D.Num()*.95))]:-1);J->SetNumberField(TEXT("max_penetration_cm"),N.Num()?N.Last():-1);
  J->SetNumberField(TEXT("min_knee_flex_degrees"),Legs[I].MinKneeFlex);J->SetNumberField(TEXT("max_knee_flex_degrees"),Legs[I].MaxKneeFlex);J->SetNumberField(TEXT("joint_limit_violations"),Legs[I].JointLimitViolations);
  J->SetNumberField(TEXT("max_segment_length_error_cm"),Legs[I].MaxStretchError);auto Supports=MakeShared<FJsonObject>();for(const auto& Pair:Legs[I].SupportSamples)Supports->SetNumberField(Pair.Key.ToString(),Pair.Value);J->SetObjectField(TEXT("support_sample_coverage"),Supports);J->SetNumberField(TEXT("reach_failures"),Legs[I].ReachFailures);J->SetNumberField(TEXT("support_loss"),Legs[I].MissingSupport);J->SetNumberField(TEXT("transitions"),Legs[I].Transitions);Array.Add(MakeShared<FJsonValueObject>(J));
 }
 auto Quantile=[](TArray<float> A){A.Sort();return A.Num()?A[FMath::Min(A.Num()-1,FMath::FloorToInt(A.Num()*.95))]:-1;};
 Root->SetNumberField(TEXT("rejected_former_interior_probe_samples"),RejectedInteriorProbeStarts);
 Root->SetNumberField(TEXT("world_time_seconds"),GetWorld()?GetWorld()->GetTimeSeconds():0);
 Root->SetNumberField(TEXT("p95_frame_interval_ms"),Quantile(FrameTimes));Root->SetNumberField(TEXT("p95_query_us"),Quantile(QueryTimes));Root->SetNumberField(TEXT("p95_solve_us"),Quantile(SolveTimes));Root->SetNumberField(TEXT("invalid_transforms"),InvalidTransforms);Root->SetNumberField(TEXT("last_solved_chains"),LastSolvedChains);
 Root->SetArrayField(TEXT("legs"),Array);Root->SetNumberField(TEXT("resets"),ResetCount);Root->SetNumberField(TEXT("last_query_us"),LastQueryMicroseconds);Root->SetNumberField(TEXT("last_solve_us"),LastSolveMicroseconds);Root->SetStringField(TEXT("measurement_stage"),TEXT("OnBoneTransformsFinalized evaluated tarsus + imported tip offset; drift uses latched stance, penetration independently queries actual collision for stance/swing/airborne; no requested-target measurement"));FString Text;auto W=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Root,W);return Text;
}

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
AAnanseContactSupport::AAnanseContactSupport()
{
 PrimaryActorTick.bCanEverTick=true;Surface=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MovingContactSurface"));SetRootComponent(Surface);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));if(Cube.Succeeded())Surface->SetStaticMesh(Cube.Object);
 Surface->SetMobility(EComponentMobility::Movable);Surface->SetCollisionProfileName(TEXT("BlockAll"));Surface->SetWorldScale3D(FVector(4,5,.2));
}
void AAnanseContactSupport::BeginPlay(){Super::BeginPlay();Origin=GetActorLocation();}
void AAnanseContactSupport::Tick(float Delta)
{
 Super::Tick(Delta);Elapsed+=Delta;SetActorLocation(Origin+FVector(25*FMath::Sin(Elapsed*.5f),0,0));
 bool Occupied=false;
 for(TActorIterator<ACharacter> It(GetWorld());It;++It)
 {
  const FVector Local=Surface->GetComponentTransform().InverseTransformPosition(It->GetActorLocation());
  if(FMath::Abs(Local.X)<50 && FMath::Abs(Local.Y)<50)Occupied=true;
 }
 if(bDisappearing && !bDisabled){OccupiedSeconds=Occupied?OccupiedSeconds+Delta:0;if(OccupiedSeconds>=3)bDisabled=true;}
 // Once occupied support disappears, defer reappearance until its footprint is clear.
 // The fixture's catch surface limits the drop to20cm; no collider appears inside an occupant.
 const bool Exists=!bDisappearing||!bDisabled;
 if(bDisabled && !Occupied){bDisabled=false;OccupiedSeconds=0;}
 Surface->SetVisibility(Exists);Surface->SetCollisionEnabled(Exists?ECollisionEnabled::QueryAndPhysics:ECollisionEnabled::NoCollision);
}
