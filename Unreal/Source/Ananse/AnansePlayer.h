#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "AbilitySystemInterface.h"
#include "InputActionValue.h"
#include "AnansePlayer.generated.h"
class UAnanseCatalogue;class UAbilitySystemComponent;class UAnanseMission;class UInputMappingContext;class UInputAction;class USpringArmComponent;class UCameraComponent;class UStaticMeshComponent;
UCLASS()
class ANANSE_API AAnansePlayer : public ACharacter,public IAbilitySystemInterface
{
    GENERATED_BODY()
public:
    AAnansePlayer();
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) FName CharacterId=TEXT("kwaku");
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual void UnPossessed() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    // Set before BeginPlay by the lab transaction. Never changes campaign records.
    UPROPERTY(Transient) bool bLabSelectionPawn=false;
    UInputMappingContext* GetOwnedInputMapping()const{return Mapping;}
    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UAnanseMission> Mission;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UAbilitySystemComponent> Abilities;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> CameraBoom;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> Camera;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Body;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Head;
    UFUNCTION(BlueprintCallable) void Interact();
    UPROPERTY(BlueprintReadOnly) bool bEpisodeMenu=false;
    UPROPERTY(BlueprintReadOnly) float SubtitleScale=1.f;
    UFUNCTION(BlueprintCallable) void WebStep();
    UFUNCTION(BlueprintCallable) void BorrowVoice();
    UFUNCTION(BlueprintCallable) void TrickMirror();
    UFUNCTION(BlueprintCallable) bool FindWebAnchor(FVector& OutLocation) const;
    UFUNCTION(BlueprintCallable) bool StartWebFlight(const FVector& Destination);
    bool CanWebFlight(const FVector& Destination) const;
    UFUNCTION(BlueprintPure) bool IsWebFlying() const { return bWebFlying; }
    UFUNCTION(BlueprintPure) UAnanseCatalogue* GetCatalogue() const;
    UFUNCTION(BlueprintPure) FString GetNativeWorldType() const;
    UFUNCTION(BlueprintPure) bool IsNativePlayReady() const;
    void SpawnMirror();
    UPROPERTY(Transient) TObjectPtr<AActor> MirrorActor;
    virtual void ResetTransientMotion();
private:
    void ReleaseInputMapping();
    TWeakObjectPtr<ULocalPlayer> MappingOwner;
    UPROPERTY() TObjectPtr<UInputMappingContext> Mapping;
    UPROPERTY() TObjectPtr<UInputAction> MoveAction;
    UPROPERTY() TObjectPtr<UInputAction> LookAction;
    UPROPERTY() TArray<TObjectPtr<UInputAction>> ButtonActions;
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
    void StartJump();
    void Save();void Load();void RestartRun();void SkipPresentation();
    void NewEpisode();void ContinueEpisode();void LargerSubtitles();void SmallerSubtitles();
    void SetEpisodeMenu(bool Show);void SetSubtitleScale(float Scale);
    void ToggleEpisodePause();
    bool bOpeningPending=false;
    void TouchPressed(ETouchIndex::Type Finger,FVector Location);
    FVector WebStart,WebEnd;
    float WebElapsed=0.f;
    bool bWebFlying=false;
};
