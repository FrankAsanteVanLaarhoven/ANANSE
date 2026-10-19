#include "AnanseDialogue.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

bool AnanseDialogue::Parse(const FString& Json,TMap<FName,FAnanseDialogueLine>& Lines,FString& Error)
{
    Lines.Empty();Error.Empty();
    TSharedPtr<FJsonObject> Root;const TArray<TSharedPtr<FJsonValue>>* Entries=nullptr;
    double Version=0;FString Locale;
    if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json),Root) || !Root.IsValid() ||
       !Root->TryGetNumberField(TEXT("schema_version"),Version) || Version!=1 ||
       !Root->TryGetStringField(TEXT("locale"),Locale) || Locale!=TEXT("en") ||
       !Root->TryGetArrayField(TEXT("lines"),Entries) || Entries->IsEmpty() || Entries->Num()>256)
    {Error=TEXT("Missing or unsupported authored dialogue document.");return false;}
    TMap<FName,FAnanseDialogueLine> Candidate;
    for(const auto& Entry:*Entries)
    {
        const TSharedPtr<FJsonObject>* Object=nullptr;FAnanseDialogueLine Line;
        if(!Entry->TryGetObject(Object) || !Object ||
           !(*Object)->TryGetStringField(TEXT("id"),Line.Id) ||
           !(*Object)->TryGetStringField(TEXT("speaker"),Line.Speaker) ||
           !(*Object)->TryGetStringField(TEXT("text"),Line.Text) ||
           !Line.Id.StartsWith(TEXT("MSN_")) || Line.Id.Len()>64 ||
           Line.Speaker.TrimStartAndEnd().IsEmpty() || Line.Speaker.Len()>64 ||
           Line.Text.TrimStartAndEnd().IsEmpty() || Line.Text.Len()>1024 ||
           Candidate.Contains(FName(*Line.Id)))
        {Error=TEXT("Invalid or duplicate dialogue line; the document was rejected.");return false;}
        Candidate.Add(FName(*Line.Id),MoveTemp(Line));
    }
    Lines=MoveTemp(Candidate);return true;
}
bool AnanseDialogue::Load(TMap<FName,FAnanseDialogueLine>& Lines,FString& Error)
{
    FString Json;
    if(!FFileHelper::LoadFileToString(Json,*(FPaths::ProjectContentDir()/TEXT("Data/market-dialogue.en.json"))))
    {Lines.Empty();Error=TEXT("Authored dialogue is absent from cooked Data; progression remains blocked.");return false;}
    return Parse(Json,Lines,Error);
}
