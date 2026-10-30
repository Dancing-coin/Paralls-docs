// Copyright Epic Games, Inc. All Rights Reserved.

#include "BattleRiderCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

ABattleRiderCharacter::ABattleRiderCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	HorseProxy = CreateDefaultSubobject<USceneComponent>(TEXT("HorseProxy"));
	HorseProxy->SetupAttachment(GetRootComponent());
	HorseProxy->SetRelativeLocation(FVector(-18.0f, 0.0f, -54.0f));
	HorseMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HorseMesh"));
	if (HorseMesh)
	{
		HorseMesh->SetupAttachment(HorseProxy);
		HorseMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		static ConstructorHelpers::FObjectFinder<UStaticMesh> HorseBody(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
		if (HorseBody.Succeeded()) HorseMesh->SetStaticMesh(HorseBody.Object);
		HorseMesh->SetRelativeLocation(FVector(-18.0f, 0.0f, 45.0f));
		HorseMesh->SetRelativeScale3D(FVector(1.55f, 0.52f, 0.58f));

		const auto AddHorsePart = [this](const TCHAR* Name, const FVector& Location, const FRotator& Rotation, const FVector& Scale)
		{
			UStaticMeshComponent* Part = CreateDefaultSubobject<UStaticMeshComponent>(FName(Name));
			Part->SetupAttachment(HorseProxy);
			Part->SetStaticMesh(HorseMesh->GetStaticMesh());
			Part->SetRelativeLocation(Location);
			Part->SetRelativeRotation(Rotation);
			Part->SetRelativeScale3D(Scale);
			Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			Part->SetMaterial(0, HorseMesh->GetMaterial(0));
			return Part;
		};
		AddHorsePart(TEXT("HorseNeck"), FVector(35, 0, 75), FRotator(0, 0, -22), FVector(.44f, .34f, .9f));
		AddHorsePart(TEXT("HorseHead"), FVector(64, 0, 109), FRotator(0, 0, -5), FVector(.42f, .31f, .36f));
		AddHorsePart(TEXT("HorseMuzzle"), FVector(82, 0, 96), FRotator(0, 0, -8), FVector(.24f, .23f, .19f));
		for (int32 Side : {-1, 1})
		{
			for (int32 Along : {-1, 1})
			{
				AddHorsePart(*FString::Printf(TEXT("HorseLeg_%d_%d"), Side, Along), FVector(Along * 39, Side * 26, 8), FRotator(0, 0, 0), FVector(.16f, .17f, .62f));
			}
		}
		AddHorsePart(TEXT("HorseTail"), FVector(-72, 0, 60), FRotator(0, 0, -18), FVector(.18f, .16f, .62f));
	}

	ThirdPersonArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("ThirdPersonArm"));
	ThirdPersonArm->SetupAttachment(RootComponent);
	ThirdPersonArm->TargetArmLength = 620.0f;
	ThirdPersonArm->SetRelativeLocation(FVector(0.0f, 0.0f, 140.0f));
	ThirdPersonArm->SetRelativeRotation(FRotator(-8.0f, 0.0f, 0.0f));
	ThirdPersonArm->bUsePawnControlRotation = true;
	ThirdPersonArm->bDoCollisionTest = true;

	ThirdPersonCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("ThirdPersonCamera"));
	ThirdPersonCamera->SetupAttachment(ThirdPersonArm, USpringArmComponent::SocketName);
	ThirdPersonCamera->bUsePawnControlRotation = false;

	FirstPersonAnchor = CreateDefaultSubobject<USceneComponent>(TEXT("FirstPersonAnchor"));
	FirstPersonAnchor->SetupAttachment(RootComponent);
	FirstPersonAnchor->SetRelativeLocation(FVector(30.0f, 0.0f, 125.0f));

	FirstPersonCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
	FirstPersonCamera->SetupAttachment(FirstPersonAnchor);
	FirstPersonCamera->bUsePawnControlRotation = true;

	GetCharacterMovement()->MaxWalkSpeed = CruiseSpeed;
	GetCharacterMovement()->MaxAcceleration = 1800.0f;
	GetCharacterMovement()->bOrientRotationToMovement = false;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 720.0f, 0.0f);
	bUseControllerRotationYaw = true;

	SetRiderViewMode(EBattleViewMode::ThirdPerson);
}

void ABattleRiderCharacter::BeginPlay()
{
	Super::BeginPlay();
	if (GetMesh())
	{
		GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 8.0f));
	}
	SetRiderViewMode(EBattleViewMode::ThirdPerson);
}

void ABattleRiderCharacter::BeginCharge()
{
	bCharging = true;
	GetCharacterMovement()->MaxWalkSpeed = ChargeSpeed;
}

void ABattleRiderCharacter::EndCharge()
{
	bCharging = false;
	GetCharacterMovement()->MaxWalkSpeed = CruiseSpeed;
}

void ABattleRiderCharacter::SetRiderViewMode(const EBattleViewMode ViewMode)
{
	ThirdPersonCamera->SetActive(ViewMode == EBattleViewMode::ThirdPerson);
	FirstPersonCamera->SetActive(ViewMode == EBattleViewMode::FirstPerson);
	if (GetMesh()) GetMesh()->SetOwnerNoSee(ViewMode == EBattleViewMode::FirstPerson);
}

USceneComponent* ABattleRiderCharacter::GetRiderCameraAnchor(const EBattleViewMode ViewMode) const
{
	return ViewMode == EBattleViewMode::FirstPerson ? FirstPersonAnchor : ThirdPersonArm;
}

FVector ABattleRiderCharacter::GetRiderCommandOrigin() const
{
	return GetActorLocation() + GetActorForwardVector() * 150.0f;
}
