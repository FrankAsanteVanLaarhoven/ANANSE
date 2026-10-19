#include "AnansePursuit.h"
#include "AnanseMission.h"
#include "AnansePlayer.h"
#include "AnanseCastLab.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Components/StaticMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "AIController.h"
#include "NavigationSystem.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
AAnansePursuit::AAnansePursuit()
{
    PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickInterval=0;
    GetCapsuleComponent()->InitCapsuleSize(36,90);
    GetCharacterMovement()->MaxWalkSpeed=320;GetCharacterMovement()->bOrientRotationToMovement=true;
    AIControllerClass=AAIController::StaticClass();AutoPossessAI=EAutoPossessAI::PlacedInWorldOrSpawned;
    ProxyBody=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("OseboEngineeringProxy"));ProxyBody->SetupAttachment(GetRootComponent());
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if(Cube.Succeeded())ProxyBody->SetStaticMesh(Cube.Object);
    ProxyBody->SetRelativeScale3D(FVector(.65,.65,1.6));ProxyBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void AAnansePursuit::Start(UAnanseMission* InMission,ACharacter* InTarget)
{
    if(bActive)return;Mission=InMission;Target=InTarget;bActive=Mission.IsValid() && Target.IsValid();
    if(!bActive)return;LastKnownLocation=Target->GetActorLocation();ActiveSeconds=Mission->State.PursuitSeconds;LostSightSeconds=Mission->State.PursuitLostSightSeconds;CaptureExposure=0;
    if(!Mission->State.PursuerLastKnown.IsNearlyZero())LastKnownLocation=Mission->State.PursuerLastKnown;Behaviour=TEXT("search");
    ProgressPosition=GetActorLocation();ProgressSeconds=0;DetourSeconds=0;
    if(FParse::Param(FCommandLine::Get(),TEXT("AnanseStoryPresentation")))
    {
        UClass* Class=LoadClass<AAnanseCastLabPlayer>(nullptr,TEXT("/Game/Ananse/Characters/OseboHuman/Story_v001/BP_OseboHuman.BP_OseboHuman_C"));
        const auto* Defaults=Class?Class->GetDefaultObject<AAnanseCastLabPlayer>():nullptr;
        if(Defaults && Defaults->AuthoredMesh && Defaults->AnimationClass)
        {PresentationClips=Defaults->AuthoredClips;GetMesh()->SetSkeletalMesh(Defaults->AuthoredMesh);GetMesh()->SetRelativeLocation(FVector(0,0,-90));GetMesh()->SetAnimInstanceClass(Defaults->AnimationClass);GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);if(auto* Anim=Cast<UAnanseCastAnimInstance>(GetMesh()->GetAnimInstance()))Anim->Clip=Defaults->AuthoredClips[0];ProxyBody->SetVisibility(false);}
    }
    if(!GetController())SpawnDefaultController();
}
void AAnansePursuit::Halt()
{
    bActive=false;bVisible=false;Behaviour=TEXT("inactive");GetCharacterMovement()->StopMovementImmediately();
    if(AAIController* AI=Cast<AAIController>(GetController()))AI->StopMovement();
}
bool AAnansePursuit::EscapeConditions(float Seconds,float GateDistance,float PursuerDistance,bool Captured)
{return !Captured && Seconds>=6.f && GateDistance<=240.f && PursuerDistance>=350.f;}
bool AAnansePursuit::CanEscape() const
{
    return bActive && Target.IsValid() && Mission.IsValid() && EscapeConditions(ActiveSeconds,FVector::Dist2D(Target->GetActorLocation(),EscapePoint),FVector::Dist2D(Target->GetActorLocation(),GetActorLocation()),Mission->State.bCaptured);
}
void AAnansePursuit::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);if(!bActive || !Target.IsValid() || !Mission.IsValid())return;
    if(Mission->State.bCaptured || Mission->State.bPursuitEscaped){Halt();return;}
    if(auto* Anim=Cast<UAnanseCastAnimInstance>(GetMesh()->GetAnimInstance()))
    {
        if(PresentationClips.Num()>=4)Anim->Clip=PresentationClips[GetVelocity().SizeSquared2D()>100?2:3];
    }
    ActiveSeconds+=DeltaSeconds;
    const FVector TargetPosition=Target->GetActorLocation();
    FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(AnansePursuitSight),false,this);
    const bool Occluded=GetWorld()->LineTraceSingleByChannel(Hit,GetActorLocation()+FVector(0,0,65),TargetPosition+FVector(0,0,35),ECC_Visibility,Params);
    bVisible=FVector::DistSquared(TargetPosition,GetActorLocation())<=FMath::Square(1400.f) && (!Occluded || Hit.GetActor()==Target.Get());
    // An existing permitted Mirror produces a real visual actor. Only an unobstructed
    // perceived decoy can redirect belief; metadata/timers alone do not create one.
    bool MirrorVisible=false;FVector PerceivedMirror;
    if(auto* Player=Cast<AAnansePlayer>(Target.Get()))if(Mission->MirrorActive() && IsValid(Player->MirrorActor))
    {
        PerceivedMirror=Player->MirrorActor->GetActorLocation();FHitResult MirrorHit;
        const bool Blocked=GetWorld()->LineTraceSingleByChannel(MirrorHit,GetActorLocation()+FVector(0,0,65),PerceivedMirror+FVector(0,0,35),ECC_Visibility,Params);
        MirrorVisible=FVector::DistSquared(PerceivedMirror,GetActorLocation())<=FMath::Square(1400.f) && (!Blocked || MirrorHit.GetActor()==Player->MirrorActor);
    }
    if(MirrorVisible){bVisible=false;LastKnownLocation=PerceivedMirror;LostSightSeconds=0;Behaviour=TEXT("investigating-mirror");}
    else if(bVisible){LastKnownLocation=TargetPosition;LostSightSeconds=0;Behaviour=TEXT("pursuing");}
    else{LostSightSeconds+=DeltaSeconds;Behaviour=LostSightSeconds<=6?TEXT("last-known-search"):TEXT("search-expired");}
    Mission->State.PursuitSeconds=ActiveSeconds;Mission->State.PursuitLostSightSeconds=LostSightSeconds;Mission->State.PursuerLastKnown=LastKnownLocation;Mission->State.PursuerPosition=GetActorLocation();
    if(bVisible && FVector::Distance(TargetPosition,GetActorLocation())<100.f)CaptureExposure+=DeltaSeconds;else CaptureExposure=0;
    if(CaptureExposure>=.3f){Mission->CapturePursuit();Halt();return;}
    if(LostSightSeconds>6){GetCharacterMovement()->StopMovementImmediately();if(AAIController* AI=Cast<AAIController>(GetController()))AI->StopMovement();return;}
    FNavLocation NavLocation;
    UNavigationSystemV1* Navigation=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());
    bNavigationAvailable=Navigation && Navigation->ProjectPointToNavigation(LastKnownLocation,NavLocation,FVector(100,100,300));
    if(bNavigationAvailable)
    {
        if(AAIController* AI=Cast<AAIController>(GetController()))AI->MoveToLocation(NavLocation.Location,75,true,true,false);
    }
    else
    {
        // Greybox fallback remains collision swept, never reads the hidden target after sight loss.
        if(AAIController* AI=Cast<AAIController>(GetController()))AI->StopMovement();
        const FVector Here=GetActorLocation();
        FVector Direction=(LastKnownLocation-Here).GetSafeNormal2D();
        ProgressSeconds+=DeltaSeconds;DetourSeconds=FMath::Max(0.f,DetourSeconds-DeltaSeconds);
        if(ProgressSeconds>=1.f)
        {
            const bool Stuck=FVector::Dist2D(Here,ProgressPosition)<20.f && FVector::Dist2D(Here,LastKnownLocation)>100.f;
            ProgressSeconds=0;ProgressPosition=Here;
            if(Stuck)
            {
                // Probe bounded local alternatives using only the cached last-known waypoint.
                // CharacterMovement still owns collision sweeps; this never teleports through geometry.
                const float Angles[]={70.f*DetourSide,-70.f*DetourSide,110.f*DetourSide,-110.f*DetourSide};
                bool Found=false;float Best=TNumericLimits<float>::Max();FVector BestDirection=FVector::ZeroVector;
                for(float Angle:Angles)
                {
                    const FVector Candidate=Direction.RotateAngleAxis(Angle,FVector::UpVector);
                    const FVector End=Here+Candidate*150.f;
                    FHitResult Block;FCollisionQueryParams SweepParams(SCENE_QUERY_STAT(AnansePursuitDetour),false,this);
                    const FCollisionShape Capsule=FCollisionShape::MakeCapsule(GetCapsuleComponent()->GetScaledCapsuleRadius(),FMath::Max(1.f,GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-2.f));
                    if(GetWorld()->SweepSingleByChannel(Block,Here,End,FQuat::Identity,ECC_Pawn,Capsule,SweepParams))continue;
                    const float Score=FVector::DistSquared2D(End,LastKnownLocation);
                    if(Score<Best){Best=Score;BestDirection=Candidate;Found=true;}
                }
                DetourSide=-DetourSide;
                if(Found){DetourDirection=BestDirection;DetourSeconds=.75f;Behaviour=TEXT("local-obstacle-detour");}
                else{DetourSeconds=0;Behaviour=TEXT("blocked-search");GetCharacterMovement()->StopMovementImmediately();}
            }
        }
        if(DetourSeconds>0){Direction=DetourDirection;Behaviour=TEXT("local-obstacle-detour");}
        if(FVector::Dist2D(LastKnownLocation,Here)>75)AddMovementInput(Direction,1,true);else GetCharacterMovement()->StopMovementImmediately();
    }
}
