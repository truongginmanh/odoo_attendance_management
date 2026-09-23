from odoo import models, fields


class AttendanceDevice(models.Model):
    _name = "attendance.device"
    _description = "Attendance Device"
    _order = "name"

    name = fields.Char(
        string="Device Name",
        required=True,
    )

    device_code = fields.Char(
        string="Device Code",
        required=True,
        index=True,
    )

    ip_address = fields.Char(
        string="IP Address",
        required=True,
    )

    port = fields.Integer(
        string="Port",
        default=4370,
        required=True,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    last_sync = fields.Datetime(
        string="Last Sync",
    )

    status = fields.Selection(
        selection=[
            ("draft", "Not Connected"),
            ("connected", "Connected"),
            ("error", "Error"),
        ],
        string="Status",
        default="draft",
        required=True,
    )

    note = fields.Text(
        string="Note",
    )

    _sql_constraints = [
        (
            "device_code_unique",
            "unique(device_code)",
            "Device code must be unique.",
        ),
    ]