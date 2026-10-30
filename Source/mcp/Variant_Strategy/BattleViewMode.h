// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "BattleViewMode.generated.h"

UENUM(BlueprintType)
enum class EBattleViewMode : uint8
{
	TopDown UMETA(DisplayName = "Top Down"),
	ThirdPerson UMETA(DisplayName = "Third Person"),
	FirstPerson UMETA(DisplayName = "First Person")
};

/** Shared view-mode state. It contains no camera or pawn ownership. */
UCLASS(ClassGroup = (Battle), BlueprintType, Blueprintable)
class UBattleViewModeComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UBattleViewModeComponent();

	UFUNCTION(BlueprintCallable, Category = "Battle|View")
	void SetViewMode(EBattleViewMode NewMode);

	UFUNCTION(BlueprintCallable, Category = "Battle|View")
	void CycleViewMode();

	UFUNCTION(BlueprintPure, Category = "Battle|View")
	EBattleViewMode GetViewMode() const { return ViewMode; }

private:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Battle|View", meta = (AllowPrivateAccess = "true"))
	EBattleViewMode ViewMode = EBattleViewMode::ThirdPerson;
};
