// Copyright Epic Games, Inc. All Rights Reserved.

#include "BattleUnit.h"

#include "Animation/AnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

ABattleUnit::ABattleUnit()
{
	PrimaryActorTick.bCanEverTick = true;
	GetCharacterMovement()->bConstrainToPlane = false;
	GetCharacterMovement()->bSnapToPlaneAtStart = false;
	SoldierMesh = GetMesh();

	static ConstructorHelpers::FObjectFinder<USkeletalMesh> MannyMesh(TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"));
	if (MannyMesh.Succeeded())
	{
		SoldierMesh->SetSkeletalMesh(MannyMesh.Object);
		SoldierMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()));
		SoldierMesh->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
		SoldierMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

		static ConstructorHelpers::FClassFinder<UAnimInstance> LocomotionAnimClass(TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed"));
		if (LocomotionAnimClass.Succeeded())
		{
			SoldierMesh->SetAnimationMode(EAnimationMode::AnimationBlueprint);
			SoldierMesh->SetAnimInstanceClass(LocomotionAnimClass.Class);
		}
	}

	WeaponMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("WeaponMesh"));
	WeaponMesh->SetupAttachment(SoldierMesh, TEXT("weapon_r"));
	WeaponMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	ShieldMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ShieldMesh"));
	ShieldMesh->SetupAttachment(SoldierMesh, TEXT("weapon_l"));
	ShieldMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	HelmetMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HelmetMesh"));
	HelmetMesh->SetupAttachment(SoldierMesh, TEXT("head"));
	HelmetMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	SpearTipMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SpearTipMesh"));
	SpearTipMesh->SetupAttachment(WeaponMesh);
	SpearTipMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> ConeMesh(TEXT("/Engine/BasicShapes/Cone.Cone"));
	if (CylinderMesh.Succeeded())
	{
		WeaponMesh->SetStaticMesh(CylinderMesh.Object);
	}
	if (CubeMesh.Succeeded())
	{
		ShieldMesh->SetStaticMesh(CubeMesh.Object);
	}
	if (SphereMesh.Succeeded())
	{
		HelmetMesh->SetStaticMesh(SphereMesh.Object);
	}
	if (ConeMesh.Succeeded())
	{
		SpearTipMesh->SetStaticMesh(ConeMesh.Object);
	}
	WeaponMesh->SetVisibility(false);
	ShieldMesh->SetVisibility(false);
	HelmetMesh->SetVisibility(false);
	SpearTipMesh->SetVisibility(false);
}

void ABattleUnit::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	ApplyIdentityAppearance();
}

void ABattleUnit::BeginPlay()
{
	Super::BeginPlay();
	ApplyIdentityAppearance();
}

void ABattleUnit::SetUnitIdentity(const FName NewUnitId, const FName NewArmyId, const int32 NewFormationSlot)
{
	UnitId = NewUnitId;
	ArmyId = NewArmyId;
	FormationSlot = NewFormationSlot;
	ApplyIdentityAppearance();
}

void ABattleUnit::SetGrayboxScale(const FVector& NewScale)
{
	// Retain the old API without allowing formation data to distort character proportions.
}

void ABattleUnit::ConfigureAppearance(const FLinearColor& TeamColor, const bool bHasShield, const bool bUseSpear, const bool bCommander)
{
	UMaterialInterface* TeamMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/LevelPrototyping/Materials/M_FlatCol.M_FlatCol"));
	if (TeamMaterial)
	{
		for (UStaticMeshComponent* Gear : {WeaponMesh.Get(), ShieldMesh.Get(), HelmetMesh.Get(), SpearTipMesh.Get()})
		{
			if (Gear)
			{
				UMaterialInstanceDynamic* Material = UMaterialInstanceDynamic::Create(TeamMaterial, this);
				const bool bTeamSurface = Gear == ShieldMesh.Get();
				const FLinearColor Color = bTeamSurface ? TeamColor
					: Gear == WeaponMesh.Get() && bUseSpear ? FLinearColor(0.22f, 0.10f, 0.035f)
					: bCommander && Gear == HelmetMesh.Get() ? FLinearColor(0.9f, 0.6f, 0.12f)
					: FLinearColor(0.29f, 0.32f, 0.36f);
				Material->SetVectorParameterValue(TEXT("Base Color"), Color);
				Gear->SetMaterial(0, Material);
			}
		}
	}

	if (SoldierMesh)
	{
		// Keep the stock head, limb and joint materials so the human silhouette retains detail.
		const int32 TorsoIndex = SoldierMesh->GetMaterialIndex(TEXT("M_Torso"));
		if (TorsoIndex != INDEX_NONE && TeamMaterial)
		{
			UMaterialInstanceDynamic* Material = UMaterialInstanceDynamic::Create(TeamMaterial, this);
			Material->SetVectorParameterValue(TEXT("Base Color"), TeamColor);
			SoldierMesh->SetMaterial(TorsoIndex, Material);
		}
	}

	ShieldMesh->SetRelativeLocation(FVector::ZeroVector);
	ShieldMesh->SetRelativeRotation(FRotator::ZeroRotator);
	ShieldMesh->SetRelativeScale3D(FVector(0.12f, 0.55f, 0.82f));
	ShieldMesh->SetVisibility(bHasShield);

	WeaponMesh->SetRelativeLocation(FVector::ZeroVector);
	if (bUseSpear)
	{
		WeaponMesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
		WeaponMesh->SetRelativeRotation(FRotator(0.0f, 0.0f, -8.0f));
		WeaponMesh->SetRelativeScale3D(FVector(0.035f, 0.035f, 2.2f));
		SpearTipMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 50.0f));
		// Cancel the shaft's nonuniform scaling so the tip keeps its intended dimensions.
		SpearTipMesh->SetRelativeScale3D(FVector(0.09f / 0.035f, 0.09f / 0.035f, 0.18f / 2.2f));
		SpearTipMesh->SetVisibility(true);
	}
	else
	{
		WeaponMesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
		WeaponMesh->SetRelativeRotation(FRotator(20.0f, 0.0f, 0.0f));
		WeaponMesh->SetRelativeScale3D(FVector(0.035f, 0.055f, 0.72f));
		SpearTipMesh->SetVisibility(false);
	}
	WeaponMesh->SetVisibility(true);

	HelmetMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -7.0f));
	HelmetMesh->SetRelativeScale3D(FVector(0.26f, 0.25f, bCommander ? 0.34f : 0.2f));
	HelmetMesh->SetVisibility(true);
}

void ABattleUnit::ApplyIdentityAppearance()
{
	const FString Army = ArmyId.ToString();
	const bool bIsGuard = Army.Contains(TEXT("guard"), ESearchCase::IgnoreCase);
	const bool bIsEnemy = Army.Contains(TEXT("enemy"), ESearchCase::IgnoreCase);
	const FLinearColor TeamColor = bIsGuard
		? FLinearColor(0.95f, 0.56f, 0.08f)
		: bIsEnemy ? FLinearColor(0.82f, 0.07f, 0.045f) : FLinearColor(0.045f, 0.24f, 0.78f);

	const int32 ClassIndex = FormationSlot > 0 ? (FormationSlot - 1) % 3 : FMath::Abs(FormationSlot) % 3;
	const bool bHasShield = !bIsGuard && ClassIndex == 0;
	const bool bUseSpear = !bIsGuard && ClassIndex == 1;
	const bool bCommander = FormationSlot == 0 || bIsGuard;
	ConfigureAppearance(TeamColor, bHasShield, bUseSpear, bCommander);
}
