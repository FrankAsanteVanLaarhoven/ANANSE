#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "AnanseMission.h"
#include "AnanseCinematic.h"
#include "Kismet/GameplayStatics.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnansePresentationEventTest,"Ananse.Cinematic.DurableEvents",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnansePresentationEventTest::RunTest(const FString& Parameters)
{
    UAnanseMission* M=NewObject<UAnanseMission>();
    TestFalse(TEXT("Empty event rejected"),M->CompletePresentationEvent(NAME_None));
    TestTrue(TEXT("Opening completion accepted once"),M->CompletePresentationEvent(TEXT("market-opening-v1")));
    TestFalse(TEXT("Duplicate skip/finish cannot repeat event"),M->CompletePresentationEvent(TEXT("market-opening-v1")));
    TestEqual(TEXT("One durable presentation event"),M->State.CompletedPresentationEvents.Num(),1);
    TestTrue(TEXT("Presentation cannot award outcome"),M->State.Outcome.IsNone());
    TestFalse(TEXT("Presentation cannot grant ledger"),M->State.bLedger);
    UAnanseSave* Save=NewObject<UAnanseSave>();Save->State=M->State;
    TArray<uint8> Bytes;
    TestTrue(TEXT("Serialize actual save envelope"),UGameplayStatics::SaveGameToMemory(Save,Bytes));
    UAnanseSave* ReadBack=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromMemory(Bytes));
    if(!TestNotNull(TEXT("Deserialize actual save envelope"),ReadBack))return false;
    UAnanseMission* Restored=NewObject<UAnanseMission>();Restored->State=ReadBack->State;
    TestFalse(TEXT("Reloaded event remains idempotent"),Restored->CompletePresentationEvent(TEXT("market-opening-v1")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseCinematicGuardTest,"Ananse.Cinematic.InvalidBinding",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseCinematicGuardTest::RunTest(const FString& Parameters)
{
    UAnanseMission* M=NewObject<UAnanseMission>();
    UAnanseCinematic* C=NewObject<UAnanseCinematic>();
    TestFalse(TEXT("Unpossessed/null sequence rejected before input lock"),C->Start(M,nullptr,TEXT("opening")));
    C->Skip();C->Cancel();
    TestFalse(TEXT("No active lifecycle after rejected start"),C->bActive);
    TestFalse(TEXT("Cancel/skip leaves no pending stop timer"),C->HasPendingStop());
    TestEqual(TEXT("Cancelled/invalid sequence awards nothing"),M->State.CompletedPresentationEvents.Num(),0);
    TestFalse(TEXT("Mission without owner cannot begin"),M->BeginCinematic(nullptr,TEXT("opening")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseCheckpointPolicyTest,"Ananse.Save.BindingAndLegacyPolicy",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseCheckpointPolicyTest::RunTest(const FString& Parameters)
{
    UAnanseSave* Save=NewObject<UAnanseSave>();
    Save->ContentHash=TEXT("candidate-hash");Save->CharacterId=TEXT("ananse");Save->MapIdentity=TEXT("/Game/Ananse/CharacterLab/L_AnanseCharacterLab");
    Save->State.ProductionBeat=TEXT("investigation");Save->State.CompletedPresentationEvents.Add(TEXT("opening_finished_or_skipped"));
    TArray<uint8> Bytes;TestTrue(TEXT("Serialize schema2"),UGameplayStatics::SaveGameToMemory(Save,Bytes));
    UAnanseSave* Read=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromMemory(Bytes));
    if(!TestNotNull(TEXT("Read schema2"),Read))return false;
    TestEqual(TEXT("Schema3"),Read->SchemaVersion,3);TestEqual(TEXT("Character survives serialization"),Read->CharacterId,Save->CharacterId);
    TestEqual(TEXT("Map survives serialization"),Read->MapIdentity,Save->MapIdentity);TestEqual(TEXT("Beat survives serialization"),Read->State.ProductionBeat,FName(TEXT("investigation")));
    FString Reason;
    TestTrue(TEXT("Same candidate binding accepted"),UAnanseMission::CheckpointCompatible(Read,Save->ContentHash,Save->CharacterId,Save->MapIdentity,Reason));
    const FString PreservedHash=Read->ContentHash;const FName PreservedCharacter=Read->CharacterId;
    TestFalse(TEXT("Cross-character restore refused"),UAnanseMission::CheckpointCompatible(Read,Save->ContentHash,TEXT("kwaku"),Save->MapIdentity,Reason));
    TestFalse(TEXT("Cross-map restore refused"),UAnanseMission::CheckpointCompatible(Read,Save->ContentHash,Save->CharacterId,TEXT("/Game/Maps/L_Market_Greybox"),Reason));
    TestFalse(TEXT("Content migration never implicit"),UAnanseMission::CheckpointCompatible(Read,TEXT("new-content"),Save->CharacterId,Save->MapIdentity,Reason));
    TestEqual(TEXT("Policy rejection preserves object hash"),Read->ContentHash,PreservedHash);TestEqual(TEXT("Policy rejection preserves identity"),Read->CharacterId,PreservedCharacter);
    UAnanseSave* Legacy=NewObject<UAnanseSave>();Legacy->SchemaVersion=1;Legacy->ContentHash=Save->ContentHash;
    TestTrue(TEXT("Legacy Kwaku market candidate accepted"),UAnanseMission::CheckpointCompatible(Legacy,Legacy->ContentHash,TEXT("kwaku"),TEXT("/Game/Maps/L_Market_Greybox"),Reason));
    TestFalse(TEXT("Legacy cannot enter spider lab"),UAnanseMission::CheckpointCompatible(Legacy,Legacy->ContentHash,TEXT("ananse"),Save->MapIdentity,Reason));
    TestFalse(TEXT("Legacy mismatched content retained"),UAnanseMission::CheckpointCompatible(Legacy,TEXT("new-content"),TEXT("kwaku"),TEXT("/Game/Maps/L_Market_Greybox"),Reason));
    UAnanseMission* Mission=NewObject<UAnanseMission>();
    TestTrue(TEXT("Opening semantic completion advances once"),Mission->CompletePresentationEvent(TEXT("opening_finished_or_skipped")));
    TestEqual(TEXT("Opening reaches investigation"),Mission->State.ProductionBeat,FName(TEXT("investigation")));
    TestFalse(TEXT("Repeated skip cannot advance again"),Mission->CompletePresentationEvent(TEXT("opening_finished_or_skipped")));
    TestTrue(TEXT("Presentation never sets outcome"),Mission->State.Outcome.IsNone());
    return true;
}
#endif
