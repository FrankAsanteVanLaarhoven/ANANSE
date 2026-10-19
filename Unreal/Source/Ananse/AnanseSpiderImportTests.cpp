#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimSequence.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#include "Rendering/SkinWeightVertexBuffer.h"
static const TCHAR* SpiderRoot=TEXT("/Game/Characters/AnanseSpider/Proxy_GLTF_v002/");
static USkeletalMesh* SpiderMesh(){return LoadObject<USkeletalMesh>(nullptr,*(FString(SpiderRoot)+TEXT("AnanseSpider_PROXY.AnanseSpider_PROXY")));}
static UAnimSequence* SpiderClip(const FString& Name){const FString Asset=TEXT("AnanseSpider_PROXY")+Name;return LoadObject<UAnimSequence>(nullptr,*(FString(SpiderRoot)+Asset+TEXT(".")+Asset));}
struct FExpectedSpiderBone{const TCHAR* Name;int32 Parent;};
static const FExpectedSpiderBone ExpectedBones[]={
    {TEXT("root"),-1},
    {TEXT("pelvis"),0},
    {TEXT("spine_01"),1},
    {TEXT("spine_02"),2},
    {TEXT("neck"),3},
    {TEXT("head"),4},
    {TEXT("jaw"),5},
    {TEXT("eye_l"),5},
    {TEXT("eye_r"),5},
    {TEXT("abdomen_01"),1},
    {TEXT("abdomen_02"),9},
    {TEXT("cloth_01"),1},
    {TEXT("cloth_02"),11},
    {TEXT("cloth_03"),12},
    {TEXT("clavicle_upper_l"),3},
    {TEXT("upperarm_upper_l"),14},
    {TEXT("forearm_upper_l"),15},
    {TEXT("hand_upper_l"),16},
    {TEXT("index_01_upper_l"),17},
    {TEXT("index_02_upper_l"),18},
    {TEXT("index_03_upper_l"),19},
    {TEXT("middle_01_upper_l"),17},
    {TEXT("middle_02_upper_l"),21},
    {TEXT("middle_03_upper_l"),22},
    {TEXT("ring_01_upper_l"),17},
    {TEXT("ring_02_upper_l"),24},
    {TEXT("ring_03_upper_l"),25},
    {TEXT("thumb_01_upper_l"),17},
    {TEXT("thumb_02_upper_l"),27},
    {TEXT("thumb_03_upper_l"),28},
    {TEXT("socket_thread_upper_l"),17},
    {TEXT("clavicle_upper_r"),3},
    {TEXT("upperarm_upper_r"),31},
    {TEXT("forearm_upper_r"),32},
    {TEXT("hand_upper_r"),33},
    {TEXT("index_01_upper_r"),34},
    {TEXT("index_02_upper_r"),35},
    {TEXT("index_03_upper_r"),36},
    {TEXT("middle_01_upper_r"),34},
    {TEXT("middle_02_upper_r"),38},
    {TEXT("middle_03_upper_r"),39},
    {TEXT("ring_01_upper_r"),34},
    {TEXT("ring_02_upper_r"),41},
    {TEXT("ring_03_upper_r"),42},
    {TEXT("thumb_01_upper_r"),34},
    {TEXT("thumb_02_upper_r"),44},
    {TEXT("thumb_03_upper_r"),45},
    {TEXT("socket_thread_upper_r"),34},
    {TEXT("clavicle_lower_l"),2},
    {TEXT("upperarm_lower_l"),48},
    {TEXT("forearm_lower_l"),49},
    {TEXT("hand_lower_l"),50},
    {TEXT("index_01_lower_l"),51},
    {TEXT("index_02_lower_l"),52},
    {TEXT("index_03_lower_l"),53},
    {TEXT("middle_01_lower_l"),51},
    {TEXT("middle_02_lower_l"),55},
    {TEXT("middle_03_lower_l"),56},
    {TEXT("ring_01_lower_l"),51},
    {TEXT("ring_02_lower_l"),58},
    {TEXT("ring_03_lower_l"),59},
    {TEXT("thumb_01_lower_l"),51},
    {TEXT("thumb_02_lower_l"),61},
    {TEXT("thumb_03_lower_l"),62},
    {TEXT("socket_thread_lower_l"),51},
    {TEXT("clavicle_lower_r"),2},
    {TEXT("upperarm_lower_r"),65},
    {TEXT("forearm_lower_r"),66},
    {TEXT("hand_lower_r"),67},
    {TEXT("index_01_lower_r"),68},
    {TEXT("index_02_lower_r"),69},
    {TEXT("index_03_lower_r"),70},
    {TEXT("middle_01_lower_r"),68},
    {TEXT("middle_02_lower_r"),72},
    {TEXT("middle_03_lower_r"),73},
    {TEXT("ring_01_lower_r"),68},
    {TEXT("ring_02_lower_r"),75},
    {TEXT("ring_03_lower_r"),76},
    {TEXT("thumb_01_lower_r"),68},
    {TEXT("thumb_02_lower_r"),78},
    {TEXT("thumb_03_lower_r"),79},
    {TEXT("socket_thread_lower_r"),68},
    {TEXT("coxa_front_l"),1},
    {TEXT("femur_front_l"),82},
    {TEXT("tibia_front_l"),83},
    {TEXT("tarsus_front_l"),84},
    {TEXT("foot_tip_front_l"),85},
    {TEXT("coxa_front_r"),1},
    {TEXT("femur_front_r"),87},
    {TEXT("tibia_front_r"),88},
    {TEXT("tarsus_front_r"),89},
    {TEXT("foot_tip_front_r"),90},
    {TEXT("coxa_rear_l"),1},
    {TEXT("femur_rear_l"),92},
    {TEXT("tibia_rear_l"),93},
    {TEXT("tarsus_rear_l"),94},
    {TEXT("foot_tip_rear_l"),95},
    {TEXT("coxa_rear_r"),1},
    {TEXT("femur_rear_r"),97},
    {TEXT("tibia_rear_r"),98},
    {TEXT("tarsus_rear_r"),99},
    {TEXT("foot_tip_rear_r"),100},
};
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseSpiderAnatomyTest,"Ananse.Character.ImportedProxy.Anatomy",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseSpiderAnatomyTest::RunTest(const FString& Parameters)
{
    USkeletalMesh* Mesh=SpiderMesh();if(!TestNotNull(TEXT("Real imported SkeletalMesh"),Mesh))return false;
    const FReferenceSkeleton& Ref=Mesh->GetRefSkeleton();TestEqual(TEXT("102 expected joints"),Ref.GetNum(),102);
    TArray<FTransform> Component;Component.SetNum(Ref.GetNum());
    for(int32 Index=0;Index<Ref.GetNum();Index++){Component[Index]=Ref.GetRefBonePose()[Index];const int32 Parent=Ref.GetParentIndex(Index);if(Parent>=0)Component[Index]=Component[Index]*Component[Parent];}
    for(const auto& Expected:ExpectedBones)
    {
        const int32 Index=Ref.FindBoneIndex(FName(Expected.Name));TestTrue(FString::Printf(TEXT("Expected bone %s"),Expected.Name),Index>=0);
        if(Index<0)continue;
        const FName ExpectedParent=Expected.Parent<0?NAME_None:FName(ExpectedBones[Expected.Parent].Name);
        const int32 Parent=Ref.GetParentIndex(Index);TestEqual(FString::Printf(TEXT("Exact parent %s"),Expected.Name),Parent<0?NAME_None:Ref.GetBoneName(Parent),ExpectedParent);
        TestTrue(TEXT("Finite bind transform"),!Component[Index].ContainsNaN());
        TestTrue(TEXT("Bind pose does not introduce stretching"),Component[Index].GetScale3D().Equals(FVector::OneVector,.001));
    }
    const FVector Size=Mesh->GetBounds().BoxExtent*2;
    AddInfo(FString::Printf(TEXT("Imported rest bounds cm: %s"),*Size.ToString()));
    TestTrue(TEXT("Source centimetre height ~207.9"),FMath::Abs(Size.Z-207.9)<2.0);
    TestTrue(TEXT("Source width ~158.4 cm"),FMath::Abs(Size.Y-158.4)<2.0);
    const int32 Eye=Ref.FindBoneIndex(TEXT("eye_l")),Abdomen=Ref.FindBoneIndex(TEXT("abdomen_01"));
    if(Eye>=0 && Abdomen>=0)TestTrue(TEXT("+X forward eye ahead of abdomen"),Component[Eye].GetLocation().X>Component[Abdomen].GetLocation().X+20);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseSpiderWeightTest,"Ananse.Character.ImportedProxy.Weights",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseSpiderWeightTest::RunTest(const FString& Parameters)
{
    USkeletalMesh* Mesh=SpiderMesh();if(!TestNotNull(TEXT("Mesh exists"),Mesh))return false;
    FSkeletalMeshRenderData* Render=Mesh->GetResourceForRendering();if(!TestNotNull(TEXT("Actual render data"),Render))return false;
    if(!TestTrue(TEXT("Actual LOD0 exists"),Render->LODRenderData.Num()>0))return false;
    const FSkinWeightVertexBuffer* Weights=Render->LODRenderData[0].GetSkinWeightVertexBuffer();
    if(!TestNotNull(TEXT("Actual skin buffer"),Weights))return false;
    if(!TestTrue(TEXT("CPU weights must be accessible to qualify"),Weights->GetDataVertexBuffer()->GetWeightData()!=nullptr))return false;
    if(!TestTrue(TEXT("Non-empty imported skin vertices"),Weights->GetNumVertices()>0))return false;
    uint32 Zero=0;double MaxError=0;
    for(uint32 Vertex=0;Vertex<Weights->GetNumVertices();Vertex++)
    {
        uint32 Sum=0;for(uint32 Influence=0;Influence<Weights->GetMaxBoneInfluences();Influence++)Sum+=Weights->GetBoneWeight(Vertex,Influence);
        if(Sum==0)Zero++;MaxError=FMath::Max(MaxError,FMath::Abs(double(Sum)/65535.0-1.0));
    }
    AddInfo(FString::Printf(TEXT("Native vertices=%u unweighted=%u max_sum_error=%g"),Weights->GetNumVertices(),Zero,MaxError));
    TestTrue(TEXT("Nonzero native vertices"),Weights->GetNumVertices()>0);TestEqual(TEXT("No unweighted vertices"),Zero,0u);TestTrue(TEXT("Weight sum error <=1e-4"),MaxError<=1e-4);
    return true;
}
static FTransform BoneAt(UAnimSequence* Clip,int32 Bone,double Time)
{
    FTransform Result;Clip->GetBoneTransform(Result,FSkeletonPoseBoneIndex(Bone),FAnimExtractContext(Time,false),false);return Result;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAnanseSpiderClipsTest,"Ananse.Character.ImportedProxy.AnimationIsolation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAnanseSpiderClipsTest::RunTest(const FString& Parameters)
{
    USkeletalMesh* Mesh=SpiderMesh();if(!TestNotNull(TEXT("Mesh exists"),Mesh))return false;
    const TCHAR* Names[]={TEXT("A_Idle_Proxy"),TEXT("A_LimbROM_Proxy"),TEXT("A_WeaveGesture_Proxy"),TEXT("A_CrawlInPlace_Proxy")};
    const double Durations[]={3,8,3,4};
    const TCHAR* MotionBones[]={TEXT("head"),TEXT("upperarm_upper_l"),TEXT("forearm_upper_l"),TEXT("femur_front_l")};
    for(int32 Index=0;Index<4;Index++)
    {
        UAnimSequence* Clip=SpiderClip(Names[Index]);if(!TestNotNull(Names[Index],Clip))continue;
        TestTrue(TEXT("Clip bound to imported custom skeleton"),Clip->GetSkeleton()==Mesh->GetSkeleton());
        TestTrue(FString::Printf(TEXT("Duration %s"),Names[Index]),FMath::Abs(Clip->GetPlayLength()-Durations[Index])<.04);
        const int32 Bone=Mesh->GetRefSkeleton().FindBoneIndex(MotionBones[Index]);
        if(Bone>=0){const FTransform Start=BoneAt(Clip,Bone,0);double MaxMotion=0;for(int32 Sample=1;Sample<32;Sample++){const FTransform Pose=BoneAt(Clip,Bone,Durations[Index]*Sample/32.0);MaxMotion=FMath::Max(MaxMotion,Start.GetRotation().AngularDistance(Pose.GetRotation()));}TestTrue(TEXT("Actual imported bone animation moves"),MaxMotion>.01);}
    }
    UAnimSequence* Isolation=SpiderClip(TEXT("A_LimbROM_Proxy"));if(!Isolation)return false;
    const TCHAR* Roots[]={TEXT("upperarm_upper_l"),TEXT("upperarm_upper_r"),TEXT("upperarm_lower_l"),TEXT("upperarm_lower_r"),TEXT("coxa_front_l"),TEXT("coxa_front_r"),TEXT("coxa_rear_l"),TEXT("coxa_rear_r")};
    for(int32 Active=0;Active<8;Active++)for(int32 Chain=0;Chain<8;Chain++)
    {
        const int32 Bone=Mesh->GetRefSkeleton().FindBoneIndex(Roots[Chain]);if(Bone<0){AddError(TEXT("Missing independent chain"));continue;}
        const double Motion=BoneAt(Isolation,Bone,0).GetRotation().AngularDistance(BoneAt(Isolation,Bone,Active+.25).GetRotation());
        TestTrue(FString::Printf(TEXT("Isolation active=%s observed=%s radians=%g"),Roots[Active],Roots[Chain],Motion),Chain==Active?Motion>.1:Motion<.002);
    }
    return true;
}
#endif
