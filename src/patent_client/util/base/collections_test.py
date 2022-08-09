from .collections import Collection
from .collections import ListManager
from .row import Row


def test_collection():
    rows = [Row(a=1, b=2, c=3), Row(a=4, b=5, c=6), Row(a=4, b=5, c=6)]
    collection = Collection(rows)
    assert list(collection) == rows
    assert collection.to_list() == rows
    assert type(collection.to_list()) == ListManager
    r = list(collection.to_records())
    assert len(r) == 3
    assert all(type(i) == Row for i in r)
    r = list(collection.to_records(item_class=dict))
    assert len(r) == 3
    assert all(type(i) == dict for i in r)


def test_unpack():
    rows = Collection(
        [
            Row(a=1, b=Row(x=1, y=2, z=3), c=3),
            Row(a=4, b=Row(x=4, y=5, z=6), c=6),
            Row(a=4, b=Row(x=9, y=8, z=7), c=6),
        ]
    )

    result = rows.unpack("b").to_list()
    assert result[0]["b.x"] == 1
    assert result[0]["b.y"] == 2
    assert result[0]["b.z"] == 3


def test_explode():
    rows = Collection(
        [
            Row(a=1, b=[4, 5, 6], c=3),
        ]
    )
    result = rows.explode("b").to_list()
    assert len(result) == 3
    assert result[0]["b"] == 4
    assert result[1]["b"] == 5
    assert result[2]["b"] == 6


def test_double_explode():
    rows = Collection(
        [
            Row(a=1, b=[4, 5, 6], c=[7, 8, 9]),
        ]
    )
    result = rows.explode("b").explode("c").to_list()
    assert len(result) == 9
    assert result[0]["b"] == 4
    assert result[0]["c"] == 7
    assert result[8]["b"] == 6
    assert result[8]["c"] == 9


def test_explode_and_unpack():
    rows = Collection(
        [
            Row(
                a=1,
                b=[
                    Row(x=1, y=2, z=3),
                    Row(x=4, y=5, z=6),
                    Row(x=7, y=8, z=9),
                ],
                c=3,
            ),
        ]
    )
    result = rows.explode("b").unpack("b").to_list()
    assert len(result) == 3
    assert result[2]["b.y"] == 8
