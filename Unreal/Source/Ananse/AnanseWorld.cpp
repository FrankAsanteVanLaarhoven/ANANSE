#include "AnanseWorld.h"
#include "AnanseAsoLedger.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "AnanseLabSelection.h"
#include "AnanseLeopardLab.h"
#include "AnanseCastLab.h"
#include "AnansePlayer.h"
#include "AnanseMission.h"
#include "AnanseCinematic.h"
#include "AnanseCatalogue.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Components/TextRenderComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"

AAnanseInteractable::AAnanseInteractable()
{
    PrimaryActorTick.bCanEverTick=true;
    Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Marker"));SetRootComponent(Mesh);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if(Cube.Succeeded())Mesh->SetStaticMesh(Cube.Object);
    Mesh->SetRelativeScale3D(FVector(0.55f,0.55f,1.f));
    Label=CreateDefaultSubobject<UTextRenderComponent>(TEXT("Label"));Label->SetupAttachment(Mesh);
    Label->SetRelativeLocation(FVector(0,0,95));Label->SetWorldSize(22);Label->SetHorizontalAlignment(EHTA_Center);
    Label->SetText(FText::FromString(TEXT("Interact")));Label->SetTextRenderColor(FColor(235,215,150));
    PropVisual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AuthoredProp"));PropVisual->SetupAttachment(Mesh);PropVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    NegotiationLedgerVisual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NegotiationLedger"));NegotiationLedgerVisual->SetupAttachment(Mesh);NegotiationLedgerVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);NegotiationLedgerVisual->SetGenerateOverlapEvents(false);NegotiationLedgerVisual->SetVisibility(false);
    CharacterVisual=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("AuthoredCharacter"));CharacterVisual->SetupAttachment(Mesh);CharacterVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);CharacterVisual->SetAbsolute(false,false,true);
}
void AAnanseInteractable::BeginPlay()
{
    Super::BeginPlay();
    SetActorTickEnabled(bNegotiationPresentation);
    if(bNegotiationLedger)CharacterVisual->RegisterOnBoneTransformsFinalizedDelegate(FOnBoneTransformsFinalizedMultiCast::FDelegate::CreateUObject(this,&AAnanseInteractable::UpdateNegotiationLedger));
    const bool HasProp=PropVisual->GetStaticMesh()!=nullptr;
    const bool HasCharacter=CharacterVisual->GetSkeletalMeshAsset() && PresentationIdle && PresentationIdle->GetSkeleton()==CharacterVisual->GetSkeletalMeshAsset()->GetSkeleton();
    if(HasCharacter){CharacterVisual->SetAnimationMode(EAnimationMode::AnimationSingleNode);CharacterVisual->PlayAnimation(PresentationIdle,true);}
    CharacterVisual->SetVisibility(HasCharacter);
    if(HasProp || HasCharacter)Mesh->SetVisibility(false,false);
    if(CharacterId.IsNone() || !GetWorld() || !GetWorld()->GetGameInstance())return;
    const UAnanseCatalogue* Catalogue=GetWorld()->GetGameInstance()->GetSubsystem<UAnanseCatalogue>();
    const FAnanseCharacterSpec* Spec=Catalogue?Catalogue->Find(CharacterId):nullptr;
    if(!Spec)return;
    Label->SetText(FText::FromString(Spec->DisplayName+TEXT(" | ")+Label->Text.ToString()));
    if(!Spec->Variants.IsEmpty())
    {
        const FAnanseAppearance& Appearance=Spec->Variants[0];
        if(UMaterialInstanceDynamic* M=Mesh->CreateDynamicMaterialInstance(0))M->SetVectorParameterValue(TEXT("ClothColor"),Appearance.Cloth);
    }
}
// Presentation reads mission state on the game thread; it never writes durable outcomes.
int32 AAnanseInteractable::NegotiationPoseFor(const FAnanseMissionState& State)
{
    if(State.Outcome==TEXT("truth-exposed"))return State.bPermit?11:9;
    if(State.Outcome==TEXT("witnesses-protected"))return 10;
    if(State.bPermit)return 8;
    return State.bEvidence?4:0;
}
void AAnanseInteractable::PlayNegotiation(int32 Index)
{
    if(!bNegotiationPresentation||!NegotiationClips.IsValidIndex(Index))return;
    auto* Clip=NegotiationClips[Index].Get();auto* Skin=CharacterVisual->GetSkeletalMeshAsset();
    if(!Clip||!Skin||Clip->GetSkeleton()!=Skin->GetSkeleton())return;
    NegotiationPose=Index;NegotiationAge=0;CharacterVisual->PlayAnimation(Clip,Index==0);
}
void AAnanseInteractable::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);if(!bNegotiationPresentation)return;
    const auto* Player=Cast<AAnansePlayer>(UGameplayStatics::GetPlayerPawn(this,0));
    if(!Player||!Player->Mission)return;
    if(bNegotiationLedger && BrokenPromiseReaction && Player->Mission->ActiveDialogueId==TEXT("MSN_BROKEN_010") && LastReactionDialogue!=Player->Mission->ActiveDialogueId && Player->Mission->Cinematic && !Player->Mission->Cinematic->bActive)
    {
        LastReactionDialogue=Player->Mission->ActiveDialogueId;PlayNegotiation(11);
        Player->Mission->Cinematic->Start(Player->Mission,BrokenPromiseReaction,TEXT("aso_broken_promise_visual_only"),true);
    }
    const bool InShot=Player->Mission->Cinematic&&Player->Mission->Cinematic->IsNegotiationPresentation();
    const double ShotClock=InShot?Player->Mission->Cinematic->PlaybackSeconds():-1;
    if(bNegotiationLedger&&InShot&&(!bWasNegotiationShot||ShotClock<LastNegotiationPlayback-.001))LastNegotiationState=-1;
    bWasNegotiationShot=InShot;LastNegotiationPlayback=ShotClock;
    int32 State=NegotiationPoseFor(Player->Mission->State);
    // Owning evidence is not presenting it: wait attentively until the real
    // negotiation interaction starts its complete reach/hold/release sequence.
    if(bNegotiationLedger&&Player->Mission->State.bEvidence&&!Player->Mission->State.bPermit&&!InShot&&Player->Mission->State.Outcome.IsNone())State=3;
    if(Player->Mission->Cinematic&&Player->Mission->Cinematic->IsNegotiationPresentation()){const float T=Player->Mission->Cinematic->PlaybackSeconds();if(bNegotiationLedger)State=T<8.f?4:T<10.8f?3:T<14.4f?7:8;else{const int32 Beats[]={6,3,7,8,3};const int32 Beat=FMath::Clamp(int32(T/3.6),0,4);State=Beats[Beat];}}
    if(State!=LastNegotiationState){LastNegotiationState=State;PlayNegotiation(State);}
    NegotiationAge+=DeltaSeconds;NegotiationClock+=DeltaSeconds;
    if(NegotiationPose!=0&&NegotiationClips.IsValidIndex(NegotiationPose)&&NegotiationClips[NegotiationPose]&&NegotiationAge>=NegotiationClips[NegotiationPose]->GetPlayLength())PlayNegotiation(0);
    const float Blink=FMath::Clamp(1.f-FMath::Abs(FMath::Fmod(NegotiationClock,4.f)-3.85f)/.12f,0.f,1.f);
    CharacterVisual->SetMorphTarget(TEXT("Blink_L"),Blink);CharacterVisual->SetMorphTarget(TEXT("Blink_R"),Blink);
    const FName Expressions[]={TEXT("Concern"),TEXT("Suspicion"),TEXT("Disapproval"),TEXT("Consideration"),TEXT("Resolve"),TEXT("Agreement"),TEXT("Refusal"),TEXT("QuietWarning"),TEXT("ControlledAnger")};
    const int32 Active=NegotiationPose==11?(NegotiationAge<.8f?0:8):NegotiationPose==7?1:NegotiationPose==3?3:NegotiationPose==10?4:NegotiationPose==8?5:NegotiationPose==9?(NegotiationAge<1.f?1:6):NegotiationPose==4?(NegotiationAge<1.6f?3:NegotiationAge<3.6f?0:4):-1;
    for(int32 I=0;I<UE_ARRAY_COUNT(Expressions);++I)CharacterVisual->SetMorphTarget(Expressions[I],I==Active?.65f:0.f);
}
void AAnanseInteractable::UpdateNegotiationLedger()
{
 if(!bNegotiationLedger)return;
 auto* Instance=CharacterVisual->GetSingleNodeInstance();
 AnanseAsoLedger::Update(CharacterVisual,NegotiationLedgerVisual,NegotiationClips.IsValidIndex(NegotiationPose)?NegotiationClips[NegotiationPose].Get():nullptr,Instance?Instance->GetCurrentTime():-1.f,true);
}
void AAnanseInteractable::Configure(FName InAction,const FString& Text,FName InCharacterId)
{
    Action=InAction;CharacterId=InCharacterId;Label->SetText(FText::FromString(Text));
}
void AAnanseInteractable::Use(AAnansePlayer* Player)
{
    if(!Player || FVector::DistSquared(Player->GetActorLocation(),GetActorLocation())>FMath::Square(240.f))return;
    UAnanseMission* Mission=Player->Mission;
    if(bNegotiationPresentation&&Action==TEXT("negotiate")&&!Mission->State.bEvidence)PlayNegotiation(9);
    if((Action==TEXT("protect") || Action==TEXT("expose")) && !Mission->State.Outcome.IsNone())
    {
        Mission->Act(TEXT("consequence_response"));return;
    }
    if(Action==TEXT("ledger") && Mission->State.bProductionPursuit && Mission->State.bLedger && !Mission->State.bPursuitStarted)
    {
        if(Mission->State.CompletedPresentationEvents.Contains(TEXT("pursuit_intro_finished_or_skipped")))Mission->StartPursuit();
        else if(Mission->PursuitIntroSequence)Mission->BeginCinematic(Mission->PursuitIntroSequence,TEXT("pursuit_intro_finished_or_skipped"));
        return; // Interrupted presentation can resume without farming ledger/progression.
    }
    if((Action==TEXT("protect") || Action==TEXT("expose")) && Mission->State.bProductionPursuit && !Mission->State.bPursuitEscaped)
        if(!Mission->Act(TEXT("escape")))return;
    const bool Acted=Mission->Act(Action);
    if(Acted&&Action==TEXT("negotiate")&&bNegotiationPresentation&&NegotiationSequence)Mission->BeginCinematic(NegotiationSequence,TEXT("aso_negotiation_finished_or_skipped"));
    if(Acted && Action==TEXT("ledger") && Mission->State.bProductionPursuit)
    {
        if(auto* CastPlayer=Cast<AAnanseCastLabPlayer>(Player))CastPlayer->PresentLedgerInteraction();
        if(Mission->PursuitIntroSequence)Mission->BeginCinematic(Mission->PursuitIntroSequence,TEXT("pursuit_intro_finished_or_skipped"));
        else Mission->Message(TEXT("Ledger recovered. Pursuit intro sequence is unbound; production route is blocked, not auto-completed."));
    }
}
AAnanseWatchman::AAnanseWatchman()
{
    PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickInterval=0.2f;
    Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Watchman"));SetRootComponent(Mesh);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if(Cube.Succeeded())Mesh->SetStaticMesh(Cube.Object);Mesh->SetRelativeScale3D(FVector(0.6f,0.6f,1.8f));
}
void AAnanseWatchman::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    AAnansePlayer* Player=Cast<AAnansePlayer>(UGameplayStatics::GetPlayerPawn(this,0));
    if(!Player || !Player->Mission->State.Outcome.IsNone() || Player->Mission->MirrorActive() ||
       Player->Mission->VoiceActive() || Player->Mission->State.bPermit)return;
    // A local checkpoint test, not a complete perception/StateTree implementation.
    const FVector Offset=Player->GetActorLocation()-GetActorLocation();
    if(Offset.SizeSquared()>FMath::Square(380.f) || FVector::DotProduct(GetActorForwardVector(),Offset.GetSafeNormal())<0.25f)return;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(AnanseWatchmanSight),false,this);FHitResult Hit;
    const bool bHit=GetWorld()->LineTraceSingleByChannel(Hit,GetActorLocation()+FVector(0,0,50),Player->GetActorLocation(),ECC_Visibility,Params);
    if(!bHit || Hit.GetActor()==Player)Player->Mission->AddSuspicion(6.f*DeltaSeconds);
}
AAnanseGameMode::AAnanseGameMode(){DefaultPawnClass=AAnansePlayer::StaticClass();HUDClass=AAnanseHUD::StaticClass();}
void AAnanseHUD::DrawHUD()
{
    Super::DrawHUD();if(!Canvas||FParse::Param(FCommandLine::Get(),TEXT("AnanseMotionReviewClean")))return;
    AAnansePlayer* Player=Cast<AAnansePlayer>(GetOwningPawn());if(!Player)return;
    if(auto* Lab=Cast<AAnanseLabController>(GetOwningPlayerController()))
        DrawText(Lab->SelectionStatus,FLinearColor(.95f,.8f,.4f),25,Canvas->ClipY-38);
    if(Player->bEpisodeMenu)
    {
        DrawRect(FLinearColor(.015f,.025f,.025f,.97f),0,0,Canvas->ClipX,Canvas->ClipY);
        DrawText(TEXT("ANANSE / MARKET OF STOLEN NAMES"),FLinearColor(.9f,.75f,.43f),50,70,GEngine->GetSmallFont(),2.f);
        DrawText(TEXT("N  New Game    C  Continue    Escape  Resume    P  Pause"),FLinearColor::White,50,140);
        DrawText(FString::Printf(TEXT("Settings: - / = subtitle size (%.0f%%). Progress is saved with F5."),Player->SubtitleScale*100),FLinearColor::White,50,175);
        DrawText(TEXT("Development presentation: proxy characters, technical environments and missing final recordings."),FLinearColor(.9f,.75f,.43f),50,215);
        DrawText(Player->Mission->LatestMessage,FLinearColor::White,50,255);
        return;
    }
    if(Player->CharacterId==TEXT("ananse"))
    {
        DrawRect(FLinearColor(.02f,.03f,.02f,.82f),12,12,FMath::Max(250.f,Canvas->ClipX-24.f),96);
        DrawText(TEXT("ANANSE / CHARACTER LAB / ENGINEERING PROXY"),FLinearColor(.9f,.75f,.43f),24,20);
        DrawText(TEXT("F1-F4 clips | WASD move | mouse look | Space jump | V wireframe | P pause | Home/End select"),FLinearColor::White,24,45);
        DrawText(TEXT("No powers permitted. Live contact candidate; L toggles source-clip preview. PROXY art, controlled walking only."),FLinearColor::White,24,70);
        return;
    }
    if(Cast<AAnanseLeopardLabPlayer>(Player))
    {
        DrawRect(FLinearColor(.02f,.03f,.02f,.82f),12,12,FMath::Max(250.f,Canvas->ClipX-24.f),96);
        DrawText(TEXT("CHARACTER LAB / OSEBO LEOPARD / AUTHORED WORK IN PROGRESS"),FLinearColor(.9f,.75f,.43f),24,20);
        DrawText(TEXT("1-9 motion categories | 0 automatic | WASD move | mouse look | P pause | Home spider / End leopard"),FLinearColor::White,24,45);
        DrawText(TEXT("Lab only; live contacts active; final art pending. F10 inspect LODs. Campaign species unchanged."),FLinearColor::White,24,70);
        return;
    }
    if(auto* Story=Cast<AAnanseCastLabPlayer>(Player);Story && Story->bLabSelectionPawn)
    {
        DrawRect(FLinearColor(.02f,.03f,.02f,.82f),12,12,FMath::Max(250.f,Canvas->ClipX-24.f),96);
        DrawText(FString::Printf(TEXT("CHARACTER LAB / %s / AUTHORED WIP"),*Story->DesignId.ToString()),FLinearColor(.9f,.75f,.43f),24,20);
        DrawText(TEXT("PageDown next design | Home spider / End leopard | 1-9 clips / 0 auto | V wireframe | P pause | F6/F8 profile"),FLinearColor::White,24,45);
        DrawText(TEXT("Separate skeletal design. Creative/deformation/mobile approval pending; campaign identity unchanged."),FLinearColor::White,24,70);
        return;
    }
    if(Cast<AAnanseLabController>(GetOwningPlayerController()))
    {
        DrawRect(FLinearColor(.02f,.03f,.02f,.82f),12,12,FMath::Max(250.f,Canvas->ClipX-24.f),96);
        DrawText(TEXT("CHARACTER LAB / KWAKU PRIMITIVE DEVELOPMENT FIXTURE"),FLinearColor(.9f,.75f,.43f),24,20);
        DrawText(TEXT("WASD move | mouse look | Space jump | P pause | Home spider | End leopard | F6/F8 lab profile"),FLinearColor::White,24,45);
        DrawText(TEXT("Narrative powers disabled in this lab binding. This is not a qualified second skeletal family."),FLinearColor::White,24,70);
        return;
    }
    const FAnanseMissionState& S=Player->Mission->State;
    if(S.ProductionBeat==TEXT("episode_complete"))
    {
        DrawRect(FLinearColor(.015f,.025f,.025f,.92f),Canvas->ClipX*.2f,180,Canvas->ClipX*.6f,100);
        DrawText(TEXT("EPISODE RUNTIME COMPLETE / DEVELOPMENT PRESENTATION"),FLinearColor(.9f,.75f,.43f),Canvas->ClipX*.2f+16,195);
        DrawText(S.Outcome==TEXT("truth-exposed")?TEXT("Truth exposed. The witnesses now need protection."):TEXT("Witnesses protected. The public account remains unresolved."),FLinearColor::White,Canvas->ClipX*.2f+16,225);
        DrawText(TEXT("F5 saves completion. Escape opens Continue / New Game."),FLinearColor::White,Canvas->ClipX*.2f+16,250);
    }
    if(!Player->Mission->ActiveDialogueId.IsNone())
    {
        const UAnanseMission* M=Player->Mission;
        const float Scale=Player->SubtitleScale,Left=24.f,Height=80+60*Scale,Top=Canvas->ClipY-Height;
        DrawRect(FLinearColor(.01f,.02f,.02f,.92f),12,Top-10,Canvas->ClipX-24,Height-4);
        DrawText(M->ActiveDialogueSpeaker.ToUpper()+TEXT(" / DRAFT - RECORDING PENDING"),FLinearColor(.9f,.75f,.43f),Left,Top);
        // Word-wrap using measured font width; retain the full line rather than Left(135).
        TArray<FString> Words;M->ActiveDialogueText.ParseIntoArray(Words,TEXT(" "),true);
        FString Line;float Y=Top+24;
        for(const FString& Word:Words)
        {
            const FString Candidate=Line.IsEmpty()?Word:Line+TEXT(" ")+Word;
            float Width=0,TextHeight=0;GetTextSize(Candidate,Width,TextHeight,GEngine->GetSmallFont(),Scale);
            if(Width>Canvas->ClipX-60 && !Line.IsEmpty())
            {DrawText(Line,FLinearColor::White,Left,Y,GEngine->GetSmallFont(),Scale);Y+=20*Scale;Line=Word;}
            else Line=Candidate;
        }
        if(!Line.IsEmpty())DrawText(Line,FLinearColor::White,Left,Y,GEngine->GetSmallFont(),Scale);
        DrawText(Player->Mission->Cinematic&&Player->Mission->Cinematic->bActive?TEXT("P: pause / resume | Escape: skip"):TEXT("E at the speaker: next line. F5 saves consumed line IDs. Escape: pause/settings."),FLinearColor(.65f,.72f,.65f),Left,Canvas->ClipY-30);
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoReview"))&&Player->Mission->Cinematic&&Player->Mission->Cinematic->bActive)return;
    DrawRect(FLinearColor(0.02f,0.03f,0.02f,0.82f),12,12,FMath::Max(250.f,Canvas->ClipX-136.f),140);
    DrawText(TEXT("ANANSE / MARKET OF STOLEN NAMES / GREYBOX"),FLinearColor(0.9f,0.75f,0.43f),24,20,GEngine->GetSmallFont(),1.2f);
    DrawText(FString::Printf(TEXT("Thread: %d/3   Suspicion: %.0f/100   Route: %s"),S.Thread,S.Suspicion,*S.Route.ToString()),FLinearColor::White,24,48);
    DrawText(FString::Printf(TEXT("Evidence %s | Voice %s | Permit %s | Ledger %s"),S.bEvidence?TEXT("YES"):TEXT("NO"),S.bLearnedVoice?TEXT("YES"):TEXT("NO"),S.bPermit?TEXT("YES"):TEXT("NO"),S.bLedger?TEXT("YES"):TEXT("NO")),FLinearColor::White,24,70);
    // Temporary debug HUD; production subtitle layout and localisation use UMG/String Tables.
    DrawText(Player->Mission->LatestMessage.Left(135),FLinearColor(0.9f,0.9f,0.8f),24,94);
    DrawText(TEXT("WASD/stick: move | Mouse/right stick: look | E: interact | 1/2/3: powers | F5/F9: local save/load | R: restart"),FLinearColor(0.65f,0.72f,0.65f),24,122);
    const TCHAR* Labels[]={TEXT("1 WEB"),TEXT("2 VOICE"),TEXT("3 MIRROR"),TEXT("E USE"),TEXT("JUMP")};
    for(int32 I=0;I<5;I++){const float Y=24.f+I*56.f;DrawRect(FLinearColor(0.15f,0.23f,0.16f,0.9f),Canvas->ClipX-100.f,Y,88,46);DrawText(Labels[I],FLinearColor::White,Canvas->ClipX-94.f,Y+12.f);}
    if(!S.Outcome.IsNone())DrawText(FString::Printf(TEXT("OUTCOME: %s | Market trust %d | Court trust %d"),*S.Outcome.ToString(),S.MarketTrust,S.CourtTrust),FLinearColor(0.95f,0.8f,0.45f),24,Canvas->ClipY-80.f,GEngine->GetSmallFont(),1.6f);
}
