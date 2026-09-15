from apps.prep.services.thaw import (
    format_container_list,
    thaw_day_reminder,
    thaw_prep_item_text,
)


def test_day_banner_uses_container_number_not_label_noun():
    line = thaw_day_reminder(
        evening=False,
        prev_day_genitive=None,
        labels=["№4 противень"],
    )
    assert line == (
        "Утром достаньте из морозилки контейнер №4 и переложите в холодильник."
    )
    assert "противень" not in line
    assert "морозилки №4" not in line


def test_evening_banner_joins_two_containers():
    line = thaw_day_reminder(
        evening=True,
        prev_day_genitive="пятницы",
        labels=["№10 заготовка овощного супа", "№12 томатный соус, морозилка"],
    )
    assert line == (
        "С вечера пятницы достаньте из морозилки контейнеры №10 и №12 "
        "и переложите в холодильник."
    )


def test_prep_item_says_take_container_from_freezer():
    line = thaw_prep_item_text(
        morning=False,
        label="№6 минтай",
        component_title="Филе минтая, сырое",
    )
    assert line == (
        "С вечера достаньте контейнер №6 (Филе минтая, сырое) "
        "из морозилки и переложите в холодильник."
    )


def test_format_list_falls_back_without_numbers():
    assert format_container_list(["тыква"]) == "тыква"
