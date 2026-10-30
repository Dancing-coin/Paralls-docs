#include "BattlePlayerController.h"
#include "BattleCameraPawn.h"
#include "BattleRiderCharacter.h"
#include "Camera/CameraComponent.h"
#include "InputCoreTypes.h"
#include "Engine/World.h"

ABattlePlayerController::ABattlePlayerController()
{
	bShowMouseCursor = false;
	bAutoManageActiveCameraTarget = false;
	ViewMode = CreateDefaultSubobject<UBattleViewModeComponent>(TEXT("ViewMode"));
}

void ABattlePlayerController::BeginPlay()
{
	Super::BeginPlay();
	FInputModeGameOnly InputMode;
	InputMode.SetConsumeCaptureMouseDown(true);
	SetInputMode(InputMode);
	bShowMouseCursor = false;
	ApplyView();
}

void ABattlePlayerController::OnPossess(APawn* InPawn)
{
	Super::OnPossess(InPawn);
	Rider = Cast<ABattleRiderCharacter>(InPawn);
	if (Rider)
	{
		SetControlRotation(FRotator(-12.f, Rider->GetActorRotation().Yaw, 0.f));
		if (!TacticalCamera)
		{
			FActorSpawnParameters Params;
			Params.Owner = this;
			Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
			TacticalCamera = GetWorld()->SpawnActor<ABattleCameraPawn>(Rider->GetActorLocation(), FRotator::ZeroRotator, Params);
		}
		ApplyView();
	}
}

void ABattlePlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
	InputComponent->BindKey(EKeys::V, IE_Pressed, this, &ABattlePlayerController::CycleView);
	// Function keys keep the number row available for future two-key military orders.
	InputComponent->BindKey(EKeys::F1, IE_Pressed, this, &ABattlePlayerController::TacticalView);
	InputComponent->BindKey(EKeys::F2, IE_Pressed, this, &ABattlePlayerController::ThirdPersonView);
	InputComponent->BindKey(EKeys::F3, IE_Pressed, this, &ABattlePlayerController::FirstPersonView);
	InputComponent->BindKey(EKeys::LeftShift, IE_Pressed, this, &ABattlePlayerController::StartCharge);
	InputComponent->BindKey(EKeys::LeftShift, IE_Released, this, &ABattlePlayerController::StopCharge);
}

void ABattlePlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);
	if (!Rider || !IsLocalController() || IsMoveInputIgnored()) return;
	float MouseX = 0.f, MouseY = 0.f;
	GetInputMouseDelta(MouseX, MouseY);
	FRotator Facing = GetControlRotation();
	Facing.Yaw += MouseX * 0.16f;
	Facing.Pitch = FMath::ClampAngle(Facing.Pitch - MouseY * 0.16f, -65.f, 25.f);
	Facing.Roll = 0.f;
	SetControlRotation(Facing);
	const FVector2D Movement(
		(IsInputKeyDown(EKeys::W) ? 1.f : 0.f) - (IsInputKeyDown(EKeys::S) ? 1.f : 0.f),
		(IsInputKeyDown(EKeys::D) ? 1.f : 0.f) - (IsInputKeyDown(EKeys::A) ? 1.f : 0.f));
	const FVector2D Clamped = Movement.GetClampedToMaxSize(1.f);
	const FRotator Yaw(0.f, Facing.Yaw, 0.f);
	Rider->AddMovementInput(Yaw.Vector(), Clamped.X);
	Rider->AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y), Clamped.Y);
	if (TacticalCamera)
	{
		TacticalCamera->SetActorLocationAndRotation(Rider->GetActorLocation(), Yaw);
	}
}

EBattleViewMode ABattlePlayerController::GetBattleViewMode() const { return ViewMode->GetViewMode(); }
void ABattlePlayerController::CycleView() { ViewMode->CycleViewMode(); ApplyView(); }
void ABattlePlayerController::TacticalView() { BattleView(0); }
void ABattlePlayerController::ThirdPersonView() { BattleView(1); }
void ABattlePlayerController::FirstPersonView() { BattleView(2); }
void ABattlePlayerController::BattleView(int32 Mode)
{
	ViewMode->SetViewMode(static_cast<EBattleViewMode>(Mode));
	ApplyView();
}
void ABattlePlayerController::StartCharge() { if (Rider) Rider->BeginCharge(); }
void ABattlePlayerController::StopCharge() { if (Rider) Rider->EndCharge(); }
void ABattlePlayerController::ApplyView()
{
	if (!Rider) return;
	const EBattleViewMode Mode = GetBattleViewMode();
	Rider->SetRiderViewMode(Mode);
	SetViewTarget(Mode == EBattleViewMode::TopDown && TacticalCamera ? static_cast<AActor*>(TacticalCamera) : static_cast<AActor*>(Rider));
}
