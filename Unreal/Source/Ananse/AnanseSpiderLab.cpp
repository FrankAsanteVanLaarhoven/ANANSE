#include "AnanseSpiderLab.h"
#include "AnanseLabSelection.h"
#include "AnanseGroundContact.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "AnanseWorld.h"
#include "AnanseMission.h"
#include "AnanseCatalogue.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/InputComponent.h"
#include "Engine/SkeletalMesh.h"
#include "UObject/ConstructorHelpers.h"
AAnanseSpiderLabPlayer::AAnanseSpiderLabPlayer()
{
 CharacterId=TEXT("ananse");
 GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
 GroundContact=CreateDefaultSubobject<UAnanseGroundContact>(TEXT("FourLegContacts"));
 GetCharacterMovement()->MaxWalkSpeed=35;GetCharacterMovement()->RotationRate=FRotator(0,35,0);
 static ConstructorHelpers::FObjectFinder<USkeletalMesh> Mesh(TEXT("/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.AnanseSpider_PROXY"));
 if(Mesh.Succeeded()){GetMesh()->SetSkeletalMesh(Mesh.Object);GetMesh()->SetRelativeLocation(FVector(0,0,-96));GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
 const TCHAR* Names[]={TEXT("A_Idle_Proxy"),TEXT("A_LimbROM_Proxy"),TEXT("A_WeaveGesture_Proxy"),TEXT("A_CrawlInPlace_Proxy")};
 for(const TCHAR* Name:Names){FString Path=FString::Printf(TEXT("/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY%s.AnanseSpider_PROXY%s"),Name,Name);ConstructorHelpers::FObjectFinder<UAnimSequence> Clip(*Path);ProxyClips.Add(Clip.Object);}
}
void AAnanseSpiderLabPlayer::BeginPlay()
{
 Super::BeginPlay();
 if(!GetMesh()->GetSkeletalMeshAsset() || GetMesh()->GetSkeletalMeshAsset()->GetPathName()!=TEXT("/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.AnanseSpider_PROXY"))
 {
     GroundContact->bEnabled=false;GetMesh()->SetVisibility(false);Body->SetVisibility(false);Head->SetVisibility(false);GetCharacterMovement()->DisableMovement();
     Mission->Message(TEXT("BLOCKED: this lab requires its qualified eight-appendage mesh. A new body asset needs rig compatibility verification; no biped fallback."));return;
 }
 // The shared optional-mesh loader uses a mannequin basis. This qualified custom
 // asset is already +X-forward; selecting the same published body must not yaw it.
 GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);
 UClass* Authored=LoadClass<UAnanseContactAnimInstance>(nullptr,TEXT("/Game/Production/Characters/SpiderRig_v001/ABP_AnanseSpider.ABP_AnanseSpider_C"));
 if(!Authored)UE_LOG(LogTemp,Warning,TEXT("Ananse authored Animation Blueprint absent; legacy native contact path only. Authored-rig gate remains open."));
 GetMesh()->SetAnimInstanceClass(Authored?Authored:UAnanseContactAnimInstance::StaticClass());
 if(auto* Anim=Cast<UAnanseContactAnimInstance>(GetMesh()->GetAnimInstance()))Anim->Contact=GroundContact;
 if(GetMesh()->GetSkeletalMeshAsset()){Body->SetVisibility(false);Head->SetVisibility(false);GetMesh()->SetVisibility(true);PlayProxyClip(0);Mission->Message(TEXT("ANANSE ENGINEERING PROXY: F1 idle / F2 limb isolation / F3 weave / F4 treadmill. Live four-leg contacts: supported walking fixtures require qualification."));}
 // Only the explicitly named proxy cloth slot is editable. Other imported materials,
 // rig proportions, facial controls and physics are unaffected by appearance metadata.
 if(const UAnanseCatalogue* Catalogue=GetCatalogue())
 if(const FAnanseCharacterSpec* Spec=Catalogue->Find(CharacterId))
 {
     FString Requested=TEXT("base");FParse::Value(FCommandLine::Get(),TEXT("AnanseVariant="),Requested);
     const FAnanseAppearance* Appearance=nullptr;
     for(const FAnanseAppearance& Candidate:Spec->Variants)if(Candidate.Id==FName(*Requested)){Appearance=&Candidate;break;}
     if(Appearance && GetMesh()->GetSkeletalMeshAsset())
     {
         const auto& Slots=GetMesh()->GetSkeletalMeshAsset()->GetMaterials();
         for(int32 Index=0;Index<Slots.Num();++Index)
             if(Slots[Index].MaterialSlotName==TEXT("Cloth_Proxy"))PublishedClothSlot=Index;
         if(PublishedClothSlot!=INDEX_NONE)
         {
             UMaterialInterface* Cloth=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Production/Characters/SpiderLook_v001/M_ProxyClothVariant.M_ProxyClothVariant"));
             if(Cloth)
             {
                 PublishedClothMaterial=GetMesh()->CreateDynamicMaterialInstance(PublishedClothSlot,Cloth);
                 if(PublishedClothMaterial)PublishedClothMaterial->SetVectorParameterValue(TEXT("ClothColor"),Appearance->Cloth);
             }
         }
     }
     if(!PublishedClothMaterial)UE_LOG(LogTemp,Warning,TEXT("ANANSE published proxy cloth binding unavailable: variant=%s slot=%d; no silent material fallback."),*Requested,PublishedClothSlot);
 }
}
void AAnanseSpiderLabPlayer::SetupPlayerInputComponent(UInputComponent* Input)
{
 Super::SetupPlayerInputComponent(Input);Input->BindKey(EKeys::L,IE_Pressed,this,&AAnanseSpiderLabPlayer::ToggleContacts);Input->BindKey(EKeys::F1,IE_Pressed,this,&AAnanseSpiderLabPlayer::Idle);Input->BindKey(EKeys::F2,IE_Pressed,this,&AAnanseSpiderLabPlayer::LimbROM);Input->BindKey(EKeys::F3,IE_Pressed,this,&AAnanseSpiderLabPlayer::Weave);Input->BindKey(EKeys::F4,IE_Pressed,this,&AAnanseSpiderLabPlayer::Crawl);
}
void AAnanseSpiderLabPlayer::PlayProxyClip(int32 Index)
{
 if(!ProxyClips.IsValidIndex(Index) || !ProxyClips[Index])return;ActiveProxyClip=Index;if(auto* Anim=Cast<UAnanseContactAnimInstance>(GetMesh()->GetAnimInstance())){Anim->Clip=ProxyClips[Index];Anim->ClipTime=0;}
}
TArray<FName> AAnanseSpiderLabPlayer::GetImportedBoneNames() const
{
 TArray<FName> Result;if(const USkeletalMesh* Mesh=GetMesh()->GetSkeletalMeshAsset())for(const FMeshBoneInfo& Bone:Mesh->GetRefSkeleton().GetRefBoneInfo())Result.Add(Bone.Name);return Result;
}
AAnanseCharacterLabMode::AAnanseCharacterLabMode(){DefaultPawnClass=AAnanseSpiderLabPlayer::StaticClass();HUDClass=AAnanseHUD::StaticClass();PlayerControllerClass=AAnanseLabController::StaticClass();}

void AAnanseSpiderLabPlayer::ResetTransientMotion(){Super::ResetTransientMotion();if(GroundContact)GroundContact->ResetContacts();}

void AAnanseSpiderLabPlayer::ToggleContacts(){GroundContact->bEnabled=!GroundContact->bEnabled;GroundContact->ResetContacts();Mission->Message(GroundContact->bEnabled?TEXT("Live contact walking enabled; supporting-leg source clips are overridden."):TEXT("Baked clip preview only; ground contacts disabled."));}
