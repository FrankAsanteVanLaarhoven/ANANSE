#include "AnanseAsoSurfaceProbe.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "StaticMeshResources.h"
#include "GameFramework/Actor.h"
#include "Engine/World.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#include "Rendering/SkinWeightVertexBuffer.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "Json.h"
namespace
{
void AuditLedgerSupport(USkeletalMeshComponent* Skin,UAnimSequence* Clip,float Time,uint32 Epoch)
{
 FString File;if(!FParse::Value(FCommandLine::Get(),TEXT("AnanseAsoSupportAudit="),File)||!Skin||!Clip||Time<0)return;
 auto* Mesh=Skin->GetSkeletalMeshAsset();if(!Mesh||(Mesh->GetPathName()!=TEXT("/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa")&&Mesh->GetPathName()!=TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa")))return;
 auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("epoch"),Epoch);J->SetNumberField(TEXT("evaluated_time"),Time);J->SetNumberField(TEXT("world_seconds"),Skin->GetWorld()->GetTimeSeconds());J->SetNumberField(TEXT("monotonic_seconds"),FPlatformTime::Seconds());J->SetStringField(TEXT("clip"),Clip->GetPathName());J->SetStringField(TEXT("actor"),Skin->GetOwner()->GetName());
 UStaticMeshComponent* Prop=nullptr;UStaticMeshComponent* Stand=nullptr;TInlineComponentArray<UStaticMeshComponent*> Components(Skin->GetOwner());for(auto* C:Components){if(C->GetFName()==TEXT("LedgerPresentation"))Prop=C;if(C->GetFName()==TEXT("AsoLedgerSupport"))Stand=C;}
 const bool Inspect=Clip->GetName().Contains(TEXT("InspectEvidence"));const bool Held=Inspect&&Time>=1.6f&&Time<6.8f;bool Valid=Prop&&Stand&&Prop->GetStaticMesh()&&Stand->GetStaticMesh();
 J->SetStringField(TEXT("support_state"),!Inspect?TEXT("presentation_stowed"):Held?TEXT("both_hands"):TEXT("table"));J->SetBoolField(TEXT("prop_visible"),Prop&&Prop->IsVisible());
 if(Valid&&!Inspect)Valid=!Prop->IsVisible();
 if(Valid&&Inspect)
 {
  Valid=Prop->IsVisible()&&Stand->IsVisible();
  if(Held)
  {
   const auto& LOD=Mesh->GetResourceForRendering()->LODRenderData[0];auto* Weights=LOD.GetSkinWeightVertexBuffer();Valid &= Weights&&Weights->GetDataVertexBuffer()->GetWeightData()!=nullptr&&LOD.StaticVertexBuffers.PositionVertexBuffer.GetVertexData()!=nullptr;
   if(Valid)
   {
    struct FMarkers{TArray<int32> Indices;double RestError=0;};static TMap<TWeakObjectPtr<USkeletalMesh>,FMarkers> Cache;auto& Markers=Cache.FindOrAdd(Mesh);
    if(Markers.Indices.IsEmpty())
    {
     const FVector Expected[]={{4.658439755,28.029343486,86.241745949},{3.766359761,26.566737890,81.295883656},{4.088330641,27.719998360,80.498969555},{4.658439755,-28.029343486,86.241745949},{3.766359761,-26.566737890,81.295883656},{4.088330641,-27.719998360,80.498969555}};
     // Same six editable source vertex identities, remapped only for the refined mesh.
     const FVector ArtExpected[]={{4.658439636230,28.029342651367,86.241744995117},{3.766359806061,26.566738128662,81.295883178711},{4.071629047394,27.721494674683,80.501312255859},{4.658439636230,-28.029342651367,86.241744995117},{3.766359806061,-26.566738128662,81.295883178711},{4.074292659760,-27.721256256104,80.500930786133}};
     const bool ArtRevision=Mesh->GetPathName()==TEXT("/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa.AsoYaa");
     const TArrayView<const FVector> ActiveExpected=ArtRevision?MakeArrayView(ArtExpected):MakeArrayView(Expected);
     for(const FVector& P:ActiveExpected){double Best=TNumericLimits<double>::Max();int32 Index=INDEX_NONE;for(uint32 I=0;I<LOD.GetNumVertices();++I){const double D=FVector::DistSquared(P,FVector(LOD.StaticVertexBuffers.PositionVertexBuffer.VertexPosition(I)));if(D<Best){Best=D;Index=I;}}Markers.Indices.Add(Index);Markers.RestError=FMath::Max(Markers.RestError,FMath::Sqrt(Best));}
    }
    Valid &= Markers.RestError<.01;J->SetNumberField(TEXT("marker_rest_error_cm"),Markers.RestError);TArray<FMatrix44f> Matrices;Skin->GetCurrentRefToLocalMatrices(Matrices,0);const FBox Box=Prop->GetStaticMesh()->GetBoundingBox();double Nearest[2]={1e9,1e9};
    for(int32 M=0;M<Markers.Indices.Num();++M){FVector P(USkeletalMeshComponent::GetSkinnedVertexPosition(Skin,Markers.Indices[M],LOD,*Weights,Matrices));P=Prop->GetComponentTransform().InverseTransformPosition(Skin->GetComponentTransform().TransformPosition(P));const FVector D(FMath::Max3(Box.Min.X-P.X,0.,P.X-Box.Max.X),FMath::Max3(Box.Min.Y-P.Y,0.,P.Y-Box.Max.Y),FMath::Max3(Box.Min.Z-P.Z,0.,P.Z-Box.Max.Z));Nearest[M/3]=FMath::Min(Nearest[M/3],D.Size());}
    J->SetNumberField(TEXT("left_contact_vertex_distance_cm"),Nearest[0]);J->SetNumberField(TEXT("right_contact_vertex_distance_cm"),Nearest[1]);Valid &= Nearest[0]<=.5&&Nearest[1]<=.5;
   }
  }
  else
  {
   const FBox Book=Prop->GetStaticMesh()->GetBoundingBox().TransformBy(Prop->GetComponentTransform().ToMatrixWithScale()),Table=Stand->GetStaticMesh()->GetBoundingBox().TransformBy(Stand->GetComponentTransform().ToMatrixWithScale());const double Gap=Book.Min.Z-Table.Max.Z;J->SetNumberField(TEXT("table_vertical_gap_cm"),Gap);Valid &= FMath::Abs(Gap)<=.2&&Book.Min.X>=Table.Min.X-.01&&Book.Max.X<=Table.Max.X+.01&&Book.Min.Y>=Table.Min.Y-.01&&Book.Max.Y<=Table.Max.Y+.01;
  }
 }
 J->SetBoolField(TEXT("supported_sample"),Valid);FString Text;auto Writer=TJsonWriterFactory<TCHAR,TCondensedJsonPrintPolicy<TCHAR>>::Create(&Text);FJsonSerializer::Serialize(J,Writer);IFileManager::Get().MakeDirectory(*FPaths::GetPath(File),true);FFileHelper::SaveStringToFile(Text+TEXT("\n"),*File,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);
}
}

void CaptureAsoSurface(USkeletalMeshComponent* Skin,UAnimSequence* Clip,float Time,TSet<FString>& Captured,uint32 Epoch)
{
 AuditLedgerSupport(Skin,Clip,Time,Epoch);
 FString Folder;if(!FParse::Value(FCommandLine::Get(),TEXT("AnanseAsoSurfaceCapture="),Folder)||!Skin||!Clip||Time<0)return;
 const FString Name=Clip->GetName();if(!Name.Contains(TEXT("WalkControlled"))&&!Name.Contains(TEXT("Turn"))&&!Name.Contains(TEXT("InspectEvidence"))&&!Name.Contains(TEXT("LimbIsolation")))return;
 const FString Key=FString::Printf(TEXT("%s_%u_%s_%03d"),*Skin->GetOwner()->GetName(),Epoch,*Name,FMath::FloorToInt(Time*4));if(Captured.Contains(Key))return;Captured.Add(Key);
 check(IsInGameThread());auto* Mesh=Skin->GetSkeletalMeshAsset();if(!Mesh||!Mesh->GetResourceForRendering())return;
 const auto& LOD=Mesh->GetResourceForRendering()->LODRenderData[0];const auto* Weights=LOD.GetSkinWeightVertexBuffer();if(!Weights)return;
 IFileManager::Get().MakeDirectory(*Folder,true);
 if(!Weights->GetDataVertexBuffer()->GetWeightData()||!LOD.StaticVertexBuffers.PositionVertexBuffer.GetVertexData()||LOD.MultiSizeIndexContainer.GetIndexBuffer()->Num()==0)
 {FFileHelper::SaveStringToFile(TEXT("Native CPU buffers unavailable; surface capture BLOCKED, not a clearance pass."),*(Folder/TEXT("probe-failure.txt")));return;}
 TArray<FMatrix44f> RefToLocal;Skin->GetCurrentRefToLocalMatrices(RefToLocal,0);
 TArray<uint8> Bytes;Bytes.Reserve(LOD.GetNumVertices()*24);auto Append=[&](const auto& V){Bytes.Append(reinterpret_cast<const uint8*>(&V),sizeof(V));};
 const uint32 Count=LOD.GetNumVertices();Append(Count);
 for(uint32 I=0;I<Count;++I){const FVector3f Rest=LOD.StaticVertexBuffers.PositionVertexBuffer.VertexPosition(I);Append(Rest);const FVector3f Final=USkeletalMeshComponent::GetSkinnedVertexPosition(Skin,I,LOD,*Weights,RefToLocal);Append(Final);}
 FFileHelper::SaveArrayToFile(Bytes,*(Folder/(Key+TEXT(".bin"))));
 auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("mesh"),Mesh->GetPathName());J->SetStringField(TEXT("skeleton"),Mesh->GetSkeleton()->GetPathName());J->SetStringField(TEXT("clip"),Clip->GetPathName());J->SetStringField(TEXT("animation_instance"),Skin->GetAnimInstance()->GetClass()->GetPathName());J->SetNumberField(TEXT("evaluated_time"),Time);J->SetBoolField(TEXT("secondary_disabled"),FParse::Param(FCommandLine::Get(),TEXT("AnanseDisableSecondaryMotion")));J->SetNumberField(TEXT("vertices"),Count);J->SetNumberField(TEXT("predicted_render_lod"),Skin->GetPredictedLODLevel());J->SetStringField(TEXT("coordinates"),TEXT("component space centimetres, final evaluated bone matrices; CPU skin position excludes material displacement/morph deltas. Garment/leg regions have no active corrective morph."));
 TInlineComponentArray<UStaticMeshComponent*> Components(Skin->GetOwner());
 for(auto* C:Components)if((C->GetFName()==TEXT("LedgerPresentation")||C->GetFName()==TEXT("AsoLedgerSupport"))&&C->GetStaticMesh())
 {
  auto P=MakeShared<FJsonObject>();const FTransform T=C->GetComponentTransform().GetRelativeTransform(Skin->GetComponentTransform());
  auto V=[](FVector A){TArray<TSharedPtr<FJsonValue>> R;for(double X:{A.X,A.Y,A.Z})R.Add(MakeShared<FJsonValueNumber>(X));return R;};
  P->SetBoolField(TEXT("visible"),C->IsVisible());P->SetStringField(TEXT("mesh"),C->GetStaticMesh()->GetPathName());P->SetArrayField(TEXT("translation"),V(T.GetLocation()));P->SetArrayField(TEXT("scale"),V(T.GetScale3D()));const FQuat Q=T.GetRotation();TArray<TSharedPtr<FJsonValue>> Quat;for(double X:{Q.X,Q.Y,Q.Z,Q.W})Quat.Add(MakeShared<FJsonValueNumber>(X));P->SetArrayField(TEXT("quaternion_xyzw"),Quat);const FBox Box=C->GetStaticMesh()->GetBoundingBox();P->SetArrayField(TEXT("bounds_min"),V(Box.Min));P->SetArrayField(TEXT("bounds_max"),V(Box.Max));J->SetObjectField(C->GetFName().ToString(),P);
 }
 // Exact imported static prop triangles for offline final-surface contact checks.
 const FString PropFile=Folder/TEXT("ledger-static-geometry.json");
 if(!IFileManager::Get().FileExists(*PropFile))for(auto* C:Components)if(C->GetFName()==TEXT("LedgerPresentation")&&C->GetStaticMesh())
 {
  const auto* Data=C->GetStaticMesh()->GetRenderData();
  if(Data&&Data->LODResources.Num()>0)
  {
   const auto& L=Data->LODResources[0];
   if(L.VertexBuffers.PositionVertexBuffer.GetVertexData()&&L.IndexBuffer.GetNumIndices()>0)
   {
    auto P=MakeShared<FJsonObject>();P->SetStringField(TEXT("mesh"),C->GetStaticMesh()->GetPathName());TArray<TSharedPtr<FJsonValue>> Vertices,Indices;
    for(uint32 I=0;I<L.VertexBuffers.PositionVertexBuffer.GetNumVertices();++I){TArray<TSharedPtr<FJsonValue>> V;const auto A=L.VertexBuffers.PositionVertexBuffer.VertexPosition(I);for(float X:{A.X,A.Y,A.Z})V.Add(MakeShared<FJsonValueNumber>(X));Vertices.Add(MakeShared<FJsonValueArray>(V));}
    for(int32 I=0;I<L.IndexBuffer.GetNumIndices();++I)Indices.Add(MakeShared<FJsonValueNumber>(L.IndexBuffer.GetIndex(I)));
    P->SetArrayField(TEXT("vertices"),Vertices);P->SetArrayField(TEXT("indices"),Indices);FString T;auto W=TJsonWriterFactory<>::Create(&T);FJsonSerializer::Serialize(P,W);FFileHelper::SaveStringToFile(T,*PropFile);
   }
  }
 }
 J->SetStringField(TEXT("intended_support"),!Name.Contains(TEXT("InspectEvidence"))?TEXT("presentation_stowed"):Time<1.6f||Time>=6.8f?TEXT("table"):TEXT("both_hands"));
 auto SkinMatrices=MakeShared<FJsonObject>();
 for(int32 I=0;I<RefToLocal.Num()&&I<Mesh->GetRefSkeleton().GetNum();++I)
 {TArray<TSharedPtr<FJsonValue>> Values;for(int32 R=0;R<4;++R)for(int32 C=0;C<4;++C)Values.Add(MakeShared<FJsonValueNumber>(RefToLocal[I].M[R][C]));SkinMatrices->SetArrayField(Mesh->GetRefSkeleton().GetBoneName(I).ToString(),Values);}
 J->SetObjectField(TEXT("final_ref_to_local_skin_matrices_row_major"),SkinMatrices);
 TArray<TSharedPtr<FJsonValue>> Sections;
 for(const auto& S:LOD.RenderSections){auto Row=MakeShared<FJsonObject>();Row->SetNumberField(TEXT("base_vertex"),S.BaseVertexIndex);Row->SetNumberField(TEXT("vertices"),S.NumVertices);Row->SetNumberField(TEXT("base_index"),S.BaseIndex);Row->SetNumberField(TEXT("triangles"),S.NumTriangles);Row->SetNumberField(TEXT("material_index"),S.MaterialIndex);Sections.Add(MakeShared<FJsonValueObject>(Row));}J->SetArrayField(TEXT("sections"),Sections);
 FString Text;auto W=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(J,W);FFileHelper::SaveStringToFile(Text,*(Folder/(Key+TEXT(".json"))));
 if(!IFileManager::Get().FileExists(*(Folder/TEXT("indices.bin")))){TArray<uint8> Indices;auto* Buffer=LOD.MultiSizeIndexContainer.GetIndexBuffer();for(uint32 I=0;I<Buffer->Num();++I){uint32 V=Buffer->Get(I);Indices.Append(reinterpret_cast<uint8*>(&V),sizeof(V));}FFileHelper::SaveArrayToFile(Indices,*(Folder/TEXT("indices.bin")));}
}
