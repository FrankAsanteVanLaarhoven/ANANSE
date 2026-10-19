#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "AnansePursuit.generated.h"
class UAnanseMission;class UAnimSequence;
class UStaticMeshComponent;
/** Bounded local pursuit fixture; primitive representation is explicitly not final Osebo art. */
UCLASS()
class ANANSE_API AAnansePursuit : public ACharacter
{
    GENERATED_BODY()
public:
    AAnansePursuit();
    virtual void Tick(float DeltaSeconds) override;
    void Start(UAnanseMission* Mission,ACharacter* Target);
    void Halt();
    bool CanEscape() const;
    UFUNCTION(BlueprintPure) bool HasVisibleTarget() const {return bVisible;}
    UPROPERTY(BlueprintReadOnly) FVector LastKnownLocation;
    UPROPERTY(BlueprintReadOnly) FName Behaviour=TEXT("inactive");
    UPROPERTY(BlueprintReadOnly) bool bNavigationAvailable=false;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> ProxyBody;
    UPROPERTY(EditAnywhere) FVector EscapePoint=FVector(1300,350,96);
    static bool EscapeConditions(float ActiveSeconds,float DistanceToGate,float DistanceToPursuer,bool bCaptured);
private:
    UPROPERTY(Transient) TArray<TObjectPtr<UAnimSequence>> PresentationClips;
    TWeakObjectPtr<UAnanseMission> Mission;
    TWeakObjectPtr<ACharacter> Target;
    bool bActive=false,bVisible=false;
    float ActiveSeconds=0,LostSightSeconds=0,CaptureExposure=0;
    float ProgressSeconds=0,DetourSeconds=0;
    FVector ProgressPosition=FVector::ZeroVector,DetourDirection=FVector::ZeroVector;
    int32 DetourSide=1;
};
