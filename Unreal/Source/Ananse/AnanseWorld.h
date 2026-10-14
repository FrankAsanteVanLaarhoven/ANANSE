#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "AnanseWorld.generated.h"
class UStaticMeshComponent;class UTextRenderComponent;class AAnansePlayer;
UCLASS()
class ANANSE_API AAnanseInteractable : public AActor
{
    GENERATED_BODY()
public:
    AAnanseInteractable();
    virtual void BeginPlay() override;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UTextRenderComponent> Label;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) FName Action=TEXT("evidence");
    UPROPERTY(EditAnywhere,BlueprintReadWrite) FName CharacterId;
    void Configure(FName InAction,const FString& Text,FName InCharacterId=NAME_None);
    void Use(AAnansePlayer* Player);
};
UCLASS()
class ANANSE_API AAnanseWatchman : public AActor
{
    GENERATED_BODY()
public:
    AAnanseWatchman();
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Mesh;
};
UCLASS()
class ANANSE_API AAnanseGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AAnanseGameMode();
};
UCLASS()
class ANANSE_API AAnanseHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
