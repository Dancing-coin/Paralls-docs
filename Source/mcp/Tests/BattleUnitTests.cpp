// Copyright Epic Games, Inc. All Rights Reserved.

#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "Variant_Strategy/BattleRiderCharacter.h"
#include "Variant_Strategy/BattleUnit.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FBattleUnitDefaultsTest,
	"Guoshang.Battle.Units.Defaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FBattleUnitDefaultsTest::RunTest(const FString& Parameters)
{
	ABattleUnit* Unit = NewObject<ABattleUnit>();
	TestNotNull(TEXT("A battle unit can be created"), Unit);
	if (!Unit)
	{
		return false;
	}

	TestTrue(TEXT("A battle unit derives from the strategy unit"), Unit->IsA<AStrategyUnit>());
	TestEqual(TEXT("Default morale is full"), Unit->GetMorale(), 100.0f);
	TestEqual(TEXT("Default training level is zero"), Unit->GetTrainingLevel(), 0.0f);
	TestTrue(TEXT("A new unit is combat capable"), Unit->IsCombatCapable());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FBattleRiderChargeStateTest,
	"Guoshang.Battle.Rider.ChargeState",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FBattleRiderChargeStateTest::RunTest(const FString& Parameters)
{
	ABattleRiderCharacter* Rider = NewObject<ABattleRiderCharacter>();
	TestNotNull(TEXT("A battle rider can be created"), Rider);
	if (!Rider)
	{
		return false;
	}

	TestFalse(TEXT("The rider is not charging by default"), Rider->IsCharging());
	Rider->BeginCharge();
	TestTrue(TEXT("BeginCharge enters the charging state"), Rider->IsCharging());
	Rider->EndCharge();
	TestFalse(TEXT("EndCharge leaves the charging state"), Rider->IsCharging());
	return true;
}

#endif
