#include "AnanseSecondaryMotion.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimInstanceProxy.h"
#include "GameFramework/Actor.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "BonePose.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

void FAnanseSecondaryMotion::Advance(float Target,float Delta,float& Position,float& Velocity)
{
 // Closed-form critically damped spring; no unstable Euler integration on stalls.
 if(!FMath::IsFinite(Target)||!FMath::IsFinite(Delta)||Delta<0||Delta>.25f){Position=Velocity=0;return;}
 constexpr float W=9.f;const float Error=Position-Target,C=Velocity+W*Error,E=FMath::Exp(-W*Delta);
 Position=Target+(Error+C*Delta)*E;Velocity=(Velocity-W*C*Delta)*E;
 Position=FMath::Clamp(Position,-6.f,6.f);
}
float FAnanseSecondaryMotion::ClothScale(FName Bone)
{
 // Exact imported bone allowlist. No pelvis, skin, limbs, hair, armour, tail or props.
 const FString N=Bone.ToString();
 if(N==TEXT("cape_L_01")||N==TEXT("cape_R_01"))return .25f;
 if(N==TEXT("cape_L_02")||N==TEXT("cape_R_02"))return .55f;
 if(N==TEXT("cape_L_03")||N==TEXT("cape_R_03"))return .8f;
 if(N==TEXT("cape"))return .6f;
 if(N==TEXT("cloth_01"))return .25f;
 if(N==TEXT("cloth_02"))return .55f;
 if(N==TEXT("cloth_03"))return .8f;
 if(N==TEXT("Dress_L")||N==TEXT("Dress_R")||N==TEXT("Apron_L")||N==TEXT("Apron_R")||N==TEXT("Garment_L")||N==TEXT("Garment_R"))return .25f;
 return 0;
}
void FAnanseSecondaryMotion::Gather(UAnimInstance* Instance,float Delta)
{
 check(IsInGameThread());const auto* Owner=Instance->GetOwningActor();const auto* Mesh=Instance->GetSkelMeshComponent();
 Enabled=!FParse::Param(FCommandLine::Get(),TEXT("AnanseDisableSecondaryMotion"));
 if(!Owner||!Mesh||!Owner->GetWorld()){Enabled=false;return;}
 const float Time=Owner->GetWorld()->GetTimeSeconds(),Yaw=Owner->GetActorRotation().Yaw;
 const FVector Location=Owner->GetActorLocation(),Velocity=Owner->GetVelocity();
 const FQuat Chest=Mesh->GetSocketTransform(TEXT("chest"),RTS_Component).GetRotation();
 const bool Reset=!Initialized||!Enabled||!FMath::IsFinite(Delta)||Delta<=0||Delta>.25f||Time<LastTime||Time-LastTime>.5f||FVector::DistSquared(Location,LastLocation)>FMath::Square(150.f);
 if(Reset){Angle=Rate=FVector2D::ZeroVector;++Resets;}
 else
 {
  const FVector LocalVelocity=Mesh->GetComponentTransform().InverseTransformVectorNoScale(Velocity);
  const FVector Acceleration=Mesh->GetComponentTransform().InverseTransformVectorNoScale((Velocity-LastVelocity)/Delta);
  const float Turn=FMath::Clamp(FMath::FindDeltaAngleDegrees(LastYaw,Yaw)/Delta,-180.f,180.f);
  Phase=FMath::Fmod(Phase+Delta,100.f);
  // Centimetre-based speed/acceleration, small wind at rest; movement adds drag
  // and delayed turn response. Conservative robe amplitude avoids leg distortion.
  const FRotator Gesture=(Chest*LastChest.Inverse()).Rotator();
  const float Pitch=FMath::Clamp(LocalVelocity.X*.009f+Acceleration.X*.0008f+FMath::Clamp(Gesture.Pitch/Delta,-90.f,90.f)*.015f+.5f*FMath::Sin(Phase*1.7f),-5.f,5.f);
  const float Sway=FMath::Clamp(-LocalVelocity.Y*.006f-Turn*.014f+FMath::Clamp(Gesture.Roll/Delta,-90.f,90.f)*.012f+.35f*FMath::Sin(Phase*2.1f),-4.f,4.f);
  float X=Angle.X,Y=Angle.Y,VX=Rate.X,VY=Rate.Y;Advance(Pitch,Delta,X,VX);Advance(Sway,Delta,Y,VY);Angle=FVector2D(X,Y);Rate=FVector2D(VX,VY);
 }
 Initialized=true;LastLocation=Location;LastVelocity=Velocity;LastYaw=Yaw;LastTime=Time;LastChest=Chest;
}
void FAnanseSecondaryMotion::Apply(FPoseContext& Output)
{
 AppliedBones=0;if(!Enabled)return;
 const auto& Bones=Output.Pose.GetBoneContainer();FCSPose<FCompactPose> CS;CS.InitPose(Output.Pose);
 for(int32 I=0;I<Output.Pose.GetNumBones();++I)
 {
  FCompactPoseBoneIndex B(I);const float Scale=ClothScale(Bones.GetReferenceSkeleton().GetBoneName(Bones.GetSkeletonIndex(B)));if(Scale<=0)continue;
  // Convert component-space bend axes to this evaluated bone's local frame.
  const FQuat Rotation=CS.GetComponentSpaceTransform(B).GetRotation();
  const FQuat Q=FQuat(Rotation.UnrotateVector(FVector::YAxisVector),FMath::DegreesToRadians(Angle.X*Scale))*FQuat(Rotation.UnrotateVector(FVector::XAxisVector),FMath::DegreesToRadians(Angle.Y*Scale));
  Output.Pose[B].SetRotation((Output.Pose[B].GetRotation()*Q).GetNormalized());++AppliedBones;
 }
 PeakDegrees=FMath::Max(PeakDegrees,float(Angle.Size()));++Evaluations;
}
