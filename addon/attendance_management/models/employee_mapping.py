from odoo import models, fields


class EmployeeMapping(models.Model):
    _name = "attendance.employee.mapping"
    _description = "Employee Attendance Mapping"
    _order = "employee_code"

    _sql_constraints = [
        (
            "employee_code_device_unique",
            "unique(employee_code, device_id)",
            "Employee code and device must be unique.",
        ),
    ]

    name = fields.Char(
        string="Mapping Name",
        required=True,
    )

    employee_code = fields.Char(
        string="Employee Code",
        required=True,
        index=True,
    )

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
        index=True,
        ondelete="restrict",
    )

    device_id = fields.Char(
        string="Device",
        index=True,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    note = fields.Text(
        string="Note",
    )