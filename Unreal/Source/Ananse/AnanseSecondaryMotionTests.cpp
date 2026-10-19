#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "AnanseSecondaryMotion.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseSecondaryResponseTest,"Ananse.Animation.SecondaryMotion",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseSecondaryResponseTest::RunTest(const FString& Parameters)
{
 float X=0,V=0,Y=0,W=0;
 for(int32 I=0;I<120;++I)FAnanseSecondaryMotion::Advance(4.f,1.f/120,X,V);
 for(int32 I=0;I<30;++I)FAnanseSecondaryMotion::Advance(4.f,1.f/30,Y,W);
 TestTrue(TEXT("Analytic response is frame-partition independent"),FMath::Abs(X-Y)<.0001f);
 TestTrue(TEXT("Driven cloth responds without snapping to target"),X>3.9f&&X<=4);
 for(int32 I=0;I<240;++I)FAnanseSecondaryMotion::Advance(0,1.f/60,X,V);
 TestTrue(TEXT("Stopped movement settles"),FMath::Abs(X)<.001f&&FMath::Abs(V)<.001f);
 X=5;V=9;FAnanseSecondaryMotion::Advance(4,1.f,X,V);
 TestTrue(TEXT("Long frame resets transient state"),X==0&&V==0);
 for(const TCHAR* Name:{TEXT("root"),TEXT("pelvis"),TEXT("chest"),TEXT("thigh_L"),TEXT("hand_R"),TEXT("tail_01"),TEXT("instrument"),TEXT("shell_root")})TestEqual(TEXT("Collision, body and prop chain excluded"),FAnanseSecondaryMotion::ClothScale(Name),0.f);
 TestTrue(TEXT("Leopard attachment is stiffer than hem"),FAnanseSecondaryMotion::ClothScale(TEXT("cape_L_01"))<FAnanseSecondaryMotion::ClothScale(TEXT("cape_L_03")));
 return true;
}
#endif
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Engine/StaticMesh.h"
#include "StaticMeshResources.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseMotionMasksTest,"Ananse.Environment.SecondaryMotionMasks",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseMotionMasksTest::RunTest(const FString& Parameters)
{
 for(const TCHAR* Name:{TEXT("CanopySwag"),TEXT("Understory"),TEXT("CrownGuardian"),TEXT("RiverFig"),TEXT("TwinnedElder"),TEXT("RiverReach"),TEXT("StreamPools"),TEXT("LayeredGrove0"),TEXT("LayeredGrove1"),TEXT("LayeredGrove2"),TEXT("EcologyIsland"),TEXT("VerandaCorner")})
 {
  const FString Path=FString::Printf(TEXT("/Game/Ananse/Environments/Motion_v001/%s/%s.%s"),Name,Name,Name);
  const auto* Mesh=LoadObject<UStaticMesh>(nullptr,*Path);if(!TestNotNull(*Path,Mesh))continue;
  TestEqual(TEXT("Conventional three LODs"),Mesh->GetNumLODs(),3);
  const auto* Data=Mesh->GetRenderData();if(!TestNotNull(TEXT("Materialised render data"),Data))continue;
  const auto& Colors=Data->LODResources[0].VertexBuffers.ColorVertexBuffer;
  const auto& Positions=Data->LODResources[0].VertexBuffers.PositionVertexBuffer;
  TestEqual(TEXT("Authored per-vertex masks survived import"),Colors.GetNumVertices(),Positions.GetNumVertices());
  int32 Moving=0,Anchored=0;
  for(uint32 I=0;I<Colors.GetNumVertices();++I){const FColor C=Colors.VertexColor(I);if(C.R||C.G||C.B||C.A)++Moving;else ++Anchored;}
  TestTrue(TEXT("Mesh contains moving vertices"),Moving>0);TestTrue(TEXT("Mesh retains anchored vertices"),Anchored>0);
  TestTrue(TEXT("Culling bounds expanded for bounded displacement"),Mesh->PositiveBoundsExtension.GetMin()>=6.f&&Mesh->NegativeBoundsExtension.GetMin()>=6.f);
 }
 return true;
}
#endif
