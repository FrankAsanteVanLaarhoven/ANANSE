#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "AnanseMission.h"
#include "AnanseDialogue.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/Material.h"
#include "Kismet/GameplayStatics.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseConsequenceDialogueTest,"Ananse.Episode.ConsequenceDialogueAndResume",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseConsequenceDialogueTest::RunTest(const FString& Parameters)
{
    for(FName Outcome:{FName(TEXT("truth-exposed")),FName(TEXT("witnesses-protected"))})
    {
        UAnanseMission* M=NewObject<UAnanseMission>();
        TestFalse(TEXT("Dialogue cannot invent an outcome"),M->PresentConsequenceLine());
        // State fixture, not a played route: test branch presentation and native serialization.
        M->State.bProductionPursuit=true;M->State.Outcome=Outcome;M->State.bPermit=true;
        TestFalse(TEXT("Played escape remains required"),M->PresentConsequenceLine());
        M->State.bPursuitEscaped=true;
        TestTrue(TEXT("First authored line resolves"),M->PresentConsequenceLine());
        const FName First=M->ActiveDialogueId;
        TestFalse(TEXT("No empty subtitle"),M->ActiveDialogueText.IsEmpty());
        TestEqual(TEXT("Trust untouched by presentation"),M->State.MarketTrust,0);
        UAnanseSave* Save=NewObject<UAnanseSave>();Save->State=M->State;
        TArray<uint8> Bytes;TestTrue(TEXT("Serialize presented line in existing envelope"),UGameplayStatics::SaveGameToMemory(Save,Bytes));
        UAnanseSave* Read=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromMemory(Bytes));
        if(!TestNotNull(TEXT("Native readback"),Read))return false;
        UAnanseMission* Restored=NewObject<UAnanseMission>();Restored->State=Read->State;
        TestTrue(TEXT("Resume next authored line"),Restored->PresentConsequenceLine());
        TestNotEqual(TEXT("Does not repeat consumed line"),Restored->ActiveDialogueId,First);
        const int32 Count=Outcome==TEXT("truth-exposed")?4:3;
        for(int32 Index=2;Index<Count;++Index)TestTrue(TEXT("Remaining branch line"),Restored->PresentConsequenceLine());
        TestFalse(TEXT("Repeat completion rejected"),Restored->PresentConsequenceLine());
        TestEqual(TEXT("Sanctuary is pending, not fabricated complete"),Restored->State.ProductionBeat,FName(TEXT("sanctuary_pending")));
        TestEqual(TEXT("Outcome unchanged"),Restored->State.Outcome,Outcome);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseDialogueValidationTest,"Ananse.Episode.DialogueValidation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseDialogueValidationTest::RunTest(const FString& Parameters)
{
    TMap<FName,FAnanseDialogueLine> Lines;FString Error;
    TestTrue(TEXT("Load actual staged draft"),AnanseDialogue::Load(Lines,Error));
    TestEqual(TEXT("Actual authored line count"),Lines.Num(),44);
    USkeletalMesh* Proxy=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.AnanseSpider_PROXY"));
    if(!TestNotNull(TEXT("Actual native proxy mesh"),Proxy))return false;
    int32 ClothSlots=0;for(const auto& Material:Proxy->GetMaterials())if(Material.MaterialSlotName==TEXT("Cloth_Proxy"))ClothSlots++;
    TestEqual(TEXT("Exactly one runtime-serialised cloth slot; no editor-only import-name dependency"),ClothSlots,1);
    UMaterial* Cloth=LoadObject<UMaterial>(nullptr,TEXT("/Game/Production/Characters/SpiderLook_v001/M_ProxyClothVariant.M_ProxyClothVariant"));
    if(!TestNotNull(TEXT("Actual versioned cloth material"),Cloth))return false;
    TestTrue(TEXT("Actual cloth shader supports skeletal mesh"),Cloth->GetUsageByFlag(MATUSAGE_SkeletalMesh));
    TestFalse(TEXT("Reject malformed document"),AnanseDialogue::Parse(TEXT("{}"),Lines,Error));
    TestEqual(TEXT("Failure exposes no partial lines"),Lines.Num(),0);
    const FString Duplicate=TEXT("{\"schema_version\":1,\"locale\":\"en\",\"lines\":[{\"id\":\"MSN_A\",\"speaker\":\"esi\",\"text\":\"one\"},{\"id\":\"MSN_a\",\"speaker\":\"esi\",\"text\":\"two\"}]}");
    TestFalse(TEXT("Case-insensitive duplicate identity rejected"),AnanseDialogue::Parse(Duplicate,Lines,Error));
    TestEqual(TEXT("Duplicate leaves no partial document"),Lines.Num(),0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseEpisodeRouteRulesTest,"Ananse.Episode.RouteOutcomeRules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseEpisodeRouteRulesTest::RunTest(const FString& Parameters)
{
    for(FName Route:{FName(TEXT("negotiation")),FName(TEXT("social")),FName(TEXT("rooftop"))})
    for(FName Choice:{FName(TEXT("protect")),FName(TEXT("expose"))})
    {
        UAnanseMission* M=NewObject<UAnanseMission>();
        TestFalse(TEXT("Archive rejects missing route prerequisites"),M->Act(TEXT("archive")));
        TestFalse(TEXT("Ledger rejects locked archive"),M->Act(TEXT("ledger")));
        TestTrue(TEXT("Inspect evidence"),M->Act(TEXT("evidence")));
        if(Route==TEXT("negotiation"))TestTrue(TEXT("Evidence-backed promise grants permit"),M->Act(TEXT("negotiate")));
        if(Route==TEXT("social"))
        {
            TestFalse(TEXT("Voice cannot fabricate an unheard identity"),M->CommitPower(TEXT("borrowed-voice")));
            TestTrue(TEXT("Listen learns identity"),M->Act(TEXT("listen")));
            TestTrue(TEXT("Voice charges thread"),M->CommitPower(TEXT("borrowed-voice")));
        }
        if(Route==TEXT("rooftop"))
        {
            TestTrue(TEXT("Web permission is a separate service contract"),M->CommitPower(TEXT("web-step")));
            TestFalse(TEXT("Roof alone does not bypass watcher"),M->Act(TEXT("archive")));
            TestTrue(TEXT("Mirror is required"),M->CommitPower(TEXT("trick-mirror")));
        }
        TestTrue(TEXT("Configured route opens archive"),M->Act(TEXT("archive")));
        TestEqual(TEXT("Correct route identity"),M->State.Route,Route);
        TestTrue(TEXT("Recover ledger through rule service"),M->Act(TEXT("ledger")));
        TestTrue(TEXT("Existing consequence rules"),M->Act(Choice));
        const FName Outcome=M->State.Outcome;const int32 MarketTrust=M->State.MarketTrust,CourtTrust=M->State.CourtTrust;
        TestFalse(TEXT("Duplicate consequence cannot duplicate trust"),M->Act(Choice));
        TestEqual(TEXT("Stable outcome"),M->State.Outcome,Outcome);
        TestEqual(TEXT("Stable market trust"),M->State.MarketTrust,MarketTrust);
        TestEqual(TEXT("Stable court trust"),M->State.CourtTrust,CourtTrust);
        if(Route==TEXT("negotiation") && Choice==TEXT("expose"))TestEqual(TEXT("Broken promise cost preserved"),M->State.MarketTrust,-1);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseEpisodeCheckpointTest,"Ananse.Save.EpisodeMapBinding",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseEpisodeCheckpointTest::RunTest(const FString& Parameters)
{
    UAnanseSave* Save=NewObject<UAnanseSave>();Save->SchemaVersion=4;Save->EpisodeId=TEXT("market-of-stolen-names-v1");
    Save->State.bEpisodeSession=true;Save->State.ProductionBeat=TEXT("sanctuary");Save->State.Outcome=TEXT("truth-exposed");
    Save->State.CompletedPresentationEvents.Add(TEXT("MSN_EXPOSE_030"));Save->CharacterId=TEXT("kwaku");Save->ContentHash=TEXT("candidate");Save->MapIdentity=UAnanseMission::SanctuaryMap();
    FString Reason;
    TestTrue(TEXT("Exact new episode binding accepted"),UAnanseMission::CheckpointCompatible(Save,TEXT("candidate"),TEXT("kwaku"),UAnanseMission::SanctuaryMap(),Reason));
    TestFalse(TEXT("Wrong map cannot load destination transform in market"),UAnanseMission::CheckpointCompatible(Save,TEXT("candidate"),TEXT("kwaku"),UAnanseMission::MarketMap(),Reason));
    TestFalse(TEXT("Cannot replace Ananse identity with Kwaku save"),UAnanseMission::CheckpointCompatible(Save,TEXT("candidate"),TEXT("ananse"),UAnanseMission::SanctuaryMap(),Reason));
    TestFalse(TEXT("Content update still requires migration"),UAnanseMission::CheckpointCompatible(Save,TEXT("new-candidate"),TEXT("kwaku"),UAnanseMission::SanctuaryMap(),Reason));
    TArray<uint8> Bytes;TestTrue(TEXT("Serialize schema4 episode"),UGameplayStatics::SaveGameToMemory(Save,Bytes));
    UAnanseSave* Read=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromMemory(Bytes));
    if(!TestNotNull(TEXT("Read actual episode envelope"),Read))return false;
    TestEqual(TEXT("Version retained"),Read->SchemaVersion,4);TestEqual(TEXT("Episode ID retained"),Read->EpisodeId,Save->EpisodeId);
    TestEqual(TEXT("Consumed narrative IDs retained"),Read->State.CompletedPresentationEvents,Save->State.CompletedPresentationEvents);
    Read->MapIdentity=TEXT("/Game/Unknown");
    TestFalse(TEXT("No arbitrary map through episode metadata"),UAnanseMission::CheckpointCompatible(Read,TEXT("candidate"),TEXT("kwaku"),Read->MapIdentity,Reason));
    Save->SchemaVersion=3;Save->State.bEpisodeSession=false;Save->EpisodeId=NAME_None;Save->MapIdentity=UAnanseMission::MarketMap();
    TestTrue(TEXT("Historical bound schema3 retained without conversion"),UAnanseMission::CheckpointCompatible(Save,TEXT("candidate"),TEXT("kwaku"),UAnanseMission::MarketMap(),Reason));
    TestFalse(TEXT("Unowned epilogue cannot fabricate completion"),NewObject<UAnanseMission>()->PresentEpilogueLine());
    TestFalse(TEXT("Traversal in a slot is rejected before read"),UAnanseMission::ValidCheckpointSlot(TEXT("../another-save")));
    TestFalse(TEXT("URL options cannot enter a slot"),UAnanseMission::ValidCheckpointSlot(TEXT("save?AnanseStart=1")));
    UAnanseMission* Complete=NewObject<UAnanseMission>();Complete->State.bPursuitEscaped=true;Complete->State.ProductionBeat=TEXT("episode_complete");
    TestFalse(TEXT("Repeated escape cannot regress episode progression"),Complete->Act(TEXT("escape")));
    TestEqual(TEXT("Episode completion retained"),Complete->State.ProductionBeat,FName(TEXT("episode_complete")));
    return true;
}
#endif
