#include "AnanseCatalogue.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

void UAnanseCatalogue::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    FString Text;
    const FString Path = FPaths::ProjectContentDir()/TEXT("Data/catalogue.json");
    TSharedPtr<FJsonObject> Root;
    if (!FFileHelper::LoadFileToString(Text,*Path) || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp,Error,TEXT("ANANSE: missing/invalid catalogue at %s. Export an immutable prototype publication before cooking."),*Path);
        return;
    }
    const TSharedPtr<FJsonObject>* Payload = nullptr;
    const TSharedPtr<FJsonObject>* Entities = nullptr;
    if (!Root->TryGetStringField(TEXT("sha256"),ContentHash) || ContentHash.Len()!=64 ||
        !Root->TryGetObjectField(TEXT("payload"),Payload) || !(*Payload)->TryGetObjectField(TEXT("entities"),Entities)) return;
    FString Channel;
    double Schema=0;
    if (!(*Payload)->TryGetNumberField(TEXT("schema_version"),Schema) || Schema!=1 ||
        !(*Payload)->TryGetStringField(TEXT("channel"),Channel) || Channel!=TEXT("prototype")) return;
    // Hash verification is enforced in the build script. This reader is NOT a signature verifier.
    TMap<FString,FString> MeshPaths;
    const TArray<TSharedPtr<FJsonValue>>* Assets=nullptr;
    if ((*Entities)->TryGetArrayField(TEXT("assets"),Assets))
    {
        for (const TSharedPtr<FJsonValue>& Value:*Assets)
        {
            const TSharedPtr<FJsonObject> Item=Value->AsObject();
            if (!Item.IsValid()) continue;
            const TSharedPtr<FJsonObject>* Data=nullptr;FString Id,Category,PathValue;
            if (Item->TryGetStringField(TEXT("id"),Id) && Item->TryGetObjectField(TEXT("data"),Data) &&
                (*Data)->TryGetStringField(TEXT("category"),Category) && Category==TEXT("skeletal-mesh") &&
                (*Data)->TryGetStringField(TEXT("unreal_path"),PathValue) && PathValue.StartsWith(TEXT("/Game/"))) MeshPaths.Add(Id,PathValue);
        }
    }
    const TArray<TSharedPtr<FJsonValue>>* List=nullptr;
    if (!(*Entities)->TryGetArrayField(TEXT("characters"),List)) return;
    for (const TSharedPtr<FJsonValue>& Value:*List)
    {
        const TSharedPtr<FJsonObject> Item=Value->AsObject();
        if (!Item.IsValid()) continue;
        const TSharedPtr<FJsonObject>* Data=nullptr;
        FString Id,Name;
        if (!Item->TryGetStringField(TEXT("id"),Id) || !Item->TryGetObjectField(TEXT("data"),Data) || !(*Data)->TryGetStringField(TEXT("name"),Name)) continue;
        FAnanseCharacterSpec Spec;Spec.Id=FName(*Id);Spec.DisplayName=Name;
        const TArray<TSharedPtr<FJsonValue>>* PowerList=nullptr;
        if((*Data)->TryGetArrayField(TEXT("powers"),PowerList))for(const auto& Power:*PowerList){FString NameValue;if(Power->TryGetString(NameValue))Spec.PowerIds.Add(FName(*NameValue));}
        const TArray<TSharedPtr<FJsonValue>>* Variants=nullptr;
        if (!(*Data)->TryGetArrayField(TEXT("variants"),Variants)) continue;
        for (const TSharedPtr<FJsonValue>& VariantValue:*Variants)
        {
            const TSharedPtr<FJsonObject> V=VariantValue->AsObject();if (!V.IsValid()) continue;
            FAnanseAppearance Appearance;FString S;double Scale=1;
            if (V->TryGetStringField(TEXT("id"),S)) Appearance.Id=FName(*S);
            if (V->TryGetStringField(TEXT("cloth_colour"),S)) Appearance.Cloth=FLinearColor::FromSRGBColor(FColor::FromHex(S));
            if (V->TryGetStringField(TEXT("accent_colour"),S)) Appearance.Accent=FLinearColor::FromSRGBColor(FColor::FromHex(S));
            V->TryGetNumberField(TEXT("body_scale"),Scale);Appearance.VisualScale=FMath::Clamp(static_cast<float>(Scale),0.8f,1.2f);
            if (V->TryGetStringField(TEXT("body_asset_id"),S)) if (const FString* P=MeshPaths.Find(S)) Appearance.BodyMesh=FSoftObjectPath(*P);
            const TSharedPtr<FJsonObject>* Morphs=nullptr;
            if (V->TryGetObjectField(TEXT("morph_targets"),Morphs))
                for (const auto& Pair:(*Morphs)->Values)
                { double Weight=0;if(Pair.Value->TryGetNumber(Weight)) Appearance.MorphTargets.Add(FName(*Pair.Key),FMath::Clamp(static_cast<float>(Weight),0.f,1.f)); }
            Spec.Variants.Add(Appearance);
        }
        if (!Spec.Variants.IsEmpty()) Characters.Add(Spec.Id,Spec);
    }
    bLoaded=Characters.Num()>0;
    UE_LOG(LogTemp,Display,TEXT("ANANSE prototype catalogue: %d characters; hash %s; requires cook/device qualification."),Characters.Num(),*ContentHash);
}
