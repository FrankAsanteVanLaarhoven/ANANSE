#pragma once
#include "CoreMinimal.h"
class USkeletalMeshComponent;class UStaticMeshComponent;class UAnimSequence;
/** Presentation only; called on game thread after final bone evaluation. */
namespace AnanseAsoLedger
{
 void Update(USkeletalMeshComponent* Skin,UStaticMeshComponent* Prop,UAnimSequence* Clip,float Time,bool bParkWhenIdle=false);
}
