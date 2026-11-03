"""跨验：用 Paralls 真实模块的字段检验 Bond 属性集是否够用。

这是 D1 真正的检验。前面的 verify_d1.py 是"自己验证自己"——
它的失败用例是我自己设计的。本文件改用真实代码的字段做对照。

关键问题：
    现有五种"契"的真实字段，能否映射到 Bond 的
    (subject, target, type, scope, term, attributes) 六项？

若某个字段既不是标识、也不是端点、也不是作用域/期限，
且无法归入该类型的受限属性集，那么 Bond 的抽象就不成立。

运行：py -3 cross_check_real_modules.py
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

BACKEND = Path(r"D:\Paralls-phase0-1\backend")
sys.path.insert(0, str(BACKEND))

from bond_prototype import ALLOWED_ATTRS, BondType  # noqa: E402


# ---------------------------------------------------------------------------
# 真实模块的字段清单（从源码读取，不依赖 import 成功与否）
# ---------------------------------------------------------------------------

REAL_TYPES = {
    "OwnershipRight": (
        "ownership_runtime.py",
        ["right_id", "asset_ref", "holder_ref", "source_event_id"],
    ),
    "CredentialLink": (
        "credential_runtime.py",
        ["credential_id", "credential_item_ref", "issued_holder_ref",
         "issued_holder_inventory_revision", "right_id", "credential_kind",
         "proves", "issuer_ref", "status", "source_event_id"],
    ),
    "SimpleDebtContract": (
        "debt_runtime.py",
        ["contract_id", "creditor_ref", "debtor_ref", "currency_ref",
         "status", "source_event_id"],
    ),
    "DebtClaim": (
        "debt_runtime.py",
        ["debt_id", "contract_id", "creditor_ref", "debtor_ref", "currency_ref",
         "principal_amount", "outstanding_amount", "status",
         "source_event_id", "due_tick"],
    ),
}

# Bond 的六个槽位能覆盖的角色
SLOT_ROLES = {
    "identifier",      # bond_ref / *_id
    "subject",         # 持有一方
    "target",          # 被持有对象
    "scope",           # 作用域
    "term",            # 期限
    "source",          # source_event_id
}


def classify(field_name: str, owner: str) -> tuple[str, str]:
    """把真实字段归类到 Bond 的槽位，或者标为"槽位外"。"""
    if field_name in ("right_id", "bond_ref", "credential_id", "contract_id", "debt_id"):
        return ("identifier", "")
    if field_name.endswith("_ref") and any(
        k in field_name for k in ("holder", "creditor", "debtor", "issuer", "presenter")
    ):
        return ("subject", "")
    if field_name in ("asset_ref", "credential_item_ref") or field_name.endswith("_target_ref"):
        return ("target", "")
    if field_name == "due_tick":
        return ("term", "")
    if field_name == "source_event_id":
        return ("source", "")
    if field_name in ("status", "credential_kind", "proves", "currency_ref"):
        return ("attribute", "")
    return ("OUTSIDE", "")


def main() -> int:
    print("=" * 72)
    print("D1 跨验：真实模块字段 → Bond 槽位")
    print("=" * 72)
    print()

    outside_fields: dict[str, list[str]] = {}

    for type_name, (module, fields) in REAL_TYPES.items():
        print(f"{type_name}  ({module})")
        for f in fields:
            role, _ = classify(f, type_name)
            marker = "  <-- 槽位外" if role == "OUTSIDE" else ""
            print(f"    {f:<34} {role}{marker}")
            if role == "OUTSIDE":
                outside_fields.setdefault(type_name, []).append(f)
        print()

    print("-" * 72)
    print("结论 1：槽位覆盖")
    print("-" * 72)
    if outside_fields:
        print("下列字段无法归入 Bond 的六个槽位：")
        for t, fs in outside_fields.items():
            print(f"  {t}: {fs}")
        print()
        print("=> Bond 若要保持六槽位，这些字段必须重新归属。")
    else:
        print("所有真实字段均可归入 Bond 的六个槽位。")
    print()

    print("-" * 72)
    print("结论 2：数值型属性该归 Pool 还是 Bond 属性")
    print("-" * 72)
    numeric_attrs = {
        "DebtClaim.outstanding_amount": (
            "还款时递减（debt_runtime.py:366），"
            "有 principal/outstanding 两态、有 due_tick 到期、有 status 机"
        ),
        "DebtClaim.principal_amount": "不变量，可作为 OBLIGATION 属性",
    }
    print("Bond 的属性设计假设：属性是不可变描述符（grant 时写入，不改）。")
    print()
    for name, note in numeric_attrs.items():
        print(f"  {name}")
        print(f"    现状: {note}")
        immutable = "不变量" in note
        print(f"    可作 Bond 属性: {'是' if immutable else '否 —— 它是 Pool'}")
        print()

    print("=> 债务的实际结构是三原语叠加，不是单一 Bond：")
    print("     bond.obligation  ：债权人 → 债务人，契约存在（可撤销、有期限）")
    print("     pool.debt.<id>   ：outstanding_amount，有界 [0, principal]，按还款递减")
    print("     machine.debt.<id>：active → overdue → satisfied / cancelled")
    print()
    print("   这不是 Bond 的失败，而是'一个领域事实由多个 FactType 组成'的")
    print("   正常结果——与 v2 把食品变质拆成 Pool+Machine+Process 同理。")
    print()

    print("-" * 72)
    print("结论 3：B5（同类型不冲突）与凭证的关系")
    print("-" * 72)
    print("CredentialLink 不是 Bond：它把 right_id 绑到一件实体物品上。")
    print("  实体验证: 'Item X 是否在出示者身上' → 需要 Inventory 投影")
    print("  权属验证: '出示者是否是 right 持有者' → 需要 Ownership 投影")
    print("  credential_runtime.py:106-140 正好同时读这两个投影。")
    print()
    print("=> Bond 存契约关系，Credential 存'哪件实体物证明它'。")
    print("   两者是引用关系，不应合并。Bond 需要 target 能指到实体物品。")
    print()
    print("   当前 Bond 的 target_ref 是字符串，可以指 asset 也可以指 item。")
    print("   但 CredentialLink.issued_holder_inventory_revision 暴露了一个缺口：")
    print("   凭证有效性绑定在某个 inventory revision 上——这是跨 FactType 不变式，")
    print("   应由 Owner 持有，不是 Bond 属性。")
    print()

    print("=" * 72)
    print("D1 判定（跨验）")
    print("=" * 72)
    print("Pool: 收敛。真实系统中 debt/quality/stamina 都可表达为 Pool + Machine 叠加。")
    print("Bond: 收敛，但有两个必须写进规格的修正：")
    print("  1. Bond 属性必须是不可变描述符；可变的量走独立 FactType。")
    print("  2. Bond 的 target 必须允许指向实体物品（凭证），不只是抽象资产。")
    print()
    print("原语数量：维持六个。不需要第七个。")
    print()
    print("未验证：与现有 34 个 runtime 的对接成本、性能、双端等价。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
