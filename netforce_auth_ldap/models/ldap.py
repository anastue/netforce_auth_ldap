# LDAP3
from ldap3 import Server, Connection, AUTH_SIMPLE, STRATEGY_SYNC, ALL

from netforce.model import Model, fields
from netforce import database
from pprint import pprint

class Ldap(Model):
    _name="ldap"
    _string = "LDAP Authentication"
    _key = ['domain']

    _fields = {
        'domain' : fields.Char("Domain", required=True, search=True),
        'port' : fields.Integer("Port", search=True),
        'server' : fields.Char("Server", required=True, search=True),
        'is_default' : fields.Boolean("Default (Warning: if turn on, default in another data will be disabled.)", search=True),
        'lines' : fields.One2Many("ldap.line","ldap_id","BaseDN")
    }

    _defaults = {
        'is_default' : False
    }

    def check_ldap(self, params, context={}):
        #### domain\username
        print("*"*30,' LADP ',"*"*30)
        pprint(params)
        print("*"*30,' LADP ',"*"*30)
        # set, search data, obj etc. -- start
        username = params.get("username")
        password = params.get("password")
        obj = None
        domain_name = None
        if "\\" not in username: # backslash
            default_ids = self.search([['is_default','=',True]])
            if default_ids:
                obj = self.browse(default_ids[0])
            else:
                return {
                    'status' : False,
                    'msg' : 'Not found default domain for LDAP'
                }
        else:
            domain_name, username = username.split("\\")
            domain_name = domain_name.lower()
            obj_ids = self.search([['domain','ilike',domain_name]])
            if obj_ids:
                obj = self.browse(obj_ids[0])
            else:
                return {
                    'status' : False,
                    'msg' : 'Not found domain name server %s for LDAP'%domain_name
                }
        # set, search data, obj etc. -- end
            
        # var for send to ldap -- start
        HOST = obj.server
        PORT = obj.port
        server = Server(HOST, port=PORT, get_info=ALL)
        # var for send to ldap -- end

        # Connect ldap -- start
        cr = Connection(server, \
            authentication=AUTH_SIMPLE,\
            user=username,\
            password=password,\
            check_names=True,\
            lazy=False,\
            client_strategy=STRATEGY_SYNC,\
            raise_exceptions=True) # use false for skip error
        # Connect ldap -- end
        try:
            cr.open()
            cr.bind()
            return cr.result
        except:
            return False

        """Simple LDAP authentication example.""" 
         
        # Define LDAP server connection (389 is the default port). 
        '''
        url = "ldap://%s"%obj.server
        if obj.port:
            url+=":%s"%obj.port
        ldap_conn = ldap.initialize(uri=url) 
        ldap_conn.protocol_version = ldap.VERSION2  # VERSION2 or VERSION3 
         
        # Get username and password. 
        assert username and password, 'Username and password required.' 
        domain = obj.domain
        username = domain + '\\' + username 
        try: 
            # Bind and unbind connection to LDAP server (synchronous). 
            ldap_conn.simple_bind_s(username, password) 
            ldap_conn.unbind_ext_s() 
            return {
                'status' : True,
                'msg' : 'Found in LDAP'
            }
        except ldap.INVALID_CREDENTIALS as e:
            return {
                'status' : False,
                'msg' : 'Not found in LDAP (%s)'%e
            }
        '''
        return {
            'status' : True,
            'msg' : 'Found in LDAP'
        }

    def clear_is_default(self):
        for obj in self.search_browse([[]]):
            obj.write({
                'is_default' : False
            })

    def create(self,vals,context={}):
        is_default = vals.get("is_default")
        self.clear_is_default if is_default else None
        new_id=super().create(vals,context)
        return new_id

    def write(self,ids,vals,**kw):
        is_default = vals.get("is_default")
        self.clear_is_default if is_default else None
        super().write(ids,vals,**kw)


    def update_db(self):
        db = database.get_connection()
        print("CUSTOM LDAP UPDATE DB")
        res = db.get("SELECT * FROM pg_class WHERE relname=%s", self._table)
        if not res:
            db.execute("CREATE TABLE %s (id SERIAL, PRIMARY KEY (id))" % self._table)
        else:
            res = db.query(
                "SELECT * FROM pg_attribute a WHERE attrelid=(SELECT oid FROM pg_class WHERE relname=%s) AND attnum>0 AND attnotnull", self._table)
            for r in res:
                n = r.attname
                if n == "id":
                    continue
                f = self._fields.get(n)
                if f and f.store:
                    continue
                print("  dropping not-null of old column %s.%s" % (self._table, n))
                q = "ALTER TABLE %s ALTER COLUMN \"%s\" DROP NOT NULL" % (self._table, n)
                db.execute(q)

Ldap.register()
