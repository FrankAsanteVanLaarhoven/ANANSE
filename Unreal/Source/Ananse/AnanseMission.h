#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameFramework/SaveGame.h"
#include "AnanseMission.generated.h"

USTRUCT(BlueprintType)
struct FAnanseMissionState
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bEvidence=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bLearnedVoice=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bPermit=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bArchive=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bLedger=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bOnRooftop=false;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 Thread=3;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float Suspicion=0.f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 MarketTrust=0;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 CourtTrust=0;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FName Route;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FName Outcome;
};
UCLASS()
class ANANSE_API UAnanseSave : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY(SaveGame) int32 SchemaVersion=1;
    UPROPERTY(SaveGame) FString ContentHash;
    UPROPERTY(SaveGame) FAnanseMissionState State;
    UPROPERTY(SaveGame) FVector Position=FVector::ZeroVector;
    UPROPERTY(SaveGame) FRotator Rotation=FRotator::ZeroRotator;
    UPROPERTY(SaveGame) float VoiceRemaining=0;
    UPROPERTY(SaveGame) float MirrorRemaining=0;
    UPROPERTY(SaveGame) TMap<FName,float> CooldownRemaining;
};
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FAnanseMissionChanged);
UCLASS(ClassGroup=(Ananse),meta=(BlueprintSpawnableComponent))
class ANANSE_API UAnanseMission : public UActorComponent
{
    GENERATED_BODY()
public:
    UAnanseMission();
    UPROPERTY(BlueprintReadOnly) FAnanseMissionState State;
    UPROPERTY(BlueprintReadOnly) FString LatestMessage=TEXT("Find the altered edict. Movement: WASD / stick. Interact: E. Powers: 1, 2, 3.");
    UPROPERTY(BlueprintAssignable) FAnanseMissionChanged Changed;
    UPROPERTY(BlueprintReadOnly) float VoiceUntil=-1.f;
    UPROPERTY(BlueprintReadOnly) float MirrorUntil=-1.f;
    UPROPERTY(BlueprintReadOnly) TMap<FName,float> Cooldowns;
    UFUNCTION(BlueprintCallable) bool Act(FName Action);
    UFUNCTION(BlueprintCallable) bool CommitPower(FName Power);
    UFUNCTION(BlueprintCallable) void AddSuspicion(float Amount);
    UFUNCTION(BlueprintCallable) void Message(const FString& Text);
    UFUNCTION(BlueprintCallable) bool SaveLocal(const FString& SlotName=TEXT("AnansePrototype"));
    UFUNCTION(BlueprintCallable) bool LoadLocal(const FString& SlotName=TEXT("AnansePrototype"));
    float Clock() const;
    UFUNCTION(BlueprintPure) bool VoiceActive() const { return Clock()<=VoiceUntil; }
    UFUNCTION(BlueprintPure) bool MirrorActive() const { return Clock()<=MirrorUntil; }
};
