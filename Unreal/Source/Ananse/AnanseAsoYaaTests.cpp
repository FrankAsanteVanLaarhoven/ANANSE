#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "AnanseMission.h"
#include "AnanseWorld.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseAsoResponses,"Ananse.AsoYaa.MissionDrivenResponse",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseAsoResponses::RunTest(const FString&)
{
 FAnanseMissionState State;
 TestEqual(TEXT("No evidence idle"),AAnanseInteractable::NegotiationPoseFor(State),0);
 State.bEvidence=true;TestEqual(TEXT("Evidence inspection"),AAnanseInteractable::NegotiationPoseFor(State),4);
 State.bPermit=true;TestEqual(TEXT("Promise agreement"),AAnanseInteractable::NegotiationPoseFor(State),8);
 State.Outcome=TEXT("truth-exposed");TestEqual(TEXT("Broken promise reaction"),AAnanseInteractable::NegotiationPoseFor(State),11);
 State.bPermit=false;TestEqual(TEXT("Exposure without promise differs"),AAnanseInteractable::NegotiationPoseFor(State),9);
 State.Outcome=TEXT("witnesses-protected");TestEqual(TEXT("Protected witnesses"),AAnanseInteractable::NegotiationPoseFor(State),10);
 TestFalse(TEXT("Presentation does not grant permit"),State.bPermit);return true;
}
#endif
#if WITH_DEV_AUTOMATION_TESTS
#include "Engine/SkeletalMesh.h"
#include "Engine/SkeletalMeshSocket.h"
#include "Animation/AnimSequence.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseAsoLedgerAsset,"Ananse.AsoYaa.AuthoredLedgerFirstContact",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseAsoLedgerAsset::RunTest(const FString&)
{
 auto* Mesh=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa"));
 auto* Clip=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaaInspectEvidence.AsoYaaInspectEvidence"));
 if(!TestNotNull(TEXT("Actual corrective mesh"),Mesh)||!TestNotNull(TEXT("Actual eight-second authored contact clip"),Clip))return false;
 TestEqual(TEXT("Independent retained rest family"),Mesh->GetRefSkeleton().GetNum(),48);TestTrue(TEXT("Eight second full performance"),FMath::Abs(Clip->GetPlayLength()-8.f)<.05f);
 const auto* Socket=Mesh->FindSocket(TEXT("socket_ledger_R"));if(!TestNotNull(TEXT("Authored nonzero grip socket"),Socket))return false;
 const auto& Ref=Mesh->GetRefSkeleton();TArray<FTransform> CS;CS.SetNum(Ref.GetNum());for(int32 I=0;I<CS.Num();++I){Clip->GetBoneTransform(CS[I],FSkeletonPoseBoneIndex(I),FAnimExtractContext(1.6,false),true);if(Ref.GetParentIndex(I)>=0)CS[I]=CS[I]*CS[Ref.GetParentIndex(I)];}
 const auto Result=Socket->GetSocketLocalTransform()*CS[Ref.FindBoneIndex(TEXT("hand_R"))];TestTrue(TEXT("Coordinate-qualified first-contact book centre"),Result.GetLocation().Equals(FVector(30,0,103),.01));
 TestTrue(TEXT("Socket is not placeholder origin"),Socket->RelativeLocation.Size()>1.f);return true;
}
#endif
