#include "AnanseRuntimeVerification.h"
#if !UE_BUILD_SHIPPING
#include "AnansePlayer.h"
#include "AnanseMission.h"
#include "AnanseCatalogue.h"
#include "AnansePowers.h"
#include "AbilitySystemComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameModeBase.h"
#include "UnrealClient.h"
#include "DynamicRHI.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Engine.h"
#include "InputKeyEventArgs.h"
#include "GameFramework/PlayerInput.h"
#include "EnhancedPlayerInput.h"
#include "Components/InputComponent.h"
#include "GenericPlatform/GenericPlatformInputDeviceMapper.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/EngineVersion.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "Containers/Ticker.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"
#include "RHI.h"
#include "RHIGlobals.h"
#if WITH_EDITOR
#include "Editor.h"
#endif
namespace
{
struct FVerification
{
    bool Initialized=false,Enabled=false,Done=false,Failed=false,Pressed=false;
    uint32 OwnerId=0;int32 Phase=0,WalkPoint=0,BeforeCount=0;double Created=0,Started=0,ActiveSeconds=0,ReadyAt=0,LastReport=0;
    FString Mode,Out,ExpectedHash,ExpectedColour,Slot;int32 ExpectedMirror=0;
    TSharedPtr<FJsonObject> Report=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Checks;
    TMap<FName,int32> Actions;
    void Write()
    {
        Report->SetArrayField(TEXT("checks"),Checks);Report->SetNumberField(TEXT("phase"),Phase);
        Report->SetNumberField(TEXT("active_play_seconds"),ActiveSeconds);
        FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Report.ToSharedRef(),Writer);
        IFileManager::Get().MakeDirectory(*FPaths::GetPath(Out),true);
        FFileHelper::SaveStringToFile(Text,*Out,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    }
} V;
void Key(APlayerController* PC,FKey KeyName,bool Down)
{
    bool Delivered=PC->InputKey(FInputKeyEventArgs::CreateSimulated(KeyName,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,IPlatformInputDeviceMapper::Get().GetDefaultInputDevice()));
    V.Report->SetBoolField(TEXT("last_input_accepted"),Delivered);
}
TSharedRef<FJsonObject> MissionState(const FAnanseMissionState& S)
{
    auto J=MakeShared<FJsonObject>();
    J->SetBoolField(TEXT("evidence"),S.bEvidence);J->SetBoolField(TEXT("learned_voice"),S.bLearnedVoice);
    J->SetBoolField(TEXT("permit"),S.bPermit);J->SetBoolField(TEXT("archive"),S.bArchive);J->SetBoolField(TEXT("ledger"),S.bLedger);J->SetBoolField(TEXT("on_rooftop"),S.bOnRooftop);
    J->SetNumberField(TEXT("thread"),S.Thread);J->SetNumberField(TEXT("suspicion"),S.Suspicion);J->SetNumberField(TEXT("market_trust"),S.MarketTrust);J->SetNumberField(TEXT("court_trust"),S.CourtTrust);
    J->SetStringField(TEXT("route"),S.Route.ToString());J->SetStringField(TEXT("outcome"),S.Outcome.ToString());return J;
}
void End(AAnansePlayer* P,const FString& Error=FString())
{
    if(V.Done)return;V.Done=true;V.Failed=!Error.IsEmpty();
    if(APlayerController* PC=Cast<APlayerController>(P->GetController()))Key(PC,EKeys::W,false);
    V.Report->SetStringField(TEXT("status"),V.Failed?TEXT("failed"):TEXT("assertions_passed"));
    if(V.Failed){V.Report->SetStringField(TEXT("error"),Error);UE_LOG(LogTemp,Error,TEXT("ANANSE verification: %s"),*Error);}
    V.Report->SetObjectField(TEXT("mission_state"),MissionState(P->Mission->State));V.Write();
    FScreenshotRequest::RequestScreenshot(FPaths::GetPath(V.Out)/TEXT("native-game.png"),true,false);
    const double Finish=FPlatformTime::Seconds()+2;bool PIE=P->GetWorld()->WorldType==EWorldType::PIE;
    FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Finish,PIE,StopSeenAt=0.0](float) mutable
    {
        if(FPlatformTime::Seconds()<Finish)return true;
#if WITH_EDITOR
        if(PIE && GEditor && GEditor->PlayWorld){GEditor->RequestEndPlayMap();return true;}
        if(PIE)
        {
            if(StopSeenAt==0){StopSeenAt=FPlatformTime::Seconds();return true;}
            if(FPlatformTime::Seconds()-StopSeenAt<2)return true;
        }
#endif
        V.Report->SetBoolField(TEXT("play_stopped"),true);V.Write();
        FPlatformMisc::RequestExitWithStatus(false,V.Failed?2:0,TEXT("ANANSE native verification completed"));return false;
    }));
}
bool Check(AAnansePlayer* P,bool Good,const FString& Name)
{
    if(!Good){End(P,Name+TEXT("; feedback: ")+P->Mission->LatestMessage);return false;}
    V.Checks.Add(MakeShared<FJsonValueString>(Name));return true;
}
bool Walk(AAnansePlayer* P,APlayerController* PC,float X,float Y)
{
    FVector D=FVector(X,Y,P->GetActorLocation().Z)-P->GetActorLocation();
    if(D.Size2D()<20){Key(PC,EKeys::W,false);return true;}
    PC->SetControlRotation(FRotator(0,FMath::RadiansToDegrees(FMath::Atan2(D.Y,D.X)),0));
    Key(PC,EKeys::W,true);return false;
}
void Next(){V.Phase++;V.Pressed=false;V.ReadyAt=FPlatformTime::Seconds()+.35;}
bool Action(AAnansePlayer* P,APlayerController* PC,FKey K,FName Name)
{
    if(!V.Pressed){V.BeforeCount=V.Actions.FindRef(Name);Key(PC,K,true);V.Pressed=true;V.ReadyAt=FPlatformTime::Seconds();return false;}
    if(V.Actions.FindRef(Name)<=V.BeforeCount && FPlatformTime::Seconds()-V.ReadyAt<1)return false;
    Key(PC,K,false);return Check(P,V.Actions.FindRef(Name)>V.BeforeCount,TEXT("simulated input reached native ")+Name.ToString());
}
}
FString AnanseVerificationSaveSlot(){return V.Enabled && !V.Slot.IsEmpty()?V.Slot:TEXT("AnansePrototype");}
void NotifyAnanseVerificationAction(AAnansePlayer*,FName Action)
{
    if(V.Enabled && !V.Done)V.Actions.FindOrAdd(Action)++;
}
void TickAnanseRuntimeVerification(AAnansePlayer* P,float Delta)
{
    if(!V.Initialized)
    {
        V.Created=FPlatformTime::Seconds();V.Initialized=true;V.Enabled=FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyMode="),V.Mode);
        if(!V.Enabled)return;
        FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyReport="),V.Out);FParse::Value(FCommandLine::Get(),TEXT("AnanseExpectedHash="),V.ExpectedHash);
        FParse::Value(FCommandLine::Get(),TEXT("AnanseExpectedColour="),V.ExpectedColour);FParse::Value(FCommandLine::Get(),TEXT("AnanseExpectedMirror="),V.ExpectedMirror);
        FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifySlot="),V.Slot);
        if(V.Out.IsEmpty() || V.Slot.IsEmpty()){V.Enabled=false;UE_LOG(LogTemp,Error,TEXT("Verification requires explicit report path and dedicated save slot."));return;}
        V.Report->SetStringField(TEXT("mode"),V.Mode);V.Report->SetStringField(TEXT("slot"),V.Slot);V.Report->SetStringField(TEXT("status"),TEXT("starting"));
        V.Report->SetStringField(TEXT("scope"),TEXT("Native development verification; simulated controller input events, not physical hardware."));
        V.Report->SetStringField(TEXT("engine"),FEngineVersion::Current().ToString());
    }
    if(!V.Enabled || V.Done)return;
    if(!P->IsNativePlayReady())
    {
        if(FPlatformTime::Seconds()-V.LastReport>5){V.LastReport=FPlatformTime::Seconds();V.Report->SetBoolField(TEXT("actor_begun_play"),P->HasActorBegunPlay());V.Report->SetBoolField(TEXT("has_controller"),P->GetController()!=nullptr);V.Report->SetBoolField(TEXT("world_begun_play"),P->GetWorld()->HasBegunPlay());V.Write();}
        if(FPlatformTime::Seconds()-V.Created>30)End(P,TEXT("BeginPlay/possession readiness expired"));return;
    }
    V.ActiveSeconds+=Delta;
    APlayerController* PC=Cast<APlayerController>(P->GetController());if(!PC)return;
    double Now=FPlatformTime::Seconds();
    if(V.Started==0)
    {
        V.Started=Now;V.OwnerId=P->GetUniqueID();V.ReadyAt=Now+1;
        V.Report->SetStringField(TEXT("world_type"),P->GetNativeWorldType());V.Report->SetStringField(TEXT("world"),P->GetWorld()->GetPathName());
        V.Report->SetStringField(TEXT("pawn"),P->GetClass()->GetName());V.Report->SetStringField(TEXT("controller"),PC->GetClass()->GetName());
        V.Report->SetStringField(TEXT("game_mode"),P->GetWorld()->GetAuthGameMode()->GetClass()->GetName());
        V.Report->SetStringField(TEXT("player_input_class"),PC->PlayerInput?PC->PlayerInput->GetClass()->GetName():TEXT("None"));
        V.Report->SetStringField(TEXT("input_component_class"),P->InputComponent?P->InputComponent->GetClass()->GetName():TEXT("None"));
        if(UEnhancedPlayerInput* Input=Cast<UEnhancedPlayerInput>(PC->PlayerInput))V.Report->SetNumberField(TEXT("enhanced_mapping_count"),Input->GetEnhancedActionMappingsView().Num());
        V.Report->SetStringField(TEXT("rhi"),GDynamicRHI?GDynamicRHI->GetName():TEXT("None"));V.Report->SetStringField(TEXT("adapter"),GRHIAdapterName);
        V.Report->SetStringField(TEXT("status"),TEXT("running"));V.Write();return;
    }
    if(P->GetUniqueID()!=V.OwnerId){End(P,TEXT("Unexpected pawn replacement/world travel during verification"));return;}
    if(Now-V.Started>150){End(P,TEXT("Native scenario timed out"));return;}
    if(Now-V.LastReport>10){V.LastReport=Now;V.Write();}
    if(Now<V.ReadyAt)return;
    UAnanseMission* M=P->Mission;UAnanseCatalogue* C=P->GetCatalogue();
    if(V.Phase==0)
    {
        if(!Check(P,C && C->bLoaded && C->ContentHash==V.ExpectedHash,TEXT("live publication hash loaded")))return;
        V.Report->SetStringField(TEXT("loaded_hash"),C->ContentHash);
        if(!Check(P,GDynamicRHI && FString(GDynamicRHI->GetName())==TEXT("Vulkan"),TEXT("real Vulkan rendering backend")))return;
        V.Report->SetBoolField(TEXT("primitive_placeholder"),true);
        FLinearColor Actual;bool HasColour=P->Body->GetMaterial(0) && P->Body->GetMaterial(0)->GetVectorParameterValue(FMaterialParameterInfo(TEXT("ClothColor")),Actual);
        FLinearColor Wanted=FLinearColor::FromSRGBColor(FColor::FromHex(V.ExpectedColour));
        if(!Check(P,HasColour && Actual.Equals(Wanted,.0001f),TEXT("primitive material matches expected sRGB-to-linear colour (tolerance 0.0001)")))return;
        V.Report->SetStringField(TEXT("actual_linear_colour"),Actual.ToString());
        bool Mirror=P->Abilities->FindAbilitySpecFromClass(UAnanseMirrorAbility::StaticClass())!=nullptr;
        if(!Check(P,Mirror==(V.ExpectedMirror!=0),TEXT("permitted mirror ability grant matches publication")))return;
        if(!Check(P,PC->GetPawn()==P && (P->GetWorld()->WorldType==EWorldType::Game || P->GetWorld()->WorldType==EWorldType::PIE),TEXT("possessed native game pawn")))return;
        Next();return;
    }
    if(V.Mode==TEXT("r2"))
    {
        if(V.Phase==1 || V.Phase==2)
        {
            if(!Action(P,PC,V.Phase==1?EKeys::Three:EKeys::Gamepad_FaceButton_Top,TEXT("mirror")))return;
            if(!Check(P,M->State.Thread==3 && !M->MirrorActive(),TEXT("absent mirror blocked through simulated keyboard/gamepad path")))return;Next();return;
        }
        if(V.Phase==3)
        {
            int32 W,H;PC->GetViewportSize(W,H);
            if(!V.Pressed){V.BeforeCount=V.Actions.FindRef(TEXT("mirror"));PC->InputTouch(FTouchId(FInputDeviceId::CreateFromInternalId(0),ETouchIndex::Touch1),ETouchType::Began,FVector2D(W-50,159),1,FPlatformTime::Cycles64());V.Pressed=true;V.ReadyAt=Now+.3;return;}
            PC->InputTouch(FTouchId(FInputDeviceId::CreateFromInternalId(0),ETouchIndex::Touch1),ETouchType::Ended,FVector2D(W-50,159),0,FPlatformTime::Cycles64());
            if(!Check(P,V.Actions.FindRef(TEXT("mirror"))>V.BeforeCount && M->State.Thread==3 && !M->MirrorActive(),TEXT("absent mirror blocked through simulated touch input path")))return;Next();return;
        }
        FVector2D Points[]={FVector2D(-900,-150),FVector2D(-700,-150),FVector2D(-700,-350),FVector2D(-900,-350)};
        auto Point=Points[V.WalkPoint%4];if(Walk(P,PC,Point.X,Point.Y))V.WalkPoint++;
        if(V.ActiveSeconds>=60){if(Check(P,V.WalkPoint>=4,TEXT("WASD binding drives collision-aware native movement")))End(P);}return;
    }
    if(V.Mode==TEXT("reload"))
    {
        if(V.Phase==1)
        {
            UAnanseSave* S=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(V.Slot,0));
            if(!Check(P,S!=nullptr,TEXT("dedicated native checkpoint exists after process restart")))return;
            if(!Action(P,PC,EKeys::F9,TEXT("load")))return;
            bool Same=FAnanseMissionState::StaticStruct()->CompareScriptStruct(&S->State,&M->State,0);
            if(!Check(P,Same && P->GetActorLocation().Equals(S->Position,.05f) && P->GetActorRotation().Equals(S->Rotation,.01f),TEXT("all mission fields and transform restored")))return;
            float Clock=P->GetWorld()->GetTimeSeconds();
            if(!Check(P,FMath::IsNearlyEqual(FMath::Max(0.f,M->VoiceUntil-Clock),S->VoiceRemaining,.03f) && FMath::IsNearlyEqual(FMath::Max(0.f,M->MirrorUntil-Clock),S->MirrorRemaining,.03f),TEXT("saved relative power timers restored")))return;
            for(const auto& Entry:S->CooldownRemaining)if(!Check(P,FMath::IsNearlyEqual(FMath::Max(0.f,M->Cooldowns.FindRef(Entry.Key)-Clock),Entry.Value,.03f),TEXT("saved cooldown restored: ")+Entry.Key.ToString()))return;
            Next();return;
        }
        if(V.ActiveSeconds>=60)End(P);return;
    }
    if(V.Mode!=TEXT("baseline")){End(P,TEXT("Unknown native verification mode"));return;}
    if(V.Phase==1)
    {
        if(!Walk(P,PC,-650,150))return;
        if(!Action(P,PC,EKeys::E,TEXT("interact")))return;
        if(Check(P,M->State.bLearnedVoice,TEXT("learned captain call via native spatial interaction")))Next();return;
    }
    if(V.Phase==2)
    {
        if(!Action(P,PC,EKeys::Two,TEXT("voice")))return;
        if(Check(P,M->VoiceActive() && M->State.Thread==2,TEXT("Borrowed Voice activated through input binding")))Next();return;
    }
    if(V.Phase==3)
    {
        if(!Action(P,PC,EKeys::Three,TEXT("mirror")))return;
        if(Check(P,M->MirrorActive() && M->State.Thread==1,TEXT("Trick Mirror activated through input binding")))Next();return;
    }
    if(V.Phase==4)
    {
        if(!V.Pressed && !Walk(P,PC,-400,300))return;
        if(!Action(P,PC,EKeys::One,TEXT("web")))return;
        if(Check(P,P->IsWebFlying() && M->State.Thread==0,TEXT("Web Step starts collision-checked native traversal"))){Next();V.ReadyAt=Now+1;}return;
    }
    if(V.Phase==5){if(Check(P,!P->IsWebFlying(),TEXT("Web Step completes native flight")))Next();return;}
    FVector2D Route[]={FVector2D(-800,-350),FVector2D(-100,-200),FVector2D(500,250),FVector2D(850,250),FVector2D(1300,350)};
    if(V.Phase>=6 && V.Phase<=10)
    {
        // Walk around the solid archive marker instead of driving through it.
        if(V.Phase==9 && V.WalkPoint<2)
        {
            const FVector2D Detour[2]={FVector2D(500,100),FVector2D(850,100)};
            auto Point=Detour[V.WalkPoint];if(Walk(P,PC,Point.X,Point.Y))V.WalkPoint++;return;
        }
        if(V.Phase==10 && V.WalkPoint<5)
        {
            const FVector2D Detour[3]={FVector2D(850,100),FVector2D(1300,100),FVector2D(1300,250)};
            auto Point=Detour[V.WalkPoint-2];if(Walk(P,PC,Point.X,Point.Y))V.WalkPoint++;return;
        }
        auto Point=Route[V.Phase-6];if(!Walk(P,PC,Point.X,Point.Y))return;
        if(!Action(P,PC,EKeys::E,TEXT("interact")))return;
        bool Good=V.Phase==6?M->State.bEvidence:V.Phase==7?M->State.bPermit:V.Phase==8?M->State.bArchive:V.Phase==9?M->State.bLedger:M->State.Outcome==TEXT("witnesses-protected");
        if(Check(P,Good,FString::Printf(TEXT("native mission spatial step %d"),V.Phase-5)))Next();return;
    }
    if(V.Phase==11)
    {
        if(!V.Pressed && !Check(P,M->State.Route==TEXT("negotiation") && !UGameplayStatics::DoesSaveGameExist(V.Slot,0),TEXT("completed route and unused dedicated save slot")))return;
        if(!Action(P,PC,EKeys::F5,TEXT("save")))return;
        if(!Check(P,UGameplayStatics::DoesSaveGameExist(V.Slot,0),TEXT("native checkpoint written through F5 input path")))return;
        V.Report->SetStringField(TEXT("save_path"),FPaths::ProjectSavedDir()/TEXT("SaveGames")/(V.Slot+TEXT(".sav")));Next();return;
    }
    if(V.ActiveSeconds>=60)End(P);
}
#else
void TickAnanseRuntimeVerification(AAnansePlayer*,float){}
void NotifyAnanseVerificationAction(AAnansePlayer*,FName){}
FString AnanseVerificationSaveSlot(){return TEXT("AnansePrototype");}
#endif
