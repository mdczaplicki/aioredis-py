import pytest

from aioredis.commands import CommandsParser


class TestCommandsParser:
    def test_init_commands(self, r):
        commands_parser = CommandsParser(r)
        assert commands_parser.commands is not None
        assert "get" in commands_parser.commands

    def test_get_keys_predetermined_key_location(self, r):
        commands_parser = CommandsParser(r)
        args1 = ["GET", "foo"]
        args2 = ["OBJECT", "encoding", "foo"]
        args3 = ["MGET", "foo", "bar", "foobar"]
        assert commands_parser.get_keys(r, *args1) == ["foo"]
        assert commands_parser.get_keys(r, *args2) == ["foo"]
        assert commands_parser.get_keys(r, *args3) == ["foo", "bar", "foobar"]

    @pytest.mark.filterwarnings("ignore:ResponseError")
    def test_get_moveable_keys(self, r):
        commands_parser = CommandsParser(r)
        args1 = [
            "EVAL",
            "return {KEYS[1],KEYS[2],ARGV[1],ARGV[2]}",
            2,
            "key1",
            "key2",
            "first",
            "second",
        ]
        args2 = ["XREAD", "COUNT", 2, b"STREAMS", "mystream", "writers", 0, 0]
        args3 = ["ZUNIONSTORE", "out", 2, "zset1", "zset2", "WEIGHTS", 2, 3]
        args4 = ["GEORADIUS", "Sicily", 15, 37, 200, "km", "WITHCOORD", b"STORE", "out"]
        args5 = ["MEMORY USAGE", "foo"]
        args6 = [
            "MIGRATE",
            "192.168.1.34",
            6379,
            "",
            0,
            5000,
            b"KEYS",
            "key1",
            "key2",
            "key3",
        ]
        args7 = ["MIGRATE", "192.168.1.34", 6379, "key1", 0, 5000]
        args8 = ["STRALGO", "LCS", "STRINGS", "string_a", "string_b"]
        args9 = ["STRALGO", "LCS", "KEYS", "key1", "key2"]

        assert commands_parser.get_keys(r, *args1).sort() == ["key1", "key2"].sort()
        assert (
            commands_parser.get_keys(r, *args2).sort() == ["mystream", "writers"].sort()
        )
        assert (
            commands_parser.get_keys(r, *args3).sort()
            == ["out", "zset1", "zset2"].sort()
        )
        assert commands_parser.get_keys(r, *args4).sort() == ["Sicily", "out"].sort()
        assert commands_parser.get_keys(r, *args5).sort() == ["foo"].sort()
        assert (
            commands_parser.get_keys(r, *args6).sort()
            == ["key1", "key2", "key3"].sort()
        )
        assert commands_parser.get_keys(r, *args7).sort() == ["key1"].sort()
        assert commands_parser.get_keys(r, *args8) is None
        assert commands_parser.get_keys(r, *args9).sort() == ["key1", "key2"].sort()

    def test_get_pubsub_keys(self, r):
        commands_parser = CommandsParser(r)
        args1 = ["PUBLISH", "foo", "bar"]
        args2 = ["PUBSUB NUMSUB", "foo1", "foo2", "foo3"]
        args3 = ["PUBSUB channels", "*"]
        args4 = ["SUBSCRIBE", "foo1", "foo2", "foo3"]
        assert commands_parser.get_keys(r, *args1) == ["foo"]
        assert commands_parser.get_keys(r, *args2) == ["foo1", "foo2", "foo3"]
        assert commands_parser.get_keys(r, *args3) == ["*"]
        assert commands_parser.get_keys(r, *args4) == ["foo1", "foo2", "foo3"]
