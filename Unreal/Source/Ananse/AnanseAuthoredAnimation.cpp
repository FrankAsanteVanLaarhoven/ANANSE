#include "AnanseAuthoredAnimation.h"
#include "AnanseSecondaryMotion.h"
#include "Animation/AnimSequence.h"
#include "Animation/MorphTarget.h"
#include "Animation/AnimInstanceProxy.h"
#include "AnanseLeopardContact.h"
#include "Components/SkeletalMeshComponent.h"
#include "BonePose.h"
#include "TwoBoneIK.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/SkeletalMeshSocket.h"
#include "Json.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Materials/MaterialInterface.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#include "Rendering/SkinWeightVertexBuffer.h"

#if WITH_EDITOR
#include "MeshDescription.h"
#include "SkeletalMeshAttributes.h"
#include "SkinnedAssetCompiler.h"
#include "UObject/Package.h"
#include "UObject/MetaData.h"
#include "Animation/AnimBlueprint.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_SequencePlayer.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphSchema.h"
#include "K2Node_VariableGet.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#endif

namespace
{
struct FLeopardPoseProxy:public FAnimInstanceProxy
{
 explicit FLeopardPoseProxy(UAnimInstance* Instance):FAnimInstanceProxy(Instance){}
 FAnanseSecondaryMotion Secondary;
 bool bAsoGarmentClearance=false;
 void RestartPresentation(){InitializeRootNode();Secondary.Initialized=false;}
 FAnanseFelinePose Input;UAnanseLeopardContact* Contact=nullptr;float Cost=0;int32 Solved=0;
 virtual void PreUpdate(UAnimInstance* Instance,float Delta)override
 {
  FAnimInstanceProxy::PreUpdate(Instance,Delta);check(IsInGameThread());
  Contact=Instance->GetOwningActor()?Instance->GetOwningActor()->FindComponentByClass<UAnanseLeopardContact>():nullptr;
  const auto* Skin=Instance->GetSkelMeshComponent();bAsoGarmentClearance=Skin&&Skin->GetSkeletalMeshAsset()&&(Skin->GetSkeletalMeshAsset()->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa")||Skin->GetSkeletalMeshAsset()->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa"))&&!FParse::Param(FCommandLine::Get(),TEXT("AnanseDisableAsoGarmentClearance"));
  Input=Contact?Contact->Snapshot:FAnanseFelinePose();auto* Anim=CastChecked<UAnanseLeopardAnimInstance>(Instance);if(Anim->bResetSecondaryMotion){Secondary.Initialized=false;Anim->bResetSecondaryMotion=false;}Secondary.Gather(Instance,Delta);
 }
 void CorrectAsoGarment(FPoseContext& Output)
 {
  if(!bAsoGarmentClearance)return;
  const auto& Bones=Output.Pose.GetBoneContainer();const auto& Ref=Bones.GetReferenceSkeleton();
  auto Index=[&](FName Name){return Bones.GetCompactPoseIndexFromSkeletonIndex(Ref.FindBoneIndex(Name));};const auto Parent=Index(TEXT("pelvis"));if(!Parent.IsValid())return;
  TArray<FTransform> RefCS=Ref.GetRefBonePose();for(int32 I=0;I<RefCS.Num();++I)if(Ref.GetParentIndex(I)>=0)RefCS[I]=RefCS[I]*RefCS[Ref.GetParentIndex(I)];
  FCSPose<FCompactPose> Pose;Pose.InitPose(Output.Pose);const FQuat RefParent=RefCS[Ref.FindBoneIndex(TEXT("pelvis"))].GetRotation();const FQuat Delta=(Pose.GetComponentSpaceTransform(Parent).GetRotation()*RefParent.Inverse()).GetNormalized();const FQuat HangingParent=FQuat(FVector::UpVector,FMath::DegreesToRadians(Delta.Rotator().Yaw))*RefParent;
  for(const TCHAR* Name:{TEXT("Dress_L"),TEXT("Dress_R")})
  {
   const auto D=Index(Name);if(!D.IsValid()||Ref.GetParentIndex(Ref.FindBoneIndex(Name))!=Ref.FindBoneIndex(TEXT("pelvis")))continue;
   const FQuat RestLocal=Bones.GetRefPoseTransform(D).GetRotation();FQuat LocalDelta=(RestLocal.Inverse()*Output.Pose[D].GetRotation()).GetNormalized();if(LocalDelta.W<0)LocalDelta=LocalDelta*-1.;const double Angle=LocalDelta.GetAngle();if(Angle>FMath::DegreesToRadians(4.))LocalDelta=FQuat::Slerp(FQuat::Identity,LocalDelta,FMath::DegreesToRadians(4.)/Angle);
   auto T=Pose.GetComponentSpaceTransform(D);T.SetRotation((HangingParent*RestLocal*LocalDelta).GetNormalized());Pose.SetComponentSpaceTransform(D,T);
  }
  FCSPose<FCompactPose>::ConvertComponentPosesToLocalPosesSafe(Pose,Output.Pose);
 }
 virtual bool Evaluate(FPoseContext& Output)override
 {
  EvaluateAnimationNode(Output);CorrectAsoGarment(Output);Secondary.Apply(Output);Solved=0;if(!Input.Enabled)return true;
  const double Start=FPlatformTime::Seconds();const auto& Bones=Output.Pose.GetBoneContainer();
  auto Index=[&](FName Name){return Bones.GetCompactPoseIndexFromSkeletonIndex(Bones.GetReferenceSkeleton().FindBoneIndex(Name));};
  for(int32 I=0;I<Output.Pose.GetNumBones();++I)
  {
   FCompactPoseBoneIndex B(I);const FName Name=Bones.GetReferenceSkeleton().GetBoneName(Bones.GetSkeletonIndex(B));
   const FString N=Name.ToString();if(N.StartsWith(TEXT("thigh_"))||N.StartsWith(TEXT("shin_"))||N.StartsWith(TEXT("foot_"))||N.StartsWith(TEXT("ball_"))||N.StartsWith(TEXT("toe_")))Output.Pose[B]=Bones.GetRefPoseTransform(B);
  }
  FCSPose<FCompactPose> Pose;Pose.InitPose(Output.Pose);const auto Pelvis=Index(TEXT("pelvis"));
  if(Pelvis.IsValid()){auto Body=Pose.GetComponentSpaceTransform(Pelvis);Body.AddToTranslation(FVector(0,0,Input.BodyZ));Pose.SetComponentSpaceTransform(Pelvis,Body);}
  for(int32 I=0;I<2;++I)
  {
   const FString S=I?TEXT("R"):TEXT("L");auto HIdx=Index(FName(*(TEXT("thigh_")+S))),KIdx=Index(FName(*(TEXT("shin_")+S))),AIdx=Index(FName(*(TEXT("foot_")+S)));
   if(!HIdx.IsValid()||!KIdx.IsValid()||!AIdx.IsValid())continue;
   auto H=Pose.GetComponentSpaceTransform(HIdx),K=Pose.GetComponentSpaceTransform(KIdx),A=Pose.GetComponentSpaceTransform(AIdx);
   const FQuat Rotation=(FQuat::FindBetweenNormals(FVector::UpVector,Input.Normal[I])*A.GetRotation()).GetNormalized();
   FVector Target=Input.Target[I]-Rotation.RotateVector(Input.SoleOffset[I]);
   const FVector Along=(A.GetLocation()-H.GetLocation()).GetSafeNormal();FVector Bend=K.GetLocation()-H.GetLocation();Bend-=Along*FVector::DotProduct(Bend,Along);
   if(Bend.IsNearlyZero())Bend=FVector::ForwardVector;
   const float Upper=FVector::Dist(H.GetLocation(),K.GetLocation()),Lower=FVector::Dist(K.GetLocation(),A.GetLocation());
   FVector Direction=Target-H.GetLocation();Target=H.GetLocation()+Direction.GetSafeNormal(SMALL_NUMBER,-FVector::UpVector)*FMath::Clamp(float(Direction.Size()),FMath::Abs(Upper-Lower)+2.f,Upper+Lower-1.f);
   AnimationCore::SolveTwoBoneIK(H,K,A,H.GetLocation()+Bend.GetSafeNormal()*100,Target,false,1,1);A.SetRotation(Rotation);
   Pose.SetComponentSpaceTransform(HIdx,H);Pose.SetComponentSpaceTransform(KIdx,K);Pose.SetComponentSpaceTransform(AIdx,A);++Solved;
  }
  FCSPose<FCompactPose>::ConvertComponentPosesToLocalPosesSafe(Pose,Output.Pose);Cost=float((FPlatformTime::Seconds()-Start)*1e6);return true;
 }
 virtual void PostEvaluate(UAnimInstance* Instance)override
 {FAnimInstanceProxy::PostEvaluate(Instance);auto* Anim=CastChecked<UAnanseLeopardAnimInstance>(Instance);Anim->SecondaryBoneCount=Secondary.AppliedBones;Anim->SecondaryEvaluations=Secondary.Evaluations;Anim->SecondaryPeakDegrees=Secondary.PeakDegrees;Anim->SecondaryResets=Secondary.Resets;if(Contact){Contact->SolveUs=Cost;Contact->SolvedChains=Solved;}}
};
}
FAnimInstanceProxy* UAnanseLeopardAnimInstance::CreateAnimInstanceProxy(){return new FLeopardPoseProxy(this);}
void UAnanseLeopardAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy){delete Proxy;}
void UAnanseLeopardAnimInstance::RestartPresentationGraph(){check(IsInGameThread());static_cast<FLeopardPoseProxy&>(GetProxyOnGameThread<FAnimInstanceProxy>()).RestartPresentation();}
void UAnanseLeopardAnimInstance::NativePostEvaluateAnimation()
{
 Super::NativePostEvaluateAnimation();++GraphEvaluations;EvaluatedGraphClip=nullptr;
 for(const auto& Player:GetProxyOnGameThread<FAnimInstanceProxy>().GetUngroupedActivePlayersRead())
  if(auto* Sequence=Cast<UAnimSequence>(Player.SourceAsset.Get()))EvaluatedGraphClip=Sequence;
}
bool UAnanseAnimationAuthoring::PopulateClipGraph(UAnimBlueprint* Blueprint,UAnimSequence* DefaultClip,FString& Error)
{
 Error.Reset();
#if WITH_EDITOR
 if(!Blueprint || !DefaultClip || Blueprint->TargetSkeleton!=DefaultClip->GetSkeleton())
 {Error=TEXT("Missing Blueprint/clip or incompatible skeleton");return false;}
 TArray<UEdGraph*> Graphs;Blueprint->GetAllGraphs(Graphs);UEdGraph* Graph=nullptr;UAnimGraphNode_Root* Root=nullptr;
 for(UEdGraph* Candidate:Graphs)if(Candidate && Candidate->GetFName()==TEXT("AnimGraph"))Graph=Candidate;
 if(!Graph || Graph->Nodes.Num()!=1){Error=TEXT("Expected untouched default animation graph; existing authored nodes preserved");return false;}
 Root=Cast<UAnimGraphNode_Root>(Graph->Nodes[0]);
 if(!Root){Error=TEXT("Animation graph root missing");return false;}
 FGraphNodeCreator<UAnimGraphNode_SequencePlayer> PlayerCreator(*Graph);
 auto* Player=PlayerCreator.CreateNode();Player->Node.SetSequence(DefaultClip);Player->NodePosX=-300;PlayerCreator.Finalize();
 bool Found=false;
 for(auto& Pin:Player->ShowPinForProperties)if(Pin.PropertyName==TEXT("Sequence")){Pin.bShowPin=true;Found=true;}
 if(!Found){Error=TEXT("Sequence property pin not exposed by installed node API");return false;}
 Player->ReconstructNode();
 FGraphNodeCreator<UK2Node_VariableGet> VariableCreator(*Graph);
 auto* Variable=VariableCreator.CreateNode();Variable->VariableReference.SetSelfMember(TEXT("Clip"));Variable->NodePosX=-600;VariableCreator.Finalize();
 auto* AssetPin=Player->FindPin(TEXT("Sequence"));auto* PosePin=Player->FindPin(TEXT("Pose"));auto* ResultPin=Root->FindPin(TEXT("Result"));
 const auto* Schema=Graph->GetSchema();
 if(!AssetPin || !PosePin || !ResultPin || !Schema->TryCreateConnection(Variable->GetValuePin(),AssetPin) || !Schema->TryCreateConnection(PosePin,ResultPin))
 {Error=TEXT("Actual Clip -> Sequence Player -> Output Pose graph linkage failed");return false;}
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);FKismetEditorUtilities::CompileBlueprint(Blueprint);
 if(Blueprint->Status!=BS_UpToDate && Blueprint->Status!=BS_UpToDateWithWarnings){Error=TEXT("Animation graph compilation failed");return false;}
 Blueprint->MarkPackageDirty();return true;
#else
 Error=TEXT("Animation authoring is editor-only");return false;
#endif
}
bool UAnanseAnimationAuthoring::AddLeopardSockets(USkeletalMesh* Mesh,FString& Error)
{
 Error.Reset();
#if WITH_EDITOR
 if(!Mesh || Mesh->GetPathName()!=TEXT("/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard") || !Mesh->GetSkeleton())
 {Error=TEXT("Only the actual project-owned authored leopard mesh is accepted");return false;}
 USkeleton* Skeleton=Mesh->GetSkeleton();const auto& Ref=Mesh->GetRefSkeleton();TArray<FTransform> CS=Ref.GetRefBonePose();
 for(int32 I=0;I<CS.Num();++I)if(Ref.GetParentIndex(I)>=0)CS[I]=CS[I]*CS[Ref.GetParentIndex(I)];
 for(const TCHAR* Name:{TEXT("head"),TEXT("jaw"),TEXT("chest"),TEXT("clavicle_L"),TEXT("clavicle_R"),TEXT("hand_L"),TEXT("hand_R")})
  if(Ref.FindBoneIndex(Name)==INDEX_NONE){Error=TEXT("Required source bone missing");return false;}
 struct FSocket{FName Name,Bone;FVector ComponentPoint;};TArray<FSocket> Proposed;
 for(const TCHAR* Side:{TEXT("L"),TEXT("R")})
 {
  const FName Hand(*FString::Printf(TEXT("hand_%s"),Side));const FVector Origin=CS[Ref.FindBoneIndex(Hand)].GetTranslation();FVector Digits=FVector::ZeroVector;
  for(int32 I=0;I<4;++I)
  {const int32 Index=Ref.FindBoneIndex(*FString::Printf(TEXT("digit_%s_%d_01"),Side,I));if(Index==INDEX_NONE){Error=TEXT("Actual authored paw digits missing");return false;}Digits+=CS[Index].GetTranslation();}
  Proposed.Add({FName(*FString::Printf(TEXT("socket_capture_%s"),Side)),Hand,FMath::Lerp(Origin,Digits/4,.65)});
 }
 const int32 Jaw=Ref.FindBoneIndex(TEXT("jaw")),Head=Ref.FindBoneIndex(TEXT("head")),Chest=Ref.FindBoneIndex(TEXT("chest"));
 FVector Front=CS[Jaw].GetTranslation()-CS[Head].GetTranslation();Front.Z=0;Front.Normalize();
 FVector Left=CS[Ref.FindBoneIndex(TEXT("clavicle_L"))].GetTranslation()-CS[Ref.FindBoneIndex(TEXT("clavicle_R"))].GetTranslation();Left.Z=0;Left.Normalize();
 Proposed.Add({TEXT("socket_voice"),TEXT("jaw"),CS[Jaw].GetTranslation()+Front*12.5+FVector(0,0,-1.8)});
 Proposed.Add({TEXT("socket_cape"),TEXT("chest"),CS[Chest].GetTranslation()+Front*13.8+Left*11+FVector(0,0,10)});
 for(const auto& Socket:Proposed)if(Skeleton->FindSocket(Socket.Name))
 {Error=TEXT("Existing socket preserved; review before changing it");return false;}
 Skeleton->Modify();
 for(const auto& Item:Proposed)
 {
  auto* Socket=NewObject<USkeletalMeshSocket>(Skeleton,NAME_None,RF_Transactional);
  Socket->SocketName=Item.Name;Socket->BoneName=Item.Bone;
  Socket->RelativeLocation=CS[Ref.FindBoneIndex(Item.Bone)].InverseTransformPosition(Item.ComponentPoint);
  Socket->RelativeRotation=FRotator::ZeroRotator;Socket->RelativeScale=FVector::OneVector;Skeleton->Sockets.Add(Socket);
 }
 Skeleton->MarkPackageDirty();return true;
#else
 Error=TEXT("Socket authoring is editor-only");return false;
#endif
}
FString UAnanseAnimationAuthoring::DescribeRig(USkeletalMesh* Mesh)
{
 if(!Mesh || !Mesh->GetSkeleton())return TEXT("{}");
 const auto Vec=[](FVector V){return TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)};};
 auto Report=MakeShared<FJsonObject>();Report->SetStringField(TEXT("mesh"),Mesh->GetPathName());Report->SetStringField(TEXT("skeleton"),Mesh->GetSkeleton()->GetPathName());
 Report->SetStringField(TEXT("units"),TEXT("Native Unreal centimetres; rotations xyzw quaternion; local parent frame"));
 const auto& Ref=Mesh->GetRefSkeleton();TArray<TSharedPtr<FJsonValue>> Bones,Sockets,Materials,Bodies;
 for(int32 I=0;I<Ref.GetNum();++I)
 {
  const FTransform& T=Ref.GetRefBonePose()[I];auto Bone=MakeShared<FJsonObject>();
  Bone->SetStringField(TEXT("name"),Ref.GetBoneName(I).ToString());Bone->SetNumberField(TEXT("parent_index"),Ref.GetParentIndex(I));
  Bone->SetArrayField(TEXT("local_translation_cm"),Vec(T.GetTranslation()));Bone->SetArrayField(TEXT("scale"),Vec(T.GetScale3D()));
  const FQuat Q=T.GetRotation();Bone->SetArrayField(TEXT("local_rotation_xyzw"),{MakeShared<FJsonValueNumber>(Q.X),MakeShared<FJsonValueNumber>(Q.Y),MakeShared<FJsonValueNumber>(Q.Z),MakeShared<FJsonValueNumber>(Q.W)});
  Bone->SetArrayField(TEXT("local_x_axis"),Vec(Q.GetAxisX()));Bone->SetArrayField(TEXT("local_y_axis"),Vec(Q.GetAxisY()));Bone->SetArrayField(TEXT("local_z_axis"),Vec(Q.GetAxisZ()));
  Bones.Add(MakeShared<FJsonValueObject>(Bone));
 }
 for(const auto& Socket:Mesh->GetActiveSocketList())if(Socket)
 {
  auto S=MakeShared<FJsonObject>();S->SetStringField(TEXT("name"),Socket->SocketName.ToString());S->SetStringField(TEXT("bone"),Socket->BoneName.ToString());
  S->SetArrayField(TEXT("relative_location_cm"),Vec(Socket->RelativeLocation));S->SetArrayField(TEXT("relative_rotation_pitch_yaw_roll"),Vec(FVector(Socket->RelativeRotation.Pitch,Socket->RelativeRotation.Yaw,Socket->RelativeRotation.Roll)));
  S->SetArrayField(TEXT("scale"),Vec(Socket->RelativeScale));Sockets.Add(MakeShared<FJsonValueObject>(S));
 }
 for(const auto& Material:Mesh->GetMaterials())
 {
  auto M=MakeShared<FJsonObject>();M->SetStringField(TEXT("slot"),Material.MaterialSlotName.ToString());M->SetStringField(TEXT("material"),Material.MaterialInterface?Material.MaterialInterface->GetPathName():TEXT("missing"));Materials.Add(MakeShared<FJsonValueObject>(M));
 }
 if(const auto* Physics=Mesh->GetPhysicsAsset())
 {
  Report->SetStringField(TEXT("physics"),Physics->GetPathName());
  for(const auto& Body:Physics->SkeletalBodySetups)if(Body)
  {auto B=MakeShared<FJsonObject>();B->SetStringField(TEXT("bone"),Body->BoneName.ToString());B->SetNumberField(TEXT("primitive_count"),Body->AggGeom.GetElementCount());B->SetBoolField(TEXT("kinematic"),Body->PhysicsType==PhysType_Kinematic);B->SetBoolField(TEXT("collision_disabled"),Body->CollisionReponse==EBodyCollisionResponse::BodyCollision_Disabled);Bodies.Add(MakeShared<FJsonValueObject>(B));}
 }
 Report->SetArrayField(TEXT("bones"),Bones);Report->SetArrayField(TEXT("socket_objects"),Sockets);Report->SetArrayField(TEXT("material_slots"),Materials);Report->SetArrayField(TEXT("physics_bodies"),Bodies);
 Report->SetNumberField(TEXT("lod_count"),Mesh->GetLODNum());Report->SetArrayField(TEXT("imported_bounds_extent_cm"),Vec(FVector(Mesh->GetBounds().BoxExtent)));
 TArray<TSharedPtr<FJsonValue>> Lods;
 if(const auto* Data=Mesh->GetResourceForRendering())for(int32 I=0;I<Data->LODRenderData.Num();++I)
 {const auto& L=Data->LODRenderData[I];auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("lod"),I);J->SetNumberField(TEXT("vertices"),L.GetNumVertices());J->SetNumberField(TEXT("triangles"),L.GetTotalFaces());int32 Influences=0;for(const auto& Section:L.RenderSections)Influences=FMath::Max(Influences,int32(Section.MaxBoneInfluences));J->SetNumberField(TEXT("max_influences"),Influences);Lods.Add(MakeShared<FJsonValueObject>(J));}
 Report->SetArrayField(TEXT("lods"),Lods);
 TArray<TSharedPtr<FJsonValue>> Morphs;for(const auto& Morph:Mesh->GetMorphTargets())if(Morph)Morphs.Add(MakeShared<FJsonValueString>(Morph->GetName()));Report->SetArrayField(TEXT("morph_targets"),Morphs);
 FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(Report,Writer);return Json;
}
bool UAnanseAnimationAuthoring::PrepareLeopardQuality(USkeletalMesh* Mesh,FString& Error)
{
 Error.Reset();
#if WITH_EDITOR
 bool Allowed=Mesh && Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard");
 Allowed |= Mesh && ((Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Visual_v001/Kwaku.Kwaku")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Visual_v002/Kwaku.Kwaku")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Visual_v003/Kwaku.Kwaku")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku"))))||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v001/OseboLeopard.OseboLeopard")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v002/OseboLeopard.OseboLeopard")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v003/OseboLeopard.OseboLeopard")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/OseboLeopard.OseboLeopard"))))||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v005/Kwaku.Kwaku")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/Interactions_v003/OseboLeopard.OseboLeopard"));
 for(const TCHAR* Key:{TEXT("Kwaku"),TEXT("AsoYaa"),TEXT("EsiHuman"),TEXT("OseboHuman"),TEXT("KojoTortoise"),TEXT("KofiHornbill"),TEXT("EsiMoth")})
  Allowed |= Mesh && Mesh->GetPathName()==FString::Printf(TEXT("/Game/Ananse/Characters/%s/Story_v001/%s.%s"),Key,Key,Key);
 const bool Aso=Mesh && (Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v001/AsoYaa.AsoYaa")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v002/AsoYaa.AsoYaa")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v001/AsoYaa.AsoYaa")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa")));
 Allowed |= Aso;
 if(!Allowed || (Mesh->GetLODNum()!=1 && !(Aso && Mesh->GetLODNum()==3)) || !Mesh->GetPhysicsAsset())
 {Error=TEXT("Expected allowlisted project-owned character LOD0 and physics; existing revisions preserved");return false;}
 auto* Physics=Mesh->GetPhysicsAsset();
 for(const auto& B:Physics->SkeletalBodySetups)
 {
  if(!B || B->AggGeom.GetElementCount()<1 || Mesh->GetRefSkeleton().FindBoneIndex(B->BoneName)<0){Error=TEXT("Missing physics primitive/bone");return false;}
  for(const auto& S:B->AggGeom.SphylElems)if(!FMath::IsFinite(S.Radius)||!FMath::IsFinite(S.Length)||S.Radius<=0||S.Length<0||S.Center.ContainsNaN()){Error=TEXT("Invalid capsule primitive");return false;}
  for(const auto& S:B->AggGeom.BoxElems)if(!FMath::IsFinite(S.X)||!FMath::IsFinite(S.Y)||!FMath::IsFinite(S.Z)||S.X<=0||S.Y<=0||S.Z<=0||S.Center.ContainsNaN()){Error=TEXT("Invalid box primitive");return false;}
 }
 Mesh->Modify();Physics->Modify();
 for(const auto& B:Physics->SkeletalBodySetups)
 {
  B->Modify();B->PhysicsType=PhysType_Kinematic;
  const FString Name=B->BoneName.ToString();B->CollisionReponse=Name.StartsWith(TEXT("cape_"))||Name.StartsWith(TEXT("tail_"))?EBodyCollisionResponse::BodyCollision_Disabled:EBodyCollisionResponse::BodyCollision_Enabled;
 }
 if(Mesh->GetLODNum()==1)for(int32 I=1;I<=2;++I)
 {auto& Info=Mesh->AddLODInfo();Info.ReductionSettings.BaseLOD=0;Info.ReductionSettings.NumOfTrianglesPercentage=I==1?.5f:.25f;Info.ReductionSettings.MaxBonesPerVertex=4;Info.ScreenSize.Default=I==1?.45f:.2f;}
 Physics->MarkPackageDirty();Mesh->MarkPackageDirty();return true;
#else
 Error=TEXT("Editor-only qualification preparation");return false;
#endif
}

bool UAnanseAnimationAuthoring::AddStorySockets(USkeletalMesh* Mesh,FString& Error)
{
 Error.Reset();
#if WITH_EDITOR
 if(!Mesh){Error=TEXT("Missing materialized mesh");return false;}
 const FString Key=Mesh->GetName();bool Allowed=false;
 for(const TCHAR* Candidate:{TEXT("Kwaku"),TEXT("AsoYaa"),TEXT("EsiHuman"),TEXT("OseboHuman"),TEXT("KojoTortoise"),TEXT("KofiHornbill"),TEXT("EsiMoth")})
  Allowed |= Key==Candidate && Mesh->GetPathName()==FString::Printf(TEXT("/Game/Ananse/Characters/%s/Story_v001/%s.%s"),Candidate,Candidate,Candidate);
 Allowed |= Key==TEXT("AsoYaa")&&(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa"));
 Allowed |= Key==TEXT("AsoYaa")&&(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v001/AsoYaa.AsoYaa")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Negotiation_v002/AsoYaa.AsoYaa")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v001/AsoYaa.AsoYaa")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa")));
 if(!Allowed){Error=TEXT("Only allowlisted project-owned story mesh revisions may be edited");return false;}
 TMap<FName,FName> Binding;
 auto Add=[&](const TCHAR* Name,const TCHAR* Bone){Binding.Add(FName(Name),FName(Bone));};
 Add(TEXT("socket_voice"),TEXT("jaw"));
 if(Key==TEXT("Kwaku")||Key==TEXT("EsiMoth")){Add(TEXT("socket_thread_L"),TEXT("hand_L"));Add(TEXT("socket_thread_R"),TEXT("hand_R"));}
 if(Key==TEXT("Kwaku")){Add(TEXT("socket_ledger"),TEXT("hand_R"));Add(TEXT("socket_pouch"),TEXT("pelvis"));}
 if(Key==TEXT("AsoYaa")){Add(TEXT("socket_ledger_L"),TEXT("hand_L"));Add(TEXT("socket_ledger_R"),TEXT("hand_R"));}
 if(Key==TEXT("EsiHuman")){Add(TEXT("socket_instrument"),TEXT("instrument"));Add(TEXT("socket_instrument_hand_L"),TEXT("hand_L"));Add(TEXT("socket_instrument_hand_R"),TEXT("hand_R"));}
 if(Key==TEXT("OseboHuman")){Add(TEXT("socket_capture_L"),TEXT("hand_L"));Add(TEXT("socket_capture_R"),TEXT("hand_R"));Add(TEXT("socket_cape"),TEXT("chest"));}
 if(Key==TEXT("KojoTortoise")){Add(TEXT("socket_staff_L"),TEXT("hand_L"));Add(TEXT("socket_staff_R"),TEXT("hand_R"));Add(TEXT("socket_pouch"),TEXT("pelvis"));Add(TEXT("socket_evidence"),TEXT("hand_L"));}
 if(Key==TEXT("KofiHornbill")){Add(TEXT("socket_satchel"),TEXT("pelvis"));Add(TEXT("socket_optic_L"),TEXT("hand_L"));Add(TEXT("socket_optic_R"),TEXT("hand_R"));}
 if(Key==TEXT("EsiMoth"))Add(TEXT("socket_pendant"),TEXT("chest"));
 for(const auto& Pair:Binding)if(Mesh->GetRefSkeleton().FindBoneIndex(Pair.Value)<0 || Mesh->FindSocket(Pair.Key))
 {Error=TEXT("Socket already exists or referenced bone is absent; existing authored data preserved");return false;}
 Mesh->Modify();
 for(const auto& Pair:Binding){auto* Socket=NewObject<USkeletalMeshSocket>(Mesh);Socket->SocketName=Pair.Key;Socket->BoneName=Pair.Value;Socket->RelativeLocation=FVector::ZeroVector;Socket->RelativeRotation=FRotator::ZeroRotator;Socket->RelativeScale=FVector::OneVector;Mesh->GetMeshOnlySocketList().Add(Socket);}
 Mesh->MarkPackageDirty();return true;
#else
 Error=TEXT("Editor-only socket authoring");return false;
#endif
}

FString UAnanseAnimationAuthoring::PrepareInteractionSurface(USkeletalMesh* Mesh)
{
#if WITH_EDITOR
 const bool Kwaku=Mesh&&(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v005/Kwaku.Kwaku")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Visual_v001/Kwaku.Kwaku")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Visual_v002/Kwaku.Kwaku")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/Visual_v003/Kwaku.Kwaku")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku")))));
 const bool Leopard=Mesh&&(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/Interactions_v003/OseboLeopard.OseboLeopard")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v001/OseboLeopard.OseboLeopard")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v002/OseboLeopard.OseboLeopard")||(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v003/OseboLeopard.OseboLeopard")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/OseboLeopard.OseboLeopard")))));
 if(!Kwaku&&!Leopard)return TEXT("Rejected: only the two new interaction revisions may be prepared");
 FString Error;if(!PrepareLeopardQuality(Mesh,Error))return TEXT("Quality preparation failed: ")+Error;
 if(Kwaku)
 {
  for(const auto& Pair:TMap<FName,FName>{{TEXT("socket_voice"),TEXT("jaw")},{TEXT("socket_thread_L"),TEXT("hand_L")},{TEXT("socket_thread_R"),TEXT("hand_R")},{TEXT("socket_ledger"),TEXT("hand_R")},{TEXT("socket_pouch"),TEXT("pelvis")}})
  {
   if(Mesh->GetRefSkeleton().FindBoneIndex(Pair.Value)<0||Mesh->FindSocket(Pair.Key))return TEXT("Missing bone or pre-existing mesh socket: ")+Pair.Key.ToString();
   auto* Socket=NewObject<USkeletalMeshSocket>(Mesh);Socket->SocketName=Pair.Key;Socket->BoneName=Pair.Value;Mesh->GetMeshOnlySocketList().Add(Socket);
  }
 }
 else for(const TCHAR* Socket:{TEXT("socket_capture_L"),TEXT("socket_capture_R"),TEXT("socket_cape"),TEXT("socket_voice")})if(!Mesh->FindSocket(Socket))return FString(TEXT("Missing preserved feline socket: "))+Socket;
 Mesh->MarkPackageDirty();return TEXT("ok");
#else
 return TEXT("Editor-only preparation");
#endif
}

FString UAnanseAnimationAuthoring::DescribeSkinProbe(USkeletalMesh* Mesh,UAnimSequence* Clip,FVector RestPoint,float Time)
{
#if WITH_EDITOR
 if(!Mesh||!Clip||Mesh->GetSkeleton()!=Clip->GetSkeleton()||!Mesh->GetResourceForRendering())return TEXT("{}");
 const auto& LOD=Mesh->GetResourceForRendering()->LODRenderData[0];auto* Weights=LOD.GetSkinWeightVertexBuffer();if(!Weights)return TEXT("{}");
 int32 Vertex=INDEX_NONE;double Distance=TNumericLimits<double>::Max();for(uint32 I=0;I<LOD.GetNumVertices();++I){const double D=FVector::DistSquared(FVector(LOD.StaticVertexBuffers.PositionVertexBuffer.VertexPosition(I)),RestPoint);if(D<Distance){Vertex=I;Distance=D;}}
 if(Vertex==INDEX_NONE)return TEXT("{}");const FSkelMeshRenderSection* Section=nullptr;for(const auto& S:LOD.RenderSections)if(uint32(Vertex)>=S.BaseVertexIndex&&uint32(Vertex)<S.BaseVertexIndex+S.NumVertices){Section=&S;break;}if(!Section)return TEXT("{}");
 const auto& Ref=Mesh->GetRefSkeleton();TArray<FTransform> CS;CS.SetNum(Ref.GetNum());for(int32 I=0;I<CS.Num();++I){Clip->GetBoneTransform(CS[I],FSkeletonPoseBoneIndex(I),FAnimExtractContext(double(Time),false),true);if(Ref.GetParentIndex(I)>=0)CS[I]=CS[I]*CS[Ref.GetParentIndex(I)];}
 FVector Result=FVector::ZeroVector;double Sum=0;for(uint32 I=0;I<Weights->GetMaxBoneInfluences();++I)Sum+=Weights->GetBoneWeight(Vertex,I);if(Sum<=0)return TEXT("{}");
 auto Json=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Influences;const FVector Rest=FVector(LOD.StaticVertexBuffers.PositionVertexBuffer.VertexPosition(Vertex));
 for(uint32 I=0;I<Weights->GetMaxBoneInfluences();++I)
 {
  const double Weight=Weights->GetBoneWeight(Vertex,I)/Sum;if(Weight<=0)continue;const int32 Local=Weights->GetBoneIndex(Vertex,I);if(!Section->BoneMap.IsValidIndex(Local))return TEXT("{}");const int32 Bone=Section->BoneMap[Local];const FMatrix Matrix=FMatrix(Mesh->GetRefBasesInvMatrix()[Bone])*CS[Bone].ToMatrixWithScale();Result+=FVector(Matrix.TransformPosition(Rest))*Weight;
  auto Entry=MakeShared<FJsonObject>();Entry->SetStringField(TEXT("bone"),Ref.GetBoneName(Bone).ToString());Entry->SetNumberField(TEXT("weight"),Weight);Influences.Add(MakeShared<FJsonValueObject>(Entry));
 }
 Json->SetNumberField(TEXT("vertex"),Vertex);Json->SetNumberField(TEXT("rest_distance_cm"),FMath::Sqrt(Distance));Json->SetStringField(TEXT("rest_position"),Rest.ToString());Json->SetStringField(TEXT("skinned_position"),Result.ToString());Json->SetArrayField(TEXT("influences"),Influences);FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Json,Writer);return Text;
#else
 return TEXT("{}");
#endif
}

FString UAnanseAnimationAuthoring::CorrectInteractionImportFrame(USkeletalMesh* Mesh)
{
#if WITH_EDITOR
 const bool AsoContact=Mesh&&(Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa")||Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa"));
 const TSet<FString> Allowed={TEXT("/Game/Ananse/Characters/Kwaku/Visual_v001/Kwaku.Kwaku"),TEXT("/Game/Ananse/Characters/Kwaku/Visual_v002/Kwaku.Kwaku"),TEXT("/Game/Ananse/Characters/Kwaku/Visual_v003/Kwaku.Kwaku"),TEXT("/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku"),TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v001/OseboLeopard.OseboLeopard"),TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v002/OseboLeopard.OseboLeopard"),TEXT("/Game/Ananse/Characters/OseboLeopard/Visual_v003/OseboLeopard.OseboLeopard"),TEXT("/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/OseboLeopard.OseboLeopard"),TEXT("/Game/Ananse/Characters/Kwaku/Interactions_v005/Kwaku.Kwaku"),TEXT("/Game/Ananse/Characters/OseboLeopard/Interactions_v003/OseboLeopard.OseboLeopard"),TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa"),TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa"),TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa")};
 if(!Mesh||!Allowed.Contains(Mesh->GetPathName()))return TEXT("Rejected: only exact fresh coordinate-qualified interaction revisions");
 if((Mesh->GetLODNum()!=1&&!AsoContact)||Mesh->GetOutermost()->GetMetaData().HasValue(Mesh,TEXT("AnanseImportFrame")))return TEXT("Rejected: one-time frame correction; prior authored data preserved");
 FMeshDescription* Description=Mesh->GetMeshDescription(0);if(!Description)return TEXT("Missing editable mesh description");FSkeletalMeshAttributes Attributes(*Description);const auto Morphs=Attributes.GetMorphTargetNames();
 if((Mesh->GetName()==TEXT("Kwaku")||AsoContact)&&(!Morphs.Contains(TEXT("Blink_L"))||!Morphs.Contains(TEXT("Blink_R"))))return TEXT("Missing editable eyelid morph deltas");
 Mesh->Modify();const FQuat4f Rotation(FVector3f::UpVector,UE_HALF_PI);auto Positions=Attributes.GetVertexPositions();FBox Bounds(ForceInit);
 for(const FVertexID Vertex:Description->Vertices().GetElementIDs()){Positions[Vertex]=Rotation.RotateVector(Positions[Vertex]);Bounds+=FVector(Positions[Vertex]);}
 auto Normals=Attributes.GetVertexInstanceNormals();auto Tangents=Attributes.GetVertexInstanceTangents();
 for(const FVertexInstanceID Vertex:Description->VertexInstances().GetElementIDs()){Normals[Vertex]=Rotation.RotateVector(Normals[Vertex]);Tangents[Vertex]=Rotation.RotateVector(Tangents[Vertex]);}
 for(const FName Morph:Morphs)
 {
  auto Delta=Attributes.GetVertexMorphPositionDelta(Morph);if(Delta.IsValid())for(const FVertexID Vertex:Description->Vertices().GetElementIDs())Delta[Vertex]=Rotation.RotateVector(Delta[Vertex]);
  auto NormalDelta=Attributes.GetVertexInstanceMorphNormalDelta(Morph);if(NormalDelta.IsValid())for(const FVertexInstanceID Vertex:Description->VertexInstances().GetElementIDs())NormalDelta[Vertex]=Rotation.RotateVector(NormalDelta[Vertex]);
 }
 if(!Mesh->CommitMeshDescription(0))return TEXT("Mesh description commit failed");Mesh->SetImportedBounds(FBoxSphereBounds(Bounds));Mesh->PostEditChange();FSkinnedAssetCompilingManager::Get().FinishCompilation({Mesh});Mesh->CalculateExtendedBounds();Mesh->GetOutermost()->GetMetaData().SetValue(Mesh,TEXT("AnanseImportFrame"),TEXT("geometry_yaw90_normals_morphs_rotated_reference_skeleton_unchanged"));Mesh->MarkPackageDirty();return TEXT("ok");
#else
 return TEXT("Editor-only frame correction");
#endif
}

FString UAnanseAnimationAuthoring::AuthorAsoLedgerGrip(USkeletalMesh* Mesh,UAnimSequence* Clip)
{
#if WITH_EDITOR
 if(!Mesh||(Mesh->GetPathName()!=TEXT("/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa")&&Mesh->GetPathName()!=TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa")&&Mesh->GetPathName()!=TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa"))||!Clip||Clip->GetSkeleton()!=Mesh->GetSkeleton()||!Clip->GetName().Contains(TEXT("InspectEvidence")))return TEXT("Rejected incompatible contact authoring revision");
 const auto& Ref=Mesh->GetRefSkeleton();TArray<FTransform> CS;CS.SetNum(Ref.GetNum());
 for(int32 I=0;I<CS.Num();++I){Clip->GetBoneTransform(CS[I],FSkeletonPoseBoneIndex(I),FAnimExtractContext(1.6,false),true);if(Ref.GetParentIndex(I)>=0)CS[I]=CS[I]*CS[Ref.GetParentIndex(I)];}
 auto* Socket=const_cast<USkeletalMeshSocket*>(Mesh->FindSocket(TEXT("socket_ledger_R")));const int32 Hand=Ref.FindBoneIndex(TEXT("hand_R"));if(!Socket||Hand<0)return TEXT("Missing real socket or hand");
 const FTransform Grip=FTransform(FQuat::Identity,FVector(30,0,103)).GetRelativeTransform(CS[Hand]);Socket->Modify();Socket->RelativeLocation=Grip.GetLocation();Socket->RelativeRotation=Grip.Rotator();Socket->RelativeScale=Grip.GetScale3D();Mesh->MarkPackageDirty();return FString();
#else
 return TEXT("Editor only");
#endif
}

FString UAnanseAnimationAuthoring::DescribeAuthoredBonePose(USkeletalMesh* Mesh,UAnimSequence* Clip,float Time)
{
#if WITH_EDITOR
 if(!Mesh||!Clip||Mesh->GetSkeleton()!=Clip->GetSkeleton()||!FMath::IsFinite(Time)||Time<0||Time>Clip->GetPlayLength())return TEXT("{}");
 const auto& Ref=Mesh->GetRefSkeleton();TArray<FTransform> CS;CS.SetNum(Ref.GetNum());auto Result=MakeShared<FJsonObject>();
 for(int32 I=0;I<CS.Num();++I)
 {
  Clip->GetBoneTransform(CS[I],FSkeletonPoseBoneIndex(I),FAnimExtractContext(double(Time),false),true);if(Ref.GetParentIndex(I)>=0)CS[I]=CS[I]*CS[Ref.GetParentIndex(I)];
  TArray<TSharedPtr<FJsonValue>> Position;const FVector P=CS[I].GetLocation();for(double V:{P.X,P.Y,P.Z})Position.Add(MakeShared<FJsonValueNumber>(V));Result->SetArrayField(Ref.GetBoneName(I).ToString(),Position);
 }
 FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Result,Writer);return Text;
#else
 return TEXT("{}");
#endif
}
