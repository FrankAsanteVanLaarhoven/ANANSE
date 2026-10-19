#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "AnanseLabSelection.h"
#include "AnanseSpiderLab.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/Material.h"
#include "Components/PointLightComponent.h"
#include "Misc/CommandLine.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseSelectionDefinitionTest,"Ananse.Selection.QualifiedDefinition",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseSelectionDefinitionTest::RunTest(const FString& Parameters)
{
 auto* Asset=LoadObject<UAnanseCharacterDefinition>(nullptr,TEXT("/Game/Production/Characters/SpiderSelection_v001/DA_AnanseSpider.DA_AnanseSpider"));
 if(!TestNotNull(TEXT("Materialized typed definition"),Asset))return false;
 Asset->Mesh.LoadSynchronous();Asset->PawnClass.LoadSynchronous();for(auto& Clip:Asset->Clips)Clip.LoadSynchronous();
 FString Error;TestTrue(TEXT("Actual mesh, generated pawn, skeleton and four clips compatible"),Asset->ValidateLoaded(Error));
 auto* Copy=DuplicateObject<UAnanseCharacterDefinition>(Asset,GetTransientPackage());
 Copy->CharacterIdentity=TEXT("kwaku");TestFalse(TEXT("Identity swap rejected"),Copy->ValidateLoaded(Error));Copy->CharacterIdentity=Asset->CharacterIdentity;
 Copy->SkeletonKey=TEXT("mannequin");TestFalse(TEXT("Wrong family rejected"),Copy->ValidateLoaded(Error));Copy->SkeletonKey=Asset->SkeletonKey;
 Copy->Clips[0].Reset();TestFalse(TEXT("Missing animation rejected"),Copy->ValidateLoaded(Error));Copy->Clips=Asset->Clips;
 Copy->Mesh.Reset();TestFalse(TEXT("Missing mesh rejected"),Copy->ValidateLoaded(Error));Copy->Mesh=Asset->Mesh;
 Copy->PawnClass=AAnansePlayer::StaticClass();TestFalse(TEXT("Wrong pawn rejected"),Copy->ValidateLoaded(Error));
 TestTrue(TEXT("Original definition unchanged"),Asset->ValidateLoaded(Error));
 auto* Wire=LoadObject<UMaterial>(nullptr,TEXT("/Game/Production/Characters/SpiderSelection_v001/M_LabWireframe.M_LabWireframe"));
 if(TestNotNull(TEXT("Real inspection shader"),Wire)){TestTrue(TEXT("Actual wireframe rasterization"),bool(Wire->Wireframe));TestTrue(TEXT("Skeletal shader usage"),Wire->GetUsageByFlag(MATUSAGE_SkeletalMesh));}
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseSelectionSaveTest,"Ananse.Selection.StableProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseSelectionSaveTest::RunTest(const FString& Parameters)
{
 auto* Save=NewObject<UAnanseLabSelectionSave>();Save->DesignId=TEXT("ananse-spider-existing");Save->CharacterIdentity=TEXT("ananse");Save->SkeletonKey=TEXT("ananse-eight-limb-v002");Save->ContentHash=TEXT("test-content");
 TArray<uint8> Bytes;TestTrue(TEXT("Serialize dedicated profile envelope"),UGameplayStatics::SaveGameToMemory(Save,Bytes));
 auto* Read=Cast<UAnanseLabSelectionSave>(UGameplayStatics::LoadGameFromMemory(Bytes));if(!TestNotNull(TEXT("Actual native profile readback"),Read))return false;
 TestEqual(TEXT("Separate design"),Read->DesignId,Save->DesignId);TestEqual(TEXT("Identity"),Read->CharacterIdentity,Save->CharacterIdentity);TestEqual(TEXT("Compatibility key"),Read->SkeletonKey,Save->SkeletonKey);TestEqual(TEXT("Revision"),Read->AssetRevision,1);TestEqual(TEXT("Cosmetic"),Read->CosmeticVariant,FName(TEXT("base")));TestEqual(TEXT("Publication identity"),Read->ContentHash,Save->ContentHash);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseNeutralLabLightTest,"Ananse.Selection.NeutralLabLightChannels",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseNeutralLabLightTest::RunTest(const FString&)
{
 const FString Original=FCommandLine::Get();auto* Light=NewObject<UPointLightComponent>();
 FCommandLine::Set(TEXT("-AnanseArtRefinement"));
 AAnanseLabController::ConfigurePreviewLight(Light,true);
 TestEqual(TEXT("Frozen refinement remains unchanged without opt-in"),Light->Intensity,0.f);
 FCommandLine::Set(TEXT("-AnanseArtRefinement -AnanseNeutralLabLighting"));
 AAnanseLabController::ConfigurePreviewLight(Light,true);
 TestEqual(TEXT("Bounded neutral fill"),Light->Intensity,3000.f);
 TestEqual(TEXT("Explicit physical light units"),Light->IntensityUnits,ELightUnits::Lumens);
 TestTrue(TEXT("Refined mesh receives channel0"),bool(Light->LightingChannels.bChannel0));
 TestFalse(TEXT("No unused refined channel1"),bool(Light->LightingChannels.bChannel1));
 AAnanseLabController::ConfigurePreviewLight(Light,false);
 TestTrue(TEXT("Returning spider/leopard receives channel0"),bool(Light->LightingChannels.bChannel0));
 FCommandLine::Set(TEXT("-AnanseNeutralLabLighting"));
 AAnanseLabController::ConfigurePreviewLight(Light,true);
 TestTrue(TEXT("Legacy cast retains its actual channel1"),bool(Light->LightingChannels.bChannel1));
 FCommandLine::Set(TEXT(""));AAnanseLabController::ConfigurePreviewLight(Light,true);
 TestEqual(TEXT("Legacy intensity preserved"),Light->Intensity,16000.f);
 FCommandLine::Set(*Original);return true;
}
#endif
