#pragma once
#include "CoreMinimal.h"
class USkeletalMeshComponent;class UAnimSequence;
// Optional read-only capture after final evaluation; never alters the pose.
void CaptureAsoSurface(USkeletalMeshComponent* Skin,UAnimSequence* Clip,float Time,TSet<FString>& Captured,uint32 Epoch);
