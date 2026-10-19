#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "AnanseEnvironmentCluster.h"
#include "AnanseMission.h"
#include "AnanseRuntimeVerification.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Engine/Level.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseEnvironmentRouteIsolation,"Ananse.Environment.RouteAndSaveIsolation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseEnvironmentRouteIsolation::RunTest(const FString&)
{
 const FString Original=FCommandLine::Get();FCommandLine::Set(TEXT("-AnanseEnvironmentRoute -AnanseAsoContact -AnanseAcceptedVisuals"));
 TestEqual(TEXT("Environment market explicit opt-in"),UAnanseMission::MarketMap(),FString(TEXT("/Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route")));
 TestEqual(TEXT("Matching sanctuary destination"),UAnanseMission::SanctuaryMap(),FString(TEXT("/Game/Ananse/Maps/EnvironmentRoute_v002/L_StoryForest_Route")));
 TestEqual(TEXT("Dedicated review save"),AnanseVerificationSaveSlot(TEXT("kwaku")),FString(TEXT("AnanseEnvironmentRoute_v1")));
 FCommandLine::Set(TEXT("-AnanseAsoContact -AnanseAsoReview"));TestEqual(TEXT("Frozen Aso default save retained"),AnanseVerificationSaveSlot(TEXT("kwaku")),FString(TEXT("AnanseAsoEpisode_v1")));
 FCommandLine::Set(*Original);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseEnvironmentModules,"Ananse.Environment.ConventionalInstancedModules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseEnvironmentModules::RunTest(const FString&)
{
 const auto* C=GetDefault<AAnanseEnvironmentCluster>();TestFalse(TEXT("No gameplay tick"),C->PrimaryActorTick.bCanEverTick);TestFalse(TEXT("Scenery cannot own collision"),C->GetActorEnableCollision());
 for(const TCHAR* Name:{TEXT("MarketFacade"),TEXT("MarketStall"),TEXT("PotterySet"),TEXT("DockSection"),TEXT("RiverSurface"),TEXT("SanctuaryTree"),TEXT("SanctuaryRock"),TEXT("ForestFern")})
 {
  FString Path=FString::Printf(TEXT("/Game/Ananse/Environments/Route_v001/%s/%s.%s"),Name,Name,Name);auto* Mesh=LoadObject<UStaticMesh>(nullptr,*Path);
  if(TestNotNull(*Path,Mesh)){TestEqual(TEXT("Three real LODs"),Mesh->GetNumLODs(),3);TestTrue(TEXT("Actual material slots"),Mesh->GetStaticMaterials().Num()>0);}
 }
 for(const TCHAR* Name:{TEXT("L_RiverMarket_Route"),TEXT("L_StoryForest_Route")})
 {
  FString Path=FString::Printf(TEXT("/Game/Ananse/Maps/EnvironmentRoute_v002/%s.%s"),Name,Name);UWorld* World=LoadObject<UWorld>(nullptr,*Path);
  if(!TestNotNull(TEXT("Saved route map reopens"),World) || !World->PersistentLevel)continue;int32 Count=0;
  for(AActor* Actor:World->PersistentLevel->Actors)if(auto* Cluster=Cast<AAnanseEnvironmentCluster>(Actor))for(int32 I=0;I<Cluster->Instances->GetInstanceCount();I++)
  {
   FTransform Transform;TestTrue(TEXT("Saved instance transform available"),Cluster->Instances->GetInstanceTransform(I,Transform));const FRotator Rotation=Transform.Rotator();
   TestTrue(TEXT("Yaw must not become scenery roll or pitch"),FMath::Abs(Rotation.Pitch)<.001 && FMath::Abs(Rotation.Roll)<.001);Count++;
  }
  TestTrue(TEXT("Real saved instanced route scenery"),Count>=30);
 }
 return true;
}
#endif
