# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from .common import LimsAdvancedCommon


@tagged("post_install", "-at_install")
class TestLimsTeam(LimsAdvancedCommon):
    def test_team_sample_count_includes_open_samples(self):
        team = self.env["lims.team"].create({"name": "Test Team Count"})
        self._create_sample(team=team)
        self._create_sample(team=team)
        self.assertEqual(team.sample_count, 2)

    def test_team_sample_count_excludes_closed_samples(self):
        team = self.env["lims.team"].create({"name": "Test Team Closed"})
        stage_published = self.env.ref("lims.lims_stage_sample_published")
        self._create_sample(stage=stage_published, team=team)
        self.assertEqual(team.sample_count, 0)

    def test_team_need_assign_count_counts_samples_without_operator(self):
        team = self.env["lims.team"].create({"name": "Test Team Unassigned"})
        self._create_sample(team=team)
        self.assertEqual(team.sample_need_assign_count, 1)

    def test_team_need_assign_count_excludes_assigned_samples(self):
        team = self.env["lims.team"].create({"name": "Test Team Assigned"})
        sample = self._create_sample(team=team)
        sample.operator_id = self.operator
        self.assertEqual(team.sample_need_assign_count, 0)

    def test_team_name_unique_per_company(self):
        from odoo.exceptions import ValidationError

        self.env["lims.team"].create({"name": "Unique Team"})
        with self.assertRaises(ValidationError):
            self.env["lims.team"].create({"name": "Unique Team"})
