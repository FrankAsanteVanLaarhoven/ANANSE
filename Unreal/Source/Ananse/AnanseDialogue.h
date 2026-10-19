#pragma once
#include "CoreMinimal.h"

// Authored English draft, independent of recording duration and gameplay authority.
struct FAnanseDialogueLine
{
    FString Id;
    FString Speaker;
    FString Text;
};
namespace AnanseDialogue
{
    bool Parse(const FString& Json,TMap<FName,FAnanseDialogueLine>& Lines,FString& Error);
    bool Load(TMap<FName,FAnanseDialogueLine>& Lines,FString& Error);
}
