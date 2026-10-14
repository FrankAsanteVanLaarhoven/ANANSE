#include "AnanseWorld.h"
#include "AnansePlayer.h"
#include "AnanseMission.h"
#include "AnanseCatalogue.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"

AAnanseInteractable::AAnanseInteractable()
{
    PrimaryActorTick.bCanEverTick=false;
    Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Marker"));SetRootComponent(Mesh);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if(Cube.Succeeded())Mesh->SetStaticMesh(Cube.Object);
    Mesh->SetRelativeScale3D(FVector(0.55f,0.55f,1.f));
    Label=CreateDefaultSubobject<UTextRenderComponent>(TEXT("Label"));Label->SetupAttachment(Mesh);
    Label->SetRelativeLocation(FVector(0,0,95));Label->SetWorldSize(22);Label->SetHorizontalAlignment(EHTA_Center);
    Label->SetText(FText::FromString(TEXT("Interact")));Label->SetTextRenderColor(FColor(235,215,150));
}
void AAnanseInteractable::BeginPlay()
{
    Super::BeginPlay();
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
void AAnanseInteractable::Configure(FName InAction,const FString& Text,FName InCharacterId)
{
    Action=InAction;CharacterId=InCharacterId;Label->SetText(FText::FromString(Text));
}
void AAnanseInteractable::Use(AAnansePlayer* Player)
{
    if(!Player || FVector::DistSquared(Player->GetActorLocation(),GetActorLocation())>FMath::Square(240.f))return;
    Player->Mission->Act(Action);
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
    Super::DrawHUD();if(!Canvas)return;
    AAnansePlayer* Player=Cast<AAnansePlayer>(GetOwningPawn());if(!Player)return;
    const FAnanseMissionState& S=Player->Mission->State;
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
