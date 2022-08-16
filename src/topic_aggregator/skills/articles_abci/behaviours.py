# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2022 Valory AG
#   Copyright 2018-2021 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the behaviours for the 'topic_extractor' skill."""
# """This package contains a scaffold of a behaviour."""

# from aea.skills.base import Behaviour


# class MyScaffoldBehaviour(Behaviour):
#     """This class scaffolds a behaviour."""

#     def setup(self) -> None:
#         """Implement the setup."""
#         raise NotImplementedError

#     def act(self) -> None:
#         """Implement the act."""
#         raise NotImplementedError

#     def teardown(self) -> None:
#         """Implement the task teardown."""
#         raise NotImplementedError


import json
from abc import ABC
from typing import Any, Generator, Set, Type, cast

from aea.skills.behaviours import TickerBehaviour


from packages.valory.connections.http_client.connection import (
    PUBLIC_ID as HTTP_CLIENT_PUBLIC_ID,
)
from packages.valory.protocols.http.message import HttpMessage
from packages.arcolife.skills.articles_abci.dialogues import HttpDialogues

from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)
from packages.arcolife.skills.articles_abci.models import Params, SharedState
from packages.arcolife.skills.articles_abci.payloads import (
    NoteTakingPayload,
    RegistrationPayload,
    ResetPayload,
    SelectKeeperPayload,
)
from packages.arcolife.skills.articles_abci.rounds import (
    NoteTakingAbciApp,
    SaveTopicsRound,
    RegistrationRound,
    ResetAndPauseRound,
    SelectKeeperRound,
    SynchronizedData,
)


DEFAULT_REQUEST_INTERVAL = 20.0


class NoteTakingABCIBaseBehaviour(BaseBehaviour, ABC):
    """Base behaviour behaviour for the Note Taking abci skill."""

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(
            SynchronizedData, cast(SharedState, self.context.state).synchronized_data
        )

    @property
    def params(self) -> Params:
        """Return the params."""
        return cast(Params, self.context.params)


class RegistrationBehaviour(NoteTakingABCIBaseBehaviour):
    """Register to the next round."""

    behaviour_id = "register"
    matching_round = RegistrationRound

    def async_act(self) -> Generator:
        """
        Do the action.

        Steps:
        - Build a registration transaction.
        - Send the transaction and wait for it to be mined.
        - Wait until ABCI application transitions to the next round.
        - Go to the next behaviour (set done event).
        """

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            payload = RegistrationPayload(self.context.agent_address)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class SelectKeeperBehaviour(NoteTakingABCIBaseBehaviour, ABC):
    """Select the keeper agent."""

    behaviour_id = "select_keeper"
    matching_round = SelectKeeperRound

    def async_act(self) -> Generator:
        """
        Do the action.

        Steps:
        - Select a keeper randomly.
        - Send the transaction with the keeper and wait for it to be mined.
        - Wait until ABCI application transitions to the next round.
        - Go to the next behaviour (set done event).
        """

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            keeper_address = sorted(self.synchronized_data.participants)[
                self.synchronized_data.period_count
                % self.synchronized_data.nb_participants
            ]

            self.context.logger.info(f"Selected a new keeper: {keeper_address}.")
            payload = SelectKeeperPayload(self.context.agent_address, keeper_address)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class NoteTakingBehaviour(NoteTakingABCIBaseBehaviour, ABC):
    """Prints the celebrated 'Note Taking!' message."""

    behaviour_id = "print_message"
    matching_round = SaveTopicsRound

    def async_act(self) -> Generator:
        """
        Do the action.

        Steps:
        - Determine if this agent is the current keeper agent.
        - Print the appropriate to the local console.
        - Send the transaction with the printed message and wait for it to be mined.
        - Wait until ABCI application transitions to the next round.
        - Go to the next behaviour (set done event).
        """

        printed_message = f"Agent {self.context.agent_name} (address {self.context.agent_address}) in period {self.synchronized_data.period_count} says: "
        if (
            self.context.agent_address
            == self.synchronized_data.most_voted_keeper_address
        ):
            printed_message += "Note Taking!"
        else:
            printed_message += ":|"

        print(printed_message)
        self.context.logger.info(f"printed_message={printed_message}")

        payload = NoteTakingPayload(self.context.agent_address, printed_message)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class ResetAndPauseBehaviour(NoteTakingABCIBaseBehaviour):
    """Reset behaviour."""

    matching_round = ResetAndPauseRound
    behaviour_id = "reset_and_pause"
    pause = True

    pause = True

    def async_act(self) -> Generator:
        """
        Do the action.

        Steps:
        - Trivially log the behaviour.
        - Sleep for configured interval.
        - Build a registration transaction.
        - Send the transaction and wait for it to be mined.
        - Wait until ABCI application transitions to the next round.
        - Go to the next behaviour (set done event).
        """
        if self.pause:
            self.context.logger.info("Period end.")
            self.context.benchmark_tool.save()
            yield from self.sleep(self.params.observation_interval)
        else:
            self.context.logger.info(
                f"Period {self.synchronized_data.period_count} was not finished. Resetting!"
            )

        payload = ResetPayload(
            self.context.agent_address, self.synchronized_data.period_count
        )

        yield from self.send_a2a_transaction(payload)
        yield from self.wait_until_round_end()
        self.set_done()


class NoteTakingRoundBehaviour(AbstractRoundBehaviour):
    """This behaviour manages the consensus stages for the Note Taking abci app."""

    initial_behaviour_cls = RegistrationBehaviour
    abci_app_cls = NoteTakingAbciApp  # type: ignore
    behaviours: Set[Type[NoteTakingABCIBaseBehaviour]] = {  # type: ignore
        RegistrationBehaviour,  # type: ignore
        SelectKeeperBehaviour,  # type: ignore
        NoteTakingBehaviour,  # type: ignore
        ResetAndPauseBehaviour,  # type: ignore
    }


class HttpRequestBehaviour(NoteTakingABCIBaseBehaviour, TickerBehaviour):
    """This class defines an http request behaviour."""

    def __init__(self, **kwargs: Any):
        """Initialise the behaviour."""
        request_interval = kwargs.pop(
            "request_interval", DEFAULT_REQUEST_INTERVAL
        )  # type: int
        self.url = kwargs.pop("url", None)
        self.method = kwargs.pop("method", None)
        self.body = kwargs.pop("body", None)
        self.lookup_termination_key = kwargs.pop("lookup_termination_key", None)
        if self.url is None or self.method is None or self.body is None:
            raise ValueError("Url, method and body must be provided.")
        super().__init__(tick_interval=request_interval, **kwargs)

    def setup(self) -> None:
        """Implement the setup."""

    def act(self) -> None:
        """Implement the act."""
        if self.lookup_termination_key is not None:
            prerequisite_satisfied = self.context.shared_state.get(
                self.lookup_termination_key, False
            )
            if not prerequisite_satisfied:
                return

        self._generate_http_request()

    def _generate_http_request(self) -> None:
        """Generate http request to provided url with provided body and method."""
        http_dialogues = cast(HttpDialogues, self.context.http_dialogues)
        request_http_message, _ = http_dialogues.create(
            counterparty=str(HTTP_CLIENT_PUBLIC_ID),
            performative=HttpMessage.Performative.REQUEST,
            method=self.method,
            url=self.url,
            headers="",
            version="",
            body=json.dumps(self.body).encode("utf-8"),
        )
        self.context.outbox.put_message(message=request_http_message)

    def teardown(self) -> None:
        """Implement the task teardown."""