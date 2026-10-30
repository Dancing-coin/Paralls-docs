#include "BattleGameMode.h"
#include "BattlePlayerController.h"
#include "BattleRiderCharacter.h"
#include "Engine/Canvas.h"

ABattleGameMode::ABattleGameMode()
{
	DefaultPawnClass = ABattleRiderCharacter::StaticClass();
	PlayerControllerClass = ABattlePlayerController::StaticClass();
	HUDClass = ABattleHUD::StaticClass();
}

void ABattleHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas) return;
	const ABattlePlayerController* PC = Cast<ABattlePlayerController>(PlayerOwner);
	const TCHAR* View = TEXT("THIRD PERSON");
	if (PC && PC->GetBattleViewMode() == EBattleViewMode::FirstPerson) View = TEXT("FIRST PERSON");
	if (PC && PC->GetBattleViewMode() == EBattleViewMode::TopDown) View = TEXT("TACTICAL PERSPECTIVE");
	DrawRect(FLinearColor(0.025f, 0.035f, 0.045f, 0.8f), 20, 20, 670, 80);
	DrawText(FString::Printf(TEXT("BATTLEFIELD   /   %s"), View), FLinearColor(0.9f, 0.75f, 0.4f), 35, 30, nullptr, 1.2f);
	DrawText(TEXT("WASD Move  |  Mouse Turn / Look  |  Hold Shift Charge"), FLinearColor::White, 35, 56);
	DrawText(TEXT("V Cycle View  |  F1 Tactical  F2 Third  F3 First"), FLinearColor::White, 35, 76);
}
