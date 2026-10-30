// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "StrategyUnit.h"
#include "BattleUnit.generated.h"

class UStaticMeshComponent;
class USkeletalMeshComponent;

/** Human soldier shared by the rider, guard and infantry formations. */
UCLASS(Blueprintable)
class ABattleUnit : public AStrategyUnit
{
	GENERATED_BODY()

public:
	ABattleUnit();

	/** Kept for older callers; human soldiers use a consistent character scale. */
	void SetGrayboxScale(const FVector& NewScale);

	/** Applies team coloring and weapon/commander details to the human soldier. */
	UFUNCTION(BlueprintCallable, Category = "Battle|Appearance")
	void ConfigureAppearance(const FLinearColor& TeamColor, bool bHasShield, bool bUseSpear, bool bCommander = false);

	UFUNCTION(BlueprintPure, Category = "Battle|Unit")
	FName GetUnitId() const { return UnitId; }

	UFUNCTION(BlueprintPure, Category = "Battle|Unit")
	FName GetArmyId() const { return ArmyId; }

	UFUNCTION(BlueprintPure, Category = "Battle|Unit")
	int32 GetFormationSlot() const { return FormationSlot; }

	UFUNCTION(BlueprintPure, Category = "Battle|Unit")
	float GetMorale() const { return Morale; }

	UFUNCTION(BlueprintPure, Category = "Battle|Unit")
	float GetTrainingLevel() const { return TrainingLevel; }

	UFUNCTION(BlueprintPure, Category = "Battle|Unit")
	bool IsCombatCapable() const { return bCombatCapable; }

	void SetUnitIdentity(FName NewUnitId, FName NewArmyId, int32 NewFormationSlot);

protected:
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;

	/** Refreshes editable, placed units as well as units spawned at runtime. */
	void ApplyIdentityAppearance();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Battle|Unit")
	FName UnitId = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Battle|Unit")
	FName ArmyId = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Battle|Unit")
	int32 FormationSlot = INDEX_NONE;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Battle|Unit", meta = (ClampMin = "0.0", ClampMax = "100.0"))
	float Morale = 100.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Battle|Unit", meta = (ClampMin = "0.0", ClampMax = "100.0"))
	float TrainingLevel = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Battle|Unit")
	bool bCombatCapable = true;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USkeletalMeshComponent> SoldierMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> WeaponMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> ShieldMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> HelmetMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> SpearTipMesh;
};
