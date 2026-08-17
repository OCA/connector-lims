# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LimsSample(models.Model):
    _inherit = "lims.sample"

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        index=True,
        help="Product representing the sample (variant).",
    )
    lot_id = fields.Many2one(
        "stock.lot",
        string="Lot / Serial",
        index=True,
        help="Lot / Serial that represents this sample.",
    )
    location_id = fields.Many2one(
        "stock.location",
        string="Current Location",
        compute="_compute_location_id",
        help="Computed from the lot's stock.quant location (if available).",
    )
    move_line_count = fields.Integer(
        compute="_compute_move_line_count",
        help="Number of stock move lines associated with this sample's lot.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._ensure_lot_for_sample()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "product_id" in vals or "lot_id" in vals:
            self._ensure_lot_for_sample()
        return res

    def _ensure_lot_for_sample(self):
        """Create a serial lot when the product is specimen-tracked and none is set."""
        for rec in self:
            product = rec.product_id
            if not product:
                continue
            is_specimen = bool(product.product_tmpl_id.is_specimen)
            serial_tracked = product.tracking == "serial" or is_specimen
            if serial_tracked and not rec.lot_id:
                lot_name = rec.identifier or self.env["ir.sequence"].next_by_code(
                    "stock.lot.serial"
                )
                rec.lot_id = self.env["stock.lot"].create(
                    {
                        "product_id": product.id,
                        "name": lot_name or rec.identifier,
                        "company_id": rec.company_id.id,
                    }
                )
            if (
                rec.lot_id
                and rec.product_id
                and rec.lot_id.product_id != rec.product_id
            ):
                raise ValidationError(
                    self.env._(
                        "Selected lot %(lot)s is not for product %(product)s",
                        lot=rec.lot_id.display_name,
                        product=rec.product_id.display_name,
                    )
                )

    @api.depends("lot_id")
    def _compute_location_id(self):
        StockQuant = self.env["stock.quant"]
        for rec in self:
            location = False
            if rec.lot_id:
                quant = StockQuant.search(
                    [
                        ("lot_id", "=", rec.lot_id.id),
                        ("quantity", ">", 0),
                    ],
                    limit=1,
                )
                if quant:
                    location = quant.location_id
            rec.location_id = location

    @api.depends("lot_id")
    def _compute_move_line_count(self):
        counts = {}
        lots = self.mapped("lot_id")
        if lots:
            grouped = self.env["stock.move.line"]._read_group(
                [("lot_id", "in", lots.ids)],
                ["lot_id"],
                ["__count"],
            )
            counts = {lot.id: count for lot, count in grouped}
        for rec in self:
            rec.move_line_count = counts.get(rec.lot_id.id, 0)

    def action_open_lot(self):
        """Open the stock lot form view for this sample."""
        self.ensure_one()
        if not self.lot_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Lot / Serial"),
            "res_model": "stock.lot",
            "view_mode": "form",
            "res_id": self.lot_id.id,
            "target": "current",
        }

    def action_view_stock_moves(self):
        """Open the stock move lines associated with this sample's lot."""
        self.ensure_one()
        if not self.lot_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Stock Move Lines"),
            "res_model": "stock.move.line",
            "view_mode": "list,form",
            "domain": [("lot_id", "=", self.lot_id.id)],
        }
