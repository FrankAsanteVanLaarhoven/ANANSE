#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "AnanseMission.h"
#include "AnansePursuit.h"
#include "Kismet/GameplayStatics.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnansePursuitGateTest,"Ananse.Mission.ProductionPursuitGates",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnansePursuitGateTest::RunTest(const FString& Parameters)
{
    UAnanseMission* M=NewObject<UAnanseMission>();
    TestTrue(TEXT("Production pursuit explicitly enabled"),M->EnableProductionPursuit());
    TestTrue(TEXT("Evidence"),M->Act(TEXT("evidence")));TestTrue(TEXT("Negotiation"),M->Act(TEXT("negotiate")));
    TestTrue(TEXT("Archive"),M->Act(TEXT("archive")));TestTrue(TEXT("Ledger"),M->Act(TEXT("ledger")));
    TestEqual(TEXT("Ledger stages discovery not completion"),M->State.ProductionBeat,FName(TEXT("discovery")));
    TestFalse(TEXT("No instant consequence before played escape"),M->Act(TEXT("protect")));
    TestFalse(TEXT("No fabricated escape without actual actor"),M->Act(TEXT("escape")));
    TestFalse(TEXT("No chase without actual world and owner"),M->StartPursuit());
    TestTrue(TEXT("Outcome unchanged by rejected completion"),M->State.Outcome.IsNone());
    TestFalse(TEXT("Cannot change production mode after ledger"),M->EnableProductionPursuit());
    TestFalse(TEXT("Cannot escape too soon"),AAnansePursuit::EscapeConditions(5.9,50,500,false));
    TestFalse(TEXT("Cannot escape away from gate"),AAnansePursuit::EscapeConditions(10,241,500,false));
    TestFalse(TEXT("Cannot escape pursuer in capture range"),AAnansePursuit::EscapeConditions(10,50,349,false));
    TestFalse(TEXT("Captured player cannot award escape"),AAnansePursuit::EscapeConditions(10,50,500,true));
    TestTrue(TEXT("Played separated gate crossing qualifies"),AAnansePursuit::EscapeConditions(6,240,350,false));
    M->State.bPursuitStarted=true;M->AddSuspicion(100.f);
    TestTrue(TEXT("Watcher cannot race chase capture with detained outcome"),M->State.Outcome.IsNone());
    TestEqual(TEXT("Chase failure has explicit Osebo ownership"),M->State.Suspicion,0.f);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnansePursuitSaveTest,"Ananse.Save.PursuitRecoveryEnvelope",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnansePursuitSaveTest::RunTest(const FString& Parameters)
{
    UAnanseSave* Save=NewObject<UAnanseSave>();Save->ContentHash=TEXT("same-candidate");Save->CharacterId=TEXT("kwaku");Save->MapIdentity=TEXT("/Game/Maps/L_Market_Greybox");
    Save->State.bProductionPursuit=true;Save->State.bPursuitStarted=true;Save->State.bCaptured=true;Save->State.ProductionBeat=TEXT("captured");
    Save->State.PursuitSeconds=12.5;Save->State.PursuitLostSightSeconds=2.3;Save->State.PursuerPosition=FVector(111,222,96);Save->State.PursuerLastKnown=FVector(300,400,96);
    Save->bHasPursuitRecovery=true;Save->PursuitRecoveryState.bLedger=true;Save->PursuitRecoveryState.bProductionPursuit=true;Save->PursuitRecoveryState.Route=TEXT("negotiation");
    Save->RecoveryVoiceRemaining=3.5;Save->RecoveryMirrorRemaining=1.25;Save->RecoveryCooldownRemaining.Add(TEXT("web-step"),2.0);
    Save->PursuitRecoveryPosition=FVector(850,250,96);Save->PursuitRecoveryRotation=FRotator(0,30,0);
    TArray<uint8> Bytes;TestTrue(TEXT("Serialize native schema3"),UGameplayStatics::SaveGameToMemory(Save,Bytes));
    UAnanseSave* Read=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromMemory(Bytes));if(!TestNotNull(TEXT("Read actual envelope"),Read))return false;
    TestEqual(TEXT("Schema3"),Read->SchemaVersion,3);TestTrue(TEXT("Recovery retained"),Read->bHasPursuitRecovery);
    TestTrue(TEXT("Capture retained"),Read->State.bCaptured);TestEqual(TEXT("Pursuit relative elapsed retained"),Read->State.PursuitSeconds,12.5f);
    TestEqual(TEXT("Lost sight duration retained"),Read->State.PursuitLostSightSeconds,2.3f);
    TestEqual(TEXT("Pursuer position retained"),Read->State.PursuerPosition,Save->State.PursuerPosition);
    TestEqual(TEXT("Hidden target knowledge retained, not refreshed"),Read->State.PursuerLastKnown,Save->State.PursuerLastKnown);
    TestEqual(TEXT("Recovery voice relative timer retained"),Read->RecoveryVoiceRemaining,3.5f);
    TestEqual(TEXT("Recovery mirror relative timer retained"),Read->RecoveryMirrorRemaining,1.25f);
    TestEqual(TEXT("Recovery cooldown relative timer retained"),Read->RecoveryCooldownRemaining.FindRef(TEXT("web-step")),2.0f);
    TestEqual(TEXT("Recovery route retained"),Read->PursuitRecoveryState.Route,FName(TEXT("negotiation")));
    TestTrue(TEXT("Recovery ledger retained"),Read->PursuitRecoveryState.bLedger);
    TestFalse(TEXT("Recovery state has no capture"),Read->PursuitRecoveryState.bCaptured);
    TestEqual(TEXT("Recovery position retained"),Read->PursuitRecoveryPosition,Save->PursuitRecoveryPosition);
    FString Reason;Save->SchemaVersion=2;
    TestTrue(TEXT("Prior schema2 bound candidate remains accepted"),UAnanseMission::CheckpointCompatible(Save,Save->ContentHash,Save->CharacterId,Save->MapIdentity,Reason));
    TestFalse(TEXT("Content change still needs explicit migration"),UAnanseMission::CheckpointCompatible(Save,TEXT("another-candidate"),Save->CharacterId,Save->MapIdentity,Reason));
    return true;
}
#endif
