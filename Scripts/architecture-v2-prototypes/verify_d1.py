"""D1 收敛验证 —— Pool 与 Bond 原型是否满足 v2 规格。

运行：py -3 -m pytest 不可用时的等价脚本；本文件也可直接 python 执行。

本文件回答 docs/architecture-v2/10-待决/01-待决清单.md 的 D1：
    六原语能否收敛？重点看 Bond 五种契能否压成同一形状，
    以及 Pool 能否承接现有 effective_stats 的修正语义。

判定标准不是"跑通了"，而是：
    1. 每条不变量都有对应的拒绝用例（证明它真的被强制）
    2. Bond 支持产权/保管/控制对不同主体同时成立（现有代码做不到）
    3. Pool 的有效值是投影，不写回、不增 revision
"""

from __future__ import annotations

import sys
import traceback

from bond_prototype import BondError, BondStore, BondTerm, BondType
from pool_prototype import (
    HysteresisBand,
    Modifier,
    Pool,
    PoolDefinition,
    PoolError,
)
from decimal import Decimal


# ---------------------------------------------------------------------------
# 极简测试框架（避免依赖 pytest）
# ---------------------------------------------------------------------------

RESULTS: list[tuple[str, bool, str]] = []


def case(name: str):
    def decorator(fn):
        try:
            fn()
            RESULTS.append((name, True, ""))
        except AssertionError as exc:
            RESULTS.append((name, False, f"断言失败: {exc}"))
        except Exception as exc:  # noqa: BLE001
            RESULTS.append((name, False, f"{type(exc).__name__}: {exc}"))
        return fn

    return decorator


def expect_raises(exc_type, code: str | None = None):
    """上下文管理器：期望抛出某异常，且 reason code 匹配。"""

    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, et, ev, tb):
            if et is None:
                raise AssertionError(f"期望 {exc_type.__name__} 但未抛出")
            if not issubclass(et, exc_type):
                return False
            if code is not None and getattr(ev, "code", None) != code:
                raise AssertionError(
                    f"期望 code={code} 实际={getattr(ev, 'code', None)}"
                )
            return True

    return _Ctx()


def health_pool(**overrides) -> Pool:
    params = dict(
        pool_id="health",
        lower=Decimal(0),
        upper=Decimal(100),
        initial=Decimal(100),
    )
    params.update(overrides)
    return Pool(
        definition=PoolDefinition(**params),
        fact_type="fact:character:char-07:health",
    )


# ---------------------------------------------------------------------------
# Pool: 七条不变量
# ---------------------------------------------------------------------------


@case("P1 上界越界被拒绝（不静默 clamp）")
def _() -> None:
    pool = health_pool()
    with expect_raises(PoolError, "pool_upper_bound_exceeded"):
        pool.adjust(Decimal(10), "heal", "w1")
    assert pool.value == Decimal(100)


@case("P1 下界越界被拒绝")
def _() -> None:
    pool = health_pool()
    with expect_raises(PoolError, "pool_lower_bound_exceeded"):
        pool.adjust(Decimal(-150), "damage", "w1")


@case("P2/P3 预留不超可用量")
def _() -> None:
    pool = health_pool()
    pool.reserve(Decimal(60), "res-1", "stamina-check")
    assert pool.available == Decimal(40)
    with expect_raises(PoolError, "pool_insufficient_available"):
        pool.reserve(Decimal(50), "res-2", "other")
    pool.check_invariants()


@case("P4 未预留直接消耗被拒绝")
def _() -> None:
    pool = health_pool()
    with expect_raises(PoolError, "pool_consume_without_reservation"):
        pool.consume("no-such-reservation")
    assert pool.value == Decimal(100)


@case("P4 消耗超过预留被拒绝且状态不变")
def _() -> None:
    pool = health_pool()
    pool.reserve(Decimal(30), "res-1", "h")
    before_value, before_reserved = pool.value, pool.reserved
    with expect_raises(PoolError, "pool_consume_exceeds_reservation"):
        pool.consume("res-1", Decimal(50))
    assert (pool.value, pool.reserved) == (before_value, before_reserved)


@case("P4 consume 原子：预留未用完部分自动归还")
def _() -> None:
    pool = health_pool()
    pool.reserve(Decimal(30), "res-1", "h")
    pool.consume("res-1", Decimal(20))
    assert pool.value == Decimal(80)
    assert pool.reserved == Decimal(0)


@case("P5 同一窗口重复积分被拒绝")
def _() -> None:
    pool = health_pool(rate_per_tick=Decimal("-0.5"))
    pool.integrate(10, "window-001")
    value_after_first = pool.value
    with expect_raises(PoolError, "pool_window_already_integrated"):
        pool.integrate(10, "window-001")
    assert pool.value == value_after_first


@case("P6/P7 滞回：进入后带内抖动不翻转")
def _() -> None:
    pool = health_pool(
        initial=Decimal(50),
        hysteresis=(HysteresisBand(state="critical", enter_below=Decimal(30), exit_above=Decimal(35)),),
    )
    pool.adjust(Decimal(-25), "damage", "w1")          # 25 -> enter critical
    assert "critical" in pool.active_states
    crossings = sum(1 for e in pool.events if e.event_type == "pool.threshold_crossed")
    assert crossings == 1, f"期望 1 次跨越，实际 {crossings}"

    # 带内来回抖动：25 -> 32 -> 28 -> 33，均不应翻转
    for delta, window in ((Decimal(7), "w2"), (Decimal(-4), "w3"), (Decimal(5), "w4")):
        pool.adjust(delta, "jitter", window)
    assert "critical" in pool.active_states, "带内抖动不应退出 critical"
    crossings = sum(1 for e in pool.events if e.event_type == "pool.threshold_crossed")
    assert crossings == 1, f"带内抖动产生了额外跨越: {crossings}"

    # 超过 exit_above 才退出
    pool.adjust(Decimal(5), "heal", "w5")              # 38 > 35
    assert "critical" not in pool.active_states
    crossings = sum(1 for e in pool.events if e.event_type == "pool.threshold_crossed")
    assert crossings == 2


@case("P6 阈值跨越在进入时触发一次")
def _() -> None:
    pool = health_pool(
        initial=Decimal(50),
        hysteresis=(HysteresisBand(state="critical", enter_below=Decimal(30), exit_above=Decimal(35)),),
    )
    pool.adjust(Decimal(-19), "damage", "w1")  # 31，未进
    assert "critical" not in pool.active_states
    pool.adjust(Decimal(-2), "damage", "w2")   # 29，进入
    assert "critical" in pool.active_states


@case("P1-P3 check_invariants 可随时调用")
def _() -> None:
    pool = health_pool()
    pool.reserve(Decimal(10), "r", "h")
    pool.consume("r", Decimal(10))
    pool.check_invariants()


# ---------------------------------------------------------------------------
# Pool: 承接 effective_stats 的修正语义
# ---------------------------------------------------------------------------


@case("有效值是投影：不写回、不增 revision")
def _() -> None:
    pool = health_pool()
    base_revision = pool.revision
    mods = (Modifier("m1", "additive", Decimal(20), source_ref="buff"),)
    effective = pool.effective(mods)
    assert effective == Decimal(100)  # 已在上界，clamp
    assert pool.value == Decimal(100)
    assert pool.revision == base_revision, "投影不得产生事件"


@case("修正源按 priority + id 稳定排序（不依赖遍历顺序）")
def _() -> None:
    pool = health_pool(initial=Decimal(50))
    mods_a = (
        Modifier("z", "multiplicative", Decimal(2)),
        Modifier("a", "additive", Decimal(10)),
    )
    mods_b = tuple(reversed(mods_a))
    assert pool.effective(mods_a) == pool.effective(mods_b)


@case("多 override 冲突被拒绝")
def _() -> None:
    pool = health_pool(initial=Decimal(50))
    mods = (
        Modifier("o1", "override", Decimal(80)),
        Modifier("o2", "override", Decimal(90)),
    )
    with expect_raises(PoolError, "modifier_conflict_unresolved"):
        pool.effective(mods)


@case("clamp 是 Pool 不变量，不是 modifier 操作")
def _() -> None:
    pool = health_pool(initial=Decimal(50))
    # 超出上界的有效值被 clamp 到界内，而不是报错（投影阶段）
    effective = pool.effective((Modifier("boost", "additive", Decimal(999)),))
    assert effective == Decimal(100)


# ---------------------------------------------------------------------------
# Bond: 六条不变量 + 共存性
# ---------------------------------------------------------------------------


def granary() -> BondStore:
    return BondStore(fact_type="fact:asset:granary-01:rights")


@case("B1 端点为空被拒绝")
def _() -> None:
    store = granary()
    with expect_raises(BondError, "bond_endpoint_missing"):
        store.grant("b1", "", "granary-01", BondType.OWNERSHIP, "county:zhaoling", BondTerm.forever(), "evt-1")


@case("B2 作用域为空被拒绝")
def _() -> None:
    store = granary()
    with expect_raises(BondError, "bond_scope_missing"):
        store.grant("b1", "house-zhao", "granary-01", BondType.OWNERSHIP, "", BondTerm.forever(), "evt-1")


@case("B6 来源为空被拒绝")
def _() -> None:
    store = granary()
    with expect_raises(BondError, "bond_source_missing"):
        store.grant("b1", "house-zhao", "granary-01", BondType.OWNERSHIP, "county:zhaoling", BondTerm.forever(), "")


@case("B5 同 (type,subject,target,scope) 重复建立被拒绝")
def _() -> None:
    store = granary()
    kwargs = dict(
        bond_ref="b1",
        subject_ref="house-zhao",
        target_ref="granary-01",
        bond_type=BondType.OWNERSHIP,
        scope="county:zhaoling",
        term=BondTerm.forever(),
        source_event_ref="evt-1",
    )
    store.grant(**kwargs)
    kwargs["bond_ref"] = "b2"
    with expect_raises(BondError, "bond_conflict_same_key"):
        store.grant(**kwargs)


@case("B5 反面：不同类型可共存于同一资产且归不同主体")
def _() -> None:
    store = granary()
    store.grant("own-1", "house-zhao", "granary-01", BondType.OWNERSHIP,
                "county:zhaoling", BondTerm.forever(), "evt-1")
    store.grant("cus-1", "magistrate", "granary-01", BondType.CUSTODY,
                "county:zhaoling", BondTerm.forever(), "evt-2")
    store.grant("ctl-1", "garrison", "granary-01", BondType.AUTHORITY,
                "county:zhaoling", BondTerm.forever(), "evt-3")

    rights = store.all_active_for("granary-01", "county:zhaoling")
    assert rights["ownership"] == ["house-zhao"]
    assert rights["custody"] == ["magistrate"]
    assert rights["authority"] == ["garrison"]

    # 这是 v1 的 active_right_by_asset 单值映射做不到的
    assert len(rights) == 3


@case("B3 到期：按世界时钟失效并产生事件")
def _() -> None:
    store = granary()
    store.grant("auth-1", "magistrate", "granary-01", BondType.AUTHORITY,
                "county:zhaoling", BondTerm.until(100), "evt-1")
    assert store.holders_of("granary-01", BondType.AUTHORITY, "county:zhaoling") == ["magistrate"]

    assert store.expire(50) == []
    expired = store.expire(100)
    assert expired == ["auth-1"]
    assert store.holders_of("granary-01", BondType.AUTHORITY, "county:zhaoling") == []


@case("B4 撤销：产生新事件，历史保留")
def _() -> None:
    store = granary()
    store.grant("auth-1", "magistrate", "granary-01", BondType.AUTHORITY,
                "county:zhaoling", BondTerm.forever(), "evt-1")
    store.revoke("auth-1", "征发权被收回")

    types = [e.event_type for e in store.events]
    assert types == ["bond.granted", "bond.revoked"], types
    # 历史记录仍在，只是 active=False
    assert store.get("auth-1").active is False


@case("转移：旧契作废 + 新契建立，两条事件")
def _() -> None:
    store = granary()
    store.grant("own-1", "house-zhao", "granary-01", BondType.OWNERSHIP,
                "county:zhaoling", BondTerm.forever(), "evt-1")
    store.transfer("own-1", "house-li", "evt-2")

    assert store.holders_of("granary-01", BondType.OWNERSHIP, "county:zhaoling") == ["house-li"]
    assert store.get("own-1").active is False


@case("B5 转移目标已有同键契时被拒绝")
def _() -> None:
    store = granary()
    store.grant("own-1", "house-zhao", "granary-01", BondType.OWNERSHIP,
                "county:zhaoling", BondTerm.forever(), "evt-1")
    store.grant("own-2", "house-li", "granary-01", BondType.OWNERSHIP,
                "county:zhaoling", BondTerm.forever(), "evt-2")
    with expect_raises(BondError, "bond_conflict_same_key"):
        store.transfer("own-1", "house-li", "evt-3")


@case("五种契用同一套 grant/revoke API")
def _() -> None:
    store = BondStore(fact_type="fact:world:*:bonds")
    specs = [
        ("o", "a", "t1", BondType.OWNERSHIP, {"share": 1}),
        ("c", "b", "t2", BondType.CUSTODY, {"capacity": 100}),
        ("a", "c", "t3", BondType.AUTHORITY, {"command_scope": "gate-east", "delegable": False}),
        ("f", "d", "t4", BondType.AFFILIATION, {"rank": "squad-lead", "slot": 3}),
        ("l", "e", "t5", BondType.OBLIGATION, {"amount": 50, "unit": "grain", "due_tick": 300}),
    ]
    for ref, subj, target, btype, attrs in specs:
        store.grant(ref, subj, target, btype, "scope-x", BondTerm.forever(), "evt", attrs)

    assert store.active_count == 5
    for ref, subj, target, btype, _attrs in specs:
        assert store.holders_of(target, btype, "scope-x") == [subj]
        store.revoke(ref, "cleanup")
    assert store.active_count == 0


@case("未知属性被拒绝（防止各类型悄悄长出专属语义）")
def _() -> None:
    store = granary()
    with expect_raises(BondError, "bond_attribute_unknown"):
        store.grant("x", "a", "b", BondType.OWNERSHIP, "s", BondTerm.forever(), "e",
                    {"command_scope": "nope"})


# ---------------------------------------------------------------------------
# D1 判定
# ---------------------------------------------------------------------------


def main() -> int:
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = len(RESULTS) - passed

    for name, ok, detail in RESULTS:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}")
        if detail:
            print(f"       {detail}")

    print()
    print(f"合计 {len(RESULTS)} 项：通过 {passed}，失败 {failed}")
    print()

    if failed:
        print("D1 判定：未通过。需先修复失败项，再决定原语清单。")
        return 1

    print("D1 判定：原型层面收敛。")
    print("  注意：这只证明两原语的规格可独立成立；")
    print("  不证明它们能与现有 runtime 无痛对接，也不证明性能。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
