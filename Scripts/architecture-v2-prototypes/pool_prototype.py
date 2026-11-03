"""Pool 原语原型 —— 验证 v2 六原语中的 Pool 能否独立成立。

本文件是 docs/architecture-v2/10-待决/01-待决清单.md 中 D1 的第一半验证。
只依赖标准库；不 import Paralls 任何代码。

要证明的不变量（见 02-原语/02-六原语规格.md）：
    P1  0 <= value <= bound
    P2  reserved >= 0 且 reserved <= bound
    P3  available = value - reserved >= 0
    P4  消耗必须先预留；未预留的消耗一律拒绝
    P5  同一世界窗口内不重复积分
    P6  阈值跨越必须触发切窗
    P7  滞回带内的值变化不触发状态翻转

以及"能否承接现有 effective_stats"这一条（见 03-承接映射.md）：
    修正源（additive/multiplicative/override/clamp）必须能表达为 Pool 的
    修正机制，而有效值必须是投影而不是存储值。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


class PoolError(Exception):
    """Pool 不变量被违反。携带 reason_code，对应校验器拒绝码。"""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


# ---------------------------------------------------------------------------
# 声明部分：这些在 v2 中属于 L4 规则包，不是原语本身
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HysteresisBand:
    """滞回带。enter_below / exit_above 构成不翻转区间。

    P7 要求：进入阈值的判断与退出的判断使用不同阈值，
    否则值在阈值附近抖动会反复触发状态翻转。
    """

    state: str
    enter_below: Decimal
    exit_above: Decimal

    def __post_init__(self) -> None:
        if self.exit_above <= self.enter_below:
            raise PoolError(
                "hysteresis_band_invalid",
                f"exit_above({self.exit_above}) 必须严格大于 enter_below({self.enter_below})",
            )


@dataclass(frozen=True)
class PoolDefinition:
    """池定义：界、初值、积分方式、滞回带。"""

    pool_id: str
    lower: Decimal
    upper: Decimal
    initial: Decimal
    hysteresis: tuple[HysteresisBand, ...] = ()
    # 积分方式：每世界 tick 的变化率。对应 L4 的 integration 声明。
    rate_per_tick: Decimal = Decimal(0)

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise PoolError("pool_bounds_invalid", "lower > upper")
        if not (self.lower <= self.initial <= self.upper):
            raise PoolError("pool_initial_out_of_bounds")
        names = [band.state for band in self.hysteresis]
        if len(names) != len(set(names)):
            raise PoolError("hysteresis_state_duplicate")


# ---------------------------------------------------------------------------
# 修正源：承接 effective_stats.py 的 StatModifier
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Modifier:
    """修正源。有效值是投影，不存储（见 01-原语总则.md §二）。

    operation 与 stacking 语义与 effective_stats.py 保持一致：
        additive / multiplicative / override
    """

    modifier_id: str
    operation: str  # additive | multiplicative | override
    value: Decimal
    priority: int = 0
    source_ref: str = ""
    condition_active: bool = True

    def __post_init__(self) -> None:
        if self.operation not in ("additive", "multiplicative", "override"):
            raise PoolError("modifier_operation_unknown", self.operation)


# ---------------------------------------------------------------------------
# 事件
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PoolEvent:
    """池事实流中的一条事件。一条事件 = 一个 revision。"""

    event_type: str
    fact_type: str
    payload: dict
    revision: int
    window_ref: str = ""


# ---------------------------------------------------------------------------
# 池实例
# ---------------------------------------------------------------------------


@dataclass
class Pool:
    """一个 Pool FactType 在某个 (scope, epoch) 上的实例。

    存储的是基础值。有效值由 effective() 计算，不落库。
    """

    definition: PoolDefinition
    fact_type: str
    epoch: int = 1

    value: Decimal = field(init=False)
    reserved: Decimal = field(init=False)
    revision: int = field(default=0, init=False)

    _events: list[PoolEvent] = field(default_factory=list, init=False)
    _reservations: dict[str, Decimal] = field(default_factory=dict, init=False)
    _consumed_windows: set[str] = field(default_factory=set, init=False)
    _integrated_windows: set[str] = field(default_factory=set, init=False)
    _active_states: set[str] = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        self.value = self.definition.initial
        self.reserved = Decimal(0)
        self._emit("pool.initialized", {"initial": str(self.value), "bound": str(self.definition.upper)})

    # -- 只读投影 ---------------------------------------------------------

    @property
    def available(self) -> Decimal:
        """P3：可用量 = 值 - 预留，永不为负。"""
        return self.value - self.reserved

    def effective(self, modifiers: tuple[Modifier, ...] = ()) -> Decimal:
        """有效值。这是投影：不写回 value，不产生事件，不增加 revision。"""
        accepted = [m for m in modifiers if m.condition_active]
        # 确定性要求：稳定排序，不依赖容器遍历顺序
        accepted.sort(key=lambda m: (m.priority, m.modifier_id))

        result = self.value
        for m in accepted:
            if m.operation == "additive":
                result += m.value
        for m in accepted:
            if m.operation == "multiplicative":
                result *= m.value
        overrides = [m for m in accepted if m.operation == "override"]
        if len(overrides) > 1:
            raise PoolError("modifier_conflict_unresolved")
        if overrides:
            result = overrides[0].value

        # 界在投影阶段同样生效（clamp 从 modifier 下沉为 Pool 不变量）
        return min(max(result, self.definition.lower), self.definition.upper)

    # -- 写入路径 ---------------------------------------------------------

    def adjust(self, delta: Decimal, reason: str, window_ref: str) -> None:
        """直接调整。用于初始化、恢复、外部效果。

        P5：同一 window_ref 不得重复积分。
        """
        if window_ref:
            if window_ref in self._integrated_windows:
                raise PoolError("pool_window_already_integrated", window_ref)
            self._integrated_windows.add(window_ref)

        self._set_value(self.value + delta, reason)

    def integrate(self, ticks: int, window_ref: str) -> None:
        """按窗口积分。P5 的核心：同一窗口只积分一次。

        这是 v1 里散落在各域正文、每域重写一遍的那条规则。
        """
        if window_ref in self._integrated_windows:
            raise PoolError("pool_window_already_integrated", window_ref)
        self._integrated_windows.add(window_ref)

        delta = self.definition.rate_per_tick * ticks
        if delta != 0:
            self._set_value(self.value + delta, f"integrate:{window_ref}")

    def reserve(self, amount: Decimal, reservation_ref: str, holder: str) -> None:
        """预留。P4：消耗前必须先预留。"""
        if amount <= 0:
            raise PoolError("pool_reserve_amount_invalid", str(amount))
        if reservation_ref in self._reservations:
            raise PoolError("pool_reservation_duplicate", reservation_ref)
        if self.available < amount:
            raise PoolError(
                "pool_insufficient_available",
                f"available={self.available} requested={amount}",
            )

        self.reserved += amount
        self._reservations[reservation_ref] = amount
        self._emit(
            "pool.reserved",
            {"reservation_ref": reservation_ref, "amount": str(amount), "holder": holder},
        )

    def release(self, reservation_ref: str) -> Decimal:
        """释放预留，不动值。"""
        amount = self._reservations.pop(reservation_ref, None)
        if amount is None:
            raise PoolError("pool_reservation_unknown", reservation_ref)
        self.reserved -= amount
        self._emit("pool.released", {"reservation_ref": reservation_ref, "amount": str(amount)})
        return amount

    def consume(self, reservation_ref: str, actual: Decimal | None = None) -> None:
        """消耗。P4：只能消耗已预留的量。

        consume 是 release + 扣值的原子形式，不可拆成两次调用。
        """
        if reservation_ref not in self._reservations:
            raise PoolError("pool_consume_without_reservation", reservation_ref)

        reserved_amount = self._reservations.pop(reservation_ref)
        spend = reserved_amount if actual is None else actual
        if spend < 0 or spend > reserved_amount:
            # 把预留放回去，保证失败不改变状态
            self._reservations[reservation_ref] = reserved_amount
            raise PoolError(
                "pool_consume_exceeds_reservation",
                f"reserved={reserved_amount} requested={spend}",
            )

        self.reserved -= reserved_amount
        self._set_value(self.value - spend, f"consume:{reservation_ref}")

        # 未用完的预留部分自动归还
        leftover = reserved_amount - spend
        if leftover > 0:
            self._emit(
                "pool.released",
                {"reservation_ref": reservation_ref, "amount": str(leftover), "reason": "leftover"},
            )

        self._emit(
            "pool.consumed",
            {"reservation_ref": reservation_ref, "amount": str(reserved_amount), "actual": str(spend)},
        )

    # -- 内部 -------------------------------------------------------------

    def _set_value(self, candidate: Decimal, reason: str) -> None:
        """P1：值必须落在界内。越界直接拒绝，不静默 clamp。

        静默 clamp 会把"配置或公式写错"变成"看起来正常但数值不对"。
        """
        previous = self.value
        if candidate > self.definition.upper:
            raise PoolError(
                "pool_upper_bound_exceeded",
                f"candidate={candidate} upper={self.definition.upper}",
            )
        if candidate < self.definition.lower:
            raise PoolError(
                "pool_lower_bound_exceeded",
                f"candidate={candidate} lower={self.definition.lower}",
            )

        self.value = candidate
        self._emit(
            "pool.adjusted",
            {"previous": str(previous), "delta": str(candidate - previous), "next": str(candidate), "reason": reason},
        )
        self._evaluate_thresholds(previous)

    def _evaluate_thresholds(self, previous: Decimal) -> None:
        """P6 + P7：阈值跨越触发事件，滞回带内不翻转。"""
        for band in self.definition.hysteresis:
            active = band.state in self._active_states
            if not active and self.value < band.enter_below:
                self._active_states.add(band.state)
                self._emit(
                    "pool.threshold_crossed",
                    {"threshold_ref": band.state, "direction": "enter", "value": str(self.value)},
                )
            elif active and self.value > band.exit_above:
                self._active_states.discard(band.state)
                self._emit(
                    "pool.threshold_crossed",
                    {"threshold_ref": band.state, "direction": "exit", "value": str(self.value)},
                )
            # 带内：不翻转。这就是 P7。

    def _emit(self, event_type: str, payload: dict) -> None:
        self.revision += 1
        self._events.append(
            PoolEvent(
                event_type=event_type,
                fact_type=self.fact_type,
                payload=payload,
                revision=self.revision,
            )
        )

    # -- 检查 -------------------------------------------------------------

    @property
    def events(self) -> tuple[PoolEvent, ...]:
        return tuple(self._events)

    @property
    def active_states(self) -> frozenset[str]:
        return frozenset(self._active_states)

    def check_invariants(self) -> None:
        """P1–P3 的可调用检查，供测试与运行时自检使用。"""
        d = self.definition
        if not (d.lower <= self.value <= d.upper):
            raise PoolError("P1_violated", f"value={self.value}")
        if self.reserved < 0 or self.reserved > d.upper:
            raise PoolError("P2_violated", f"reserved={self.reserved}")
        if self.available < 0:
            raise PoolError("P3_violated", f"available={self.available}")
