// Copyright Epic Games, Inc. All Rights Reserved.

#include "BattleCameraPawn.h"

#include "Camera/CameraComponent.h"

ABattleCameraPawn::ABattleCameraPawn()
{
	// The strategy template's orthographic camera is useful for a board editor,
	// but it flattens the battlefield during play. Keep the tactical view
	// elevated while using perspective so formations retain depth and scale.
	if (UCameraComponent* TacticalCamera = GetCamera())
	{
		TacticalCamera->ProjectionMode = ECameraProjectionMode::Perspective;
		TacticalCamera->FieldOfView = 55.0f;
		TacticalCamera->SetRelativeLocation(FVector(-1800.0f, 0.0f, 2500.0f));
		TacticalCamera->SetRelativeRotation(FRotator(-55.0f, 0.0f, 0.0f));
	}
}
