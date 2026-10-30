// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "BattleUnit.h"
#include "BattleViewMode.h"
#include "BattleRiderCharacter.generated.h"

class UCameraComponent;
class USceneComponent;
class USpringArmComponent;
class UStaticMeshComponent;

/** Graybox mounted commander. A future horse skeletal mesh can replace HorseProxy. */
UCLASS(Blueprintable)
class ABattleRiderCharacter : public ABattleUnit
{
	GENERATED_BODY()

public:
	ABattleRiderCharacter();
	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, Category = "Battle|Rider")
	void BeginCharge();

	UFUNCTION(BlueprintCallable, Category = "Battle|Rider")
	void EndCharge();

	UFUNCTION(BlueprintPure, Category = "Battle|Rider")
	bool IsCharging() const { return bCharging; }

	UFUNCTION(BlueprintCallable, Category = "Battle|View")
	void SetRiderViewMode(EBattleViewMode ViewMode);

	UFUNCTION(BlueprintPure, Category = "Battle|View")
	USceneComponent* GetRiderCameraAnchor(EBattleViewMode ViewMode) const;

	UFUNCTION(BlueprintPure, Category = "Battle|Command")
	FVector GetRiderCommandOrigin() const;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USceneComponent* HorseProxy;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* HorseMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USpringArmComponent* ThirdPersonArm;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UCameraComponent* ThirdPersonCamera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USceneComponent* FirstPersonAnchor;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UCameraComponent* FirstPersonCamera;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Battle|Rider")
	float CruiseSpeed = 600.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Battle|Rider")
	float ChargeSpeed = 1000.0f;

	bool bCharging = false;
};
