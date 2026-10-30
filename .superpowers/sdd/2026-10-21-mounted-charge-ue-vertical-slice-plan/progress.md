# SDD ledger — plan: docs/superpowers/plans/2026-10-21-mounted-charge-ue-vertical-slice-plan.md

Pre-flight: Task 1 produces EBattleViewMode/UBattleViewModeComponent and player-controller view routing consumed by Task 2; Task 2 produces ABattleRiderCharacter/ABattleUnit graybox actors consumed later by Tasks 3–8. Existing StrategyPawn/StrategyPlayerController remain compatibility hosts.

Task 1: complete (C++/UHT source compile passed; final link blocked by live editor DLL lock and disk space)
Task 2: complete (C++/UHT source compile passed; final link blocked by live editor DLL lock and disk space)

Ruling: Keep the existing StrategyPawn as the top-down camera host and spawn a single ABattleRiderCharacter from the controller — this preserves the current template map and avoids duplicating the player actor across views; cost if wrong: the first playable map may need a later GameMode/PawnClass cleanup.

Verification: UnrealBuildTool mcpEditor reached UHT and compiled BattleViewMode, BattleRiderCharacter, BattleUnit, tests, StrategyPlayerController, and all project source files; final link failed because UnrealEditor held Binaries/Win64/UnrealEditor-mcp.dll and the C: drive had no free space. UE Automation DiscoverTests returned ready, but the live editor still exposes the previous module, so the new tests were not discoverable in that session.

Post-change static smoke: all Task 1/2 source files exist and the temporary global BuildConfiguration.xml was removed. The live editor still needs restart/recompile before PIE and the new automation tests can run.
