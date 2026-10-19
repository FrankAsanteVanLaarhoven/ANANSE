#pragma once
#include "CoreMinimal.h"
class AAnansePlayer;
class FJsonObject;
void TickPursuitVerification(AAnansePlayer* Player,float DeltaSeconds,double RequiredSeconds,bool& Finished,FString& Error,TSharedPtr<FJsonObject> Report,FString Out,FString Slot,bool Reload,bool EpisodeReload=false);
bool IsExpectedEpisodeTravelPawn(AAnansePlayer* Player);
