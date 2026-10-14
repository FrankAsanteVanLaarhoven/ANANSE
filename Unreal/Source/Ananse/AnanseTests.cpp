#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "AnanseMission.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseNegotiationTest,"Ananse.Mission.Negotiation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseNegotiationTest::RunTest(const FString& Parameters)
{
    UAnanseMission* M=NewObject<UAnanseMission>();
    TestFalse(TEXT("No evidence, no permit"),M->Act(TEXT("negotiate")));
    TestTrue(TEXT("Collect evidence"),M->Act(TEXT("evidence")));
    TestTrue(TEXT("Negotiate permit"),M->Act(TEXT("negotiate")));
    TestTrue(TEXT("Access archive"),M->Act(TEXT("archive")));
    TestTrue(TEXT("Take ledger"),M->Act(TEXT("ledger")));
    TestFalse(TEXT("Cannot farm ledger"),M->Act(TEXT("ledger")));
    TestTrue(TEXT("Protect witnesses"),M->Act(TEXT("protect")));
    TestEqual(TEXT("Outcome"),M->State.Outcome,FName(TEXT("witnesses-protected")));
    TestEqual(TEXT("Trust"),M->State.MarketTrust,3);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnansePowerTest,"Ananse.Mission.PowerBudget",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnansePowerTest::RunTest(const FString& Parameters)
{
    UAnanseMission* M=NewObject<UAnanseMission>();
    TestFalse(TEXT("No learned voice"),M->CommitPower(TEXT("borrowed-voice")));
    TestEqual(TEXT("Failure consumes no thread"),M->State.Thread,3);
    TestTrue(TEXT("Learn voice"),M->Act(TEXT("listen")));
    TestTrue(TEXT("Use voice"),M->CommitPower(TEXT("borrowed-voice")));
    TestFalse(TEXT("Cooldown blocks repeat"),M->CommitPower(TEXT("borrowed-voice")));
    TestTrue(TEXT("Use mirror"),M->CommitPower(TEXT("trick-mirror")));
    TestTrue(TEXT("Use web"),M->CommitPower(TEXT("web-step")));
    TestEqual(TEXT("Resource exhausted"),M->State.Thread,0);
    TestFalse(TEXT("Unknown power cannot mint resources"),M->CommitPower(TEXT("invalid")));return true;
}
#endif
