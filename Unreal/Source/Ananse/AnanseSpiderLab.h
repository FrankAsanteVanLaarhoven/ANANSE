#pragma once
#include "CoreMinimal.h"
#include "AnansePlayer.h"
#include "GameFramework/GameModeBase.h"
#include "AnanseSpiderLab.generated.h"
class UAnimSequence;class UAnanseGroundContact;class UMaterialInstanceDynamic;
/** Imported engineering proxy only; campaign identity and production assets are separate. */
UCLASS()
class ANANSE_API AAnanseSpiderLabPlayer : public AAnansePlayer
{
 GENERATED_BODY()
public:
 AAnanseSpiderLabPlayer();
 virtual void BeginPlay() override;
 virtual void ResetTransientMotion() override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UAnanseGroundContact> GroundContact;
 virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
 UFUNCTION(BlueprintCallable) void PlayProxyClip(int32 Index);
 UFUNCTION(BlueprintPure) TArray<FName> GetImportedBoneNames() const;
 UPROPERTY(BlueprintReadOnly) int32 ActiveProxyClip=0;
 UPROPERTY(BlueprintReadOnly) TObjectPtr<UMaterialInstanceDynamic> PublishedClothMaterial;
 UPROPERTY(BlueprintReadOnly) int32 PublishedClothSlot=INDEX_NONE;
 UPROPERTY() TArray<TObjectPtr<UAnimSequence>> ProxyClips;
private:
 void ToggleContacts();
 void Idle(){PlayProxyClip(0);}void LimbROM(){PlayProxyClip(1);}void Weave(){PlayProxyClip(2);}void Crawl(){PlayProxyClip(3);}
};
UCLASS()
class ANANSE_API AAnanseCharacterLabMode : public AGameModeBase
{
 GENERATED_BODY()
public:AAnanseCharacterLabMode();
};
