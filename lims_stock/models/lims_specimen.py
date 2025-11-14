# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LIMSSpecimen(models.Model):
    _inherit = "lims.specimen"

    # NEW fields for lims_stock
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        index=True,
        help="Product representing the specimen (variant).",
    )
    lot_id = fields.Many2one(
        "stock.lot",
        string="Lot / Serial",
        index=True,
        help="Lot / Serial that represents this specimen.",
    )
    location_id = fields.Many2one(
        "stock.location",
        string="Current Location",
        compute="_compute_location_id",
        store=False,
        help="Computed from the lot's stock.quant location (if available).",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # After create: ensure lot creation/validation for specimen products
        for rec in records:
            rec._ensure_lot_for_specimen()
        return records

    def write(self, vals):
        res = super().write(vals)
        # Recompute location for records touched
        self.filtered(lambda r: r.lot_id)._compute_location_id()
        # If product_id changed for any record we might ensure lot validity
        if "product_id" in vals:
            for rec in self:
                rec._ensure_lot_for_specimen()
        return res

    def _ensure_lot_for_specimen(self):
        """If product is serial tracked and lot not provided,
        create a lot/serial automatically."""
        for rec in self:
            product = rec.product_id
            if not product:
                continue
            # check product template flag or product tracking
            is_specimen_flag = (
                product.product_tmpl_id.is_specimen
                if product.product_tmpl_id
                else False
            )
            serial_tracked = (product.tracking == "serial") or is_specimen_flag
            if serial_tracked and not rec.lot_id:
                # create a new lot/serial. Use specimen name or sequence for lot name.
                lot_name = (
                    rec.name
                    or self.env["ir.sequence"].next_by_code("stock.lot")
                    or None
                )
                lot_vals = {
                    "product_id": product.id,
                    "name": lot_name or rec.name,
                }
                new_lot = self.env["stock.lot"].create(lot_vals)
                rec.lot_id = new_lot

            # if lot exists, validate product match
            if rec.lot_id and rec.product_id:
                lot_product = getattr(rec.lot_id, "product_id", False)
                if lot_product and lot_product.id != rec.product_id.id:
                    raise ValidationError(
                        _(
                            f"""Selected lot {rec.lot_id.name} is not for
                            product {rec.product_id.display_name}"""
                        )
                    )

    @api.depends("lot_id")
    def _compute_location_id(self):
        """Safely compute location without recursive re-entry."""
        # Prevent recursion loop if already computing this in current call stack
        if self.env.context.get("lims_location_recursion_guard"):
            return

        StockQuant = self.env["stock.quant"]
        for rec in self.with_context(lims_location_recursion_guard=True):
            location = False
            try:
                if rec.lot_id:
                    quant = (
                        StockQuant.sudo()
                        .with_context(active_test=False)
                        .search([("lot_id", "=", rec.lot_id.id)], limit=1)
                    )
                    if quant:
                        location = quant.location_id
            except Exception:
                # swallow errors to prevent next_stage from breaking
                location = False

            # assign value silently (no write)
            object.__setattr__(rec, "location_id", location)

    # helper action to open the lot record

    def action_open_lot(self):
        """Open the Stock Lot (Serial Number) form view for this specimen."""
        self.ensure_one()
        if not self.lot_id:
            return {"type": "ir.actions.act_window_close"}

        # Use the canonical action for stock lots/serials
        action = self.env.ref("stock.action_product_production_lot_form").read()[0]
        action.update(
            {
                "name": "Lot / Serial",
                "view_mode": "form",
                "res_id": self.lot_id.id,
                "views": [(False, "form")],
                "target": "current",
            }
        )
        return action
