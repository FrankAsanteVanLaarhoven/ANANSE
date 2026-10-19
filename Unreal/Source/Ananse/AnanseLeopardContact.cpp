#include "AnanseLeopardContact.h"
#include "AnansePlayer.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "Json.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace { const TCHAR* Side[2]={TEXT("L"),TEXT("R")};
FName LegBone(const TCHAR* Prefix,int32 I){return FName(*(FString(Prefix)+Side[I]));} }
UAnanseLeopardContact::UAnanseLeopardContact()
{PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PrePhysics;}
void UAnanseLeopardContact::BeginPlay()
{
 Super::BeginPlay();auto* P=CastChecked<AAnansePlayer>(GetOwner());auto* Mesh=P->GetMesh();
 if(!Mesh->GetSkeletalMeshAsset())return;
 const auto& Ref=Mesh->GetSkeletalMeshAsset()->GetRefSkeleton();TArray<FTransform> CS=Ref.GetRefBonePose();
 for(int32 I=0;I<CS.Num();++I)if(Ref.GetParentIndex(I)>=0)CS[I]=CS[I]*CS[Ref.GetParentIndex(I)];
 for(int32 I=0;I<2;++I)
 {
  const int32 H=Ref.FindBoneIndex(LegBone(TEXT("thigh_"),I)),K=Ref.FindBoneIndex(LegBone(TEXT("shin_"),I)),A=Ref.FindBoneIndex(LegBone(TEXT("foot_"),I)),B=Ref.FindBoneIndex(LegBone(TEXT("ball_"),I));
  if(FMath::Min(FMath::Min(H,K),FMath::Min(A,B))<0)return;
  // Authored source sole plane is Z=0 cm; retain the actual ball's XY location.
  Nominal[I]=CS[B].GetLocation();Nominal[I].Z=0;
  Snapshot.SoleOffset[I]=CS[A].InverseTransformPosition(Nominal[I]);
  Hip[I]=CS[H].GetLocation();Upper[I]=FVector::Distance(CS[H].GetLocation(),CS[K].GetLocation());Lower[I]=FVector::Distance(CS[K].GetLocation(),CS[A].GetLocation());
 }
 PrimaryComponentTick.AddPrerequisite(P->GetCharacterMovement(),P->GetCharacterMovement()->PrimaryComponentTick);
 Mesh->AddTickPrerequisiteComponent(this);
 PoseDelegate=Mesh->RegisterOnBoneTransformsFinalizedDelegate(FOnBoneTransformsFinalizedMultiCast::FDelegate::CreateUObject(this,&UAnanseLeopardContact::SampleFinalPose));
 FString Report;bCollect=FParse::Value(FCommandLine::Get(),TEXT("AnanseLeopardVerify="),Report)||FParse::Value(FCommandLine::Get(),TEXT("AnanseLeopardContactVerify="),Report)||FParse::Value(FCommandLine::Get(),TEXT("AnanseCrossFamilyVerify="),Report)||FParse::Value(FCommandLine::Get(),TEXT("AnanseStoryCastVerify="),Report);
 PreviousPosition=P->GetActorLocation();bReady=true;ResetContacts();
}
void UAnanseLeopardContact::EndPlay(const EEndPlayReason::Type Reason)
{if(auto* P=Cast<AAnansePlayer>(GetOwner()))P->GetMesh()->UnregisterOnBoneTransformsFinalizedDelegate(PoseDelegate);Super::EndPlay(Reason);}
void UAnanseLeopardContact::ResetContacts()
{check(IsInGameThread());for(int32 I=0;I<2;++I){auto& L=Legs[I];L.Phase=FAnanseLegContact::EPhase::Released;L.Support.Reset();L.Reachable=false;++L.Transitions;Snapshot.Target[I]=(bReady?Nominal[I]:FVector::ZeroVector)+FVector(0,0,25);Snapshot.Normal[I]=FVector::UpVector;}Snapshot.Valid[0]=Snapshot.Valid[1]=false;Snapshot.BodyZ=-6;++Resets;}
bool UAnanseLeopardContact::Ground(const FVector& Point,FHitResult& Hit)const
{
 FCollisionQueryParams Q(SCENE_QUERY_STAT(LeopardFootGround),false,GetOwner());
 return GetWorld()->LineTraceSingleByChannel(Hit,Point+FVector(0,0,100),Point-FVector(0,0,130),ECC_Visibility,Q)
  && Hit.GetComponent() && Hit.ImpactNormal.Z>=FMath::Cos(FMath::DegreesToRadians(25.f));
}
void UAnanseLeopardContact::Plant(int32 I,const FHitResult& H)
{
 auto& L=Legs[I];L.Support=H.GetComponent();L.Point=H.ImpactPoint;L.Normal=H.ImpactNormal;
 L.LocalPoint=L.Support->GetComponentTransform().InverseTransformPosition(L.Point);
 L.LocalNormal=L.Support->GetComponentTransform().InverseTransformVectorNoScale(L.Normal);
 L.Phase=FAnanseLegContact::EPhase::Stance;L.Progress=0;L.Reachable=true;++L.Transitions;
}
void UAnanseLeopardContact::TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Tick)
{
 Super::TickComponent(Dt,Type,Tick);check(IsInGameThread());if(!bReady)return;
 const double Start=FPlatformTime::Seconds();auto* P=CastChecked<AAnansePlayer>(GetOwner());auto* Mesh=P->GetMesh();
 if(FVector::Dist(P->GetActorLocation(),PreviousPosition)>100)ResetContacts();PreviousPosition=P->GetActorLocation();
 Snapshot.Enabled=bEnabled;
 if(!bEnabled || !P->GetCharacterMovement()->IsMovingOnGround())
 {
  ResetContacts();Snapshot.Enabled=bEnabled;
  for(int32 I=0;I<2;++I){Snapshot.Target[I]=Nominal[I]+FVector(0,0,25);Snapshot.Normal[I]=FVector::UpVector;}
  QueryUs=float((FPlatformTime::Seconds()-Start)*1e6);return;
 }
 const FTransform World=Mesh->GetComponentTransform();FHitResult Hits[2];bool Grounded[2];float Body=0;int32 Count=0;
 for(int32 I=0;I<2;++I){const FVector Desired=World.TransformPosition(Nominal[I]);Grounded[I]=Ground(Desired,Hits[I]);if(Grounded[I]){Body+=Hits[I].ImpactPoint.Z-Desired.Z;++Count;}}
 Snapshot.BodyZ=FMath::FInterpTo(Snapshot.BodyZ,Count?FMath::Clamp(Body/Count-6.f,-18.f,10.f):-6.f,Dt,10);
 bool Swinging=false;
 for(int32 I=0;I<2;++I)
 {
  auto& L=Legs[I];const FVector Desired=World.TransformPosition(Nominal[I]);
  if(L.Phase==FAnanseLegContact::EPhase::Stance)
  {
   if(!L.Support.IsValid() || !L.Support->IsCollisionEnabled()){L.Phase=FAnanseLegContact::EPhase::Released;++L.MissingSupport;}
   else
   {
    L.Point=L.Support->GetComponentTransform().TransformPosition(L.LocalPoint);L.Normal=L.Support->GetComponentTransform().TransformVectorNoScale(L.LocalNormal).GetSafeNormal();
    FHitResult H;if(!Ground(L.Point,H)||H.GetComponent()!=L.Support.Get()||FVector::Dist(H.ImpactPoint,L.Point)>2){L.Phase=FAnanseLegContact::EPhase::Released;++L.MissingSupport;}
   }
  }
  if(L.Phase==FAnanseLegContact::EPhase::Released)
  {if(Grounded[I])Plant(I,Hits[I]);else{L.Reachable=false;++L.MissingSupport;}}
  if(L.Phase==FAnanseLegContact::EPhase::Swing)
  {
   Swinging=true;L.Progress=FMath::Min(1.f,L.Progress+Dt/.24f);
   const float ClearZ=FMath::Max(L.SwingStart.Z,L.SwingEnd.Z)+18;
   if(L.Progress<.25f){L.Point=L.SwingStart;L.Point.Z=FMath::Lerp(L.SwingStart.Z,ClearZ,FMath::SmoothStep(0.f,1.f,L.Progress*4));}
   else if(L.Progress<.75f){L.Point=FMath::Lerp(L.SwingStart,L.SwingEnd,FMath::SmoothStep(0.f,1.f,(L.Progress-.25f)*2));L.Point.Z=ClearZ;}
   else{L.Point=L.SwingEnd;L.Point.Z=FMath::Lerp(ClearZ,L.SwingEnd.Z,FMath::SmoothStep(0.f,1.f,(L.Progress-.75f)*4));}
   if(L.Progress>=1){FHitResult H;if(Ground(L.SwingEnd,H))Plant(I,H);else{L.Phase=FAnanseLegContact::EPhase::Released;++L.MissingSupport;}}
  }
  const FVector H=World.TransformPosition(Hip[I]+FVector(0,0,Snapshot.BodyZ));
  if(L.Phase!=FAnanseLegContact::EPhase::Released && FVector::Dist(H,L.Point)>Upper[I]+Lower[I]+Snapshot.SoleOffset[I].Size()-2)
  {L.Phase=FAnanseLegContact::EPhase::Released;L.Reachable=false;++L.ReachFailures;}
  Snapshot.Valid[I]=L.Phase!=FAnanseLegContact::EPhase::Released;
  Snapshot.Target[I]=World.InverseTransformPosition(Snapshot.Valid[I]?L.Point:Desired+FVector(0,0,25));
  Snapshot.Normal[I]=World.InverseTransformVectorNoScale(Snapshot.Valid[I]?L.Normal:FVector::UpVector).GetSafeNormal();
  if(L.Phase!=FAnanseLegContact::EPhase::Stance)
  {
   FVector Target=World.TransformPosition(Snapshot.Target[I]);FHitResult Clearance;
   if(Ground(Target,Clearance) && FVector::DotProduct(Target-Clearance.ImpactPoint,Clearance.ImpactNormal)<.1f)
   {Target=Clearance.ImpactPoint+Clearance.ImpactNormal*.1f;Snapshot.Target[I]=World.InverseTransformPosition(Target);}
  }
 }
 if(!Swinging)
 {
  for(int32 J=0;J<2;++J)
  {
   const int32 I=(NextLeg+J)%2;auto& L=Legs[I];const FVector Desired=World.TransformPosition(Nominal[I]);
   if(L.Phase!=FAnanseLegContact::EPhase::Stance || !Grounded[I] || FVector::Dist2D(Desired,L.Point)<14)continue;
   const FVector Forward=P->GetVelocity().GetClampedToMaxSize(45)*.16f;FHitResult Target;
   if(Ground(Desired+Forward,Target)){L.SwingStart=L.Point;L.SwingEnd=Target.ImpactPoint;L.Progress=0;L.Phase=FAnanseLegContact::EPhase::Swing;++L.Transitions;NextLeg=1-I;}break;
  }
 }
 QueryUs=float((FPlatformTime::Seconds()-Start)*1e6);
}
void UAnanseLeopardContact::SampleFinalPose()
{
 check(IsInGameThread());if(!bReady || !Snapshot.Enabled || !bCollect)return;
 auto* Mesh=CastChecked<AAnansePlayer>(GetOwner())->GetMesh();
 const double Now=FPlatformTime::Seconds();if(LastFrame)Frames.Add(float((Now-LastFrame)*1000));LastFrame=Now;Queries.Add(QueryUs);Solves.Add(SolveUs);
 for(int32 I=0;I<2;++I)
 {
  auto& L=Legs[I];const FTransform Foot=Mesh->GetSocketTransform(LegBone(TEXT("foot_"),I));
  const FVector Actual=Foot.TransformPosition(Snapshot.SoleOffset[I]);
  if(Actual.ContainsNaN() || !Foot.IsValid()){++InvalidTransforms;++L.Excluded;continue;}
  FHitResult H;float Pen=0;if(Ground(Actual,H))Pen=FMath::Max(0.f,FVector::DotProduct(H.ImpactPoint-Actual,H.ImpactNormal));L.Penetration.Add(Pen);
  if(Pen>MaxPenetration[I]){MaxPenetration[I]=Pen;PenetrationContext[I]=FString::Printf(TEXT("time=%.6f phase=%d actual=%s hit=%s actor=%s bodyZ=%.6f"),GetWorld()->GetTimeSeconds(),int32(L.Phase),*Actual.ToString(),*H.ImpactPoint.ToString(),H.GetActor()?*H.GetActor()->GetName():TEXT("none"),Snapshot.BodyZ);}
  if(L.Phase!=FAnanseLegContact::EPhase::Stance || !L.Support.IsValid()){++L.Excluded;continue;}
  const FVector Expected=L.Support->GetComponentTransform().TransformPosition(L.LocalPoint);L.Drift.Add(FVector::Dist(Actual,Expected));
  L.SupportSamples.FindOrAdd(L.Support->GetOwner()->GetFName())++;
  for(FName Tag:L.Support->GetOwner()->Tags)if(Tag.ToString().StartsWith(TEXT("AnanseFixture:")))L.SupportSamples.FindOrAdd(Tag)++;
  const FVector HipPos=Mesh->GetSocketLocation(LegBone(TEXT("thigh_"),I)),Knee=Mesh->GetSocketLocation(LegBone(TEXT("shin_"),I)),Ankle=Foot.GetLocation();
  L.MaxStretchError=FMath::Max(L.MaxStretchError,FMath::Max(FMath::Abs(float(FVector::Dist(HipPos,Knee))-Upper[I]),FMath::Abs(float(FVector::Dist(Knee,Ankle))-Lower[I])));
 }
}
FString UAnanseLeopardContact::MetricsJson()const
{
 auto Quantile=[](TArray<float> V){V.Sort();return V.Num()?V[FMath::Min(V.Num()-1,FMath::FloorToInt(.95*V.Num()))]:-1.f;};
 auto R=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> List;
 R->SetStringField(TEXT("left_max_penetration_context"),PenetrationContext[0]);R->SetStringField(TEXT("right_max_penetration_context"),PenetrationContext[1]);
 for(int32 I=0;I<2;++I){auto J=MakeShared<FJsonObject>();const auto& L=Legs[I];J->SetStringField(TEXT("leg"),Side[I]);J->SetNumberField(TEXT("samples"),L.Drift.Num());J->SetNumberField(TEXT("excluded_swing_airborne_invalid"),L.Excluded);J->SetNumberField(TEXT("p95_stance_drift_cm"),Quantile(L.Drift));float Max=0;for(float V:L.Penetration)Max=FMath::Max(Max,V);J->SetNumberField(TEXT("max_penetration_cm"),Max);J->SetNumberField(TEXT("max_segment_length_error_cm"),L.MaxStretchError);J->SetNumberField(TEXT("support_loss"),L.MissingSupport);J->SetNumberField(TEXT("transitions"),L.Transitions);auto Coverage=MakeShared<FJsonObject>();for(auto& Pair:L.SupportSamples)Coverage->SetNumberField(Pair.Key.ToString(),Pair.Value);J->SetObjectField(TEXT("support_sample_coverage"),Coverage);List.Add(MakeShared<FJsonValueObject>(J));}
 R->SetArrayField(TEXT("legs"),List);R->SetNumberField(TEXT("invalid_transforms"),InvalidTransforms);R->SetNumberField(TEXT("solved_chains"),SolvedChains);R->SetNumberField(TEXT("resets"),Resets);R->SetNumberField(TEXT("p95_query_us"),Quantile(Queries));R->SetNumberField(TEXT("p95_solve_us"),Quantile(Solves));R->SetNumberField(TEXT("p95_frame_interval_ms"),Quantile(Frames));R->SetStringField(TEXT("contact_point"),TEXT("Actual finalized foot transform with authored rest ball XY projected onto source sole Z=0cm; offset per actual bone. No requested-target-only samples."));FString Text;auto W=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(R,W);return Text;
}
