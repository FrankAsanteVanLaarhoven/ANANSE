#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "AnanseAuthoredAnimation.h"
#include "AnanseCastLab.h"
#include "AnanseLabSelection.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/SkeletalMeshSocket.h"
#include "Json.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseAsoPlacementTest,"Ananse.Animation.AsoSupportedPlacement",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseAsoPlacementTest::RunTest(const FString& Parameters)
{
 const TCHAR* Base=TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/");
 auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*(FString(Base)+TEXT("AsoYaa.AsoYaa")));auto* Clip=LoadObject<UAnimSequence>(nullptr,*(FString(Base)+TEXT("AsoYaaInspectEvidence.AsoYaaInspectEvidence")));auto* Prior=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa"));
 if(!TestNotNull(TEXT("Actual corrected mesh"),Mesh)||!TestNotNull(TEXT("Actual placement clip"),Clip)||!TestNotNull(TEXT("Prior mesh preserved"),Prior))return false;
 TestEqual(TEXT("Bone count retained"),Mesh->GetRefSkeleton().GetNum(),Prior->GetRefSkeleton().GetNum());
 for(int32 I=0;I<Mesh->GetRefSkeleton().GetNum();++I){TestEqual(TEXT("Bone identity retained"),Mesh->GetRefSkeleton().GetBoneName(I),Prior->GetRefSkeleton().GetBoneName(I));TestTrue(TEXT("Rest transform retained"),Mesh->GetRefSkeleton().GetRefBonePose()[I].Equals(Prior->GetRefSkeleton().GetRefBonePose()[I],.0001));}
 TestTrue(TEXT("Compatible independent animation binding"),Clip->GetSkeleton()==Mesh->GetSkeleton());TestEqual(TEXT("Placement clip duration retained"),Clip->GetPlayLength(),8.f);TestEqual(TEXT("Three materialised LODs"),Mesh->GetLODNum(),3);TestNotNull(TEXT("Real ledger socket"),Mesh->FindSocket(TEXT("socket_ledger_R")));
 TSharedPtr<FJsonObject> Start,End;auto A=TJsonReaderFactory<>::Create(UAnanseAnimationAuthoring::DescribeAuthoredBonePose(Mesh,Clip,6.f));auto B=TJsonReaderFactory<>::Create(UAnanseAnimationAuthoring::DescribeAuthoredBonePose(Mesh,Clip,6.79f));if(!TestTrue(TEXT("Imported contact poses readable"),FJsonSerializer::Deserialize(A,Start)&&FJsonSerializer::Deserialize(B,End)))return false;
 for(const TCHAR* Bone:{TEXT("hand_L"),TEXT("hand_R"),TEXT("digit_L_0_02"),TEXT("digit_R_0_02")}){const auto& P=Start->GetArrayField(Bone);const auto& Q=End->GetArrayField(Bone);double D=0;for(int32 I=0;I<3;++I)D+=FMath::Square(P[I]->AsNumber()-Q[I]->AsNumber());TestTrue(TEXT("Hands retain placement support until withdrawal"),FMath::Sqrt(D)<.02);}
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseAsoArtRevisionTest,"Ananse.Animation.AsoArtRevisionBindings",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseAsoArtRevisionTest::RunTest(const FString& Parameters)
{
 auto* Mesh=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa"));
 auto* Prior=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa"));
 auto* Definition=LoadObject<UAnanseCharacterDefinition>(nullptr,TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/DA_AsoYaa.DA_AsoYaa"));
 if(!TestNotNull(TEXT("Actual new art mesh"),Mesh)||!TestNotNull(TEXT("Protected corrected mesh"),Prior)||!TestNotNull(TEXT("Revision8 definition"),Definition))return false;
 TestEqual(TEXT("Unpublished art revision"),Definition->Revision,8);TestTrue(TEXT("Exact compatible skeleton reused"),Mesh->GetSkeleton()==Prior->GetSkeleton());TestTrue(TEXT("Existing physics retained"),Mesh->GetPhysicsAsset()==Prior->GetPhysicsAsset());TestEqual(TEXT("Rest bone count retained"),Mesh->GetRefSkeleton().GetNum(),48);TestEqual(TEXT("Material slot budget unchanged"),Mesh->GetMaterials().Num(),Prior->GetMaterials().Num());TestEqual(TEXT("Conventional LOD count retained"),Mesh->GetLODNum(),3);
 for(int32 I=0;I<48;++I)TestTrue(TEXT("Exact rest transforms retained"),Mesh->GetRefSkeleton().GetRefBonePose()[I].Equals(Prior->GetRefSkeleton().GetRefBonePose()[I],.0001));
 auto* Class=Definition->PawnClass.LoadSynchronous();if(!TestNotNull(TEXT("Art pawn class resolves"),Class))return false;const auto* CDO=Cast<AAnanseCastLabPlayer>(Class->GetDefaultObject());if(!TestNotNull(TEXT("Compatible existing pawn implementation"),CDO))return false;
 TestTrue(TEXT("CDO uses new mesh and receiving stand"),CDO->AuthoredMesh==Mesh&&CDO->LedgerSupportMesh!=nullptr);TestEqual(TEXT("All sixteen existing clips retained"),CDO->AuthoredClips.Num(),16);TestNotNull(TEXT("Ledger grip socket retained"),Mesh->FindSocket(TEXT("socket_ledger_R")));
 for(const auto& Clip:CDO->AuthoredClips)TestTrue(TEXT("Every clip still uses existing skeleton"),Clip&&Clip->GetSkeleton()==Prior->GetSkeleton());
 return true;
}
#endif
