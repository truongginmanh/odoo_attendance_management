from odoo import models, fields


class AttendanceSyncLog(models.Model):
    _name = "attendance.sync.log"
    _description = "Attendance Sync Log"
    _order = "sync_start desc"

    name = fields.Char(
        string="Log Name",
        required=True,
    )

    device_id = fields.Many2one(
        comodel_name="attendance.device",
        string="Device",
        ondelete="set null",
        index=True,
    )

    sync_start = fields.Datetime(
        string="Sync Start",
        required=True,
    )

    sync_end = fields.Datetime(
        string="Sync End",
    )

    status = fields.Selection(
        selection=[
            ("running", "Running"),
            ("success", "Success"),
            ("partial", "Partial"),
            ("error", "Error"),
        ],
        string="Status",
        default="running",
        required=True,
        index=True,
    )

    total_records = fields.Integer(
        string="Total Records",
        default=0,
    )

    new_records = fields.Integer(
        string="New Records",
        default=0,
    )

    duplicate_records = fields.Integer(
        string="Duplicate Records",
        default=0,
    )

    error_records = fields.Integer(
        string="Error Records",
        default=0,
    )

    message = fields.Text(
        string="Message",
    )