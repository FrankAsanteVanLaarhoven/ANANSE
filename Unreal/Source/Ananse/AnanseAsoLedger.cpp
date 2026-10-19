#include "AnanseAsoLedger.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/Actor.h"
void AnanseAsoLedger::Update(USkeletalMeshComponent* Skin,UStaticMeshComponent* Prop,UAnimSequence* Clip,float Time,bool bParkWhenIdle)
{
 check(IsInGameThread());
 if(!Skin||!Prop||!Prop->GetStaticMesh())return;
 const bool Inspect=Clip&&Clip->GetName().Contains(TEXT("InspectEvidence"))&&Time>=0&&Time<=8.f;
 Prop->SetVisibility(Inspect||bParkWhenIdle);
 if(!Inspect&&!bParkWhenIdle)
 {
  if(auto* Owner=Skin->GetOwner())for(auto* C:Owner->GetComponents())if(auto* Stand=Cast<UStaticMeshComponent>(C);Stand&&Stand->GetFName()==TEXT("AsoLedgerSupport"))Stand->SetVisibility(false);
  return;
 }
 // Imported component-space book centre in centimetres. Authoring probe verifies
 // this transform against the same clip at first contact; no guessed hand socket.
 float BodyOffset=0.f;
 if(const auto* Mesh=Skin->GetSkeletalMeshAsset())
 {
  const auto& Ref=Mesh->GetRefSkeleton();const int32 Pelvis=Ref.FindBoneIndex(TEXT("pelvis"));
  if(Pelvis>=0){FTransform Rest=Ref.GetRefBonePose()[Pelvis];for(int32 P=Ref.GetParentIndex(Pelvis);P>=0;P=Ref.GetParentIndex(P))Rest=Rest*Ref.GetRefBonePose()[P];BodyOffset=Skin->GetSocketTransform(TEXT("pelvis"),RTS_Component).GetLocation().Z-Rest.GetLocation().Z;}
 }
 const FTransform Park(FQuat::Identity,FVector(30.f,0.f,103.f+BodyOffset));
 if(auto* Owner=Skin->GetOwner())
  for(auto* Component:Owner->GetComponents())
   if(auto* Stand=Cast<UStaticMeshComponent>(Component);Stand&&Stand->GetFName()==TEXT("AsoLedgerSupport")){
    // Fit this presentation fixture between the mesh sole plane and the actual
    // imported book underside; never move pawn collision or bury the base.
    if(Stand->GetStaticMesh())
    {
     const FBox B=Stand->GetStaticMesh()->GetBoundingBox();const double Height=103.f+BodyOffset+Prop->GetStaticMesh()->GetBoundingBox().Min.Z;const double Scale=Height/FMath::Max(1.,B.Max.Z-B.Min.Z);Stand->SetRelativeScale3D(FVector(1,1,Scale));Stand->SetRelativeLocation(FVector(30,0,-B.Min.Z*Scale));
    }
    Stand->SetVisibility(Inspect);
   }
 const bool SupportedReturn=Clip&&(Clip->GetPathName().StartsWith(TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/"))||Clip->GetPathName().StartsWith(TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/")));
 FTransform Frame=Inspect?Skin->GetSocketTransform(TEXT("socket_ledger_R"),RTS_Component):Park;
 if(SupportedReturn)
 {
  // Source v019 maintains hand contact through placement at6.8s.
  // Before contact and after placement the visible lab table supports the book.
  if(!Inspect||Time<1.6f||Time>=6.8f)Frame=Park;
 }
 else if(Inspect&&(Time<1.6f||Time>=6.f))
 {
  const float Alpha=Time<1.6f?0.f:1.f-FMath::SmoothStep(6.f,6.8f,Time);
  FTransform Blended;Blended.Blend(Park,Frame,Alpha);Frame=Blended;
 }
 Prop->SetWorldTransform(Frame*Skin->GetComponentTransform());
}
