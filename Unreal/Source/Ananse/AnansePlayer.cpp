#include "AnansePlayer.h"
#include "AnanseAuthoredAnimation.h"
#include "AnanseGroundContact.h"
#include "AnanseRuntimeVerification.h"
#include "AnanseLabSelection.h"
#include "AnansePowers.h"
#include "AnanseMission.h"
#include "AnanseCinematic.h"
#include "LevelSequence.h"
#include "Misc/ConfigCacheIni.h"
#include "AnanseCatalogue.h"
#include "AnanseWorld.h"
#include "AbilitySystemComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameUserSettings.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/LocalPlayer.h"
#include "Engine/GameInstance.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

AAnansePlayer::AAnansePlayer()
{
    PrimaryActorTick.bCanEverTick=true;GetCapsuleComponent()->InitCapsuleSize(40.f,96.f);
    bUseControllerRotationYaw=false;GetCharacterMovement()->bOrientRotationToMovement=true;
    GetCharacterMovement()->RotationRate=FRotator(0,540.f,0);GetCharacterMovement()->MaxWalkSpeed=420.f;
    GetCharacterMovement()->JumpZVelocity=600.f;GetCharacterMovement()->AirControl=0.25f;
    CameraBoom=CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));CameraBoom->SetupAttachment(RootComponent);CameraBoom->TargetArmLength=380.f;CameraBoom->bUsePawnControlRotation=true;CameraBoom->SocketOffset=FVector(0,50,80);
    Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));Camera->SetupAttachment(CameraBoom,USpringArmComponent::SocketName);
    Body=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GreyboxBody"));Body->SetupAttachment(RootComponent);Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);Body->SetRelativeScale3D(FVector(0.55f,0.4f,1.25f));Body->SetRelativeLocation(FVector(0,0,-20));
    Head=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GreyboxHead"));Head->SetupAttachment(RootComponent);Head->SetCollisionEnabled(ECollisionEnabled::NoCollision);Head->SetRelativeScale3D(FVector(0.42f));Head->SetRelativeLocation(FVector(0,0,65));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if(Cube.Succeeded())Body->SetStaticMesh(Cube.Object);if(Sphere.Succeeded())Head->SetStaticMesh(Sphere.Object);
    Abilities=CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("AbilitySystem"));Mission=CreateDefaultSubobject<UAnanseMission>(TEXT("Mission"));
}
UAbilitySystemComponent* AAnansePlayer::GetAbilitySystemComponent() const{return Abilities;}
UAnanseCatalogue* AAnansePlayer::GetCatalogue() const
{
    UGameInstance* Instance=GetGameInstance();
    return Instance?Instance->GetSubsystem<UAnanseCatalogue>():nullptr;
}
FString AAnansePlayer::GetNativeWorldType() const
{
    if(!GetWorld())return TEXT("None");
    if(GetWorld()->WorldType==EWorldType::PIE)return TEXT("PIE");
    if(GetWorld()->WorldType==EWorldType::Game)return TEXT("Game");
    if(GetWorld()->WorldType==EWorldType::Editor)return TEXT("Editor");
    return TEXT("Other");
}
bool AAnansePlayer::IsNativePlayReady() const
{
    return HasActorBegunPlay() && GetController() && GetWorld() && GetWorld()->HasBegunPlay();
}
void AAnansePlayer::BeginPlay()
{
    Super::BeginPlay();Abilities->InitAbilityActorInfo(this,this);
    GConfig->GetFloat(TEXT("/Script/Ananse.PresentationSettings"),TEXT("SubtitleScale"),SubtitleScale,GGameUserSettingsIni);
    if(!FMath::IsFinite(SubtitleScale))SubtitleScale=1.f;
    SubtitleScale=FMath::Clamp(SubtitleScale,.75f,2.f);
    if(CharacterId==TEXT("kwaku") && FParse::Param(FCommandLine::Get(),TEXT("AnanseEpisode")))
    {
        FString Verify;const bool Verification=FParse::Value(FCommandLine::Get(),TEXT("AnanseVerifyMode="),Verify);
        const bool Continuing=FCString::Strlen(GetWorld()->URL.GetOption(TEXT("AnanseContinueSlot="),TEXT("")))>0;
        bOpeningPending=FCString::Atoi(GetWorld()->URL.GetOption(TEXT("AnanseStart="),TEXT("0")))==1;
        if(!Verification && !Continuing && !bOpeningPending)SetEpisodeMenu(true);
    }
    // Local-only proof of mechanics. Networking/replication is deliberately not claimed.
    const UAnanseCatalogue* Catalogue=GetGameInstance()->GetSubsystem<UAnanseCatalogue>();
    const FAnanseCharacterSpec* PlayerSpec=Catalogue?Catalogue->Find(CharacterId):nullptr;
    if(HasAuthority() && PlayerSpec && !bLabSelectionPawn)
    {
        if(PlayerSpec->PowerIds.Contains(TEXT("web-step")))Abilities->GiveAbility(FGameplayAbilitySpec(UAnanseWebStepAbility::StaticClass(),1));
        if(PlayerSpec->PowerIds.Contains(TEXT("borrowed-voice")))Abilities->GiveAbility(FGameplayAbilitySpec(UAnanseVoiceAbility::StaticClass(),1));
        if(PlayerSpec->PowerIds.Contains(TEXT("trick-mirror")))Abilities->GiveAbility(FGameplayAbilitySpec(UAnanseMirrorAbility::StaticClass(),1));
    }
    if(!PlayerSpec)Mission->Message(TEXT("BLOCKED: missing active character catalogue record. Export a prototype publication; abilities are not silently fabricated."));
    FAnanseAppearance Appearance;
    if(Catalogue)
    {
        if(const FAnanseCharacterSpec* Spec=Catalogue->Find(CharacterId))
        {
            FString Requested=TEXT("base");FParse::Value(FCommandLine::Get(),TEXT("AnanseVariant="),Requested);
            for(const FAnanseAppearance& Candidate:Spec->Variants)if(Candidate.Id==FName(*Requested)){Appearance=Candidate;break;}
        }
    }
    UMaterialInterface* Material=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Art/Prototype/M_AnansePrototype.M_AnansePrototype"));
    if(Material)
    {
        Body->SetMaterial(0,Material);Head->SetMaterial(0,Material);
        if(UMaterialInstanceDynamic* M=Body->CreateDynamicMaterialInstance(0))M->SetVectorParameterValue(TEXT("ClothColor"),Appearance.Cloth);
        if(UMaterialInstanceDynamic* M=Head->CreateDynamicMaterialInstance(0))M->SetVectorParameterValue(TEXT("ClothColor"),Appearance.Accent);
    }
    Body->SetRelativeScale3D(FVector(0.55f,0.4f,1.25f)*Appearance.VisualScale);Head->SetRelativeScale3D(FVector(0.42f)*Appearance.VisualScale);
    if(!Appearance.BodyMesh.IsNull())
    {
        // Synchronous prototype load; replace with an AssetManager async bundle before production.
        if(USkeletalMesh* Mesh=Cast<USkeletalMesh>(Appearance.BodyMesh.TryLoad()))
        {
            GetMesh()->SetSkeletalMesh(Mesh);GetMesh()->SetRelativeLocation(FVector(0,0,-96));GetMesh()->SetRelativeRotation(FRotator(0,-90,0));GetMesh()->SetRelativeScale3D(FVector(Appearance.VisualScale));
            Body->SetVisibility(false);Head->SetVisibility(false);
            for(const auto& Morph:Appearance.MorphTargets)GetMesh()->SetMorphTarget(Morph.Key,Morph.Value);
            Mission->Message(TEXT("External mesh loaded. Assign and validate its Animation Blueprint; this starter does not invent rig compatibility."));
        }
        else Mission->Message(TEXT("Configured skeletal mesh could not load. A greybox stand-in remains visible."));
    }
#if PLATFORM_ANDROID || PLATFORM_IOS
    if(GEngine && GEngine->GetGameUserSettings())GEngine->GetGameUserSettings()->SetFrameRateLimit(30.f);
#endif
}
void AAnansePlayer::Move(const FInputActionValue& Value)
{
    if(!Controller || bWebFlying)return;
    const FVector2D Axis=Value.Get<FVector2D>();const FRotator R(0,Controller->GetControlRotation().Yaw,0);
    AddMovementInput(FRotationMatrix(R).GetUnitAxis(EAxis::X),Axis.Y);AddMovementInput(FRotationMatrix(R).GetUnitAxis(EAxis::Y),Axis.X);
}
void AAnansePlayer::Look(const FInputActionValue& Value){const FVector2D Axis=Value.Get<FVector2D>();AddControllerYawInput(Axis.X);AddControllerPitchInput(Axis.Y);}
void AAnansePlayer::StartJump(){if(!bWebFlying)Jump();}
void AAnansePlayer::SkipPresentation()
{
    NotifyAnanseVerificationAction(this,TEXT("skip"));
    if(bEpisodeMenu && Mission->State.bEpisodeSession){SetEpisodeMenu(false);return;}
    if(Mission->Cinematic && Mission->Cinematic->bActive){Mission->SkipCinematic();return;}
    if(Mission->State.bEpisodeSession)SetEpisodeMenu(!bEpisodeMenu);
}
void AAnansePlayer::SetEpisodeMenu(bool Show)
{
    bEpisodeMenu=Show;UGameplayStatics::SetGamePaused(this,Show);
    UE_LOG(LogTemp,Display,TEXT("ANANSE episode menu=%d paused=%d"),bEpisodeMenu,UGameplayStatics::IsGamePaused(this));
    if(Mission && Mission->Cinematic && Mission->Cinematic->bActive)UE_LOG(LogTemp,Display,TEXT("ANANSE paused presentation time=%.4f"),Mission->Cinematic->PlaybackSeconds());
}
void AAnansePlayer::ToggleEpisodePause(){if(Mission->State.bEpisodeSession)SetEpisodeMenu(!bEpisodeMenu);}
void AAnansePlayer::SetSubtitleScale(float Scale)
{
    SubtitleScale=FMath::Clamp(Scale,.75f,2.f);
    GConfig->SetFloat(TEXT("/Script/Ananse.PresentationSettings"),TEXT("SubtitleScale"),SubtitleScale,GGameUserSettingsIni);
    GConfig->Flush(false,GGameUserSettingsIni);
    UE_LOG(LogTemp,Display,TEXT("ANANSE subtitle scale=%.2f"),SubtitleScale);
}
void AAnansePlayer::LargerSubtitles(){if(bEpisodeMenu)SetSubtitleScale(SubtitleScale+.1f);}
void AAnansePlayer::SmallerSubtitles(){if(bEpisodeMenu)SetSubtitleScale(SubtitleScale-.1f);}
void AAnansePlayer::NewEpisode()
{
    if(!bEpisodeMenu || !Mission->State.bEpisodeSession)return;
    Mission->CancelCinematic();ResetTransientMotion();SetEpisodeMenu(false);
    UGameplayStatics::OpenLevel(this,FName(*UAnanseMission::MarketMap()),true,TEXT("AnanseStart=1"));
}
void AAnansePlayer::ContinueEpisode()
{
    if(!bEpisodeMenu || !Mission->State.bEpisodeSession)return;
    const FString Slot=AnanseVerificationSaveSlot(CharacterId);
    if(!UAnanseMission::ValidCheckpointSlot(Slot)){Mission->Message(TEXT("Invalid checkpoint slot; no file accessed."));return;}
    const UAnanseSave* Save=Cast<UAnanseSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));
    const UAnanseCatalogue* Catalogue=GetCatalogue();FString Reason;
    if(!Save || (Save->MapIdentity!=UAnanseMission::MarketMap() && Save->MapIdentity!=UAnanseMission::SanctuaryMap()) ||
       !UAnanseMission::CheckpointCompatible(Save,Catalogue?Catalogue->ContentHash:FString(),CharacterId,Save->MapIdentity,Reason))
    {Mission->Message(Reason.IsEmpty()?TEXT("No compatible episode checkpoint in the selected slot; existing saves retained."):Reason);return;}
    Mission->CancelCinematic();ResetTransientMotion();SetEpisodeMenu(false);
    UGameplayStatics::OpenLevel(this,FName(*Save->MapIdentity),true,TEXT("AnanseContinueSlot=")+Slot);
}
void AAnansePlayer::Save(){if(auto* Lab=Cast<AAnanseLabController>(Controller);Lab && !AnanseUsesDiagnosticCheckpoint()){Lab->SaveSelection();return;}NotifyAnanseVerificationAction(this,TEXT("save"));if(!bWebFlying)Mission->SaveLocal(AnanseVerificationSaveSlot(CharacterId));else Mission->Message(TEXT("Land before saving."));}
void AAnansePlayer::Load(){if(auto* Lab=Cast<AAnanseLabController>(Controller);Lab && !AnanseUsesDiagnosticCheckpoint()){Lab->LoadSelection();return;}NotifyAnanseVerificationAction(this,TEXT("load"));if(!bWebFlying)Mission->LoadLocal(AnanseVerificationSaveSlot(CharacterId));}
void AAnansePlayer::RestartRun(){UGameplayStatics::OpenLevel(this,FName(*UGameplayStatics::GetCurrentLevelName(this,true)));}
void AAnansePlayer::WebStep(){NotifyAnanseVerificationAction(this,TEXT("web"));Abilities->TryActivateAbilityByClass(UAnanseWebStepAbility::StaticClass());}
void AAnansePlayer::BorrowVoice(){NotifyAnanseVerificationAction(this,TEXT("voice"));Abilities->TryActivateAbilityByClass(UAnanseVoiceAbility::StaticClass());}
void AAnansePlayer::TrickMirror(){NotifyAnanseVerificationAction(this,TEXT("mirror"));Abilities->TryActivateAbilityByClass(UAnanseMirrorAbility::StaticClass());}
void AAnansePlayer::SetupPlayerInputComponent(UInputComponent* Input)
{
    ReleaseInputMapping();ButtonActions.Reset();
    Super::SetupPlayerInputComponent(Input);
    UEnhancedInputComponent* Enhanced=Cast<UEnhancedInputComponent>(Input);if(!Enhanced)return;
    Mapping=NewObject<UInputMappingContext>(this);MoveAction=NewObject<UInputAction>(this);MoveAction->ValueType=EInputActionValueType::Axis2D;LookAction=NewObject<UInputAction>(this);LookAction->ValueType=EInputActionValueType::Axis2D;
    auto MapAxis=[this](UInputAction* Action,FKey Key,bool bY,bool bNegate)
    {
        FEnhancedActionKeyMapping& K=Mapping->MapKey(Action,Key);
        if(bNegate)K.Modifiers.Add(NewObject<UInputModifierNegate>(this));
        if(bY){UInputModifierSwizzleAxis* Swap=NewObject<UInputModifierSwizzleAxis>(this);Swap->Order=EInputAxisSwizzle::YXZ;K.Modifiers.Add(Swap);}
    };
    MapAxis(MoveAction,EKeys::D,false,false);MapAxis(MoveAction,EKeys::A,false,true);MapAxis(MoveAction,EKeys::W,true,false);MapAxis(MoveAction,EKeys::S,true,true);
    MapAxis(MoveAction,EKeys::Gamepad_LeftX,false,false);MapAxis(MoveAction,EKeys::Gamepad_LeftY,true,false);
    MapAxis(LookAction,EKeys::MouseX,false,false);MapAxis(LookAction,EKeys::MouseY,true,true);MapAxis(LookAction,EKeys::Gamepad_RightX,false,false);MapAxis(LookAction,EKeys::Gamepad_RightY,true,true);
    Enhanced->BindAction(MoveAction,ETriggerEvent::Triggered,this,&AAnansePlayer::Move);Enhanced->BindAction(LookAction,ETriggerEvent::Triggered,this,&AAnansePlayer::Look);
    auto Button=[&](FKey Key,FKey Pad,void(AAnansePlayer::*Function)())
    {
        UInputAction* Action=NewObject<UInputAction>(this);Action->ValueType=EInputActionValueType::Boolean;ButtonActions.Add(Action);Mapping->MapKey(Action,Key);if(Pad.IsValid())Mapping->MapKey(Action,Pad);Enhanced->BindAction(Action,ETriggerEvent::Started,this,Function);
    };
    Button(EKeys::SpaceBar,EKeys::Gamepad_FaceButton_Bottom,&AAnansePlayer::StartJump);
    Button(EKeys::E,EKeys::Gamepad_FaceButton_Left,&AAnansePlayer::Interact);
    Button(EKeys::One,EKeys::Gamepad_LeftShoulder,&AAnansePlayer::WebStep);
    Button(EKeys::Two,EKeys::Gamepad_RightShoulder,&AAnansePlayer::BorrowVoice);
    Button(EKeys::Three,EKeys::Gamepad_FaceButton_Top,&AAnansePlayer::TrickMirror);
    Input->BindKey(EKeys::Escape,IE_Pressed,this,&AAnansePlayer::SkipPresentation).bExecuteWhenPaused=true;
    Input->BindKey(EKeys::Gamepad_Special_Right,IE_Pressed,this,&AAnansePlayer::SkipPresentation).bExecuteWhenPaused=true;
    Input->BindKey(EKeys::N,IE_Pressed,this,&AAnansePlayer::NewEpisode).bExecuteWhenPaused=true;
    Input->BindKey(EKeys::C,IE_Pressed,this,&AAnansePlayer::ContinueEpisode).bExecuteWhenPaused=true;
    Input->BindKey(EKeys::P,IE_Pressed,this,&AAnansePlayer::ToggleEpisodePause).bExecuteWhenPaused=true;
    Input->BindKey(EKeys::Equals,IE_Pressed,this,&AAnansePlayer::LargerSubtitles).bExecuteWhenPaused=true;
    Input->BindKey(EKeys::Hyphen,IE_Pressed,this,&AAnansePlayer::SmallerSubtitles).bExecuteWhenPaused=true;
    Button(EKeys::F5,FKey(),&AAnansePlayer::Save);Button(EKeys::F9,FKey(),&AAnansePlayer::Load);Button(EKeys::R,FKey(),&AAnansePlayer::RestartRun);
    APlayerController* PC=Cast<APlayerController>(Controller);
    ULocalPlayer* LP=PC?PC->GetLocalPlayer():nullptr;
    UEnhancedInputLocalPlayerSubsystem* Sub=LP?ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LP):nullptr;
    UE_LOG(LogTemp,Display,TEXT("ANANSE input context: controller=%s local_player=%s subsystem=%s authored_mappings=%d"),*GetNameSafe(PC),*GetNameSafe(LP),*GetNameSafe(Sub),Mapping->GetMappings().Num());
    if(Sub){Sub->AddMappingContext(Mapping,0);MappingOwner=LP;}
    Input->BindTouch(IE_Pressed,this,&AAnansePlayer::TouchPressed);
}
void AAnansePlayer::ReleaseInputMapping()
{
    if(ULocalPlayer* LP=MappingOwner.Get())
        if(auto* Sub=ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LP))
            if(Mapping)Sub->RemoveMappingContext(Mapping);
    MappingOwner.Reset();
}
void AAnansePlayer::UnPossessed()
{
    ReleaseInputMapping();ResetTransientMotion();Super::UnPossessed();
}
void AAnansePlayer::EndPlay(const EEndPlayReason::Type Reason)
{
    ReleaseInputMapping();Super::EndPlay(Reason);
}
void AAnansePlayer::TouchPressed(ETouchIndex::Type Finger,FVector Location)
{
    APlayerController* PC=Cast<APlayerController>(Controller);if(!PC)return;int32 W=0,H=0;PC->GetViewportSize(W,H);
    if(Location.X<W-100 || Location.X>W-12)return;
    const int32 Index=FMath::FloorToInt((Location.Y-24.f)/56.f);
    if(Location.Y<24 || Index<0 || Index>4 || FMath::Fmod(Location.Y-24.f,56.f)>46.f)return;
    if(Index==0)WebStep();else if(Index==1)BorrowVoice();else if(Index==2)TrickMirror();else if(Index==3)Interact();else StartJump();
}
void AAnansePlayer::Interact()
{
    NotifyAnanseVerificationAction(this,TEXT("interact"));
    if(bWebFlying)return;
    TArray<AActor*> Actors;UGameplayStatics::GetAllActorsOfClass(this,AAnanseInteractable::StaticClass(),Actors);
    AAnanseInteractable* Nearest=nullptr;float Best=240.f*240.f;
    for(AActor* Actor:Actors)
    {
        const float D=FVector::DistSquared(GetActorLocation(),Actor->GetActorLocation());if(D>Best)continue;
        FCollisionQueryParams Params(SCENE_QUERY_STAT(AnanseInteract),false,this);FHitResult Hit;
        const bool Blocked=GetWorld()->LineTraceSingleByChannel(Hit,GetActorLocation(),Actor->GetActorLocation(),ECC_Visibility,Params);
        if(!Blocked || Hit.GetActor()==Actor){Nearest=Cast<AAnanseInteractable>(Actor);Best=D;}
    }
    if(Nearest)Nearest->Use(this);else Mission->Message(TEXT("Move within 240 cm of a marker with a clear line of sight, then interact."));
}
bool AAnansePlayer::FindWebAnchor(FVector& OutLocation) const
{
    if(bWebFlying)return false;TArray<AActor*> Actors;UGameplayStatics::GetAllActorsWithTag(this,TEXT("WebAnchor"),Actors);float Best=800.f*800.f;bool Found=false;
    for(AActor* Actor:Actors){const FVector Delta=Actor->GetActorLocation()-GetActorLocation();if(Delta.SizeSquared()<Best && FVector::DotProduct(GetActorForwardVector(),Delta.GetSafeNormal())>0.1f){Best=Delta.SizeSquared();OutLocation=Actor->GetActorLocation();Found=true;}}
    return Found;
}
bool AAnansePlayer::CanWebFlight(const FVector& Destination) const
{
    if(bWebFlying || !GetWorld() || FVector::DistSquared(GetActorLocation(),Destination)>800.f*800.f)return false;
    const FVector Start=GetActorLocation();FVector Prev=Start;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(AnanseWebPreflight),false,this);
    const FCollisionShape Shape=FCollisionShape::MakeCapsule(GetCapsuleComponent()->GetScaledCapsuleRadius(),GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
    for(int32 I=1;I<=16;I++)
    {
        const float A=I/16.f;const FVector Next=FMath::Lerp(Start,Destination,A)+FVector(0,0,320.f*FMath::Sin(PI*A));FHitResult Hit;
        if(GetWorld()->SweepSingleByChannel(Hit,Prev,Next,FQuat::Identity,ECC_Pawn,Shape,Params))
        {
            UE_LOG(LogTemp,Warning,TEXT("ANANSE Web Step blocked: actor=%s sample=%d impact=%s destination=%s"),*GetNameSafe(Hit.GetActor()),I,*Hit.ImpactPoint.ToString(),*Destination.ToString());
            return false;
        }
        Prev=Next;
    }
    return true;
}
bool AAnansePlayer::StartWebFlight(const FVector& Destination)
{
    if(bWebFlying)return false;WebStart=GetActorLocation();WebEnd=Destination;WebElapsed=0;bWebFlying=true;GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->SetMovementMode(MOVE_Flying);return true;
}
void AAnansePlayer::Tick(float Delta)
{
    if(bOpeningPending && IsNativePlayReady() && !bEpisodeMenu)
    {
        bOpeningPending=false;
        ULevelSequence* Opening=LoadObject<ULevelSequence>(nullptr,TEXT("/Game/Production/Market/Technical_v001/LS_MarketOpening_Technical.LS_MarketOpening_Technical"));
        if(!Mission->BeginCinematic(Opening,TEXT("opening_finished_or_skipped")))Mission->Message(TEXT("Opening presentation unavailable; inspect the bound sequence before episode acceptance."));
    }
    Super::Tick(Delta);TickAnanseRuntimeVerification(this,Delta);if(!bWebFlying)return;WebElapsed+=Delta;const float A=FMath::Clamp(WebElapsed/0.6f,0.f,1.f);
    const FVector Next=FMath::Lerp(WebStart,WebEnd,A)+FVector(0,0,320.f*FMath::Sin(PI*A));FHitResult Hit;
    SetActorLocation(Next,true,&Hit);
    if(Hit.bBlockingHit || A>=1.f){bWebFlying=false;GetCharacterMovement()->SetMovementMode(MOVE_Walking);if(Hit.bBlockingHit)Mission->Message(TEXT("Web Step stopped by an obstacle; collision is never bypassed."));}
}
void AAnansePlayer::SpawnMirror()
{
    if(IsValid(MirrorActor))MirrorActor->Destroy();MirrorActor=nullptr;
    AStaticMeshActor* Actor=GetWorld()->SpawnActor<AStaticMeshActor>(GetActorLocation()+GetActorForwardVector()*160.f,GetActorRotation());if(!Actor)return;
    Actor->SetMobility(EComponentMobility::Movable);Actor->GetStaticMeshComponent()->SetStaticMesh(Body->GetStaticMesh());Actor->SetActorScale3D(FVector(0.55f,0.4f,1.8f));Actor->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    if(Body->GetMaterial(0))Actor->GetStaticMeshComponent()->SetMaterial(0,Body->GetMaterial(0));Actor->SetLifeSpan(8.f);MirrorActor=Actor;Actor->SetOwner(this);
}

void AAnansePlayer::ResetTransientMotion(){if(auto* A=Cast<UAnanseLeopardAnimInstance>(GetMesh()->GetAnimInstance()))A->bResetSecondaryMotion=true;if(auto* A=Cast<UAnanseContactAnimInstance>(GetMesh()->GetAnimInstance()))A->bResetSecondaryMotion=true;if(IsValid(MirrorActor))MirrorActor->Destroy();MirrorActor=nullptr;bWebFlying=false;WebElapsed=0;WebStart=WebEnd=GetActorLocation();GetCharacterMovement()->StopMovementImmediately();}
