"""Bond 原语原型 —— 验证 v2 六原语中的 Bond 能否把五种契压成同一形状。

本文件是 docs/architecture-v2/10-待决/01-待决清单.md 中 D1 的第二半验证。
只依赖标准库；不 import Paralls 任何代码。

D1 的判定问题：产权 / 保管 / 授权 / 归属 / 义务
能不能用同一条 grant/revoke/transfer/supersede 语义表达？

要证明的不变量（见 02-原语/02-六原语规格.md）：
    B1  有向：subject -> target，方向不可互换
    B2  有作用域：只在 scope 内有效
    B3  有有效期：可永久，但必须显式声明
    B4  可撤销：撤销产生新事件，不删除历史
    B5  同一 (type, subject, target, scope) 的有效契不得冲突
    B6  凭据来源必须可追溯（source_event_ref）

重点验证 B5 的反面：
    现有 ownership_runtime.py 的 active_right_by_asset 是单值映射，
    无法表达"产权归甲、保管归乙、控制归丙"同时成立。
    Bond 必须支持不同类型的契共存于同一资产。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class BondError(Exception):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


# ---------------------------------------------------------------------------
# 契的类型：五种，同一个原语
# ---------------------------------------------------------------------------


class BondType(str, Enum):
    OWNERSHIP = "ownership"      # 产权：这块地属谁
    CUSTODY = "custody"          # 保管：谁看着这批粮
    AUTHORITY = "authority"      # 授权：谁能征发
    AFFILIATION = "affiliation"  # 归属：谁属哪支队伍
    OBLIGATION = "obligation"    # 义务/债务：谁欠谁


# 每种类型允许的扩展属性。这是 D1 的关键：
# 如果某类型需要无法用通用 attribute 表达的语义，Bond 就不成立。
ALLOWED_ATTRS: dict[BondType, frozenset[str]] = {
    BondType.OWNERSHIP: frozenset({"share"}),
    BondType.CUSTODY: frozenset({"capacity"}),
    BondType.AUTHORITY: frozenset({"command_scope", "delegable"}),
    BondType.AFFILIATION: frozenset({"rank", "slot"}),
    BondType.OBLIGATION: frozenset({"amount", "unit", "due_tick"}),
}


@dataclass(frozen=True)
class BondTerm:
    """有效期。B3：可永久，但必须显式声明 -- 用 BondTerm.forever() 而不是省略。"""

    expires_at_tick: int | None

    @staticmethod
    def forever() -> "BondTerm":
        return BondTerm(expires_at_tick=None)

    @staticmethod
    def until(tick: int) -> "BondTerm":
        if tick < 0:
            raise BondError("bond_term_invalid", str(tick))
        return BondTerm(expires_at_tick=tick)

    @property
    def is_forever(self) -> bool:
        return self.expires_at_tick is None

    def expired_at(self, world_tick: int) -> bool:
        return self.expires_at_tick is not None and world_tick >= self.expires_at_tick


@dataclass(frozen=True)
class BondEvent:
    event_type: str
    fact_type: str
    payload: dict
    revision: int


# ---------------------------------------------------------------------------
# 契实例
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _BondRecord:
    bond_ref: str
    subject_ref: str
    target_ref: str
    bond_type: BondType
    scope: str
    term: BondTerm
    source_event_ref: str
    attributes: dict
    active: bool = True

    def key(self) -> tuple[str, str, str, str]:
        """B5 的冲突键：(type, subject, target, scope)。"""
        return (self.bond_type.value, self.subject_ref, self.target_ref, self.scope)


@dataclass
class BondStore:
    """一个 Bond FactType 在某个 (scope, epoch) 上的事实流。

    注意：这里存的是"某资产上的全部契"，不是"每条资产一个持有者"。
    这正是与 ownership_runtime.py 的 active_right_by_asset 的根本差别。
    """

    fact_type: str
    epoch: int = 1
    revision: int = field(default=0, init=False)

    _records: dict[str, _BondRecord] = field(default_factory=dict, init=False)
    _events: list[BondEvent] = field(default_factory=list, init=False)

    # -- 写 ---------------------------------------------------------------

    def grant(
        self,
        bond_ref: str,
        subject_ref: str,
        target_ref: str,
        bond_type: BondType,
        scope: str,
        term: BondTerm,
        source_event_ref: str,
        attributes: dict | None = None,
    ) -> None:
        """建立一条契。B1/B2/B3/B5/B6 全部在这里校验。"""
        if not subject_ref or not target_ref:
            raise BondError("bond_endpoint_missing")  # B1
        if not scope:
            raise BondError("bond_scope_missing")  # B2
        if term is None:
            raise BondError("bond_term_missing")  # B3：必须显式
        if not source_event_ref:
            raise BondError("bond_source_missing")  # B6
        if bond_ref in self._records:
            raise BondError("bond_ref_duplicate", bond_ref)

        attrs = dict(attributes or {})
        unknown = set(attrs) - ALLOWED_ATTRS[bond_type]
        if unknown:
            raise BondError("bond_attribute_unknown", f"{bond_type.value}:{sorted(unknown)}")

        record = _BondRecord(
            bond_ref=bond_ref,
            subject_ref=subject_ref,
            target_ref=target_ref,
            bond_type=bond_type,
            scope=scope,
            term=term,
            source_event_ref=source_event_ref,
            attributes=attrs,
        )

        # B5：同 (type, subject, target, scope) 的有效契不得冲突
        if any(r.active and r.key() == record.key() for r in self._records.values()):
            raise BondError("bond_conflict_same_key", str(record.key()))

        self._records[bond_ref] = record
        self._emit(
            "bond.granted",
            {
                "bond_ref": bond_ref,
                "subject": subject_ref,
                "target": target_ref,
                "type": bond_type.value,
                "scope": scope,
                "term": term.expires_at_tick,
                "source_event_ref": source_event_ref,
                "attributes": attrs,
            },
        )

    def revoke(self, bond_ref: str, reason: str) -> None:
        """B4：撤销产生新事件，不删除历史。"""
        record = self._require(bond_ref)
        if not record.active:
            raise BondError("bond_already_inactive", bond_ref)
        self._records[bond_ref] = _BondRecord(**{**record.__dict__, "active": False})
        self._emit("bond.revoked", {"bond_ref": bond_ref, "reason": reason})

    def transfer(self, bond_ref: str, new_holder: str, source_event_ref: str) -> None:
        """转移持有者。旧契作废，新契建立 -- 两条事件，不是一条。"""
        record = self._require(bond_ref)
        if not record.active:
            raise BondError("bond_already_inactive", bond_ref)

        self._records[bond_ref] = _BondRecord(**{**record.__dict__, "active": False})
        self._emit(
            "bond.transferred",
            {"bond_ref": bond_ref, "previous_subject": record.subject_ref, "new_subject": new_holder},
        )

        new_ref = f"{bond_ref}:t{self.revision}"
        new_record = _BondRecord(
            bond_ref=new_ref,
            subject_ref=new_holder,
            target_ref=record.target_ref,
            bond_type=record.bond_type,
            scope=record.scope,
            term=record.term,
            source_event_ref=source_event_ref,
            attributes=record.attributes,
        )
        if any(r.active and r.key() == new_record.key() for r in self._records.values()):
            raise BondError("bond_conflict_same_key", str(new_record.key()))
        self._records[new_ref] = new_record

    def supersede(self, old_ref: str, new_ref_spec: dict) -> None:
        """一契取代另一契。用于继任、授权轮替。"""
        old = self._require(old_ref)
        if not old.active:
            raise BondError("bond_already_inactive", old_ref)
        self.revoke(old_ref, "superseded")
        self.grant(**new_ref_spec)

    def expire(self, world_tick: int) -> list[str]:
        """B3：按世界时钟到期。返回本次到期的 bond_ref 列表。"""
        expired: list[str] = []
        for bond_ref, record in list(self._records.items()):
            if record.active and record.term.expired_at(world_tick):
                self._records[bond_ref] = _BondRecord(**{**record.__dict__, "active": False})
                self._emit("bond.expired", {"bond_ref": bond_ref, "world_tick": world_tick})
                expired.append(bond_ref)
        return expired

    # -- 读 ---------------------------------------------------------------

    def holders_of(self, target_ref: str, bond_type: BondType, scope: str) -> list[str]:
        """某资产在某类契上的全部持有一方。

        这是 v1 做不到的操作：返回列表而不是单个值。
        """
        return [
            r.subject_ref
            for r in self._records.values()
            if r.active
            and r.target_ref == target_ref
            and r.bond_type is bond_type
            and r.scope == scope
        ]

    def all_active_for(self, target_ref: str, scope: str) -> dict[str, list[str]]:
        """某资产的全部有效契，按类型分组。

        关键断言：同一个资产上，产权、保管、控制可以对不同人同时成立。
        """
        result: dict[str, list[str]] = {t.value: [] for t in BondType}
        for r in self._records.values():
            if r.active and r.target_ref == target_ref and r.scope == scope:
                result[r.bond_type.value].append(r.subject_ref)
        return {k: v for k, v in result.items() if v}

    def get(self, bond_ref: str) -> _BondRecord:
        return self._require(bond_ref)

    # -- 内部 -------------------------------------------------------------

    def _require(self, bond_ref: str) -> _BondRecord:
        record = self._records.get(bond_ref)
        if record is None:
            raise BondError("bond_not_found", bond_ref)
        return record

    def _emit(self, event_type: str, payload: dict) -> None:
        self.revision += 1
        self._events.append(
            BondEvent(
                event_type=event_type,
                fact_type=self.fact_type,
                payload=payload,
                revision=self.revision,
            )
        )

    @property
    def events(self) -> tuple[BondEvent, ...]:
        return tuple(self._events)

    @property
    def active_count(self) -> int:
        return sum(1 for r in self._records.values() if r.active)
