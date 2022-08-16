# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021-2022 Valory AG
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

"""End2end tests for the valory/hello_world skill."""
import pytest

from autonomy.test_tools.base_test_classes.agents import (
    BaseTestEnd2EndExecution,
    RoundChecks,
)


HAPPY_PATH = (
    RoundChecks("registration"),
    RoundChecks("print_message", n_periods=3),
    RoundChecks("select_keeper", n_periods=2),
    RoundChecks("reset_and_pause", n_periods=2),
)

# strict check log messages of the happy path
STRICT_CHECK_STRINGS = (
    "Period end",
    " in period 0 says: Note Taking!",
    " in period 1 says: Note Taking!",
    " in period 2 says: Note Taking!",
    " in period 3 says: Note Taking!",
)


@pytest.mark.parametrize("nb_nodes", (4,))
class TestHelloWorldABCIFourAgents(
    BaseTestEnd2EndExecution,
):
    """Test the ABCI topic_extractor skill with four agents."""

    agent_package = "valory/topic_aggregator:0.1.0"
    skill_package = "valory/topic_extractor:0.1.0"
    wait_to_finish = 160
    happy_path = HAPPY_PATH
    strict_check_strings = STRICT_CHECK_STRINGS