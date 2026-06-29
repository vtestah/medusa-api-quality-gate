"""Property-based check for cart line-item aggregation by ``variant_id``.

# Feature: test-coverage-expansion, Property 4: Состав корзины корректно агрегируется по variant_id
"""

from collections import OrderedDict
from collections.abc import Sequence

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quality_gate.models import aggregate_line_items

pytestmark = [pytest.mark.cart]


# A small alphabet keeps the variant_id space narrow so sequences naturally
# produce collisions, exercising the aggregation (summing) path. Stripped and
# filtered to guarantee non-empty variant ids (the NonEmptyStr contract).
variant_ids = (
    st.text(alphabet="abcde", min_size=1, max_size=4)
    .map(str.strip)
    .filter(lambda value: value != "")
)

# Quantities are integers >= 1 (LineItem enforces ge=1).
quantities = st.integers(min_value=1, max_value=1000)

# Sequences of (variant_id, quantity) additions.
additions_strategy = st.lists(st.tuples(variant_ids, quantities), max_size=30)


# Feature: test-coverage-expansion, Property 4: Состав корзины корректно агрегируется по variant_id
@settings(max_examples=100)
@given(additions=additions_strategy)
def test_aggregate_line_items_collapses_by_variant_id(
    additions: Sequence[tuple[str, int]],
) -> None:
    """One LineItem per unique variant_id, quantity equal to the sum of additions.

    Validates: Requirements 4.3, 4.4
    """

    result = aggregate_line_items(additions)

    # Expected totals computed independently of the implementation, preserving
    # first-occurrence order for the unique-count comparison.
    expected_totals: OrderedDict[str, int] = OrderedDict()
    for variant_id, quantity in additions:
        expected_totals[variant_id] = expected_totals.get(variant_id, 0) + quantity

    # 1. One LineItem per unique variant_id.
    assert len(result) == len(expected_totals)

    # 2. Each LineItem's quantity equals the sum of all quantities for its variant.
    for line_item in result:
        assert line_item.quantity == expected_totals[line_item.variant_id]

    # 3. The result's variant_ids are exactly the set of unique input variant_ids.
    assert {line_item.variant_id for line_item in result} == set(expected_totals)
