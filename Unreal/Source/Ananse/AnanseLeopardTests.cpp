#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "AnanseLeopardLab.h"
#include "AnanseSpiderLab.h"
#include "AnanseLabSelection.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMeshSocket.h"
#include "Materials/Material.h"
#include "Engine/SkeletalMesh.h"
#include "Components/CapsuleComponent.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseLeopardBindingsTest,"Ananse.Leopard.AuthoredBindings",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseLeopardBindingsTest::RunTest(const FString& Parameters)
{
 UClass* Class=LoadClass<AAnanseLeopardLabPlayer>(nullptr,TEXT("/Game/Ananse/Characters/OseboLeopard/Runtime_v001/BP_OseboLeopard.BP_OseboLeopard_C"));
 if(!TestNotNull(TEXT("Materialized generated feline class"),Class))return false;
 auto* Pawn=Class->GetDefaultObject<AAnanseLeopardLabPlayer>();
 if(!TestNotNull(TEXT("Actual authored mesh binding"),Pawn->LeopardMesh.Get()))return false;
 TestEqual(TEXT("Distinct authored bone hierarchy"),Pawn->LeopardMesh->GetRefSkeleton().GetNum(),64);
 TestTrue(TEXT("Lab-only ability profile"),Pawn->bLabSelectionPawn);
 TestEqual(TEXT("Existing narrative candidate preserved"),Pawn->CharacterId,FName(TEXT("osebo")));
 TestEqual(TEXT("Nine separate motion assets"),Pawn->LeopardClips.Num(),9);
 TSet<const UAnimSequence*> Unique;
 for(UAnimSequence* Clip:Pawn->LeopardClips)
 {
  if(!TestNotNull(TEXT("Materialized animation"),Clip))continue;
  Unique.Add(Clip);TestEqual(TEXT("Animation belongs to feline skeleton"),Clip->GetSkeleton(),Pawn->LeopardMesh->GetSkeleton());
  TestTrue(TEXT("Animation has actual duration"),Clip->GetPlayLength()>1.f);
 }
 TestEqual(TEXT("No duplicate clips renamed to fill categories"),Unique.Num(),9);
 TestNotNull(TEXT("Actual imported PhysicsAsset (tuning review still required)"),Pawn->LeopardMesh->GetPhysicsAsset());
 for(const auto& Slot:Pawn->LeopardMesh->GetMaterials())
 {
  if(TestNotNull(TEXT("Materialized feline material slot"),Slot.MaterialInterface.Get()))
   TestTrue(TEXT("Stored material supports skeletal rendering"),Slot.MaterialInterface->GetMaterial()->GetUsageByFlag(MATUSAGE_SkeletalMesh));
 }
 for(const TCHAR* Socket:{TEXT("socket_capture_L"),TEXT("socket_capture_R"),TEXT("socket_voice"),TEXT("socket_cape")})
  TestNotNull(FString::Printf(TEXT("Actual socket object %s"),Socket),Pawn->LeopardMesh->GetSkeleton()->FindSocket(Socket));
 const auto& Ref=Pawn->LeopardMesh->GetRefSkeleton();int32 Roots=0;
 for(int32 I=0;I<Ref.GetNum();++I)if(Ref.GetParentIndex(I)==INDEX_NONE)++Roots;
 TestEqual(TEXT("Single root hierarchy"),Roots,1);
 for(const TCHAR* Bone:{TEXT("hand_L"),TEXT("hand_R"),TEXT("foot_L"),TEXT("foot_R"),TEXT("tail_06"),TEXT("ear_L"),TEXT("ear_R")})
  TestTrue(FString::Printf(TEXT("Real feline anatomy bone %s"),Bone),Ref.FindBoneIndex(Bone)!=INDEX_NONE);
 auto* Definition=LoadObject<UAnanseCharacterDefinition>(nullptr,TEXT("/Game/Ananse/Characters/OseboLeopard/Data/DA_OseboLeopard.DA_OseboLeopard"));
 if(TestNotNull(TEXT("Materialized typed feline definition"),Definition))
 {
  Definition->Mesh.LoadSynchronous();Definition->PawnClass.LoadSynchronous();for(auto& Clip:Definition->Clips)Clip.LoadSynchronous();
  FString Error;TestTrue(TEXT("Actual feline definition validates"),Definition->ValidateLoaded(Error));
  auto* Copy=DuplicateObject<UAnanseCharacterDefinition>(Definition,GetTransientPackage());
  Copy->SkeletonKey=TEXT("ananse-eight-limb-v002");TestFalse(TEXT("Spider compatibility declaration rejected"),Copy->ValidateLoaded(Error));
  Copy->SkeletonKey=Definition->SkeletonKey;Copy->CharacterIdentity=TEXT("kwaku");TestFalse(TEXT("Narrative identity substitution rejected"),Copy->ValidateLoaded(Error));
  Copy->CharacterIdentity=Definition->CharacterIdentity;Copy->Clips[0].Reset();TestFalse(TEXT("Missing clip rejected"),Copy->ValidateLoaded(Error));
  TestTrue(TEXT("Original immutable definition remains valid"),Definition->ValidateLoaded(Error));
 }
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseLeopardSeparationTest,"Ananse.Leopard.IndependentFamily",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseLeopardSeparationTest::RunTest(const FString& Parameters)
{
 auto* Leopard=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard"));
 auto* Spider=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.AnanseSpider_PROXY"));
 if(!TestNotNull(TEXT("Leopard exists"),Leopard)||!TestNotNull(TEXT("Original spider exists"),Spider))return false;
 TestTrue(TEXT("Different materialized skeleton objects"),Leopard->GetSkeleton()!=Spider->GetSkeleton());
 TestEqual(TEXT("Original spider joint count retained"),Spider->GetRefSkeleton().GetNum(),102);
 TestEqual(TEXT("No spider support chain masquerading as feline"),Leopard->GetRefSkeleton().FindBoneIndex(TEXT("femur_front_l")),INDEX_NONE);
 TestEqual(TEXT("No feline tail added to spider"),Spider->GetRefSkeleton().FindBoneIndex(TEXT("tail_06")),INDEX_NONE);
 TestTrue(TEXT("Separate player class families"),!AAnanseLeopardLabPlayer::StaticClass()->IsChildOf(AAnanseSpiderLabPlayer::StaticClass()));
 return true;
}
#endif
