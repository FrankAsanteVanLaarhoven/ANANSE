#pragma once
#include "CoreMinimal.h"
class UAnimInstance;
struct FPoseContext;

// Game-thread snapshot + bounded, critically damped response. Worker evaluation
// touches only copied values and garment-only local transforms; never world/physics.
struct FAnanseSecondaryMotion
{
 FVector2D Angle=FVector2D::ZeroVector,Rate=FVector2D::ZeroVector;
 FVector LastLocation=FVector::ZeroVector,LastVelocity=FVector::ZeroVector;
 FQuat LastChest=FQuat::Identity;
 float LastYaw=0,LastTime=-1,Phase=0;
 bool Initialized=false,Enabled=true;
 int32 AppliedBones=0,Resets=0,Evaluations=0;
 float PeakDegrees=0;
 void Gather(UAnimInstance* Instance,float Delta);
 void Apply(FPoseContext& Output);
 static void Advance(float Target,float Delta,float& Position,float& Velocity);
 static float ClothScale(FName Bone);
};
