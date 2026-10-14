#include "AnansePowers.h"
#include "AnansePlayer.h"
#include "AnanseMission.h"
UAnanseWebStepAbility::UAnanseWebStepAbility(){InstancingPolicy=EGameplayAbilityInstancingPolicy::InstancedPerActor;NetExecutionPolicy=EGameplayAbilityNetExecutionPolicy::LocalOnly;}
UAnanseVoiceAbility::UAnanseVoiceAbility(){InstancingPolicy=EGameplayAbilityInstancingPolicy::InstancedPerActor;NetExecutionPolicy=EGameplayAbilityNetExecutionPolicy::LocalOnly;}
UAnanseMirrorAbility::UAnanseMirrorAbility(){InstancingPolicy=EGameplayAbilityInstancingPolicy::InstancedPerActor;NetExecutionPolicy=EGameplayAbilityNetExecutionPolicy::LocalOnly;}
void UAnanseWebStepAbility::ActivateAbility(const FGameplayAbilitySpecHandle H,const FGameplayAbilityActorInfo* Info,const FGameplayAbilityActivationInfo A,const FGameplayEventData* Event)
{
    bool bSuccess=false;
    if(AAnansePlayer* P=Cast<AAnansePlayer>(Info->AvatarActor.Get()))
    {
        FVector Target;
        if(P->FindWebAnchor(Target) && P->CanWebFlight(Target))
        { if(P->Mission->CommitPower(TEXT("web-step"))) bSuccess=P->StartWebFlight(Target); }
        else P->Mission->Message(TEXT("No clear Web Step anchor within 800 cm. Face the lit rooftop marker; blocked routes cannot be traversed."));
    }
    EndAbility(H,Info,A,false,!bSuccess);
}
void UAnanseVoiceAbility::ActivateAbility(const FGameplayAbilitySpecHandle H,const FGameplayAbilityActorInfo* Info,const FGameplayAbilityActivationInfo A,const FGameplayEventData* Event)
{
    bool bSuccess=false;if(AAnansePlayer* P=Cast<AAnansePlayer>(Info->AvatarActor.Get()))bSuccess=P->Mission->CommitPower(TEXT("borrowed-voice"));
    EndAbility(H,Info,A,false,!bSuccess);
}
void UAnanseMirrorAbility::ActivateAbility(const FGameplayAbilitySpecHandle H,const FGameplayAbilityActorInfo* Info,const FGameplayAbilityActivationInfo A,const FGameplayEventData* Event)
{
    bool bSuccess=false;if(AAnansePlayer* P=Cast<AAnansePlayer>(Info->AvatarActor.Get()))if(P->Mission->CommitPower(TEXT("trick-mirror"))){P->SpawnMirror();bSuccess=true;}
    EndAbility(H,Info,A,false,!bSuccess);
}
