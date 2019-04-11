import frappe


def execute():
	try:
		frappe.db.sql("""ALTER TABLE `tabDocPerm` add apply_user_permissions INT NULL DEFAULT '0'
 """)
	except:
		pass
	try:
		frappe.db.sql("""ALTER TABLE `tabCustom DocPerm` add apply_user_permissions INT NULL DEFAULT '0'
 """)
	except:
		pass
        frappe.db.sql("""ALTER TABLE `tabDocPerm` modify apply_user_permissions INT NULL DEFAULT '0';
 """)
        frappe.db.sql("""ALTER TABLE `tabCustom DocPerm` modify apply_user_permissions INT NULL DEFAULT '0';
 """)


