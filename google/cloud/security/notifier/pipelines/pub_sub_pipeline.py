# Copyright 2017 The Forseti Security Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Pub/Sub pipeline to perform notifications."""

import requests

# TODO: Investigate improving so we can avoid the pylint disable.
# pylint: disable=line-too-long
from google.cloud.security.common.gcp_api import pubsub
from google.cloud.security.common.util import log_util
from google.cloud.security.notifier.pipelines import base_notification_pipeline as bnp
# pylint: enable=line-too-long

LOGGER = log_util.get_logger(__name__)

class PubSubPipeline(bnp.BaseNotificationPipeline):
    """PubSub pipeline to perform notifications"""

    def _send(self, **kwargs):
        """Sends a post to PubSub topic.

        Args:
            **kwargs: Arbitrary keyword arguments.
                violation: violation to send in Pub/Sub
        """
        topic = self.pipeline_config.get('topic')
        violation = kwargs.get('violation')

        pubsub_client = pubsub.PubSubClient()
        request = pubsub_client.publish_message(
            topic, violation)

        LOGGER.info(request)

    def run(self):
        """Run the Pub/Sub pipeline"""
        if not self.pipeline_config.get('topic'):
            LOGGER.warn('No topic found, not running Pub/Sub pipeline.')
            return

        for violation in self.violations:
            if self._check_send_only_new(violation=violation):
                self._send(violation=violation)
