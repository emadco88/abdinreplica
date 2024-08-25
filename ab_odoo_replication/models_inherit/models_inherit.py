from odoo import api, models
from odoo.exceptions import ValidationError


class IgnoreWriteDateUpdate(models.AbstractModel):
    _name = 'ignore_write_date_update'
    _description = 'ignore_write_date_update'

    def _ignore_write_date_update(self, values):
        curr_write_date = self.read(['write_date'])[0]['write_date']
        res = super().write(values)
        self.env.cr.execute(f"UPDATE {self._table} SET write_date = %s WHERE id = %s", (curr_write_date, self.id))
        return res


class Costcenter(models.Model):
    _name = 'ab_costcenter'
    _inherit = ['ignore_write_date_update', 'ab_costcenter']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class Store(models.Model):
    _name = 'ab_store'
    _inherit = ['ignore_write_date_update', 'ab_store']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class HrRegion(models.Model):
    _name = 'ab_hr_region'
    _inherit = ['ignore_write_date_update', 'ab_hr_region']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class HrJob(models.Model):
    _name = 'ab_hr_job'
    _inherit = ['ignore_write_date_update', 'ab_hr_job']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class HrDepartment(models.Model):
    _name = 'ab_hr_department'
    _inherit = ['ignore_write_date_update', 'ab_hr_department']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class HrEmployee(models.Model):
    _name = 'ab_hr_employee'
    _inherit = ['ignore_write_date_update', 'ab_hr_employee']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class ProductCompany(models.Model):
    _name = 'ab_product_company'
    _inherit = ['ignore_write_date_update', 'ab_product_company']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class ProductOrigin(models.Model):
    _name = 'ab_product_origin'
    _inherit = ['ignore_write_date_update', 'ab_product_origin']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class ProductGroup(models.Model):
    _name = 'ab_product_group'
    _inherit = ['ignore_write_date_update', 'ab_product_group']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class UsageCauses(models.Model):
    _name = 'ab_usage_causes'
    _inherit = ['ignore_write_date_update', 'ab_usage_causes']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class UsageManner(models.Model):
    _name = 'ab_usage_manner'
    _inherit = ['ignore_write_date_update', 'ab_usage_manner']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class ProductCard(models.Model):
    _name = 'ab_product_card'
    _inherit = ['ignore_write_date_update', 'ab_product_card']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class UomType(models.Model):
    _name = 'ab_uom_type'
    _inherit = ['ignore_write_date_update', 'ab_uom_type']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class Uom(models.Model):
    _name = 'ab_uom'
    _inherit = ['ignore_write_date_update', 'ab_uom']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class ProductBarcode(models.Model):
    _name = 'ab_product_barcode'
    _inherit = ['ignore_write_date_update', 'ab_product_barcode']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        return self._ignore_write_date_update(values)
        # if self.env.context.get('replication'):
        #     return self._ignore_write_date_update(values)
        # raise ValidationError("Not Valid")


class Product(models.Model):
    _name = 'ab_product'
    _inherit = ['ignore_write_date_update', 'ab_product']

    @api.model
    def create(self, values):
        raise ValidationError("Not Valid")

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        if self.env.context.get('replication'):
            return self._ignore_write_date_update(values)
        raise ValidationError("Not Valid")


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = ['ignore_write_date_update', 'res.users']

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        return self._ignore_write_date_update(values)


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['ignore_write_date_update', 'res.partner']

    def unlink(self):
        raise ValidationError("Not Valid")

    def write(self, values):
        return self._ignore_write_date_update(values)
