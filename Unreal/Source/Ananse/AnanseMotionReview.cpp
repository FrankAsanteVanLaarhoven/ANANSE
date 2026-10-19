#include "AnanseMotionReview.h"
#if !UE_BUILD_SHIPPING
#include "AnansePlayer.h"
#include "AnanseEnvironmentCluster.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "Json.h"
#include "Containers/Ticker.h"
bool TickAnanseMotionReview(AAnansePlayer* P,float Delta)
{
 static FString File;static bool Init=false,Done=false;static float Age=0;static int32 Stage=0;static TWeakObjectPtr<ACameraActor> Camera;
 if(!Init){Init=true;FParse::Value(FCommandLine::Get(),TEXT("AnanseMotionReview="),File);}
 if(File.IsEmpty())return false;if(Done)return true;
 auto* PC=Cast<APlayerController>(P->GetController());if(!PC)return true;Age+=Delta;
 const bool Forest=P->GetWorld()->GetOutermost()->GetName().Contains(TEXT("StoryForest"));
 if(!Camera.IsValid())
 {
  Camera=P->GetWorld()->SpawnActor<ACameraActor>();Camera->GetCameraComponent()->SetFieldOfView(50);PC->SetViewTarget(Camera.Get());
 }
 const FVector Views[3]={Forest?FVector(-950,-1200,400):FVector(2100,-1600,430),Forest?FVector(-450,-650,700):FVector(-850,-550,280),Forest?FVector(150,-550,95):FVector(3700,-600,150)};
 const FVector Targets[3]={Forest?FVector(0,300,150):FVector(3500,300,-10),Forest?FVector(0,150,850):FVector(-900,250,250),Forest?FVector(350,-200,10):FVector(4200,500,-35)};
 const int32 View=FMath::Min(Stage/2,2);Camera->SetActorLocation(Views[View]);Camera->SetActorRotation((Targets[View]-Views[View]).Rotation());
 const float Times[]={3,3.7f,6,6.7f,9,9.7f};
 if(Stage<6&&Age>=Times[Stage]){FScreenshotRequest::RequestScreenshot(FPaths::GetPath(File)/FString::Printf(TEXT("motion_%d.png"),Stage),false,false);++Stage;}
 if(Age<11)return true;
 auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("world"),P->GetWorld()->GetOutermost()->GetName());R->SetNumberField(TEXT("seconds"),Age);R->SetBoolField(TEXT("secondary_disabled"),FParse::Param(FCommandLine::Get(),TEXT("AnanseDisableSecondaryMotion")));TArray<TSharedPtr<FJsonValue>> Rows;int32 Count=0;
 for(TActorIterator<AAnanseEnvironmentCluster> It(P->GetWorld());It;++It)if(It->bMotionVariantLoaded)
 {
  auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("mesh"),It->Instances->GetStaticMesh()->GetPathName());Row->SetNumberField(TEXT("instances"),It->Instances->GetInstanceCount());Row->SetBoolField(TEXT("actor_tick"),It->IsActorTickEnabled());Row->SetBoolField(TEXT("collision"),It->GetActorEnableCollision());TArray<TSharedPtr<FJsonValue>> Mats;for(int32 I=0;I<It->Instances->GetNumMaterials();++I){auto* M=It->Instances->GetMaterial(I);Mats.Add(MakeShared<FJsonValueString>(M?M->GetPathName():TEXT("missing")));}Row->SetArrayField(TEXT("materials"),Mats);Rows.Add(MakeShared<FJsonValueObject>(Row));++Count;
 }
 R->SetArrayField(TEXT("motion_clusters"),Rows);const bool Disabled=FParse::Param(FCommandLine::Get(),TEXT("AnanseDisableSecondaryMotion"));R->SetBoolField(TEXT("passed"),Stage==6&&(Disabled?Count==0:Count>0));R->SetStringField(TEXT("scope"),TEXT("Fixed-camera packaged render evidence and loaded bindings; naturalness and GPU/mobile cost require review. World time continues; no asset edits."));
 TArray<TSharedPtr<FJsonValue>> Cameras;for(int32 I=0;I<3;++I){auto C=MakeShared<FJsonObject>();C->SetStringField(TEXT("location_cm"),Views[I].ToString());C->SetStringField(TEXT("target_cm"),Targets[I].ToString());C->SetNumberField(TEXT("horizontal_fov_degrees"),50);Cameras.Add(MakeShared<FJsonValueObject>(C));}R->SetArrayField(TEXT("cameras"),Cameras);
 FString Text;auto W=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(R,W);FFileHelper::SaveStringToFile(Text,*File);Done=true;
 FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float){GEngine->Exec(nullptr,TEXT("quit"));return false;}),.5f);return true;
}
#else
bool TickAnanseMotionReview(AAnansePlayer*,float){return false;}
#endif
