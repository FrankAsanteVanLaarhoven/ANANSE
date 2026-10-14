#pragma once
#include "CoreMinimal.h"
class AAnansePlayer;
void TickAnanseRuntimeVerification(AAnansePlayer* Player,float DeltaSeconds);
void NotifyAnanseVerificationAction(AAnansePlayer* Player,FName Action);
FString AnanseVerificationSaveSlot();
