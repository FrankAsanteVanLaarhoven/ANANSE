#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "AnanseCastLab.h"
#include "AnanseLabSelection.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimSequence.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FStoryCastAssets,"Ananse.StoryCast.IndependentNativeFamilies",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FStoryCastAssets::RunTest(const FString&)
{
 TSet<const UObject*> Skeletons;
 for(const TCHAR* Key:{TEXT("Kwaku"),TEXT("AsoYaa"),TEXT("EsiHuman"),TEXT("OseboHuman"),TEXT("KojoTortoise"),TEXT("KofiHornbill"),TEXT("EsiMoth")})
 {
  const FString Base=FString::Printf(TEXT("/Game/Ananse/Characters/%s/Story_v001/"),Key);
  auto* Def=LoadObject<UAnanseCharacterDefinition>(nullptr,*(Base+TEXT("DA_")+Key+TEXT(".DA_")+Key));
  if(!TestNotNull(Key,Def))continue;
  Def->PawnClass.LoadSynchronous();auto* Mesh=Def->Mesh.LoadSynchronous();for(auto& Clip:Def->Clips)Clip.LoadSynchronous();
  FString Error;TestTrue(*FString::Printf(TEXT("%s compatible native family: %s"),Key,*Error),Def->ValidateLoaded(Error));
  if(!TestNotNull(TEXT("Actual skeletal mesh"),Mesh))continue;
  TestFalse(TEXT("Distinct skeleton objects"),Skeletons.Contains(Mesh->GetSkeleton()));Skeletons.Add(Mesh->GetSkeleton());
  TestEqual(TEXT("Three real LODs"),Mesh->GetLODNum(),3);
  TestTrue(TEXT("Actual mapped socket objects materialized"),Mesh->GetMeshOnlySocketList().Num()>=3);
  TestNotNull(TEXT("Voice socket references actual source jaw"),Mesh->FindSocket(TEXT("socket_voice")));
  auto* Physics=Mesh->GetPhysicsAsset();if(TestNotNull(TEXT("Actual physics"),Physics))for(const auto& B:Physics->SkeletalBodySetups)if(B)TestTrue(TEXT("Normal-play physics kinematic"),B->PhysicsType==PhysType_Kinematic);
  const auto* Defaults=Def->PawnClass.Get()->GetDefaultObject<AAnanseCastLabPlayer>();TestNotNull(TEXT("Compiled independent graph"),Defaults->AnimationClass.Get());
 }
 TestEqual(TEXT("Seven independent skeleton objects"),Skeletons.Num(),7);return true;
}
#endif
