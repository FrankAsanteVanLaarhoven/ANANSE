#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Engine/SkeletalMesh.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseLeopardQualityTest,"Ananse.Leopard.LodAndPhysicsPolicy",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseLeopardQualityTest::RunTest(const FString&)
{
 auto* Mesh=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard"));
 if(!TestNotNull(TEXT("Actual saved feline mesh"),Mesh))return false;
 TestEqual(TEXT("Three materialised LODs"),Mesh->GetLODNum(),3);auto* Render=Mesh->GetResourceForRendering();
 if(!TestNotNull(TEXT("Reopened real render data"),Render))return false;
 int32 Previous=MAX_int32;for(const auto& Lod:Render->LODRenderData)
 {TestTrue(TEXT("Actual triangles decrease and remain nonzero"),Lod.GetTotalFaces()>0 && Lod.GetTotalFaces()<Previous);Previous=Lod.GetTotalFaces();for(const auto& S:Lod.RenderSections)TestTrue(TEXT("Qualified four influence ceiling"),S.MaxBoneInfluences>0 && S.MaxBoneInfluences<=4);}
 auto* Physics=Mesh->GetPhysicsAsset();if(!TestNotNull(TEXT("Reopened physics policy"),Physics))return false;
 int32 Secondary=0;for(const auto& B:Physics->SkeletalBodySetups)
 {if(!TestNotNull(TEXT("Existing body retained"),B.Get()))continue;TestTrue(TEXT("Normal motion has no dynamic ragdoll authority"),B->PhysicsType==PhysType_Kinematic);const FString Name=B->BoneName.ToString();const bool Expected=Name.StartsWith(TEXT("cape_"))||Name.StartsWith(TEXT("tail_"));TestEqual(TEXT("Secondary bodies cannot push player"),B->CollisionReponse==EBodyCollisionResponse::BodyCollision_Disabled,Expected);Secondary+=Expected;TestTrue(TEXT("Reviewed binding resolves actual bone"),Mesh->GetRefSkeleton().FindBoneIndex(B->BoneName)!=INDEX_NONE);}
 TestEqual(TEXT("Cape and tail body masks"),Secondary,8);return true;
}
#endif
