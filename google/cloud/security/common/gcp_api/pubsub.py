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

"""Wrapper for PubSub API client."""
import StringIO
import urlparse
import json
import base64
from googleapiclient import errors
from googleapiclient import http
from httplib2 import HttpLib2Error

from google.cloud.security.common.gcp_api import _base_repository
from google.cloud.security.common.gcp_api import api_helpers
from google.cloud.security.common.gcp_api import errors as api_errors
from google.cloud.security.common.gcp_api import repository_mixins
from google.cloud.security.common.util import log_util

LOGGER = log_util.get_logger(__name__)


class PubSubRepositoryClient(_base_repository.BaseRepositoryClient):
    """PubSub API Respository."""

    def __init__(self,
                 credentials=None,
                 quota_max_calls=None,
                 quota_period=1.0,
                 use_rate_limiter=True):
        """Constructor.

        Args:
            credentials (GoogleCredentials): An optional GoogleCredentials
                object to use.
            quota_max_calls (int): Allowed requests per <quota_period> for the
                API.
            quota_period (float): The time period to limit the requests within.
            use_rate_limiter (bool): Set to false to disable the use of a rate
                limiter for this service.
        """
        if not quota_max_calls:
            use_rate_limiter = False

        self._subscriptions = None
        self._topics = None

        super(PubSubRepositoryClient, self).__init__(
            'pubsub', versions=['v1'],
            credentials=credentials,
            quota_max_calls=quota_max_calls,
            quota_period=quota_period,
            use_rate_limiter=use_rate_limiter)

    @property
    def subscriptions(self):
        """An _PubSubSubscriptionsRepository instance.

        Returns:
            object: An _PubSubSubscriptionsRepository instance.
        """
        if not self._subscriptions:
            self._subscriptions = self._init_repository(
                _PubSubSubscriptionsRepository)
        return self._subscriptions

    @property
    def topics(self):
        """An _PubSubTopicsRepository instance.

        Returns:
            object: An _PubSubTopicsRepository instance.
        """
        if not self._topics:
            self._topics = self._init_repository(
                _PubSubTopicsRepository)
        return self._topics


class _PubSubSubscriptionsRepository(
        repository_mixins.GetIamPolicyQueryMixin,
        repository_mixins.ListQueryMixin,
        _base_repository.GCPRepository):
    """Implementation of PubSub Subscriptions repository."""

    def __init__(self, **kwargs):
        """Constructor.

        Args:
          **kwargs (dict): The args to pass into GCPRepository.__init__()
        """
        super(_PubSubSubscriptionsRepository, self).__init__(
            key_field='', component='projects.subscriptions', **kwargs)


class _PubSubTopicsRepository(
        repository_mixins.GetIamPolicyQueryMixin,
        repository_mixins.ListQueryMixin,
        _base_repository.GCPRepository):
    """Implementation of SubPub Topics repository."""

    def __init__(self, **kwargs):
        """Constructor.

        Args:
            **kwargs (dict): The args to pass into GCPRepository.__init__()
        """
        super(_PubSubTopicsRepository, self).__init__(
            key_field='', component='projects.topics', **kwargs)

    # Extend the base get_iam_policy implementation to support objects.
    # pylint: disable=arguments-differ
    def get_iam_policy(self, topic_name, fields=None, **kwargs):
        """Get Topic IAM Policy.

        Args:
            topic_name (str): The name of the topic to fetch.
            fields (str): Fields to include in the response - partial response.
            **kwargs (dict): Optional additional arguments to pass to the query.

        Returns:
            dict: Response from the API.
        """
        # The Resource getIamPolicy does not allow the 'body' argument, so this
        # overrides the default behavior by setting include_body to False. It
        # also takes a bucket id and object id instead of a resource path.
        return repository_mixins.GetIamPolicyQueryMixin.get_iam_policy(
            self, topic_name, fields=fields, include_body=False,
            resource_field='resource', **kwargs)

    def create(self, topic_name):
        """Create an PubSub topic.

        Args:
            topic_name (str): The name of the topic to create.

        Returns:
            dict: Response from the API.
        """
        body = {
            'name': topic_name
        }
        verb_arguments = {
            'name': topic_name,
            'body': body
        }
        return self.execute_command(verb='create',
                                    verb_arguments=verb_arguments)

    def publish(self, topic_name, data):
        """Upload an object to a bucket.

        Args:
            topic_name (str): The topic name.
            data (dict): The data to publish in topic message.

        Returns:
            dict: Response from the API.
        """
        data = base64.b64encode(json.dumps(data))

        body = {
            'messages': [
                {
                    'data': data
                }
            ]
        }

        verb_arguments = {
            'topic': topic_name,
            'body': body,
        }
        return self.execute_command(verb='publish',
                                    verb_arguments=verb_arguments)

class PubSubClient(object):
    """PubSub Client."""

    def __init__(self, *args, **kwargs):
        """Initialize.

        Args:
            *args (dict): Default args passed to all API Clients, not used by
                the PubSubClient.
            **kwargs (dict): The kwargs.
        """
        del args
        # Storage API has unlimited rate.
        self.repository = PubSubRepositoryClient(
            credentials=kwargs.get('credentials'),
            quota_max_calls=0,
            use_rate_limiter=False)

    def create_topic(self, topic_name):
        """Creates a PubSub topic.

        Args:
            topic_name (str): The local path of the file to upload.

        Returns:
            dict: Response from the API.
        """

        try:
            return self.repository.topics.create(topic_name)

        except (errors.HttpError, HttpLib2Error) as e:
            LOGGER.warn(api_errors.ApiExecutionError(topic_name, e))
            raise api_errors.ApiExecutionError('topicPublish', e)

    def publish_message(self, topic_name, data):
        """Gets all GCS buckets for a project.

        Args:
            topic_name (str): The topic name.
            data (dict): The data to publish in topic message.

        Returns:
            dict: Response from the API.
            {u'messageIds': [u'12026839522093']}

        Raises:
            ApiExecutionError: ApiExecutionError is raised if the call to the
                GCP PubSub API fails.
        """
        try:
            return self.repository.topics.publish(topic_name,
                                                  data=data)
        except (errors.HttpError, HttpLib2Error) as e:
            LOGGER.warn(api_errors.ApiExecutionError(topic_name, e))
            raise api_errors.ApiExecutionError('topicPublish', e)

    def get_topic_iam_policy(self, topic_name):
        """Gets the IAM policy for a topic.

        Args:
            topic_name (str): The topic to fetch the policy for.

        Returns:
            dict: The IAM policy for the topic.
        Raises:
            ApiExecutionError: ApiExecutionError is raised if the call to the
                GCP PubSub API fails
        """
        try:
            return self.repository.topics.get_iam_policy(topic_name)
        except (errors.HttpError, HttpLib2Error) as e:
            LOGGER.warn(api_errors.ApiExecutionError(topic_name, e))
            raise api_errors.ApiExecutionError('topicIamPolicy', e)
