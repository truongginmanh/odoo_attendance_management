from odoo import models, fields


class RawAttendance(models.Model):
    _name = "attendance.raw"
    _description = "Raw Attendance"
    _order = "timestamp desc"

    employee_code = fields.Char(
        string="Employee Code",
        required=True,
        index=True,
    )

    timestamp = fields.Datetime(
        string="Timestamp",
        required=True,
        index=True,
    )

    device_id = fields.Char(
        string="Device",
        index=True,
    )

    source = fields.Selection(
        selection=[
            ("device", "Attendance Device"),
            ("file", "Imported File"),
            ("api", "API"),
            ("manual", "Manual"),
        ],
        string="Source",
        default="device",
        required=True,
    )

    import_date = fields.Datetime(
        string="Import Date",
        default=fields.Datetime.now,
        required=True,
    )

    processed = fields.Boolean(
        string="Processed",
        default=False,
        index=True,
    )

    mapping_id = fields.Many2one(
        comodel_name="attendance.employee.mapping",
        string="Employee Mapping",
        index=True,
        ondelete="set null",
    )

    note = fields.Text(
        string="Note",
    )