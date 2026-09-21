from __future__ import annotations

from types import SimpleNamespace

from apps.recipes.query import BadQuery, parse_have, parse_have_groups, parse_intent
from apps.recipes.services.pantry import resolve_pantry_text
from apps.recipes.services.snapshots import snapshot_fits
from apps.recipes.services.solve import (
    CookingSolution,
    assign_buckets,
    axis_combos,
    build_board,
    combo_fits,
    combo_method_equipment,
    intent_adjust,
    is_core_line,
    match_pantry,
    pantry_why,
    protein_from_pantry,
    serialize_solution,
    solve_recipe,
)
from apps.recipes.services.substitutions import SubRule, cover_need


class FakeRelated:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


def test_u15_oven_override_not_base_stew():
    oven = SimpleNamespace(
        axis="equipment",
        has_delta=True,
        code="oven",
        equipment="oven",
        cook_method_override="oven",
    )
    recipe = SimpleNamespace(
        cook_method="stew",
        equipment="pot",
        variants=FakeRelated([oven]),
    )
    combos = axis_combos(recipe, explore=True)
    matching = [
        combo
        for combo in combos
        if combo_fits(recipe, combo[0], combo[1], ["oven"], [])
    ]
    assert matching
    method, equipment = combo_method_equipment(recipe, matching[-1][0], matching[-1][1])
    assert method == "oven"
    assert equipment == "oven"
    assert not combo_fits(recipe, None, None, ["oven"], [])


def test_u15b_protein_override_not_base_poultry():
    beef = SimpleNamespace(
        axis="addon",
        has_delta=True,
        code="beef",
        protein_base_override="beef",
    )
    garnish = SimpleNamespace(
        axis="addon",
        has_delta=True,
        code="spicy",
        protein_base_override=None,
    )
    recipe = SimpleNamespace(
        protein_base="poultry",
        protein_bases_extra=[],
        cook_method="pan_fry",
        equipment="skillet",
        variants=FakeRelated([beef, garnish]),
    )
    combos = axis_combos(recipe, explore=True)
    matching = [
        combo
        for combo in combos
        if combo_fits(recipe, combo[0], combo[1], [], [], ["beef"])
    ]
    assert matching
    assert all(combo[0] is beef for combo in matching)
    assert not combo_fits(recipe, None, None, [], [], ["beef"])
    assert combo_fits(recipe, None, None, [], [], ["poultry"])


def test_combo_fits_extra_protein_without_chip():
    recipe = SimpleNamespace(
        protein_base="beef",
        protein_bases_extra=["pork"],
        cook_method="boil",
        equipment="pot",
        variants=FakeRelated([]),
    )
    assert combo_fits(recipe, None, None, [], [], ["pork"])
    assert combo_fits(recipe, None, None, [], [], ["beef"])
    assert not combo_fits(recipe, None, None, [], [], ["poultry"])


def test_u16_pantry_buckets_and_why_has_no_score():
    lines = [
        {
            "canonical_id": "chicken_thighs",
            "name": "куриные бёдра",
            "optional": False,
            "unit": "g",
        },
        {
            "canonical_id": "onion",
            "name": "лук",
            "optional": False,
            "unit": "g",
        },
        {
            "canonical_id": "salt",
            "name": "соль",
            "optional": False,
            "unit": "g",
        },
    ]
    shopping, substitutions, hits, missing, desirable, covered, _used = match_pantry(
        lines, ["chicken_thighs", "onion"], []
    )
    assert missing == 0
    assert hits == 2
    assert covered == {"chicken_thighs", "onion"}
    assert shopping == []
    assert substitutions == []
    why = pantry_why(shopping, substitutions, has_have=True)
    assert "можно приготовить сейчас" in why
    assert all("score" not in line.lower() for line in why)

    almost_shop, _subs, _hits, almost_missing, _des, _cov, _used = match_pantry(
        lines, ["chicken_thighs"], []
    )
    assert almost_missing == 1
    assert almost_shop[0]["title"] == "лук"

    now = CookingSolution(
        slug="a",
        title="A",
        protein_base="poultry",
        cook_method="pan_fry",
        dish_type="main",
        equipment="skillet",
        applied_axes={"variant": None, "equipment": "skillet"},
        bucket="match",
        why=why,
        score=20,
        shopping_delta=[],
        substitutions=[],
        allergens={"contains": [], "may_contain": [], "unknown": []},
        high_risk_flags=[],
        has_delta_variants=False,
        pantry_hits=2,
    )
    almost = CookingSolution(
        slug="b",
        title="B",
        protein_base="poultry",
        cook_method="pan_fry",
        dish_type="main",
        equipment="skillet",
        applied_axes={"variant": None, "equipment": "skillet"},
        bucket="match",
        why=["нужно докупить: лук"],
        score=10,
        shopping_delta=[{"canonical_id": "onion", "title": "лук"}],
        substitutions=[],
        allergens={"contains": [], "may_contain": [], "unknown": []},
        high_risk_flags=[],
        has_delta_variants=False,
        pantry_hits=1,
    )
    buckets = assign_buckets([now, almost], has_have=True)
    assert buckets["now"][0].slug == "a"
    assert buckets["almost"][0].slug == "b"
    assert now.bucket == "now"
    assert almost.bucket == "almost"


def test_u17_substitution_quality_and_forbidden():
    rules = [
        SubRule(frm="vegetable_oil", to="olive_oil", quality=0.86, forbidden=False),
        SubRule(frm="yogurt", to="water", quality=0.12, forbidden=True),
        SubRule(frm="stock", to="water", quality=0.40, forbidden=False),
        SubRule(frm="onion", to="shallot", quality=0.85, forbidden=False),
    ]
    have = {"olive_oil", "water"}
    covered, quality = cover_need("vegetable_oil", have, rules)
    assert covered == "olive_oil"
    assert quality == 0.86
    assert cover_need("yogurt", have, rules) == (None, None)
    assert cover_need("stock", have, rules) == (None, None)

    lines = [
        {
            "canonical_id": "onion",
            "name": "лук",
            "optional": False,
            "unit": "g",
        }
    ]
    shopping, substitutions, hits, missing, _des, _cov, _used = match_pantry(
        lines, ["shallot"], rules, {"shallot": "шалот"}
    )
    assert missing == 0
    assert hits == 1
    assert substitutions[0]["to_id"] == "shallot"


def test_u18_unknown_have_is_400():
    class DummyRequest:
        query_params = type(
            "Q",
            (),
            {
                "getlist": staticmethod(lambda key: ["nope"] if key == "have" else []),
            },
        )()

    try:
        parse_have(DummyRequest(), known={"onion"})
        raise AssertionError("expected BadQuery")
    except BadQuery:
        pass

    class EmptyRequest:
        query_params = type(
            "Q",
            (),
            {"getlist": staticmethod(lambda key: [])},
        )()

    assert parse_have(EmptyRequest(), known={"onion"}) == []


def _dummy(params: dict[str, list[str]]):
    class DummyRequest:
        query_params = type(
            "Q",
            (),
            {"getlist": staticmethod(lambda key, mapping=params: mapping.get(key, []))},
        )()

    return DummyRequest()


def test_resolve_kuritsa_and_spaces():
    titles = {
        "chicken_thighs": "куриные бёдра",
        "onion": "лук",
        "buckwheat": "гречка",
    }
    known = set(titles)
    found, unknown = resolve_pantry_text("курица, гречка, лук", titles=titles, known=known)
    assert unknown == []
    assert "chicken_thighs" in found
    assert "chicken_breast" in found
    assert "buckwheat" in found
    assert "onion" in found
    spaced, spaced_unknown = resolve_pantry_text("курица гречка лук", titles=titles, known=known)
    assert spaced_unknown == []
    assert "chicken_thighs" in spaced
    chicken = parse_have(_dummy({"have": ["курица"]}), known=known, titles=titles)
    assert "chicken_thighs" in chicken
    assert "chicken_breast" in chicken


def test_unknown_intent_and_have_group_are_400():
    try:
        parse_intent(_dummy({"intent": ["nope"]}))
        raise AssertionError("expected BadQuery")
    except BadQuery:
        pass
    try:
        parse_have_groups(_dummy({"have_group": ["nope"]}))
        raise AssertionError("expected BadQuery")
    except BadQuery:
        pass
    assert parse_intent(_dummy({"intent": ["fast"]})) == ["fast"]
    assert parse_have_groups(_dummy({"have_group": ["chicken"]})) == ["chicken"]
    assert parse_have_groups(_dummy({"have_group": ["fish"]})) == ["fish"]


def test_pork_and_oil_aliases():
    from apps.recipes.pantry_vocab import HAVE_GROUPS

    pork = parse_have(_dummy({"have": ["свинина"]}), known=set(), titles={})
    assert "pork_neck" in pork
    assert "pork_shoulder" in pork
    assert len(pork) > 1
    assert HAVE_GROUPS["fish"]
    assert "pollock" in HAVE_GROUPS["fish"]
    assert parse_have(_dummy({"have": ["капуста"]}), known={"onion"}, titles={"onion": "лук"}) == [
        "cabbage"
    ]
    assert parse_have(
        _dummy({"have": ["говяжья вырезка"]}), known=set(), titles={}
    ) == ["beef_tenderloin"]
    try:
        parse_have(_dummy({"have": ["масло"]}), known=set(), titles={})
        raise AssertionError("expected BadQuery")
    except BadQuery:
        pass


def test_common_spice_does_not_block():
    lines = [
        {"canonical_id": "onion", "name": "лук", "optional": False, "unit": "g"},
        {"canonical_id": "paprika", "name": "паприка", "optional": False, "unit": "g"},
    ]
    shopping, _subs, hits, missing, desirable, _cov, _used = match_pantry(lines, ["onion"], [])
    assert missing == 0
    assert hits == 1
    assert shopping == []
    assert desirable[0]["canonical_id"] == "paprika"
    why = pantry_why(shopping, [], has_have=True, desirable=desirable)
    assert any("желательно" in line for line in why)


def _sol(
    slug: str,
    method: str,
    steps: int,
    title: str | None = None,
    *,
    hits: int = 1,
    missing: int = 0,
    score: int = 10,
    protein: str = "poultry",
    have_used: int = 0,
    have_all: bool = False,
    dish_type: str = "main",
    time_total: int | None = None,
) -> CookingSolution:
    shopping = [{"canonical_id": "x", "title": "x"}] * missing
    return CookingSolution(
        slug=slug,
        title=title or slug,
        protein_base=protein,
        cook_method=method,
        dish_type=dish_type,
        equipment="skillet",
        applied_axes={"variant": None, "equipment": None},
        bucket="now",
        why=[],
        score=score,
        shopping_delta=shopping,
        substitutions=[],
        allergens={"contains": [], "may_contain": [], "unknown": []},
        high_risk_flags=[],
        has_delta_variants=False,
        pantry_hits=hits,
        step_count=steps,
        have_used=have_used,
        have_all=have_all,
        time_total_minutes=time_total,
    )


def test_build_board_featured_and_alts():
    stew = _sol("a", "stew", 8, "Тушёное", time_total=90)
    pan = _sol("b", "pan_fry", 4, "На сковороде", time_total=20)
    oven = _sol("c", "oven", 6, "В духовке", time_total=45)
    featured, alts = build_board(
        [stew, pan, oven],
        {"now": [stew, pan, oven], "almost": [], "best": []},
        has_have=True,
    )
    assert featured is not None
    assert featured.slug == "a"
    labels = [label for label, _item in alts]
    assert "Быстрее" in labels
    assert "В духовке" in labels
    assert "Проще" not in labels
    faster = next(item for label, item in alts if label == "Быстрее")
    assert faster.slug == "b"


def test_build_board_no_faster_without_minutes():
    stew = _sol("a", "stew", 8, "Тушёное")
    pan = _sol("b", "pan_fry", 2, "На сковороде")
    featured, alts = build_board(
        [stew, pan],
        {"now": [stew, pan], "almost": [], "best": []},
        has_have=True,
    )
    assert featured is not None
    labels = [label for label, _item in alts]
    assert "Быстрее" not in labels
    assert "На плите" in labels


def test_salt_is_not_core():
    assert not is_core_line(
        {"canonical_id": "salt", "optional": False, "unit": "g"}
    )
    assert is_core_line(
        {"canonical_id": "onion", "optional": False, "unit": "g"}
    )
    assert is_core_line(
        {"canonical_id": "steak", "optional": False, "unit": "to_taste", "is_anchor": True}
    )
    assert not is_core_line(
        {"canonical_id": "cumin", "optional": False, "unit": "tsp"}
    )
    assert not is_core_line(
        {"canonical_id": "vegetable_oil", "optional": False, "unit": "tbsp"}
    )
    assert not is_core_line(
        {"canonical_id": "water_or_stock", "optional": False, "unit": "ml"}
    )
    assert not is_core_line(
        {"canonical_id": "", "name": "хвостик", "optional": False, "unit": "g"}
    )
    shopping, _subs, hits, missing, _des, _cov, _used = match_pantry(
        [{"canonical_id": "", "name": "хвостик", "optional": False, "unit": "g"}],
        ["onion"],
        [],
    )
    assert shopping == []
    assert hits == 0
    assert missing == 0


def test_u20_mince_is_not_steak_or_butter():
    recipe = SimpleNamespace(protein_base="beef")
    pts, why = protein_from_pantry(
        recipe, ["beef_mince"], covered_ids=set(), titles={"beef_mince": "говяжий фарш"}
    )
    assert pts == 0
    assert why == []

    pts, why = protein_from_pantry(
        recipe,
        ["beef_mince"],
        covered_ids={"beef_mince"},
        titles={"beef_mince": "говяжий фарш"},
    )
    assert pts == 6
    assert why == ["есть говяжий фарш"]

    cases = (
        ("poultry", "chicken_breast", "куриная грудка", "chicken_thighs", "куриные бёдра"),
        ("beef", "steak", "стейк", "ribeye", "рибай"),
        ("beef", "beef", "говядина", "beef_chuck", "говяжья лопатка"),
        ("vegetables", "onion", "лук", "shallot", "лук-шалот"),
        ("eggs_dairy", "eggs", "яйца", "egg", "яйцо"),
    )
    for base, need, need_title, have_id, have_title in cases:
        titles = {need: need_title, have_id: have_title}
        rules = [SubRule(frm=need, to=have_id, quality=0.88, forbidden=False)]
        lines = [
            {
                "canonical_id": need,
                "name": need_title,
                "optional": False,
                "unit": "g",
            }
        ]
        _shop, subs, hits, missing, _des, covered, used = match_pantry(
            lines, [have_id], rules, titles
        )
        assert missing == 0
        assert hits == 1
        assert covered == {need}
        assert used == {have_id}
        assert subs[0]["to_id"] == have_id
        pts, why = protein_from_pantry(
            SimpleNamespace(protein_base=base),
            [have_id],
            covered_ids=covered,
            used_have=used,
            titles=titles,
        )
        assert pts == 6, (base, need, have_id, pts, why)
        assert why == [f"есть {have_title}"], (base, need, have_id, why)
        assert f"есть {need_title}" not in why

    steak = _sol("stejk-reverse-sear", "oven", 8, "Reverse sear", hits=0, missing=1, protein="beef")
    butter = _sol(
        "vzbitoe-slivochnoe-maslo",
        "no_cook",
        2,
        "Взбитое масло",
        hits=0,
        missing=1,
        dish_type="sauce",
        score=20,
    )
    mince = _sol("kotlety-iz-govyadiny", "pan_fry", 6, "Котлеты", hits=1, missing=2, protein="beef")
    buckets = assign_buckets([steak, butter, mince], has_have=True)
    assert [item.slug for item in buckets["almost"]] == ["kotlety-iz-govyadiny"]
    assert buckets["now"] == []
    assert buckets["best"] == []
    featured, alts = build_board([steak, butter, mince], buckets, has_have=True)
    assert featured is not None
    assert featured.slug == "kotlety-iz-govyadiny"
    assert all(item.slug != "vzbitoe-slivochnoe-maslo" for _label, item in alts)
    assert all(item.slug != "stejk-reverse-sear" for _label, item in alts)

    empty_buckets = assign_buckets([steak, butter], has_have=True)
    assert empty_buckets["now"] == []
    assert empty_buckets["almost"] == []
    assert empty_buckets["best"] == []
    featured_none, alts_none = build_board([steak, butter], empty_buckets, has_have=True)
    assert featured_none is None
    assert alts_none == []

    needy = _sol("tefteli-iz-govyadiny", "stew", 9, "Тефтели", hits=1, missing=3, protein="beef")
    needy_buckets = assign_buckets([steak, butter, needy], has_have=True)
    assert [item.slug for item in needy_buckets["best"]] == ["tefteli-iz-govyadiny"]
    featured_needy, _alts = build_board([steak, butter, needy], needy_buckets, has_have=True)
    assert featured_needy is not None
    assert featured_needy.slug == "tefteli-iz-govyadiny"


def test_u21_all_selected_ingredients_win():
    both = _sol(
        "gulyash",
        "stew",
        8,
        "Гуляш",
        hits=2,
        missing=2,
        have_used=2,
        have_all=True,
        protein="beef",
    )
    only_mince = _sol(
        "kotlety",
        "pan_fry",
        4,
        "Котлеты",
        hits=1,
        missing=0,
        have_used=1,
        have_all=False,
        protein="beef",
    )
    buckets = assign_buckets([only_mince, both], has_have=True)
    featured, _alts = build_board([only_mince, both], buckets, has_have=True)
    assert featured is not None
    assert featured.slug == "gulyash"


def test_u22_helpers_not_featured_when_a_dish_exists():
    butter = _sol(
        "vzbitoe-slivochnoe-maslo",
        "no_cook",
        2,
        "Взбитое масло",
        dish_type="sauce",
        score=20,
        hits=0,
        missing=1,
    )
    oil = _sol(
        "korichnevoe-maslo",
        "pan_fry",
        3,
        "Коричневое масло",
        dish_type="sauce",
        score=18,
        hits=0,
        missing=1,
    )
    omelette = _sol(
        "omlet",
        "pan_fry",
        6,
        "Омлет",
        dish_type="breakfast",
        score=8,
    )
    featured, alts = build_board(
        [butter, oil, omelette],
        {"now": [], "almost": [], "best": []},
        has_have=False,
    )
    assert featured is not None
    assert featured.slug == "omlet"
    assert all(item.slug != "vzbitoe-slivochnoe-maslo" for _label, item in alts)
    assert all(item.slug != "korichnevoe-maslo" for _label, item in alts)

    only_helpers, alts_helpers = build_board(
        [butter, oil],
        {"now": [], "almost": [], "best": []},
        has_have=False,
    )
    assert only_helpers is not None
    assert only_helpers.dish_type == "sauce"
    assert alts_helpers[0][1].dish_type == "sauce"


def test_meat_tree_and_parent_skip():
    from apps.recipes.pantry_vocab import (
        HAVE_GROUP_CHILDREN,
        HAVE_GROUP_LABEL_RU,
        HAVE_GROUPS,
        groups_to_expand,
        items_for_have_group,
    )

    assert HAVE_GROUP_CHILDREN["meat"] == ("pork", "beef", "lamb", "offal", "prep")
    beef = items_for_have_group("beef")
    assert beef[0] == "beef"
    assert "beef_tenderloin" in beef
    assert "beef_ribs" in beef
    assert "beef_round" in beef
    assert "beef_mince" in beef
    assert len(beef) > 5
    assert "rabbit" in HAVE_GROUPS["offal"]
    assert HAVE_GROUP_LABEL_RU["offal"] == "Субпродукты"
    assert items_for_have_group("prep") == ("shredded_beef",)
    assert groups_to_expand(["meat", "beef"]) == ["beef"]
    assert groups_to_expand(["meat", "prep"]) == ["prep"]
    assert groups_to_expand(["meat"]) == []
    assert groups_to_expand(["veg"]) == []
    assert groups_to_expand(["chicken"]) == []
    assert groups_to_expand(["chicken", "veg"]) == []
    assert groups_to_expand(["fish"]) == []
    assert groups_to_expand(["eggs"]) == []
    assert groups_to_expand(["other"]) == []
    assert groups_to_expand(["other", "canned"]) == ["canned"]
    assert HAVE_GROUP_CHILDREN["other"] == (
        "legumes",
        "canned",
        "frozen",
        "bakery",
        "sauces",
        "fats",
    )
    assert "canned_tuna" not in HAVE_GROUPS["canned"]
    assert "canned_beans" not in HAVE_GROUPS["legumes"]
    assert "canned_beans" in HAVE_GROUPS["canned"]
    assert "sour_cream" not in HAVE_GROUPS["sauces"]
    assert "butter" not in HAVE_GROUPS["fats"]
    assert "beetroot" in HAVE_GROUPS["veg"]
    assert "cabbage" in HAVE_GROUPS["veg"]

    from apps.recipes.services.pantry import fill_have_from_groups

    assert fill_have_from_groups([], ["veg"]) == []
    assert fill_have_from_groups([], ["chicken"]) == []
    assert fill_have_from_groups(["chicken_breast"], ["veg"]) == ["chicken_breast"]
    assert fill_have_from_groups(["chicken_breast"], ["chicken"]) == ["chicken_breast"]
    beef_pantry = fill_have_from_groups([], ["beef"])
    assert "beef_tenderloin" in beef_pantry
    assert "beef_mince" in beef_pantry
    assert "shredded_beef" not in beef_pantry
    assert "shredded_beef" not in HAVE_GROUPS["beef"]
    assert fill_have_from_groups(["beef_tenderloin"], ["beef"]) == ["beef_tenderloin"]
    assert fill_have_from_groups([], ["prep"]) == ["shredded_beef"]
    canned_pantry = fill_have_from_groups([], ["canned"])
    assert "canned_tomatoes" in canned_pantry
    assert "canned_tuna" not in canned_pantry
    assert fill_have_from_groups([], ["other"]) == []


def test_u21c_prep_leftover_is_not_raw_species():
    from apps.recipes.pantry_vocab import HAVE_GROUPS, availability_class
    from apps.recipes.services.solver_scoring import unmet_prep_core

    assert availability_class("shredded_beef") == "prep"
    lines = [
        {
            "canonical_id": "shredded_beef",
            "name": "говядина на волокна",
            "optional": False,
            "unit": "g",
            "is_anchor": True,
        }
    ]
    assert unmet_prep_core(lines, []) is True
    assert unmet_prep_core(lines, list(HAVE_GROUPS["beef"])) is True
    assert unmet_prep_core(lines, ["shredded_beef"]) is False

    recipe = SimpleNamespace(
        slug="govyadina-na-volokna-s-garnirom",
        title="Говядина на волокна с гарниром",
        dish_type="main",
        editorial_tested=False,
        protein_base="beef",
        cook_method="pan_fry",
        equipment="skillet",
        energy_profile="standard",
        variants=FakeRelated([]),
        content_version=1,
        snapshot_version=1,
        axis_snapshots=[
            {
                "variant": None,
                "equipment": "skillet",
                "home": True,
                "protein_base": "beef",
                "protein_bases": ["beef"],
                "cook_method": "pan_fry",
                "lines": lines,
                "allergens": {"contains": [], "may_contain": [], "unknown": []},
                "high_risk_flags": [],
                "step_count": 4,
                "time_total_minutes": 20,
                "time_active_minutes": 15,
                "addon_penalty": 0,
                "equipment_penalty": 0,
            }
        ],
    )
    catalog = {
        "has_delta_variants": False,
        "allowed_cuts": [],
        "protein_bases": ["beef"],
        "protein_variants": [],
    }
    kwargs = dict(
        filter_protein=[],
        filter_method=[],
        filter_dish=[],
        filter_equipment=[],
        catalog_item=catalog,
        rules=[],
        titles={"shredded_beef": "говядина на волокна"},
        intents=["fast"],
    )
    assert solve_recipe(recipe, have=list(HAVE_GROUPS["beef"]), **kwargs) is None
    assert solve_recipe(recipe, have=[], **kwargs) is None
    solved = solve_recipe(recipe, have=["shredded_beef"], **kwargs)
    assert solved is not None
    assert solved.requires_prep is True
    assert solved.slug == "govyadina-na-volokna-s-garnirom"

    from apps.recipes.services.pantry import fill_have_from_groups

    prep_have = fill_have_from_groups([], ["prep"])
    assert solve_recipe(recipe, have=prep_have, **kwargs) is not None


def test_calculator_chip_titles_drop_species_and_capitalize():
    from apps.recipes.pantry_vocab import chip_title

    assert chip_title("beef") == "Любая говядина"
    assert chip_title("beef_neck") == "Шея"
    assert chip_title("beef_mince") == "Фарш"
    assert chip_title("pork_neck") == "Шея"
    assert chip_title("chicken_breast") == "Грудка"
    assert chip_title("shredded_beef") == "Говядина на волокна"
    assert chip_title("onion") == "Лук"
    assert chip_title("beef_liver") == "Печень говяжья"
    assert chip_title("canned_tomatoes") == "Томаты"
    assert chip_title("canned_beans") == "Фасоль в банке"
    assert chip_title("sunflower_oil") == "Подсолнечное"


def test_u16b_substitution_status_is_not_now_copy():
    why = pantry_why(
        [],
        [{"from_title": "лук", "to_title": "шалот"}],
        has_have=True,
    )
    assert "можно приготовить с заменой" in why
    assert "можно приготовить сейчас" not in why


def test_u39_fast_uses_minutes_without_dropping():
    assembled = SimpleNamespace(cook_method="stew")
    recipe = SimpleNamespace(energy_profile="standard")
    short, short_why = intent_adjust(
        recipe, assembled, ["fast"], 4, time_total_minutes=20
    )
    long, long_why = intent_adjust(
        recipe, assembled, ["fast"], 4, time_total_minutes=90
    )
    assert short > long
    assert "быстрее по времени" in short_why
    assert "быстрее по времени" not in long_why


def test_u40_serialize_time_and_combo_allergens():
    item = _sol("x", "pan_fry", 3, time_total=35)
    item.time_active_minutes = 15
    item.allergens = {"contains": [], "may_contain": [], "unknown": []}
    payload = serialize_solution(item)
    assert payload["time_profile"] == {"total_minutes": 35, "active_minutes": 15}
    assert payload["allergens"]["contains"] == []
    assert "milk" not in payload["allergens"]["contains"]


def test_snapshot_fits_axes():
    snap = {
        "cook_method": "oven",
        "equipment": "dutch_oven",
        "protein_bases": ["beef"],
        "home": False,
    }
    assert snapshot_fits(snap, ["oven"], [], ["beef"])
    assert not snapshot_fits(snap, ["pan_fry"], [], ["beef"])
    assert not snapshot_fits(snap, [], ["skillet"], ["beef"])
    assert not snapshot_fits(snap, ["oven"], [], ["poultry"])


def test_u42_snapshots_skip_assemble(monkeypatch):
    from apps.recipes.services import solve as solve_mod
    from apps.recipes.services.solve import solve_recipe

    def boom(*_args, **_kwargs):
        raise AssertionError("assemble should not run when snapshots exist")

    monkeypatch.setattr(solve_mod, "assemble_recipe", boom)
    recipe = SimpleNamespace(
        slug="grudka",
        title="Грудка",
        dish_type="main",
        editorial_tested=False,
        protein_base="poultry",
        cook_method="pan_fry",
        equipment="skillet",
        energy_profile="standard",
        variants=FakeRelated([]),
        content_version=1,
        snapshot_version=1,
        axis_snapshots=[
            {
                "variant": None,
                "equipment": "skillet",
                "home": True,
                "protein_base": "poultry",
                "protein_bases": ["poultry"],
                "cook_method": "pan_fry",
                "lines": [
                    {
                        "canonical_id": "chicken_breast",
                        "name": "грудка",
                        "optional": False,
                        "unit": "g",
                        "is_anchor": True,
                    }
                ],
                "allergens": {"contains": [], "may_contain": [], "unknown": []},
                "high_risk_flags": [],
                "step_count": 4,
                "time_total_minutes": 25,
                "time_active_minutes": 15,
                "addon_penalty": 0,
                "equipment_penalty": 0,
            }
        ],
    )
    solved = solve_recipe(
        recipe,
        filter_protein=[],
        filter_method=[],
        filter_dish=[],
        filter_equipment=[],
        have=["chicken_breast"],
        catalog_item={
            "has_delta_variants": False,
            "allowed_cuts": [],
            "protein_bases": ["poultry"],
            "protein_variants": [],
        },
        rules=[],
        titles={"chicken_breast": "грудка"},
        intents=["fast"],
        explicit_have=["chicken_breast"],
    )
    assert solved is not None
    assert solved.time_total_minutes == 25
    assert solved.allergens["contains"] == []
    assert solved.applied_axes["variant"] is None


def test_pre_versioning_snapshots_are_fresh(monkeypatch):
    from apps.recipes.services import solve as solve_mod
    from apps.recipes.services.solve import solve_recipe

    def boom(*_args, **_kwargs):
        raise AssertionError("assemble should not run for pre-0013 snapshots")

    monkeypatch.setattr(solve_mod, "assemble_recipe", boom)
    recipe = SimpleNamespace(
        slug="grudka",
        title="Грудка",
        dish_type="main",
        editorial_tested=False,
        protein_base="poultry",
        cook_method="pan_fry",
        equipment="skillet",
        energy_profile="standard",
        variants=FakeRelated([]),
        content_version=1,
        snapshot_version=0,
        axis_snapshots=[
            {
                "variant": None,
                "equipment": "skillet",
                "home": True,
                "protein_base": "poultry",
                "protein_bases": ["poultry"],
                "cook_method": "pan_fry",
                "lines": [
                    {
                        "canonical_id": "chicken_breast",
                        "name": "грудка",
                        "optional": False,
                        "unit": "g",
                        "is_anchor": True,
                    }
                ],
                "allergens": {"contains": [], "may_contain": [], "unknown": []},
                "high_risk_flags": [],
                "step_count": 4,
                "time_total_minutes": 25,
                "time_active_minutes": 15,
                "addon_penalty": 0,
                "equipment_penalty": 0,
            }
        ],
    )
    solved = solve_recipe(
        recipe,
        filter_protein=[],
        filter_method=[],
        filter_dish=[],
        filter_equipment=[],
        have=["chicken_breast"],
        catalog_item={
            "has_delta_variants": False,
            "allowed_cuts": [],
            "protein_bases": ["poultry"],
            "protein_variants": [],
        },
        rules=[],
        titles={"chicken_breast": "грудка"},
        intents=["fast"],
        explicit_have=["chicken_breast"],
    )
    assert solved is not None
    assert solved.time_total_minutes == 25


def test_stale_snapshots_fall_back_to_assemble(monkeypatch):
    from apps.recipes.services import solve as solve_mod
    from apps.recipes.services.assemble import AssembledRecipe
    from apps.recipes.services.solve import solve_recipe

    calls: list[int] = []

    def fake_assemble(_recipe, **_kwargs):
        calls.append(1)
        return AssembledRecipe(
            ingredients=[
                {
                    "canonical_id": "chicken_breast",
                    "name": "грудка",
                    "optional": False,
                    "unit": "g",
                    "is_anchor": True,
                }
            ],
            steps=[{}, {}, {}, {}],
            allergens={"contains": [], "may_contain": [], "unknown": []},
            high_risk_flags=[],
            caution_text=None,
            cook_method="pan_fry",
            protein_base="poultry",
            equipment="skillet",
            applied_axes={"variant": None, "equipment": "skillet"},
            available_variants=[],
            available_equipment=["skillet"],
            variations=[],
            notes=[],
            prep=[],
        )

    monkeypatch.setattr(solve_mod, "assemble_recipe", fake_assemble)
    recipe = SimpleNamespace(
        slug="grudka",
        title="Грудка",
        dish_type="main",
        editorial_tested=False,
        protein_base="poultry",
        cook_method="pan_fry",
        equipment="skillet",
        energy_profile="standard",
        variants=FakeRelated([]),
        content_version=2,
        snapshot_version=1,
        axis_snapshots=[
            {
                "variant": None,
                "equipment": "skillet",
                "home": True,
                "protein_base": "poultry",
                "protein_bases": ["poultry"],
                "cook_method": "pan_fry",
                "lines": [
                    {
                        "canonical_id": "stale_only",
                        "name": "устарело",
                        "optional": False,
                        "unit": "g",
                        "is_anchor": True,
                    }
                ],
                "allergens": {"contains": [], "may_contain": [], "unknown": []},
                "high_risk_flags": [],
                "step_count": 4,
                "time_total_minutes": 25,
                "time_active_minutes": 15,
                "addon_penalty": 0,
                "equipment_penalty": 0,
            }
        ],
    )
    solved = solve_recipe(
        recipe,
        filter_protein=[],
        filter_method=[],
        filter_dish=[],
        filter_equipment=[],
        have=["chicken_breast"],
        catalog_item={
            "has_delta_variants": False,
            "allowed_cuts": [],
            "protein_bases": ["poultry"],
            "protein_variants": [],
        },
        rules=[],
        titles={"chicken_breast": "грудка"},
        intents=[],
        explicit_have=["chicken_breast"],
    )
    assert calls
    assert solved is not None
    assert solved.shopping_delta == []


def test_idle_recommendations_skip_solver():
    from apps.recipes.views import _idle_recommendations

    payload = _idle_recommendations(
        {
            "protein_base": [],
            "cook_method": [],
            "dish_type": [],
            "equipment": [],
            "cuts": [],
            "have": [],
            "have_group": [],
            "intent": [],
        }
    )
    assert payload["featured"] is None
    assert payload["alternatives"] == []
    assert payload["results"] == []
    assert payload["buckets"]["now"] == []
