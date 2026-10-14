#pragma once
#include "CoreMinimal.h"
#include "Abilities/GameplayAbility.h"
#include "AnansePowers.generated.h"
/** Local prototype GAS dispatch. Resource/cooldown rules are centralized in Mission.
 * Production promotion must move resource/cooldown attributes into tested Gameplay Effects. */
UCLASS()
class ANANSE_API UAnanseWebStepAbility : public UGameplayAbility
{
    GENERATED_BODY()
public:
    UAnanseWebStepAbility();
    virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle,const FGameplayAbilityActorInfo* ActorInfo,const FGameplayAbilityActivationInfo ActivationInfo,const FGameplayEventData* TriggerEventData) override;
};
UCLASS()
class ANANSE_API UAnanseVoiceAbility : public UGameplayAbility
{
    GENERATED_BODY()
public:
    UAnanseVoiceAbility();
    virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle,const FGameplayAbilityActorInfo* ActorInfo,const FGameplayAbilityActivationInfo ActivationInfo,const FGameplayEventData* TriggerEventData) override;
};
UCLASS()
class ANANSE_API UAnanseMirrorAbility : public UGameplayAbility
{
    GENERATED_BODY()
public:
    UAnanseMirrorAbility();
    virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle,const FGameplayAbilityActorInfo* ActorInfo,const FGameplayAbilityActivationInfo ActivationInfo,const FGameplayEventData* TriggerEventData) override;
};
