#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "AnanseAuthoredAnimation.h"
#include "AnanseGroundContact.h"
#include "Animation/AnimBlueprint.h"
#include "Animation/AnimClassInterface.h"
#include "Animation/AnimSequence.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_SequencePlayer.h"
#include "K2Node_VariableGet.h"
#include "EdGraph/EdGraph.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseAuthoredGraphsTest,"Ananse.Animation.AuthoredGraphs",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseAuthoredGraphsTest::RunTest(const FString& Parameters)
{
 const TCHAR* Paths[]={TEXT("/Game/Production/Characters/SpiderRig_v001/ABP_AnanseSpider.ABP_AnanseSpider"),TEXT("/Game/Ananse/Characters/OseboLeopard/Animations/ABP_OseboLeopard.ABP_OseboLeopard")};
 USkeleton* Prior=nullptr;
 for(int32 I=0;I<2;++I)
 {
  auto* Blueprint=LoadObject<UAnimBlueprint>(nullptr,Paths[I]);
  if(!TestNotNull(TEXT("Real saved Animation Blueprint"),Blueprint))continue;
  UClass* Class=Blueprint->GeneratedClass;
  if(!TestNotNull(TEXT("Compiled animation class"),Class))continue;
  TestTrue(TEXT("Independent native animation parent"),Class->IsChildOf(I==0?UAnanseContactAnimInstance::StaticClass():UAnanseLeopardAnimInstance::StaticClass()));
  const auto* Interface=IAnimClassInterface::GetFromClass(Class);
  TestTrue(TEXT("Actual target skeleton resolves"),Interface && Interface->GetTargetSkeleton()==Blueprint->TargetSkeleton);
  if(Prior)TestTrue(TEXT("Skeletons are genuinely independent"),Prior!=Blueprint->TargetSkeleton);
  Prior=Blueprint->TargetSkeleton;
  int32 Players=0,Variables=0,Roots=0;
  TArray<UEdGraph*> Graphs;Blueprint->GetAllGraphs(Graphs);
  for(const auto* Graph:Graphs)if(Graph->GetFName()==TEXT("AnimGraph"))
   for(const UEdGraphNode* Node:Graph->Nodes)
   {
    if(const auto* Player=Cast<UAnimGraphNode_SequencePlayer>(Node))
    {++Players;const auto* Pin=Player->FindPin(TEXT("Sequence"));TestTrue(TEXT("Source asset actually linked"),Pin && Pin->LinkedTo.Num()==1);}
    if(const auto* Variable=Cast<UK2Node_VariableGet>(Node))
    {++Variables;TestEqual(TEXT("Clip property supplies the graph"),Variable->VariableReference.GetMemberName(),FName(TEXT("Clip")));}
    if(const auto* Root=Cast<UAnimGraphNode_Root>(Node))
    {++Roots;const auto* Pin=Root->FindPin(TEXT("Result"));TestTrue(TEXT("Pose output is linked"),Pin && Pin->LinkedTo.Num()==1);}
   }
  TestEqual(TEXT("One real sequence player"),Players,1);TestEqual(TEXT("One variable binding"),Variables,1);TestEqual(TEXT("One output pose"),Roots,1);
  if(I==0)TestTrue(TEXT("One final native spider contact path is enabled after authored source graph"),Class->GetDefaultObject<UAnanseContactAnimInstance>()->bUseAuthoredGraph);
 }
 return true;
}
#endif
