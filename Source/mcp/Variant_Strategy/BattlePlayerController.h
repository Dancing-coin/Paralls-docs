#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "BattleViewMode.h"
#include "BattlePlayerController.generated.h"

class ABattleCameraPawn;
class ABattleRiderCharacter;

/** Mounted player input, independent of the strategy template's click-to-move bindings. */
UCLASS()
class ABattlePlayerController : public APlayerController
{
	GENERATED_BODY()
public:
	ABattlePlayerController();
	virtual void BeginPlay() override;
	virtual void OnPossess(APawn* InPawn) override;
	virtual void SetupInputComponent() override;
	virtual void PlayerTick(float DeltaTime) override;
	EBattleViewMode GetBattleViewMode() const;
	UFUNCTION(Exec) void BattleView(int32 Mode);
private:
	void CycleView();
	void TacticalView();
	void ThirdPersonView();
	void FirstPersonView();
	void StartCharge();
	void StopCharge();
	void ApplyView();
	UPROPERTY() TObjectPtr<UBattleViewModeComponent> ViewMode;
	UPROPERTY() TObjectPtr<ABattleRiderCharacter> Rider;
	UPROPERTY() TObjectPtr<ABattleCameraPawn> TacticalCamera;
};
