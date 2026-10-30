// Copyright Epic Games, Inc. All Rights Reserved.

#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "Camera/CameraComponent.h"
#include "Variant_Strategy/BattleCameraPawn.h"
#include "Variant_Strategy/BattleViewMode.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FBattleViewModeComponentTest,
	"Guoshang.Battle.ViewMode.Component",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FBattleViewModeComponentTest::RunTest(const FString& Parameters)
{
	UBattleViewModeComponent* Component = NewObject<UBattleViewModeComponent>();
	TestNotNull(TEXT("View mode component can be created"), Component);
	if (!Component)
	{
		return false;
	}

	TestEqual(TEXT("The default view is top-down"), Component->GetViewMode(), EBattleViewMode::TopDown);

	Component->CycleViewMode();
	TestEqual(TEXT("Cycling from top-down selects third-person"), Component->GetViewMode(), EBattleViewMode::ThirdPerson);

	Component->CycleViewMode();
	TestEqual(TEXT("Cycling from third-person selects first-person"), Component->GetViewMode(), EBattleViewMode::FirstPerson);

	Component->CycleViewMode();
	TestEqual(TEXT("Cycling from first-person returns to top-down"), Component->GetViewMode(), EBattleViewMode::TopDown);

	Component->SetViewMode(EBattleViewMode::FirstPerson);
	TestEqual(TEXT("A view mode can be selected directly"), Component->GetViewMode(), EBattleViewMode::FirstPerson);

	Component->SetViewMode(static_cast<EBattleViewMode>(255));
	TestEqual(TEXT("An invalid view falls back to third-person"), Component->GetViewMode(), EBattleViewMode::ThirdPerson);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FBattleCameraPawnProjectionTest,
	"Guoshang.Battle.Camera.TopDownProjection",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FBattleCameraPawnProjectionTest::RunTest(const FString& Parameters)
{
	const ABattleCameraPawn* CameraPawn = GetDefault<ABattleCameraPawn>();
	TestNotNull(TEXT("The battle camera pawn class default object exists"), CameraPawn);
	if (!CameraPawn)
	{
		return false;
	}

	const UCameraComponent* Camera = CameraPawn->GetCamera();
	TestNotNull(TEXT("The battle camera component exists"), Camera);
	if (!Camera)
	{
		return false;
	}

	TestEqual(TEXT("The tactical view uses perspective projection"), Camera->ProjectionMode, ECameraProjectionMode::Perspective);
	TestTrue(TEXT("The tactical camera is elevated above its focus"), Camera->GetRelativeLocation().Z > 0.0f);
	TestTrue(TEXT("The tactical camera looks down toward the battlefield"), Camera->GetRelativeRotation().Pitch < -10.0f);
	return true;
}

#endif
