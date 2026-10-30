// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "StrategyPawn.h"
#include "BattleCameraPawn.generated.h"

/** Strategy camera pawn kept as a replaceable top-down view host. */
UCLASS()
class ABattleCameraPawn : public AStrategyPawn
{
	GENERATED_BODY()

public:
	ABattleCameraPawn();
};
