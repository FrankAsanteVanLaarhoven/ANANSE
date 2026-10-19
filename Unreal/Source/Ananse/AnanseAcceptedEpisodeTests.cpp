#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "AnanseRuntimeVerification.h"
#include "AnanseMission.h"
#include "AnanseCastLab.h"
#include "Engine/SkeletalMesh.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseAcceptedSaveIsolation,"Ananse.Episode.AcceptedVisualsKeepLegacySaves",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseAcceptedSaveIsolation::RunTest(const FString&)
{
 const FString Original=FCommandLine::Get();
 FCommandLine::Set(TEXT(""));
 TestEqual(TEXT("Legacy campaign slot unchanged"),AnanseVerificationSaveSlot(TEXT("kwaku")),FString(TEXT("AnansePrototype")));
 FCommandLine::Set(TEXT("-AnanseAcceptedVisuals"));
 TestEqual(TEXT("Accepted visuals have independent default slot"),AnanseVerificationSaveSlot(TEXT("kwaku")),FString(TEXT("AnanseAcceptedEpisode_v1")));
 TestEqual(TEXT("Other character slot unchanged"),AnanseVerificationSaveSlot(TEXT("ananse")),FString(TEXT("AnanseCharacter_ananse")));
 TestEqual(TEXT("Accepted market travel"),UAnanseMission::MarketMap(),FString(TEXT("/Game/Ananse/Maps/EpisodeAccepted_v001/L_Market_AcceptedVisuals")));
 TestEqual(TEXT("Accepted sanctuary travel"),UAnanseMission::SanctuaryMap(),FString(TEXT("/Game/Ananse/Maps/EpisodeAccepted_v001/L_Sanctuary_AcceptedVisuals")));
 FCommandLine::Set(*Original);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseAcceptedCampaignBinding,"Ananse.Episode.AcceptedKwakuRetainsIdentityAndRig",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseAcceptedCampaignBinding::RunTest(const FString&)
{
 UClass* Class=LoadClass<AAnanseCastLabPlayer>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/EpisodeAccepted_v001/BP_KwakuAcceptedEpisode.BP_KwakuAcceptedEpisode_C"));
 if(!TestNotNull(TEXT("Saved campaign pawn class"),Class))return false;
 const auto* Hero=Class->GetDefaultObject<AAnanseCastLabPlayer>();
 TestEqual(TEXT("Campaign protagonist remains Kwaku"),Hero->CharacterId,FName(TEXT("kwaku")));
 TestTrue(TEXT("Existing campaign mode, not lab authority"),Hero->bStoryCampaignPresentation);
 if(TestNotNull(TEXT("Approved skeletal mesh"),Hero->AuthoredMesh.Get()))
 {
  TestEqual(TEXT("Exact user-accepted mesh"),Hero->AuthoredMesh->GetPathName(),FString(TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku")));
  TestEqual(TEXT("Original human skeleton retained"),Hero->AuthoredMesh->GetRefSkeleton().GetNum(),46);
 }
 TestEqual(TEXT("All existing motion identities retained"),Hero->AuthoredClips.Num(),11);
 TestTrue(TEXT("Existing ledger presentation retained"),Hero->bLedgerPresentation);
 return true;
}
#endif
