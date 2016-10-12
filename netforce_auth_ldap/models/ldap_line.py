from netforce.model import Model, fields

class LdapLine(Model):
    _name = "ldap.line"
    _fields = {
        'ldap_id' : fields.Many2One("ldap","LDAP", on_delete="cascade"),
        'option' : fields.Char("Option", required=True),
        'value' : fields.Char("Value", required=True),
    }

LdapLine.register()
