# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe.model.document import Document
from frappe.permissions import (get_valid_perms, update_permission_property)
from frappe import _

class UserPermission(Document):
	def validate(self):
		duplicate_exists = frappe.db.get_all(self.doctype, filters={
			'allow': self.allow,
			'for_value': self.for_value,
			'user': self.user,
			'name': ['!=', self.name]
		}, limit=1)
		if duplicate_exists:
			frappe.msgprint(_("User permission already exists"), raise_exception=True)

	def on_update(self):
		frappe.cache().delete_value('user_permissions')
		frappe.publish_realtime('update_user_permissions')

	def on_trash(self): # pylint: disable=no-self-use
		frappe.cache().delete_value('user_permissions')
		frappe.publish_realtime('update_user_permissions')

@frappe.whitelist()
def get_user_permissions(user=None):
	'''Get all users permissions for the user as a dict of doctype'''
	# if this is called from client-side,
	# user can access only his/her user permissions
	if frappe.request and frappe.local.form_dict.cmd == 'get_user_permissions':
		user = frappe.session.user

	if not user:
		user = frappe.session.user

	cached_user_permissions = frappe.cache().hget("user_permissions", user)

	if cached_user_permissions is not None:
		return cached_user_permissions

	out = {}
	try:
		for perm in frappe.get_all('User Permission',
			fields=['allow', 'for_value', 'skip_for_doctype'], filters=dict(user=user)):
			meta = frappe.get_meta(perm.allow)
			if not perm.allow in out:
				out[perm.allow] = {
					"docs": [],
					"skip_for_doctype": perm.skip_for_doctype.split("\n") if perm.skip_for_doctype else []
				}
			out[perm.allow]["docs"].append(perm.for_value)
			try:
				is_nested = meta.is_nested_set()
			except:
				is_nested = False
			if is_nested:
				try:
					out[perm.allow]["docs"].extend(frappe.db.get_descendants(perm.allow, perm.for_value))
				except: pass
		frappe.cache().hset("user_permissions", user, out)
	except frappe.SQLError as e:
		if e.args[0]==1146:
			# called from patch
			pass

	return out
