#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "AnanseCatalogue.generated.h"

USTRUCT(BlueprintType)
struct FAnanseAppearance
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FName Id = TEXT("base");
    UPROPERTY(BlueprintReadOnly) FLinearColor Cloth = FLinearColor(0.42f,0.2f,0.06f);
    UPROPERTY(BlueprintReadOnly) FLinearColor Accent = FLinearColor(0.7f,0.5f,0.18f);
    UPROPERTY(BlueprintReadOnly) float VisualScale = 1.f;
    UPROPERTY(BlueprintReadOnly) FSoftObjectPath BodyMesh;
    UPROPERTY(BlueprintReadOnly) TMap<FName,float> MorphTargets;
};
USTRUCT(BlueprintType)
struct FAnanseCharacterSpec
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FName Id;
    UPROPERTY(BlueprintReadOnly) FString DisplayName;
    UPROPERTY(BlueprintReadOnly) TArray<FName> PowerIds;
    UPROPERTY(BlueprintReadOnly) TArray<FAnanseAppearance> Variants;
};
/** Reads only the build-time catalogue. No studio token, HTTP client or runtime code download. */
UCLASS()
class ANANSE_API UAnanseCatalogue : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    UPROPERTY(BlueprintReadOnly) TMap<FName,FAnanseCharacterSpec> Characters;
    UPROPERTY(BlueprintReadOnly) FString ContentHash;
    UPROPERTY(BlueprintReadOnly) bool bLoaded = false;
    // Visual publications do not replace campaign character identities or collision.
    UPROPERTY(BlueprintReadOnly) FLinearColor LeopardCape=FLinearColor::FromSRGBColor(FColor(117,36,51));
    UPROPERTY(BlueprintReadOnly) FLinearColor LeopardAccent=FLinearColor::FromSRGBColor(FColor(194,152,72));
    UPROPERTY(BlueprintReadOnly) int32 LeopardVisualRevision=0;
    UPROPERTY(BlueprintReadOnly) bool bLeopardVisualPublished=false;
    UPROPERTY(BlueprintReadOnly) int32 AsoVisualRevision=1;
    UPROPERTY(BlueprintReadOnly) bool bAsoVisualPublished=false;
    UPROPERTY(BlueprintReadOnly) int32 KwakuVisualRevision=1;
    UPROPERTY(BlueprintReadOnly) bool bKwakuVisualPublished=false;
    static int32 KwakuBindingRevision(const FString& Source,const FString& Mesh,const FString& Definition,const FString& Family);
    const FAnanseCharacterSpec* Find(FName Id) const { return Characters.Find(Id); }
};
