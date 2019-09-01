#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019
#
# This file is part of Hikari.
#
# Hikari is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hikari is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hikari. If not, see <https://www.gnu.org/licenses/>.
import datetime
from unittest import mock

import pytest

from hikari.core.model import message
from hikari.core.model import model_cache


@pytest.mark.model
class TestMessage:
    @pytest.fixture()
    def mock_user(self):
        return {"id": "1234", "username": "potato"}

    def test_Message_from_dict(self, mock_user):
        s = mock.MagicMock(spec=model_cache.AbstractModelCache)
        m = message.Message.from_dict(
            s,
            {
                "type": 0,
                "id": "12345",
                "channel_id": "67890",
                "guild_id": None,
                "author": mock_user,
                "edited_timestamp": None,
                "tts": True,
                "mention_everyone": False,
                "attachments": [],
                "embeds": [],
                "pinned": False,
                "application": None,
                "activity": None,
                "content": "ayyyyyyy lmao",
                "flags": 7,
            },
        )

        assert m.type is message.MessageType.DEFAULT
        assert m.id == 12345
        assert m._channel_id == 67890
        assert m._guild_id is None
        assert m.edited_at is None
        assert m.tts is True
        assert m.mentions_everyone is False
        assert len(m.attachments) == 0
        assert len(m.embeds) == 0
        assert m.pinned is False
        assert m.application is None
        assert m.activity is None
        assert m.content == "ayyyyyyy lmao"
        assert m.flags & message.MessageFlag.CROSSPOSTED
        assert m.flags & message.MessageFlag.IS_CROSSPOST
        assert m.flags & message.MessageFlag.SUPPRESS_EMBEDS
        s.parse_user.assert_called_with(mock_user)

    def test_Message_from_dict_INTEGRATION_TEST(self, mock_user):
        s = mock.MagicMock(spec=model_cache.AbstractModelCache)
        m = message.Message.from_dict(
            s,
            {
                "author": mock_user,
                "type": 10,
                "id": "12345",
                "channel_id": "67890",
                "guild_id": "102234",
                "edited_timestamp": "2019-10-10T05:22:33.023456+02:30",
                "tts": False,
                "mention_everyone": True,
                "attachments": [
                    {
                        "id": "5555555555555555",
                        "filename": "catto.png",
                        "size": 180,
                        "url": "http://c.at",
                        "proxy_url": "http://c.at/?proxy",
                        "width": 92,
                        "height": 69,
                    }
                ],
                "embeds": [
                    {
                        "type": "whelp",
                        "title": "hello, world",
                        "description": "ayyy lmao",
                        "fields": [{"name": "ping", "value": "pong", "inline": True}],
                        "thumbnail": {"url": "hello", "proxy_url": "world"},
                    },
                    {"type": "something", "title": "hello, world, again."},
                ],
                "pinned": True,
                "application": {
                    "id": "969696",
                    "cover_image": "123454",
                    "description": "this is a description",
                    "icon": "900",
                    "name": "fubar",
                },
                "activity": {"type": 2, "party_id": "44332211"},
                "content": "some pointless text",
                "something_we_didnt_account_for": "meh, it is fine to ignore it.",
            },
        )

        assert m.type is message.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2
        assert m.id == 12345
        assert m._channel_id == 67890
        assert m._guild_id == 102234
        assert m.edited_at == datetime.datetime(
            2019, 10, 10, 5, 22, 33, 23456, tzinfo=datetime.timezone(datetime.timedelta(hours=2, minutes=30))
        )
        assert m.tts is False
        assert m.mentions_everyone is True
        assert m.pinned is True
        assert m.content == "some pointless text"

        assert len(m.attachments) == 1
        assert len(m.embeds) == 2
        assert m.application is not None
        assert m.activity is not None

        attachment0 = m.attachments[0]

        assert attachment0.id == 5555555555555555
        assert attachment0.filename == "catto.png"
        assert attachment0.size == 180
        assert attachment0.url == "http://c.at"
        assert attachment0.proxy_url == "http://c.at/?proxy"
        assert attachment0.width == 92
        assert attachment0.height == 69

        embed0, embed1 = m.embeds[0], m.embeds[1]
        assert embed0.type == "whelp"
        assert embed0.title == "hello, world"
        assert embed0.description == "ayyy lmao"
        assert len(embed0.fields) == 1
        embed0field0 = embed0.fields[0]
        assert embed0field0.name == "ping"
        assert embed0field0.value == "pong"
        assert embed0field0.inline is True
        assert embed1.title == "hello, world, again."
        assert embed1.type == "something"

        assert m.application.id == 969696
        assert m.application.cover_image_id == 123454
        assert m.application.description == "this is a description"
        assert m.application.icon_image_id == 900
        assert m.application.name == "fubar"

        assert m.activity.type == message.MessageActivityType.SPECTATE
        assert m.activity.party_id == 44332211

    def test_Message_guild_if_guild_message(self):
        cache = mock.MagicMock(spec_set=model_cache.AbstractModelCache)
        obj = message.Message.from_dict(cache, {"guild_id": "91827"})

        guild = mock.MagicMock()
        cache.get_guild_by_id = mock.MagicMock(return_value=guild)

        g = obj.guild
        assert g is guild

        cache.get_guild_by_id.assert_called_with(91827)

    def test_Message_guild_if_dm_message(self):
        cache = mock.MagicMock(spec_set=model_cache.AbstractModelCache)
        obj = message.Message.from_dict(cache, {})
        assert obj.guild is None

        cache.get_guild_by_id.assert_not_called()

    def test_Message_channel_if_guild_message(self):
        cache = mock.MagicMock(spec_set=model_cache.AbstractModelCache)
        guild = mock.MagicMock()
        guild.channels = {1234: mock.MagicMock(), 1235: mock.MagicMock()}
        cache.get_guild_by_id = mock.MagicMock(return_value=guild)

        obj = message.Message.from_dict(cache, {"channel_id": "1234", "guild_id": "5432"})

        c = obj.channel
        cache.get_guild_by_id.assert_called_with(5432)
        assert c is guild.channels[1234]

    def test_Message_channel_if_dm_message(self):
        cache = mock.MagicMock(spec_set=model_cache.AbstractModelCache)
        channel = mock.MagicMock()
        cache.get_dm_channel_by_id = mock.MagicMock(return_value=channel)

        obj = message.Message.from_dict(cache, {"channel_id": "1234"})

        c = obj.channel
        cache.get_dm_channel_by_id.assert_called_with(1234)
        assert c is channel

    def test_Message_author(self):
        cache = mock.MagicMock(spec_set=model_cache.AbstractModelCache)
        user = mock.MagicMock()
        cache.get_user_by_id = mock.MagicMock(return_value=user)

        obj = message.Message.from_dict(cache, {"author_id": "1234"})
        obj._author_id = 1234

        a = obj.author
        cache.get_user_by_id.assert_called_with(1234)
        assert a is user


@pytest.mark.model
def test_MessageActivity_from_dict():
    ma = message.MessageActivity.from_dict({"type": 3, "party_id": "999"})

    assert ma.type == message.MessageActivityType.LISTEN
    assert ma.party_id == 999


@pytest.mark.model
def test_MessageApplication_from_dict():
    ma = message.MessageApplication.from_dict(
        {"id": "19", "cover_image": "112233", "description": "potato", "icon": "332211", "name": "poof"}
    )

    assert ma.id == 19
    assert ma.icon_image_id == 332211
    assert ma.cover_image_id == 112233
    assert ma.description == "potato"
    assert ma.name == "poof"