#include "AnanseCatalogue.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

int32 UAnanseCatalogue::KwakuBindingRevision(const FString& Source,const FString& Mesh,const FString& Definition,const FString& Family)
{
    if(Family!=TEXT("Kwaku-independent-v001"))return 0;
    if(Source==TEXT("authored-v002")&&Mesh==TEXT("/Game/Ananse/Characters/Kwaku/Story_v001/Kwaku.Kwaku")&&Definition==TEXT("/Game/Ananse/Characters/Kwaku/Story_v001/DA_Kwaku.DA_Kwaku"))return 1;
    if(Source==TEXT("authored-v006")&&Mesh==TEXT("/Game/Ananse/Characters/Kwaku/Refined_v001/Kwaku.Kwaku")&&Definition==TEXT("/Game/Ananse/Characters/Kwaku/Refined_v001/DA_Kwaku.DA_Kwaku"))return 2;
    if(Source==TEXT("authored-v008")&&Mesh==TEXT("/Game/Ananse/Characters/Kwaku/Refined_v002/Kwaku.Kwaku")&&Definition==TEXT("/Game/Ananse/Characters/Kwaku/Refined_v002/DA_Kwaku.DA_Kwaku"))return 3;
    if(Source==TEXT("authored-v015")&&Mesh==TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v003/Kwaku.Kwaku")&&Definition==TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v003/DA_Kwaku.DA_Kwaku"))return 4;
    if(Source==TEXT("authored-v016")&&Mesh==TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v005/Kwaku.Kwaku")&&Definition==TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v005/DA_Kwaku.DA_Kwaku"))return 5;
    return 0;
}

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
                (*Data)->TryGetStringField(TEXT("unreal_path"),PathValue) && PathValue.StartsWith(TEXT("/Game/")))
            {
                MeshPaths.Add(Id,PathValue);
                const TSharedPtr<FJsonObject>* Visual=nullptr;
                if((*Data)->TryGetObjectField(TEXT("visual_design"),Visual))
                {
                    FString PublishedDesign;(*Visual)->TryGetStringField(TEXT("design_id"),PublishedDesign);
                    if(PublishedDesign==TEXT("aso-yaa-human-v1"))
                    {
                        FString Source,Definition,Family;(*Visual)->TryGetStringField(TEXT("source_revision"),Source);(*Visual)->TryGetStringField(TEXT("definition_path"),Definition);(*Visual)->TryGetStringField(TEXT("skeleton_key"),Family);
                        const FString Base=Source==TEXT("authored-v007")?TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v002/"):Source==TEXT("authored-v004")?TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v001/"):TEXT("/Game/Ananse/Characters/AsoYaa/Story_v001/");
                        if(Id!=TEXT("aso-yaa-human-v1-design")||bAsoVisualPublished||Family!=TEXT("AsoYaa-independent-v001")||(Source!=TEXT("authored-v007")&&Source!=TEXT("authored-v004")&&Source!=TEXT("authored-v001"))||PathValue!=Base+TEXT("AsoYaa.AsoYaa")||Definition!=Base+TEXT("DA_AsoYaa.DA_AsoYaa")){UE_LOG(LogTemp,Error,TEXT("ANANSE rejected incompatible Aso Yaa publication."));return;}
                        AsoVisualRevision=Source==TEXT("authored-v007")?3:Source==TEXT("authored-v004")?2:1;bAsoVisualPublished=true;continue;
                    }
                    if(PublishedDesign==TEXT("kwaku-human-v1"))
                    {
                        FString Source,Definition,Family;(*Visual)->TryGetStringField(TEXT("source_revision"),Source);(*Visual)->TryGetStringField(TEXT("definition_path"),Definition);(*Visual)->TryGetStringField(TEXT("skeleton_key"),Family);
                        const int32 Binding=KwakuBindingRevision(Source,PathValue,Definition,Family);
                        if(Id!=TEXT("kwaku-human-v1-design")||Binding==0||bKwakuVisualPublished){UE_LOG(LogTemp,Error,TEXT("ANANSE rejected an incompatible or duplicate Kwaku visual publication."));return;}
                        KwakuVisualRevision=Binding;bKwakuVisualPublished=true;continue;
                    }
                    if(PublishedDesign!=TEXT("osebo-leopard-v1"))continue;
                    FString Design,Key,Definition,Colour,Accent;double Revision=0;
                    const bool Match=PathValue==TEXT("/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard") &&
                      (*Visual)->TryGetStringField(TEXT("design_id"),Design) && Design==TEXT("osebo-leopard-v1") &&
                      (*Visual)->TryGetStringField(TEXT("skeleton_key"),Key) && Key==TEXT("osebo-feline-biped-v001") &&
                      (*Visual)->TryGetStringField(TEXT("definition_path"),Definition) && Definition==TEXT("/Game/Ananse/Characters/OseboLeopard/Data/DA_OseboLeopard.DA_OseboLeopard") &&
                      (*Visual)->TryGetStringField(TEXT("cape_colour"),Colour) && (*Visual)->TryGetStringField(TEXT("accent_colour"),Accent) &&
                      Item->TryGetNumberField(TEXT("version"),Revision) && Revision>=1;
                    auto Hex=[](const FString& C){if(C.Len()!=7||C[0]!='#')return false;for(int32 I=1;I<7;++I)if(!FChar::IsHexDigit(C[I]))return false;return true;};
                    if(Match && Hex(Colour) && Hex(Accent) && !bLeopardVisualPublished)
                    {LeopardCape=FLinearColor::FromSRGBColor(FColor::FromHex(Colour));LeopardAccent=FLinearColor::FromSRGBColor(FColor::FromHex(Accent));LeopardVisualRevision=int32(Revision);bLeopardVisualPublished=true;}
                    else UE_LOG(LogTemp,Warning,TEXT("ANANSE rejected incompatible or duplicate leopard visual publication; character identity unchanged."));
                }
            }
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
