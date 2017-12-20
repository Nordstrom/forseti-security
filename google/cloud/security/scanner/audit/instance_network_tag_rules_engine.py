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

"""Rules engine for Instance Tags."""
from collections import namedtuple
import itertools
import re

from google.cloud.security.common.util.regex_util import escape_and_globify
from google.cloud.security.common.util import log_util
from google.cloud.security.scanner.audit import base_rules_engine as bre
from google.cloud.security.scanner.audit import errors as audit_errors


LOGGER = log_util.get_logger(__name__)


class InstanceNetworkTagRulesEngine(bre.BaseRulesEngine):
    """Rules engine for InstanceNetworkTagRules."""

    def __init__(self, rules_file_path, snapshot_timestamp=None):
        """Initialize.

        Args:
            rules_file_path (str): file location of rules
            snapshot_timestamp (str): timestamp for database.
        """
        super(InstanceNetworkTagRulesEngine,
              self).__init__(rules_file_path=rules_file_path)
        self.rule_book = None

    def build_rule_book(self, global_configs=None):
        """Build InstanceNetworkTagRuleBook from rules definition file.

        Args:
            global_configs (dict): Global Configs
        """
        self.rule_book = InstanceNetworkTagRuleBook(
            self._load_rule_definitions())

    def find_policy_violations(self, instance_network_tag,
                               force_rebuild=False):
        """Determine whether the tag violates any rules.

        Args:
            instance_network_tag (list): list of
                instance_network_tag
            force_rebuild (bool): set to false to not force a rebuiid

        Return:
            list: iterator of all violations
        """
        violations = itertools.chain()
        if self.rule_book is None or force_rebuild:
            self.build_rule_book()
        resource_rules = self.rule_book.get_resource_rules()
        for rule in resource_rules:
            violations = itertools.chain(violations,
                                         rule.find_violations(
                                             instance_network_tag))
        return violations

    def add_rules(self, rules):
        """Add rules to the rule book.

        Args:
            rules (dicts): rule definitions
        """
        if self.rule_book is not None:
            self.rule_book.add_rules(rules)


class InstanceNetworkTagRuleBook(bre.BaseRuleBook):
    """The RuleBook for enforced networks resources."""

    def __init__(self,
                 rule_defs=None):
        """Initialize.

        Args:
            rule_defs (dict): The parsed dictionary of rules from the YAML
                definition file.
        """
        super(InstanceNetworkTagRuleBook, self).__init__()
        self.resource_rules_map = {}
        if not rule_defs:
            self.rule_defs = {}
        else:
            self.rule_defs = rule_defs
            self.add_rules(rule_defs)

    def add_rules(self, rule_defs):
        """Add rules to the rule book.

        Args:
            rule_defs (dict): rules definitions
        """
        for (i, rule) in enumerate(rule_defs.get('rules', [])):
            self.add_rule(rule, i)

    def add_rule(self, rule_def, rule_index):
        """Add a rule to the rule book.

        Add a rule to the rule book.

        The rule supplied to this method is the dictionary parsed from
        the rules definition file.

        For example, this rule...

        # rules yaml:
            rules:
            - name: reserved network tags
              project: '*'
              network: 'network-1'
              blacklist:
              - 'reserved-tag'

        ... gets parsed into:
        {
            "rules": [
                {
                    "name": "reserved network tags",
                    "project": "*",
                    "network": "network-1",
                    "blacklist": [
                        "reserved-tag"
                    ]
                }
            ]
        }

        Args:
            rule_def (dict): A dictionary containing rule definition properties.
            rule_index (int): The index of the rule from the rule definitions.
                Assigned automatically when the rule book is built.
        """
        project_id = rule_def.get('project_id')
        network = rule_def.get('network')
        whitelist = rule_def.get('whitelist', [])
        blacklist = rule_def.get('blacklist', [])

        if (not whitelist and not blacklist) or (
                project_id is None) or (network is None):
            raise audit_errors.InvalidRulesSchemaError(
                'Faulty rule {}'.format(rule_def.get('name')))

        rule_def_resource = {'whitelist': whitelist,
                             'blacklist': blacklist,
                             'project_id': escape_and_globify(project_id),
                             'network': escape_and_globify(network)}

        rule = Rule(rule_name=rule_def.get('name'),
                    rule_index=rule_index,
                    rules=rule_def_resource)

        resource_rules = self.resource_rules_map.get(rule_index)
        if not resource_rules:
            self.resource_rules_map[rule_index] = rule

    def get_resource_rules(self):
        """Get all the resource rules.

        Return:
            list: resource_rules_map values
        """
        return self.resource_rules_map.values()


class Rule(object):
    """The rules class for instance_network_interface."""

    def __init__(self, rule_name, rule_index, rules):
        """Initialize.

        Args:
            rule_name (str): Name of the loaded rule
            rule_index (int): The index of the rule from the  definitions
            rules (dict): The resources associated with the rules like
                the whitelist
        """
        self.rule_name = rule_name
        self.rule_index = rule_index
        self.rules = rules

    def find_violations(self, instance_network_tag_list):
        """Raise violation if the tag is not in the whitelist.

        Args:
            instance_network_tag_list (list): list
                of InstanceNetworkTag objects

         Yields:
            namedtuple: Returns RuleViolation named tuple
        """
        for instance_network_tag in instance_network_tag_list:
            print instance_network_tag
            network_and_project = re.search(
                r'compute/.*/projects/([^/]*).*networks/([^/]*)',
                instance_network_tag.network)
            network = network_and_project.group(2)
            project_id = instance_network_tag.project_id
            tags = instance_network_tag.tags or []
            if (re.match(self.rules['network'], network) and
                    re.match(self.rules['project_id'], project_id)):
                if any(t in self.rules.get('blacklist', []) for t in tags) or (
                        any(t not in self.rules.get(
                            'whitelist', []) for t in tags if self.rules.get(
                                'whitelist', []))
                ):
                    yield self.RuleViolation(
                        resource_type='instance',
                        rule_name=self.rule_name,
                        rule_index=self.rule_index,
                        violation_type='INSTANCE_NETWORK_TAG_VIOLATION',
                        project=project_id,
                        network=network,
                        tags=tags,
                        instance_name=instance_network_tag.instance_name,
                        raw_data=instance_network_tag.as_json())

    # Rule violation.
    # resource_type: string
    # rule_name: string
    # rule_index: int
    # violation_type: INSTANCE_NETWORK_TAGS_VIOLATION
    # project: string
    # network: string
    # tags: list
    RuleViolation = namedtuple('RuleViolation',
                               ['resource_type', 'rule_name',
                                'rule_index', 'violation_type', 'project',
                                'network', 'tags', 'instance_name',
                                'raw_data'])
