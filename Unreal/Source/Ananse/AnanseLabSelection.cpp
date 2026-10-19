#include "AnanseLabSelection.h"
#include "AnanseCastLab.h"
#include "AnansePlayer.h"
#include "AnanseSpiderLab.h"
#include "AnanseLeopardLab.h"
#include "AnanseGroundContact.h"
#include "AnanseCatalogue.h"
#include "AbilitySystemComponent.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Engine/PointLight.h"
#include "Components/PointLightComponent.h"
#include "Engine/ExponentialHeightFog.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Camera/CameraComponent.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Engine/SkeletalMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/BoxComponent.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "AIController.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Materials/Material.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Json.h"
#include "EnhancedInputSubsystems.h"
#include "EnhancedPlayerInput.h"
#include "InputMappingContext.h"
#include "Engine/GameViewportClient.h"
#include "RHI.h"
#include "TimerManager.h"
#include "Containers/Ticker.h"
#include "Trace/Trace.h"
#include "ProfilingDebugging/TraceAuxiliary.h"
namespace
{
 const TCHAR* DefinitionPath=TEXT("/Game/Production/Characters/SpiderSelection_v001/DA_AnanseSpider.DA_AnanseSpider");
 const TCHAR* QualifiedMesh=TEXT("/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.AnanseSpider_PROXY");
 bool ArtPass2(){return FParse::Param(FCommandLine::Get(),TEXT("AnanseArtPass2"));}
 bool VisualReview(){return FParse::Param(FCommandLine::Get(),TEXT("AnanseVisualReview"));}
 bool ArtRefinement(){return FParse::Param(FCommandLine::Get(),TEXT("AnanseArtRefinement"));}
 bool InteractionRefinement(){return FParse::Param(FCommandLine::Get(),TEXT("AnanseInteractionRefinement"));}
 bool AsoReview(){return FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoReview"));}
 const TCHAR* Profile(){if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoArtRefine")))return TEXT("AnanseLabSelection_AsoArtRefine_v2");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoClearance")))return TEXT("AnanseLabSelection_AsoClearance_v1");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoContact")))return TEXT("AnanseLabSelection_AsoContact_v2");if(AsoReview())return TEXT("AnanseLabSelection_Aso_v1");if(ArtPass2())return TEXT("AnanseLabSelection_ArtPass2_v3");if(VisualReview())return TEXT("AnanseLabSelection_Visual_v3");if(InteractionRefinement())return TEXT("AnanseLabSelection_Interactions_v1");if(FParse::Param(FCommandLine::Get(),TEXT("AnanseFormsScenery")))return TEXT("AnanseLabSelection_Forms_v1");return ArtRefinement()?TEXT("AnanseLabSelection_Art_v2"):TEXT("AnanseLabSelection_v1");}
 int32 SelectionRevision(FName Id,int32 Published,int32 AsoPublished=1){if(AsoReview()&&Id==TEXT("aso-yaa-human-v1")&&FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoArtRefine")))return 8;if(AsoReview()&&Id==TEXT("aso-yaa-human-v1")&&FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoClearance")))return 6;if(AsoReview()&&Id==TEXT("aso-yaa-human-v1"))return FParse::Param(FCommandLine::Get(),TEXT("AnanseAsoContact"))?5:AsoPublished;if(ArtPass2()&&Id==TEXT("kwaku-human-v1"))return 11;if(ArtPass2()&&Id==TEXT("osebo-leopard-v1"))return 7;if(VisualReview()&&Id==TEXT("osebo-leopard-v1"))return 5;if(InteractionRefinement()&&Id==TEXT("osebo-leopard-v1"))return 2;return ArtRefinement()&&Id==TEXT("kwaku-human-v1")?Published:1;}
 struct FStoryDesign{const TCHAR* Key;const TCHAR* Id;const TCHAR* Identity;};
 const FStoryDesign StoryDesigns[]={{TEXT("Kwaku"),TEXT("kwaku-human-v1"),TEXT("kwaku")},{TEXT("AsoYaa"),TEXT("aso-yaa-human-v1"),TEXT("aso-yaa")},{TEXT("EsiHuman"),TEXT("esi-human-v1"),TEXT("esi")},{TEXT("OseboHuman"),TEXT("osebo-human-v1"),TEXT("osebo")},{TEXT("KojoTortoise"),TEXT("kojo-tortoise-v1"),TEXT("kojo")},{TEXT("KofiHornbill"),TEXT("kofi-hornbill-v1"),TEXT("kofi")},{TEXT("EsiMoth"),TEXT("esi-moth-v1"),TEXT("esi")}};
 const FStoryDesign* StoryFor(FName Id){for(const auto& D:StoryDesigns)if(Id==D.Id)return &D;return nullptr;}
 const TCHAR* DefinitionFor(FName Id,int32 Revision=1)
 {
  if(Id==TEXT("aso-yaa-human-v1")&&Revision==8)return TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/DA_AsoYaa.DA_AsoYaa");
  if(Id==TEXT("aso-yaa-human-v1")&&Revision==6)return TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/DA_AsoYaa.DA_AsoYaa");
  if(Id==TEXT("aso-yaa-human-v1")&&Revision==5)return TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/DA_AsoYaa.DA_AsoYaa");
  if(Id==TEXT("aso-yaa-human-v1")&&Revision==4)return TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v001/DA_AsoYaa.DA_AsoYaa");
  if(Id==TEXT("aso-yaa-human-v1")&&Revision==3)return TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v002/DA_AsoYaa.DA_AsoYaa");
  if(Id==TEXT("aso-yaa-human-v1")&&Revision==2)return TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v001/DA_AsoYaa.DA_AsoYaa");
  if(Id==TEXT("kwaku-human-v1")&&Revision==11)return TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("osebo-leopard-v1")&&Revision==7)return TEXT("/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/DA_OseboLeopard.DA_OseboLeopard");
  if(Id==TEXT("kwaku-human-v1")&&Revision==10)return TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v002/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("kwaku-human-v1")&&Revision==9)return TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v001/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("osebo-leopard-v1")&&Revision==6)return TEXT("/Game/Ananse/Characters/OseboLeopard/ArtPass2_v002/DA_OseboLeopard.DA_OseboLeopard");
  if(Id==TEXT("kwaku-human-v1")&&Revision==8)return TEXT("/Game/Ananse/Characters/Kwaku/Visual_v003/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("kwaku-human-v1")&&Revision==7)return TEXT("/Game/Ananse/Characters/Kwaku/Visual_v002/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("kwaku-human-v1")&&Revision==6)return TEXT("/Game/Ananse/Characters/Kwaku/Visual_v001/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("osebo-leopard-v1")&&VisualReview())return TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v003/DA_OseboLeopard.DA_OseboLeopard");
  if(Id==TEXT("kwaku-human-v1")&&Revision==5)return TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v005/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("kwaku-human-v1")&&Revision==4)return TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v003/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("kwaku-human-v1")&&Revision==3)return TEXT("/Game/Ananse/Characters/Kwaku/Refined_v002/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("kwaku-human-v1")&&Revision==2)return TEXT("/Game/Ananse/Characters/Kwaku/Refined_v001/DA_Kwaku.DA_Kwaku");
  if(Id==TEXT("ananse-spider-existing"))return DefinitionPath;
  if(Id==TEXT("osebo-leopard-v1")&&InteractionRefinement())return TEXT("/Game/Ananse/Characters/OseboLeopard/Interactions_v003/DA_OseboLeopard.DA_OseboLeopard");
  if(Id==TEXT("osebo-leopard-v1"))return TEXT("/Game/Ananse/Characters/OseboLeopard/Data/DA_OseboLeopard.DA_OseboLeopard");
  for(const auto& D:StoryDesigns)if(Id==D.Id){static FString Path;Path=FString::Printf(TEXT("/Game/Ananse/Characters/%s/Story_v001/DA_%s.DA_%s"),D.Key,D.Key,D.Key);return *Path;}
  return nullptr;
 }
 bool Known(FName Id){return DefinitionFor(Id) || Id==TEXT("kwaku-development");}
 FName IdentityFor(FName Id){if(const auto* D=StoryFor(Id))return FName(D->Identity);return Id==TEXT("ananse-spider-existing")?FName(TEXT("ananse")):Id==TEXT("osebo-leopard-v1")?FName(TEXT("osebo")):FName(TEXT("kwaku"));}
 FName FamilyFor(FName Id){if(const auto* D=StoryFor(Id))return FName(*FString::Printf(TEXT("%s-independent-v001"),D->Key));return Id==TEXT("ananse-spider-existing")?FName(TEXT("ananse-eight-limb-v002")):Id==TEXT("osebo-leopard-v1")?FName(TEXT("osebo-feline-biped-v001")):FName(TEXT("primitive-development"));}
}
int32 AAnanseLabController::KwakuPresentationRevision()const
{
 if(ArtPass2())return 11;if(VisualReview())return 8;const auto* Catalogue=GetGameInstance()->GetSubsystem<UAnanseCatalogue>();return ArtRefinement()&&Catalogue&&Catalogue->bLoaded?Catalogue->KwakuVisualRevision:1;
}
bool UAnanseCharacterDefinition::ValidateLoaded(FString& Error)const
{
 Error.Reset();
 if(const auto* D=StoryFor(DesignId))
 {
  auto* Loaded=Mesh.Get();auto* Class=PawnClass.Get();
  const bool Refined=DesignId==TEXT("kwaku-human-v1")&&(Revision==2||Revision==3||Revision==4||Revision==5||Revision==6||Revision==7||Revision==8||Revision==9||Revision==10||Revision==11);
  const bool Aso=DesignId==TEXT("aso-yaa-human-v1")&&(Revision==2||Revision==3||Revision==4||Revision==5||Revision==6||Revision==8);
  const FString ExpectedMesh=Aso&&Revision==8?TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa"):Aso&&Revision==6?TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa"):Aso&&Revision==5?TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa"):Aso&&Revision==4?TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v001/AsoYaa.AsoYaa"):Aso&&Revision==3?TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v002/AsoYaa.AsoYaa"):Aso?TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v001/AsoYaa.AsoYaa"):Refined&&Revision==11?TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku"):Refined&&Revision==10?TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v002/Kwaku.Kwaku"):Refined&&Revision==9?TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v001/Kwaku.Kwaku"):Refined&&Revision==8?TEXT("/Game/Ananse/Characters/Kwaku/Visual_v003/Kwaku.Kwaku"):Refined&&Revision==7?TEXT("/Game/Ananse/Characters/Kwaku/Visual_v002/Kwaku.Kwaku"):Refined&&Revision==6?TEXT("/Game/Ananse/Characters/Kwaku/Visual_v001/Kwaku.Kwaku"):Refined&&Revision==5?TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v005/Kwaku.Kwaku"):Refined&&Revision==4?TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v003/Kwaku.Kwaku"):Refined&&Revision==3?TEXT("/Game/Ananse/Characters/Kwaku/Refined_v002/Kwaku.Kwaku"):Refined?TEXT("/Game/Ananse/Characters/Kwaku/Refined_v001/Kwaku.Kwaku"):FString::Printf(TEXT("/Game/Ananse/Characters/%s/Story_v001/%s.%s"),D->Key,D->Key,D->Key);
  if(CharacterIdentity!=FName(D->Identity)||SkeletonKey!=FamilyFor(DesignId)||(!Refined&&!Aso&&Revision!=1)||!bEngineeringFixture||!Loaded||!Loaded->GetSkeleton()||Mesh.ToSoftObjectPath().ToString()!=ExpectedMesh||!Class||!Class->IsChildOf(AAnanseCastLabPlayer::StaticClass()))
  {Error=TEXT("Story design identity, revision, mesh or class incompatible");return false;}
  const auto* CDO=Class->GetDefaultObject<AAnanseCastLabPlayer>();
  if(CDO->DesignId!=DesignId||CDO->FamilyKey!=SkeletonKey||CDO->AuthoredMesh!=Loaded||!CDO->AnimationClass||Clips.Num()<8||CDO->AuthoredClips.Num()!=Clips.Num()||(Aso&&Clips.Num()!=16))
  {Error=TEXT("Incomplete independent animation binding");return false;}
  if(Aso&&(Revision==5||Revision==6||Revision==8)&&(!CDO->bAsoLedgerPresentation||!CDO->LedgerMesh||!Loaded->FindSocket(TEXT("socket_ledger_R")))){Error=TEXT("Aso ledger presentation dependency is missing; previous pawn retained");return false;}
  if(Aso&&(Revision==6||Revision==8)&&!CDO->LedgerSupportMesh){Error=TEXT("Aso placement table dependency missing; previous pawn retained");return false;}
  if(Refined&&(Revision==4||Revision==5||Revision==6||Revision==7||Revision==8||Revision==9||Revision==10||Revision==11)&&(!CDO->bLedgerPresentation||!CDO->LedgerMesh||!Clips.IsValidIndex(8)||!(Revision>=8?Clips[8].ToSoftObjectPath().ToString().StartsWith(TEXT("/Game/Ananse/Characters/Kwaku/Visual_v003/")):Clips[8].ToSoftObjectPath().ToString().StartsWith(TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v003/")))))
  {Error=TEXT("Interaction revision requires its separate prop and authored ledger clip");return false;}
  for(int32 I=0;I<Clips.Num();++I)if(!Clips[I].Get()||Clips[I].Get()->GetSkeleton()!=Loaded->GetSkeleton()||CDO->AuthoredClips[I]!=Clips[I].Get())
  {Error=TEXT("Story design animation family mismatch");return false;}
  return true;
 }
 if(DesignId==TEXT("osebo-leopard-v1"))
 {
  if(CharacterIdentity!=TEXT("osebo") || SkeletonKey!=TEXT("osebo-feline-biped-v001") || (Revision!=1&&Revision!=2&&Revision!=3&&Revision!=4&&Revision!=5&&Revision!=6&&Revision!=7) || !bEngineeringFixture)
  {Error=TEXT("Unsupported feline identity/revision/family or development classification");return false;}
  USkeletalMesh* Loaded=Mesh.Get();UClass* Class=PawnClass.Get();
  if(!Loaded || Mesh.ToSoftObjectPath().ToString()!=(Revision==7?TEXT("/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/OseboLeopard.OseboLeopard"):Revision==6?TEXT("/Game/Ananse/Characters/OseboLeopard/ArtPass2_v002/OseboLeopard.OseboLeopard"):Revision==5?TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v003/OseboLeopard.OseboLeopard"):Revision==4?TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v002/OseboLeopard.OseboLeopard"):Revision==3?TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v001/OseboLeopard.OseboLeopard"):Revision==2?TEXT("/Game/Ananse/Characters/OseboLeopard/Interactions_v003/OseboLeopard.OseboLeopard"):TEXT("/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard")) || !Class || !Class->IsChildOf(AAnanseLeopardLabPlayer::StaticClass()))
  {Error=TEXT("Missing authored feline mesh or incompatible pawn");return false;}
  const auto* Defaults=Class->GetDefaultObject<AAnanseLeopardLabPlayer>();
  if(!Loaded->GetSkeleton() || Loaded->GetRefSkeleton().GetNum()!=64 || Clips.Num()!=9 || Defaults->LeopardMesh!=Loaded || Defaults->LeopardClips.Num()!=9)
  {Error=TEXT("Feline skeleton, pawn defaults or nine clips missing");return false;}
  for(int32 I=0;I<Clips.Num();++I)
   if(!Clips[I].Get() || Clips[I].Get()->GetSkeleton()!=Loaded->GetSkeleton() || Defaults->LeopardClips[I]!=Clips[I].Get())
   {Error=TEXT("Missing animation or incompatible feline binding");return false;}
  return true;
 }
 if(DesignId!=TEXT("ananse-spider-existing") || CharacterIdentity!=TEXT("ananse") || SkeletonKey!=TEXT("ananse-eight-limb-v002") || Revision!=1 || !bEngineeringFixture)
 {Error=TEXT("Unsupported identity/revision/family or fixture classification");return false;}
 USkeletalMesh* Loaded=Mesh.Get();UClass* Class=PawnClass.Get();
 if(!Loaded || Mesh.ToSoftObjectPath().ToString()!=QualifiedMesh || !Class || !Class->IsChildOf(AAnanseSpiderLabPlayer::StaticClass()))
 {Error=TEXT("Missing qualified mesh or incompatible pawn");return false;}
 if(!Loaded->GetSkeleton() || Loaded->GetRefSkeleton().GetNum()!=102 || Clips.Num()!=4)
 {Error=TEXT("Qualified skeleton or four imported clips missing");return false;}
 for(const auto& Clip:Clips)
  if(!Clip.Get() || Clip.Get()->GetSkeleton()!=Loaded->GetSkeleton())
  {Error=TEXT("Missing animation or incompatible skeleton");return false;}
 return true;
}
void AAnanseLabController::ConfigurePreviewLight(UPointLightComponent* Light,bool bStory)
{
 if(!Light)return;
 const bool NeutralReview=FParse::Param(FCommandLine::Get(),TEXT("AnanseNeutralLabLighting"));
 if(NeutralReview)
 {
  Light->SetIntensityUnits(ELightUnits::Lumens);
  Light->SetLightColor(FLinearColor::White);
  Light->SetIntensity(3000.f);
  // Refined cast meshes use channel 0; legacy cast meshes use channel 1.
  Light->SetLightingChannels(!bStory||ArtRefinement(),bStory&&!ArtRefinement(),false);
 }
 else
 {
  Light->SetIntensity(ArtRefinement()?0:(bStory?16000:1200));
  Light->SetLightingChannels(!bStory,bStory,false);
 }
}
void AAnanseLabController::BeginPlay()
{
 Super::BeginPlay();
 // Two neutral preview fills per isolated lab controller, never per character swap.
 // It improves visibility without changing protected map assets or mesh materials.
 for(const FVector& Position : {FVector(250,-150,300),FVector(-250,150,300)})
 if(auto* Fill=GetWorld()->SpawnActor<APointLight>())
 {
  Fill->SetActorLocation(Position);
  if(auto* Light=Cast<UPointLightComponent>(Fill->GetLightComponent()))
  {Light->SetMobility(EComponentMobility::Movable);ConfigurePreviewLight(Light,Cast<AAnanseCastLabPlayer>(GetPawn())!=nullptr);Light->SetAttenuationRadius(1200);Light->SetCastShadows(false);}
  PreviewLights.Add(Fill);
 }
 if(!ArtRefinement())if(auto* Fog=GetWorld()->SpawnActor<AExponentialHeightFog>())
 {Fog->GetComponent()->SetFogDensity(.006f);Fog->GetComponent()->SetFogInscatteringColor(FLinearColor(.11f,.13f,.16f));Fog->GetComponent()->SetStartDistance(300);PreviewFog=Fog;}
}
void AAnanseLabController::OnPossess(APawn* InPawn)
{
 Super::OnPossess(InPawn);
 const bool Story=Cast<AAnanseCastLabPlayer>(InPawn)!=nullptr;
 for(auto& Actor:PreviewLights)if(auto* Fill=Cast<APointLight>(Actor.Get()))if(auto* Light=Cast<UPointLightComponent>(Fill->GetLightComponent()))
 {ConfigurePreviewLight(Light,Story);}

 if(Generation==0 && !Pending)
  SelectedDesign=Cast<AAnanseCastLabPlayer>(InPawn)?Cast<AAnanseCastLabPlayer>(InPawn)->DesignId:Cast<AAnanseLeopardLabPlayer>(InPawn)?FName(TEXT("osebo-leopard-v1")):Cast<AAnanseSpiderLabPlayer>(InPawn)?FName(TEXT("ananse-spider-existing")):FName(TEXT("kwaku-development"));
}
void AAnanseLabController::SetupInputComponent()
{
 Super::SetupInputComponent();
 InputComponent->BindKey(EKeys::PageDown,IE_Pressed,this,&AAnanseLabController::NextStoryDesign);
 InputComponent->BindKey(EKeys::Home,IE_Pressed,this,&AAnanseLabController::SelectSpider);
 InputComponent->BindKey(EKeys::End,IE_Pressed,this,&AAnanseLabController::SelectLeopard);
 InputComponent->BindKey(EKeys::Gamepad_DPad_Left,IE_Pressed,this,&AAnanseLabController::SelectSpider);
 InputComponent->BindKey(EKeys::Gamepad_DPad_Right,IE_Pressed,this,&AAnanseLabController::SelectLeopard);
 InputComponent->BindKey(EKeys::BackSpace,IE_Pressed,this,&AAnanseLabController::CancelSelection);
 InputComponent->BindKey(EKeys::F6,IE_Pressed,this,&AAnanseLabController::SaveLab);
 InputComponent->BindKey(EKeys::F8,IE_Pressed,this,&AAnanseLabController::LoadLab);
 InputComponent->BindKey(EKeys::V,IE_Pressed,this,&AAnanseLabController::ToggleWireframe);
 InputComponent->BindKey(EKeys::P,IE_Pressed,this,&AAnanseLabController::ToggleLabPause).bExecuteWhenPaused=true;
 InputComponent->BindKey(EKeys::Gamepad_Special_Right,IE_Pressed,this,&AAnanseLabController::ToggleLabPause).bExecuteWhenPaused=true;
}
void AAnanseLabController::NextStoryDesign(){int32 Index=-1;for(int32 I=0;I<UE_ARRAY_COUNT(StoryDesigns);++I)if(SelectedDesign==StoryDesigns[I].Id)Index=I;SelectDesign(FName(StoryDesigns[(Index+1)%UE_ARRAY_COUNT(StoryDesigns)].Id));}
void AAnanseLabController::ToggleLabPause(){SetPause(!IsPaused());UE_LOG(LogTemp,Display,TEXT("ANANSE lab paused=%d world_time=%.4f"),IsPaused(),GetWorld()->GetTimeSeconds());}
void AAnanseLabController::RestorePreview()
{
 if(auto* Mesh=PreviewMesh.Get())for(int32 I=0;I<PreviewMaterials.Num();++I)Mesh->SetMaterial(I,PreviewMaterials[I]);
 PreviewMesh.Reset();PreviewMaterials.Reset();
}
void AAnanseLabController::ToggleWireframe()
{
 if(PreviewMesh.IsValid()){RestorePreview();SelectionStatus=TEXT("Normal materials restored.");UE_LOG(LogTemp,Display,TEXT("ANANSE lab wireframe=off"));return;}
 auto* Spider=Cast<AAnansePlayer>(GetPawn());if(!Spider || !Spider->GetMesh()->GetSkeletalMeshAsset())return;
 auto* Wire=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Production/Characters/SpiderSelection_v001/M_LabWireframe.M_LabWireframe"));
 if(!Wire){SelectionStatus=TEXT("Wireframe material missing; current appearance retained.");return;}
 PreviewMesh=Spider->GetMesh();for(int32 I=0;I<Spider->GetMesh()->GetNumMaterials();++I)
 {PreviewMaterials.Add(Spider->GetMesh()->GetMaterial(I));Spider->GetMesh()->SetMaterial(I,Wire);}
 SelectionStatus=TEXT("V: actual mesh wireframe inspection; not final art approval.");
 UE_LOG(LogTemp,Display,TEXT("ANANSE lab wireframe=on bound=%d"),Spider->GetMesh()->GetMaterial(0)==Wire);
}
void AAnanseLabController::CancelSelection()
{
 ++Generation;RestoreGeneration=0;if(Pending)Pending->CancelHandle();Pending.Reset();SelectionStatus=TEXT("Selection cancelled; current pawn retained.");
}
bool AAnanseLabController::SelectDesign(FName Design)
{
 CancelSelection();
 RestorePreview();
 if(IsPaused()){SelectionStatus=TEXT("Resume the lab before changing characters.");return false;}
 if(!Known(Design)){SelectionStatus=TEXT("Unavailable design: no allowlisted lab binding. Current pawn retained.");return false;}
 if(!Cast<AAnansePlayer>(GetPawn())){SelectionStatus=TEXT("No usable lab pawn to retain.");return false;}
 const uint64 Request=Generation;
 SelectionStatus=TEXT("Loading allowlisted development appearance; current pawn remains usable.");
 TArray<FSoftObjectPath> Paths;
 FSoftObjectPath RequestedDefinition;
 if(const TCHAR* Path=DefinitionFor(Design,SelectionRevision(Design,KwakuPresentationRevision(),GetGameInstance()->GetSubsystem<UAnanseCatalogue>()->AsoVisualRevision)))
 {
  RequestedDefinition=FSoftObjectPath(Path);
#if !UE_BUILD_SHIPPING
  if(TestSelectionFault==1)RequestedDefinition=FSoftObjectPath(TEXT("/Game/Ananse/Characters/OseboLeopard/MissingQualification/DA_Missing.DA_Missing"));
#endif
  Paths.Add(RequestedDefinition);
 }
 else Paths.Add(FSoftObjectPath(AAnansePlayer::StaticClass()));
 Pending=UAssetManager::GetStreamableManager().RequestAsyncLoad(Paths,FStreamableDelegate::CreateWeakLambda(this,[this,Request,Design,RequestedDefinition]()
 {
  if(Request!=Generation){++RejectedStaleCompletions;return;}
  if(DefinitionFor(Design))
  {
   auto* Def=Cast<UAnanseCharacterDefinition>(RequestedDefinition.ResolveObject());
   if(!Def){Pending.Reset();SelectionStatus=TEXT("Missing design definition; current pawn retained.");return;}
   LoadedDefinition=Def;
#if !UE_BUILD_SHIPPING
   if(TestSelectionFault==2)
   {
    LoadedDefinition=DuplicateObject<UAnanseCharacterDefinition>(Def,GetTransientPackage());
    LoadedDefinition->Clips[0]=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXYA_Idle_Proxy.AnanseSpider_PROXYA_Idle_Proxy")));
   }
#endif
   TArray<FSoftObjectPath> Dependencies={Def->Mesh.ToSoftObjectPath(),Def->PawnClass.ToSoftObjectPath()};
   for(const auto& Clip:Def->Clips)Dependencies.Add(Clip.ToSoftObjectPath());
   Pending=UAssetManager::GetStreamableManager().RequestAsyncLoad(Dependencies,FStreamableDelegate::CreateWeakLambda(this,[this,Request,Design](){FinishSelection(Request,Design);}));
  }
  else FinishSelection(Request,Design);
 }));
 return Pending.IsValid();
}
void AAnanseLabController::FinishSelection(uint64 Request,FName Design)
{
 if(Request!=Generation){++RejectedStaleCompletions;return;}
 AAnansePlayer* Old=Cast<AAnansePlayer>(GetPawn());
 if(!IsValid(Old)){Pending.Reset();SelectionStatus=TEXT("Previous pawn unavailable; selection aborted.");return;}
 UClass* Class=AAnansePlayer::StaticClass();
 if(DefinitionFor(Design))
 {
  auto* Def=LoadedDefinition.Get();FString Error;
  if(!Def || Def->DesignId!=Design || !Def->ValidateLoaded(Error)){Pending.Reset();SelectionStatus=TEXT("Design compatibility blocked: ")+Error;return;}
  Class=Def->PawnClass.Get();
 }
 FTransform Spawn=Old->GetActorTransform();const bool Collision=Old->GetActorEnableCollision();
 const auto* Defaults=Class->GetDefaultObject<AAnansePlayer>();
 const auto* StoryDefaults=Cast<AAnanseCastLabPlayer>(Defaults);
 const float SpawnHalfHeight=StoryDefaults?FMath::Max(Defaults->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),StoryDefaults->AuthoringHeight*.5f+3):Defaults->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
 Spawn.AddToTranslation(FVector(0,0,SpawnHalfHeight-Old->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()+2.f));
#if !UE_BUILD_SHIPPING
 if(TestSelectionFault==3 && TestSpawnBlocker.IsValid())Spawn.SetLocation(TestSpawnBlocker->GetActorLocation());
#endif
 // Synchronous spawn only: ignore the old collision, restore it before possession.
 Old->SetActorEnableCollision(false);
 AAnansePlayer* Candidate=GetWorld()->SpawnActorDeferred<AAnansePlayer>(Class,Spawn,nullptr,nullptr,ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButDontSpawnIfColliding);
 if(Candidate){Candidate->bLabSelectionPawn=true;UGameplayStatics::FinishSpawningActor(Candidate,Spawn);}
 Old->SetActorEnableCollision(Collision);
 if(!IsValid(Candidate)){Pending.Reset();SelectionStatus=TEXT("No collision-safe spawn; current pawn retained.");return;}
 // Engine depenetration may move a candidate far outside the requested space.
 // A lab selection must stay nearby and pass an actual capsule obstruction query.
 FCollisionQueryParams SpawnQuery(SCENE_QUERY_STAT(AnanseLabSelectionSpawn),false,Candidate);SpawnQuery.AddIgnoredActor(Old);
 const auto* Capsule=Candidate->GetCapsuleComponent();
 const bool Blocked=GetWorld()->OverlapBlockingTestByChannel(Candidate->GetActorLocation(),Candidate->GetActorQuat(),ECC_Pawn,
  FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()),SpawnQuery);
 if(Candidate->IsActorBeingDestroyed() || FVector::Dist(Candidate->GetActorLocation(),Spawn.GetLocation())>100.f || Blocked)
 {Candidate->Destroy();Pending.Reset();SelectionStatus=FString::Printf(TEXT("Spawn blocked=%d offset=%.2f target=%s actual=%s capsule=%.2f; previous pawn retained."),Blocked,FVector::Dist(Candidate->GetActorLocation(),Spawn.GetLocation()),*Spawn.GetLocation().ToString(),*Candidate->GetActorLocation().ToString(),Capsule->GetScaledCapsuleHalfHeight());return;}
 if(auto* Spider=Cast<AAnanseSpiderLabPlayer>(Candidate))
  if(!Cast<UAnanseContactAnimInstance>(Spider->GetMesh()->GetAnimInstance()) || !Cast<UAnanseContactAnimInstance>(Spider->GetMesh()->GetAnimInstance())->bUseAuthoredGraph || !Spider->GetMesh()->IsVisible())
  {Candidate->Destroy();Pending.Reset();SelectionStatus=TEXT("Spider pose initialization failed; current pawn retained.");return;}
 if(auto* Leopard=Cast<AAnanseLeopardLabPlayer>(Candidate))
  if(!Leopard->bFamilyReady || !Leopard->GetMesh()->GetAnimInstance())
  {Candidate->Destroy();Pending.Reset();SelectionStatus=TEXT("Feline pose initialization failed; current pawn retained.");return;}
 if(auto* Story=Cast<AAnanseCastLabPlayer>(Candidate))if(!Story->bFamilyReady || !Story->GetMesh()->GetAnimInstance()){Candidate->Destroy();Pending.Reset();SelectionStatus=TEXT("Story pose initialization failed; current pawn retained.");return;}
 const FRotator View=GetControlRotation();Possess(Candidate);
 if(GetPawn()!=Candidate)
 {Candidate->Destroy();Possess(Old);Pending.Reset();SelectionStatus=TEXT("Possession failed; previous pawn restored.");return;}
 Candidate->ResetTransientMotion();SetControlRotation(View);SetViewTarget(Candidate);
 Old->ResetTransientMotion();Old->Abilities->CancelAllAbilities();Old->Destroy();
 SelectedDesign=Design;Pending.Reset();
 UE_LOG(LogTemp,Display,TEXT("ANANSE lab selection committed design=%s"),*Design.ToString());
 if(Candidate->GetMesh()->GetSkeletalMeshAsset() && Candidate->GetMesh()->GetAnimInstance())
  UE_LOG(LogTemp,Display,TEXT("ANANSE lab live binding pawn=%s mesh=%s skeleton=%s animation=%s"),*Candidate->GetClass()->GetPathName(),*Candidate->GetMesh()->GetSkeletalMeshAsset()->GetPathName(),*Candidate->GetMesh()->GetSkeletalMeshAsset()->GetSkeleton()->GetPathName(),*Candidate->GetMesh()->GetAnimInstance()->GetClass()->GetPathName());
 if(Request==RestoreGeneration){bRestoredProfile=true;UE_LOG(LogTemp,Display,TEXT("ANANSE lab profile restored=1"));}
 const int32 VisualRevision=LoadedDefinition&&LoadedDefinition->DesignId==Design?LoadedDefinition->Revision:1;
 SelectionStatus=FString::Printf(TEXT("%s / revision %d / development appearance. Home spider; End leopard; F6/F8 lab profile."),*Design.ToString(),VisualRevision);
}
bool AAnanseLabController::SaveSelection()
{
 if(Pending || !Known(SelectedDesign)){SelectionStatus=TEXT("Finish or cancel selection before saving.");return false;}
 auto* Catalogue=GetGameInstance()->GetSubsystem<UAnanseCatalogue>();
 if(!Catalogue || !Catalogue->bLoaded)return false;
 if(UGameplayStatics::DoesSaveGameExist(Profile(),0))
 {
  auto* Prior=Cast<UAnanseLabSelectionSave>(UGameplayStatics::LoadGameFromSlot(Profile(),0));
  if(!Prior || Prior->SchemaVersion!=1 || Prior->AssetRevision!=SelectionRevision(Prior->DesignId,Catalogue->KwakuVisualRevision,Catalogue->AsoVisualRevision) || !Known(Prior->DesignId) || Prior->ContentHash!=Catalogue->ContentHash || Prior->CharacterIdentity!=IdentityFor(Prior->DesignId) || Prior->SkeletonKey!=FamilyFor(Prior->DesignId) || Prior->CosmeticVariant!=TEXT("base"))
  {SelectionStatus=TEXT("Existing lab profile incompatible; preserved. Explicit recovery/archive is required before saving.");return false;}
 }
 auto* Save=NewObject<UAnanseLabSelectionSave>();Save->DesignId=SelectedDesign;Save->AssetRevision=SelectionRevision(SelectedDesign,Catalogue->KwakuVisualRevision,Catalogue->AsoVisualRevision);Save->ContentHash=Catalogue->ContentHash;
 Save->CharacterIdentity=IdentityFor(SelectedDesign);Save->SkeletonKey=FamilyFor(SelectedDesign);
 const bool Result=UGameplayStatics::SaveGameToSlot(Save,Profile(),0);SelectionStatus=Result?TEXT("Dedicated lab profile saved; campaign saves untouched."):TEXT("Lab profile write failed.");return Result;
}
bool AAnanseLabController::LoadSelection()
{
 auto* Save=Cast<UAnanseLabSelectionSave>(UGameplayStatics::LoadGameFromSlot(Profile(),0));
 auto* Catalogue=GetGameInstance()->GetSubsystem<UAnanseCatalogue>();
 if(!Save || !Catalogue || Save->SchemaVersion!=1 || Save->AssetRevision!=SelectionRevision(Save->DesignId,Catalogue->KwakuVisualRevision,Catalogue->AsoVisualRevision) || !Known(Save->DesignId) || Save->ContentHash!=Catalogue->ContentHash || Save->CosmeticVariant!=TEXT("base") ||
 Save->CharacterIdentity!=IdentityFor(Save->DesignId) || Save->SkeletonKey!=FamilyFor(Save->DesignId))
 {SelectionStatus=TEXT("Lab profile missing or incompatible; file preserved and current pawn retained.");return false;}
 const bool Started=SelectDesign(Save->DesignId);if(Started)RestoreGeneration=Generation;return Started;
}
void AAnanseLabController::EndPlay(const EEndPlayReason::Type Reason){CancelSelection();for(auto& Light:PreviewLights)if(Light.IsValid())Light->Destroy();PreviewLights.Reset();if(PreviewFog.IsValid())PreviewFog->Destroy();PreviewFog.Reset();Super::EndPlay(Reason);}
void AAnanseLabController::Tick(float DeltaSeconds)
{
 Super::Tick(DeltaSeconds);
 if(const APawn* Pawn=GetPawn())for(int32 I=0;I<PreviewLights.Num();++I)
  if(PreviewLights[I].IsValid())
  {
   FVector Offset(I? -250:250,I?150:-150,180);
   if(FParse::Param(FCommandLine::Get(),TEXT("AnanseNeutralLabLighting")))
   {
    const FRotator ViewYaw(0,GetControlRotation().Yaw,0);
    Offset=ViewYaw.RotateVector(FVector(-250,I?150:-150,180));
   }
   PreviewLights[I]->SetActorLocation(Pawn->GetActorLocation()+Offset);
  }
 if(APawn* Pawn=GetPawn())if(auto* Camera=Pawn->FindComponentByClass<UCameraComponent>())
 {
  float Bias=Cast<AAnanseCastLabPlayer>(Pawn)?-.25f:-1.5f;FParse::Value(FCommandLine::Get(),TEXT("AnanseLabExposureBias="),Bias);
  if(!FMath::IsFinite(Bias))Bias=-1.5f;
  Camera->PostProcessSettings.bOverride_AutoExposureBias=!ArtRefinement();
  Camera->PostProcessSettings.AutoExposureBias=FMath::Clamp(Bias,-3.f,1.f);Camera->PostProcessBlendWeight=1.f;
 }
#if !UE_BUILD_SHIPPING
 FString StoryFile;if(FParse::Value(FCommandLine::Get(),TEXT("AnanseStoryCastVerify="),StoryFile)){TickStoryCast(DeltaSeconds);return;}
 FString CrossFile;
 if(FParse::Value(FCommandLine::Get(),TEXT("AnanseCrossFamilyVerify="),CrossFile)){TickCrossFamily(DeltaSeconds);return;}
 if(bVerifyDone || !FParse::Value(FCommandLine::Get(),TEXT("AnanseLabVerify="),VerifyFile))return;
 VerifySeconds+=DeltaSeconds;
 if(VerifySeconds>90){bVerifyFailed=true;VerifyStage=3;}
 if(VerifySeconds>=NextVerifyAction && !Pending && VerifyStage<3)
 {
  NextVerifyAction=VerifySeconds+.25f;
  auto* Player=Cast<AAnansePlayer>(GetPawn());
  if(!Player || Player->GetController()!=this){bVerifyFailed=true;VerifyStage=3;}
  else if(VerifyStage==0)
  {
   const uint32 Before=Player->GetUniqueID();
   if(SelectDesign(TEXT("not-allowlisted")) || GetPawn()->GetUniqueID()!=Before)bVerifyFailed=true;
   SelectDesign(TEXT("ananse-spider-existing"));CancelSelection();
   SelectDesign(TEXT("kwaku-development"));SelectDesign(TEXT("ananse-spider-existing"));
   if(FParse::Param(FCommandLine::Get(),TEXT("AnanseLabRestoreCheck")))
   {if(!LoadSelection())bVerifyFailed=true;}
   VerifyStage=1;
  }
  else if(VerifyStage==1)
  {
   const bool ExpectSpider=SwapCount%2==0;
   const FName ExpectedDesign=ExpectSpider?FName(TEXT("ananse-spider-existing")):FName(TEXT("kwaku-development"));
   if(SelectedDesign!=ExpectedDesign || (Cast<AAnanseSpiderLabPlayer>(Player)!=nullptr)!=ExpectSpider)bVerifyFailed=true;
   int32 Count=0;for(TActorIterator<AAnansePlayer> It(GetWorld());It;++It)if(!It->IsActorBeingDestroyed())Count++;
   auto* LP=GetLocalPlayer();auto* Sub=LP?ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LP):nullptr;
   if(Count!=1 || !Sub || !Sub->HasMappingContext(Player->GetOwnedInputMapping()) || Player->Abilities->GetActivatableAbilities().Num()!=0)bVerifyFailed=true;
   if(Sub)for(const auto& Prior:VerifyMappings)if(Prior.IsValid() && Prior.Get()!=Player->GetOwnedInputMapping() && Sub->HasMappingContext(Prior.Get()))bVerifyFailed=true;
   VerifyMappings.AddUnique(Player->GetOwnedInputMapping());
   if(auto* Spider=Cast<AAnanseSpiderLabPlayer>(Player))
   {
    if(!Spider->GroundContact || Spider->GetImportedBoneNames().Num()!=102 || Spider->GroundContact->ResetCount<1)bVerifyFailed=true;
   }
   if(++SwapCount<=40)SelectDesign(SwapCount%2?FName(TEXT("kwaku-development")):FName(TEXT("ananse-spider-existing")));
   else {if(!SaveSelection())bVerifyFailed=true;VerifyStage=2;}
  }
  else if(VerifyStage==2 && VerifySeconds>=60)VerifyStage=3;
 }
 if(VerifyStage==3)
 {
  bVerifyDone=true;auto* Player=Cast<AAnanseSpiderLabPlayer>(GetPawn());
  const bool Rendered=GetWorld()->GetGameViewport() && GDynamicRHI && FString(GDynamicRHI->GetName())!=TEXT("Null");
  if(!Player || !Rendered || SwapCount<40 || VerifySeconds<60)bVerifyFailed=true;
  TSharedRef<FJsonObject> Report=MakeShared<FJsonObject>();Report->SetBoolField(TEXT("passed"),!bVerifyFailed);
  Report->SetNumberField(TEXT("seconds"),VerifySeconds);Report->SetNumberField(TEXT("selection_transactions"),SwapCount-1);
  Report->SetBoolField(TEXT("restored_profile"),bRestoredProfile);
  Report->SetBoolField(TEXT("rendered_rhi"),Rendered);Report->SetStringField(TEXT("coverage"),TEXT("Native API requests; primitive Kwaku baseline is not a second qualified skeletal family. No physical controller claim."));
  if(Player)
  {
   TArray<TSharedPtr<FJsonValue>> Bones;const auto& Ref=Player->GetMesh()->GetSkeletalMeshAsset()->GetRefSkeleton();
   for(int32 I=0;I<Ref.GetNum();++I){auto Bone=MakeShared<FJsonObject>();Bone->SetStringField(TEXT("name"),Ref.GetBoneName(I).ToString());Bone->SetNumberField(TEXT("parent"),Ref.GetParentIndex(I));Bones.Add(MakeShared<FJsonValueObject>(Bone));}
   Report->SetArrayField(TEXT("actual_bones"),Bones);
   Report->SetStringField(TEXT("post_swap_contact_metrics"),Player->GroundContact->MetricsJson());
   FScreenshotRequest::RequestScreenshot(FPaths::ChangeExtension(VerifyFile,TEXT("png")),true,false);
  }
  FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(Report,Writer);FFileHelper::SaveStringToFile(Json,*VerifyFile);
  const double Finish=FPlatformTime::Seconds()+2;
  FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Finish,Failed=bVerifyFailed](float)
  {
   if(FPlatformTime::Seconds()<Finish)return true;
#if UE_TRACE_ENABLED
   FTraceAuxiliary::Pause();FTraceAuxiliary::Stop();UE::Trace::Shutdown();
#endif
   FPlatformMisc::RequestExitWithStatus(false,Failed?2:0,TEXT("ANANSE lab selection verification complete"));return false;
  }));
 }
#endif
}
