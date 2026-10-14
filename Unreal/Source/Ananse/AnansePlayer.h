#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "AbilitySystemInterface.h"
#include "InputActionValue.h"
#include "AnansePlayer.generated.h"
class UAbilitySystemComponent;class UAnanseMission;class UInputMappingContext;class UInputAction;class USpringArmComponent;class UCameraComponent;class UStaticMeshComponent;
UCLASS()
class ANANSE_API AAnansePlayer : public ACharacter,public IAbilitySystemInterface
{
    GENERATED_BODY()
public:
    AAnansePlayer();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UAnanseMission> Mission;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UAbilitySystemComponent> Abilities;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> CameraBoom;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> Camera;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Body;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Head;
    UFUNCTION(BlueprintCallable) void Interact();
    UFUNCTION(BlueprintCallable) void WebStep();
    UFUNCTION(BlueprintCallable) void BorrowVoice();
    UFUNCTION(BlueprintCallable) void TrickMirror();
    UFUNCTION(BlueprintCallable) bool FindWebAnchor(FVector& OutLocation) const;
    UFUNCTION(BlueprintCallable) bool StartWebFlight(const FVector& Destination);
    bool CanWebFlight(const FVector& Destination) const;
    bool IsWebFlying() const { return bWebFlying; }
    void SpawnMirror();
private:
    UPROPERTY() TObjectPtr<UInputMappingContext> Mapping;
    UPROPERTY() TObjectPtr<UInputAction> MoveAction;
    UPROPERTY() TObjectPtr<UInputAction> LookAction;
    UPROPERTY() TArray<TObjectPtr<UInputAction>> ButtonActions;
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
    void StartJump();
    void Save();void Load();void Restart();
    void TouchPressed(ETouchIndex::Type Finger,FVector Location);
    FVector WebStart,WebEnd;
    float WebElapsed=0.f;
    bool bWebFlying=false;
};
