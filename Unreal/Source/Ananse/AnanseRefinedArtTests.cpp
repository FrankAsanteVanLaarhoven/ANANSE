#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "AnanseCastLab.h"
#include "AnanseCatalogue.h"
#include "AnanseLabSelection.h"
#include "Animation/MorphTarget.h"
#include "Animation/AnimSequence.h"
#include "Json.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/Material.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#include "AnanseWorld.h"
#include "Engine/World.h"
#include "Engine/Level.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRefinedKwakuAssets,"Ananse.ArtRefinement.KwakuVisualCompatibility",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRefinedKwakuAssets::RunTest(const FString&)
{
 auto* Original=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/Story_v001/Kwaku.Kwaku"));
 auto* Refined=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/Refined_v001/Kwaku.Kwaku"));
 auto* Def=LoadObject<UAnanseCharacterDefinition>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/Refined_v001/DA_Kwaku.DA_Kwaku"));
 if(!TestNotNull(TEXT("Original mesh"),Original)||!TestNotNull(TEXT("Refined mesh"),Refined)||!TestNotNull(TEXT("Refined definition"),Def))return false;
 TestEqual(TEXT("Reuse exact existing skeleton object"),Refined->GetSkeleton(),Original->GetSkeleton());
 const auto& A=Original->GetRefSkeleton();const auto& B=Refined->GetRefSkeleton();TestEqual(TEXT("Same mapped bones"),A.GetNum(),B.GetNum());
 for(int32 I=0;I<FMath::Min(A.GetNum(),B.GetNum());++I){TestEqual(TEXT("Bone name"),B.GetBoneName(I),A.GetBoneName(I));TestEqual(TEXT("Parent index"),B.GetParentIndex(I),A.GetParentIndex(I));TestTrue(TEXT("Rest transform unchanged"),B.GetRefBonePose()[I].Equals(A.GetRefBonePose()[I],.001));}
 TestEqual(TEXT("Unknown source cannot select a refined mesh"),UAnanseCatalogue::KwakuBindingRevision(TEXT("unknown"),TEXT("/Game/Ananse/Characters/Kwaku/Refined_v001/Kwaku.Kwaku"),TEXT("/Game/Ananse/Characters/Kwaku/Refined_v001/DA_Kwaku.DA_Kwaku"),TEXT("Kwaku-independent-v001")),0);
 TestEqual(TEXT("Three real LODs"),Refined->GetLODNum(),3);
 for(const FName Name:{FName(TEXT("Blink_L")),FName(TEXT("Blink_R"))})
 {
  auto* Morph=Refined->FindMorphTarget(Name);if(!TestNotNull(TEXT("Materialized eyelid target"),Morph))continue;
  const auto& Models=Morph->GetMorphLODModels();AddInfo(FString::Printf(TEXT("%s: target LOD models=%d"),*Name.ToString(),Models.Num()));if(!TestTrue(TEXT("Actual LOD0 deltas"),Models.Num()>0))continue;bool Changed=false;
  for(const auto& Delta:Models[0].Vertices){TestTrue(TEXT("Finite morph delta"),!Delta.PositionDelta.ContainsNaN());const auto* Render=Refined->GetResourceForRendering();const uint32 Count=Render&&Render->LODRenderData.Num()>0?Render->LODRenderData[0].GetNumVertices():0;
   TestTrue(TEXT("Morph indexes actual LOD vertex buffer"),Count>0&&Delta.SourceIdx<Count);
   bool InSection=false;if(Render&&Render->LODRenderData.Num()>0)for(const auto& Section:Render->LODRenderData[0].RenderSections)
   {
    if(Delta.SourceIdx>=Section.BaseVertexIndex&&Delta.SourceIdx<Section.BaseVertexIndex+Section.NumVertices)
    {
     InSection=true;auto* Interface=Refined->GetMaterials().IsValidIndex(Section.MaterialIndex)?Refined->GetMaterials()[Section.MaterialIndex].MaterialInterface.Get():nullptr;auto* Material=Interface?Interface->GetMaterial():nullptr;
     TestTrue(TEXT("Morphed rendered section has compiled morph material usage"),Material&&Material->GetUsageByFlag(MATUSAGE_MorphTargets));
    }
   }
   TestTrue(TEXT("Morph vertex belongs to a rendered section"),InSection);Changed|=Delta.PositionDelta.Size()>.01f;}
  TestTrue(TEXT("Nonzero eyelid deformation"),Changed);
 }
 Def->PawnClass.LoadSynchronous();Def->Mesh.LoadSynchronous();for(auto& Clip:Def->Clips)Clip.LoadSynchronous();FString Error;TestTrue(TEXT("Allowlisted revision2 binding"),Def->ValidateLoaded(Error));
 const auto* Defaults=Def->PawnClass.Get()->GetDefaultObject<AAnanseCastLabPlayer>();TestTrue(TEXT("Refined expression binding enabled"),Defaults->bRefinedFace);TestEqual(TEXT("Original eleven clips retained"),Defaults->AuthoredClips.Num(),11);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRepairedKwakuAssets,"Ananse.ArtRefinement.KwakuRepairedSurfaceCompatibility",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRepairedKwakuAssets::RunTest(const FString&)
{
 auto* Original=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/Story_v001/Kwaku.Kwaku"));
 auto* Refined=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/Refined_v002/Kwaku.Kwaku"));
 auto* Def=LoadObject<UAnanseCharacterDefinition>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/Refined_v002/DA_Kwaku.DA_Kwaku"));
 if(!TestNotNull(TEXT("Original mesh"),Original)||!TestNotNull(TEXT("Refined mesh"),Refined)||!TestNotNull(TEXT("Refined definition"),Def))return false;
 TestEqual(TEXT("Reuse exact existing skeleton object"),Refined->GetSkeleton(),Original->GetSkeleton());
 const auto& A=Original->GetRefSkeleton();const auto& B=Refined->GetRefSkeleton();TestEqual(TEXT("Same mapped bones"),A.GetNum(),B.GetNum());
 for(int32 I=0;I<FMath::Min(A.GetNum(),B.GetNum());++I){TestEqual(TEXT("Bone name"),B.GetBoneName(I),A.GetBoneName(I));TestEqual(TEXT("Parent index"),B.GetParentIndex(I),A.GetParentIndex(I));TestTrue(TEXT("Rest transform unchanged"),B.GetRefBonePose()[I].Equals(A.GetRefBonePose()[I],.001));}
 TestEqual(TEXT("Unknown source cannot select a refined mesh"),UAnanseCatalogue::KwakuBindingRevision(TEXT("unknown"),TEXT("/Game/Ananse/Characters/Kwaku/Refined_v002/Kwaku.Kwaku"),TEXT("/Game/Ananse/Characters/Kwaku/Refined_v002/DA_Kwaku.DA_Kwaku"),TEXT("Kwaku-independent-v001")),0);
 TestEqual(TEXT("Three real LODs"),Refined->GetLODNum(),3);
 for(const FName Name:{FName(TEXT("Blink_L")),FName(TEXT("Blink_R"))})
 {
  auto* Morph=Refined->FindMorphTarget(Name);if(!TestNotNull(TEXT("Materialized eyelid target"),Morph))continue;
  const auto& Models=Morph->GetMorphLODModels();AddInfo(FString::Printf(TEXT("%s: target LOD models=%d"),*Name.ToString(),Models.Num()));if(!TestTrue(TEXT("Actual LOD0 deltas"),Models.Num()>0))continue;bool Changed=false;
  for(const auto& Delta:Models[0].Vertices){TestTrue(TEXT("Finite morph delta"),!Delta.PositionDelta.ContainsNaN());const auto* Render=Refined->GetResourceForRendering();const uint32 Count=Render&&Render->LODRenderData.Num()>0?Render->LODRenderData[0].GetNumVertices():0;
   TestTrue(TEXT("Morph indexes actual LOD vertex buffer"),Count>0&&Delta.SourceIdx<Count);
   bool InSection=false;if(Render&&Render->LODRenderData.Num()>0)for(const auto& Section:Render->LODRenderData[0].RenderSections)
   {
    if(Delta.SourceIdx>=Section.BaseVertexIndex&&Delta.SourceIdx<Section.BaseVertexIndex+Section.NumVertices)
    {
     InSection=true;auto* Interface=Refined->GetMaterials().IsValidIndex(Section.MaterialIndex)?Refined->GetMaterials()[Section.MaterialIndex].MaterialInterface.Get():nullptr;auto* Material=Interface?Interface->GetMaterial():nullptr;
     TestTrue(TEXT("Morphed rendered section has compiled morph material usage"),Material&&Material->GetUsageByFlag(MATUSAGE_MorphTargets));
    }
   }
   TestTrue(TEXT("Morph vertex belongs to a rendered section"),InSection);Changed|=Delta.PositionDelta.Size()>.01f;}
  TestTrue(TEXT("Nonzero eyelid deformation"),Changed);
 }
 Def->PawnClass.LoadSynchronous();Def->Mesh.LoadSynchronous();for(auto& Clip:Def->Clips)Clip.LoadSynchronous();FString Error;TestTrue(TEXT("Allowlisted revision3 binding"),Def->ValidateLoaded(Error));
 const auto* Defaults=Def->PawnClass.Get()->GetDefaultObject<AAnanseCastLabPlayer>();TestTrue(TEXT("Refined expression binding enabled"),Defaults->bRefinedFace);TestEqual(TEXT("Original eleven clips retained"),Defaults->AuthoredClips.Num(),11);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRepairedSceneBindings,"Ananse.ArtRefinement.InteractionPresentationOwnership",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRepairedSceneBindings::RunTest(const FString&)
{
 auto* World=LoadObject<UWorld>(nullptr,TEXT("/Game/Ananse/Maps/Refinement_v007/L_Market_EpisodeForms.L_Market_EpisodeForms"));
 if(!TestNotNull(TEXT("Saved repaired market"),World)||!TestNotNull(TEXT("Persistent level"),World->PersistentLevel.Get()))return false;
 int32 Count=0,Humans=0,OseboOrders=0;
 for(auto Actor:World->PersistentLevel->Actors)if(auto* A=Cast<AAnanseInteractable>(Actor))
 {
  ++Count;TestEqual(TEXT("Original root retains collision authority"),A->GetRootComponent(),static_cast<USceneComponent*>(A->Mesh.Get()));
  TestTrue(TEXT("Gameplay collision remains enabled"),A->Mesh->GetCollisionEnabled()!=ECollisionEnabled::NoCollision);
  TestEqual(TEXT("Prop presentation cannot collide"),A->PropVisual->GetCollisionEnabled(),ECollisionEnabled::NoCollision);
  TestEqual(TEXT("Character presentation cannot collide"),A->CharacterVisual->GetCollisionEnabled(),ECollisionEnabled::NoCollision);
  if(A->CharacterVisual->GetSkeletalMeshAsset())++Humans;
  if(A->CharacterId==TEXT("osebo"))
  {
   ++OseboOrders;TestNull(TEXT("Listening marker cannot duplicate the pursuer body"),A->CharacterVisual->GetSkeletalMeshAsset());
   TestNotNull(TEXT("Listening marker has an authored notice prop"),A->PropVisual->GetStaticMesh().Get());
   TestEqual(TEXT("Existing listening interaction retained"),A->Action,FName(TEXT("listen")));
  }
 }
 TestEqual(TEXT("Eight existing interaction roots"),Count,8);TestEqual(TEXT("Two static human NPC presentations"),Humans,2);TestEqual(TEXT("One Osebo orders interaction"),OseboOrders,1);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FInteractionSurfaceBindings,"Ananse.ArtRefinement.InteractionSurfaceBindings",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FInteractionSurfaceBindings::RunTest(const FString&)
{
 auto* Def=LoadObject<UAnanseCharacterDefinition>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v005/DA_Kwaku.DA_Kwaku"));
 auto* Feline=LoadObject<UAnanseCharacterDefinition>(nullptr,TEXT("/Game/Ananse/Characters/OseboLeopard/Interactions_v003/DA_OseboLeopard.DA_OseboLeopard"));
 if(!TestNotNull(TEXT("Actual interaction definition"),Def)||!TestNotNull(TEXT("Actual feline revision definition"),Feline))return false;
 Def->Mesh.LoadSynchronous();Def->PawnClass.LoadSynchronous();for(auto& Clip:Def->Clips)Clip.LoadSynchronous();Feline->Mesh.LoadSynchronous();Feline->PawnClass.LoadSynchronous();for(auto& Clip:Feline->Clips)Clip.LoadSynchronous();
 FString Error;TestTrue(TEXT("Strict interaction binding"),Def->ValidateLoaded(Error));TestTrue(TEXT("Strict feline revision binding"),Feline->ValidateLoaded(Error));
 const auto* Defaults=Def->PawnClass.Get()->GetDefaultObject<AAnanseCastLabPlayer>();TestTrue(TEXT("Ledger presentation explicitly enabled"),Defaults->bLedgerPresentation);TestNotNull(TEXT("Materialized separate ledger"),Defaults->LedgerMesh.Get());TestEqual(TEXT("Prop cannot own collision"),Defaults->LedgerVisual->GetCollisionEnabled(),ECollisionEnabled::NoCollision);
 TestEqual(TEXT("Original 46 bones"),Def->Mesh.Get()->GetRefSkeleton().GetNum(),46);TestEqual(TEXT("Independent 64 feline bones"),Feline->Mesh.Get()->GetRefSkeleton().GetNum(),64);TestTrue(TEXT("Families stay separate"),Def->Mesh.Get()->GetSkeleton()!=Feline->Mesh.Get()->GetSkeleton());TestEqual(TEXT("Original eleven motion slots"),Def->Clips.Num(),11);TestEqual(TEXT("Existing nine feline slots"),Feline->Clips.Num(),9);
 TestTrue(TEXT("New ledger motion is actually bound"),Def->Clips[8].ToSoftObjectPath().ToString().StartsWith(TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v003/")));
 for(const float Side:{1.f,-1.f})
 {
  const FString Text=UAnanseAnimationAuthoring::DescribeSkinProbe(Def->Mesh.Get(),Def->Clips[8].Get(),FVector(3.2447692,Side*28.0075967,74.7303426),1.2f);TSharedPtr<FJsonObject> Probe;auto Reader=TJsonReaderFactory<>::Create(Text);if(!TestTrue(TEXT("Actual native skin probe is readable"),FJsonSerializer::Deserialize(Reader,Probe)&&Probe.IsValid()))return false;
  TestTrue(TEXT("Native rest vertex aligns with actual source digit"),Probe->GetNumberField(TEXT("rest_distance_cm"))<.01);FVector Point;TestTrue(TEXT("Skinned position is finite"),Point.InitFromString(Probe->GetStringField(TEXT("skinned_position")))&&!Point.ContainsNaN());TestTrue(TEXT("Skinned source contact preserved in native held pose"),FVector::Dist(Point,FVector(24.3419304,Side*8.4995091,103.4530997))<.1);
 }
 TestNotNull(TEXT("New mesh has ledger socket"),Def->Mesh.Get()->FindSocket(TEXT("socket_ledger")));TestNotNull(TEXT("Preserved feline capture socket"),Feline->Mesh.Get()->FindSocket(TEXT("socket_capture_R")));return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FInteractionPreparationBoundary,"Ananse.ArtRefinement.InteractionPreparationBoundary",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FInteractionPreparationBoundary::RunTest(const FString&)
{
 auto* Original=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Ananse/Characters/Kwaku/Story_v001/Kwaku.Kwaku"));if(!Original)return false;const int32 Count=Original->GetLODNum();TestTrue(TEXT("Preparation rejects protected old revision explicitly"),UAnanseAnimationAuthoring::PrepareInteractionSurface(Original)!=TEXT("ok"));TestEqual(TEXT("Protected mesh LODs unchanged"),Original->GetLODNum(),Count);TestTrue(TEXT("Missing mesh is rejected explicitly"),UAnanseAnimationAuthoring::PrepareInteractionSurface(nullptr)!=TEXT("ok"));return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FVisualReviewAssets,"Ananse.ArtRefinement.VisualReviewDataNotCreativeApproval",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FVisualReviewAssets::RunTest(const FString&)
{
 for(const TCHAR* Key:{TEXT("Kwaku"),TEXT("OseboLeopard")})
 {
  const FString Folder=FString::Printf(TEXT("/Game/Ananse/Characters/%s/Visual_v003/"),Key);
  auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*(Folder+Key+TEXT(".")+Key));
  auto* Def=LoadObject<UAnanseCharacterDefinition>(nullptr,*(Folder+TEXT("DA_")+Key+TEXT(".DA_")+Key));
  if(!TestNotNull(TEXT("Saved visual-review mesh"),Mesh)||!TestNotNull(TEXT("Typed review definition"),Def))continue;
  Def->PawnClass.LoadSynchronous();Def->Mesh.LoadSynchronous();for(auto& Clip:Def->Clips)Clip.LoadSynchronous();
  FString Error;TestTrue(TEXT("Exact new family/mesh/class/clip allowlist"),Def->ValidateLoaded(Error));TestEqual(TEXT("Three materialized LODs"),Mesh->GetLODNum(),3);
  for(const TCHAR* Name:{TEXT("Blink_L"),TEXT("Blink_R"),TEXT("BrowUp"),TEXT("BrowDown"),TEXT("Concern"),TEXT("Suspicion"),TEXT("Determination")})
  {
   auto* Morph=Mesh->FindMorphTarget(Name);if(!TestNotNull(TEXT("Actual facial target"),Morph))continue;
   const auto& Models=Morph->GetMorphLODModels();TestTrue(TEXT("LOD0 contains actual deltas"),Models.Num()>0&&Models[0].Vertices.Num()>0);
  }
 }
 AddInfo(TEXT("This test validates bindings/deltas only; likeness, speech, natural grasp and creative approval remain open."));return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseArtPass2Evidence,"Ananse.ArtRefinement.Pass2InputsDoNotGrantCreativeApproval",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseArtPass2Evidence::RunTest(const FString&)
{
 for(const auto& Row:{TPair<const TCHAR*,int32>(TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/DA_Kwaku.DA_Kwaku"),11),TPair<const TCHAR*,int32>(TEXT("/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/DA_OseboLeopard.DA_OseboLeopard"),7)})
 {
  auto* Def=LoadObject<UAnanseCharacterDefinition>(nullptr,Row.Key);if(!TestNotNull(TEXT("Versioned art-only definition"),Def))continue;
  Def->PawnClass.LoadSynchronous();auto* Mesh=Def->Mesh.LoadSynchronous();for(auto& Clip:Def->Clips)Clip.LoadSynchronous();FString Error;
  TestEqual(TEXT("Exact unpublished revision"),Def->Revision,Row.Value);TestTrue(TEXT("Retained compatible mesh/class/clips"),Def->ValidateLoaded(Error));if(!TestNotNull(TEXT("Actual skeletal mesh"),Mesh))continue;
  for(const TCHAR* Name:{TEXT("Blink_L"),TEXT("Blink_R"),TEXT("MouthOpen"),TEXT("Speech_A"),TEXT("Speech_O"),TEXT("Speech_M"),TEXT("FearStartle")})
  {auto* Morph=Mesh->FindMorphTarget(Name);if(TestNotNull(TEXT("Materialized target"),Morph))TestTrue(TEXT("Nonzero actual geometry delta"),Morph->GetMorphLODModels().Num()>0&&Morph->GetMorphLODModels()[0].Vertices.Num()>0);}
 }
 AddInfo(TEXT("Technical asset evidence only; no likeness, natural anatomy or speech-performance approval."));return true;
}
#endif
