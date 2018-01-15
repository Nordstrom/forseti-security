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

"""Provides the database connector."""

import os
import MySQLdb
from MySQLdb import OperationalError

from google.cloud.security.common.data_access.errors import MySQLError
from google.cloud.security.common.util import log_util

LOGGER = log_util.get_logger(__name__)

class DbConnector(object):
    """Database connector."""

    def __init__(self, global_configs=None):
        """Initialize the db connector.

        Args:
            global_configs (dict): Global configurations.

        Raises:
            MySQLError: An error with MySQL has occurred.
        """

        host = os.getenv('CLOUD_SQL_DB_HOST', global_configs['db_host'])
        user = os.getenv('CLOUD_SQL_DB_USER', global_configs['db_user'])
        db_name = os.getenv('CLOUD_SQL_DB_NAME', global_configs['db_name'])
        db_pass = os.getenv('CLOUD_SQL_DB_PASSWORD', global_configs.get('db_password', ''))

        print("host")

        try:
            self.conn = MySQLdb.connect(
                host=host,
                user=user,
                db=db_name,
                passwd=db_pass,
                local_infile=1)
        except OperationalError as e:
            LOGGER.error('Unable to create mysql connector:\n%s', e)
            raise MySQLError('DB Connector', e)

    def __del__(self):
        """Closes the database connection."""
        try:
            self.conn.close()
        except AttributeError:
            # This happens when conn is not created in the first place,
            # thus does not need to be cleaned up.
            pass
