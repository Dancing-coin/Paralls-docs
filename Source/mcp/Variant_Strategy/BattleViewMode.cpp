// Copyright Epic Games, Inc. All Rights Reserved.

#include "BattleViewMode.h"

UBattleViewModeComponent::UBattleViewModeComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UBattleViewModeComponent::SetViewMode(const EBattleViewMode NewMode)
{
	ViewMode = NewMode == EBattleViewMode::TopDown || NewMode == EBattleViewMode::ThirdPerson || NewMode == EBattleViewMode::FirstPerson
		? NewMode
		: EBattleViewMode::ThirdPerson;
}

void UBattleViewModeComponent::CycleViewMode()
{
	switch (ViewMode)
	{
	case EBattleViewMode::TopDown:
		ViewMode = EBattleViewMode::ThirdPerson;
		break;
	case EBattleViewMode::ThirdPerson:
		ViewMode = EBattleViewMode::FirstPerson;
		break;
	case EBattleViewMode::FirstPerson:
	default:
		ViewMode = EBattleViewMode::TopDown;
		break;
	}
}
