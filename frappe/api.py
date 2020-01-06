
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import json
import frappe
import frappe.handler
import frappe.client
from frappe.utils.response import build_response
from frappe import _
from six.moves.urllib.parse import urlparse, urlencode
from erpnext.utilities.send_telegram import send_msg_telegram


def handle():
	"""
	Handler for `/api` methods

	### Examples:

	`/api/method/{methodname}` will call a whitelisted method

	`/api/resource/{doctype}` will query a table
		examples:
		- `?fields=["name", "owner"]`
		- `?filters=[["Task", "name", "like", "%005"]]`
		- `?limit_start=0`
		- `?limit_page_length=20`

	`/api/resource/{doctype}/{name}` will point to a resource
		`GET` will return doclist
		`POST` will insert
		`PUT` will update
		`DELETE` will delete

	`/api/resource/{doctype}/{name}?run_method={method}` will run a whitelisted controller method
	"""

	validate_oauth()

	parts = frappe.request.path[1:].split("/",3)
	call = doctype = name = None

	if len(parts) > 1:
		call = parts[1]

	if len(parts) > 2:
		doctype = parts[2]

	if len(parts) > 3:
		name = parts[3]

	if call=="method":
		frappe.form_dict.data = dict()
		frappe.local.form_dict.cmd = doctype
        	try:
            		json_data = json.loads(frappe.request.data)
            		for key in json_data:
                		frappe.form_dict[key] = json_data[key]
				frappe.form_dict.data[key] = json_data[key]
        	except Exception as e:
            		pass
        	for key in frappe.request.form:

            		frappe.form_dict.data[key] = frappe.request.form[key]
			frappe.form_dict[key] = frappe.request.form[key]
        	# Get the query string from GET url method, eg: ?search_keyword='test'&...
        	# then split it into segments each segment has "key=value" text
        	query_string = frappe.request.query_string.split("&") if frappe.request.query_string else []
		# send_msg_telegram(str(query_string))
       	 	# Loop into segments list, for each loop split text into key and value
        	# then store them into form_dict to make keys accessible into functions.
        	for part in query_string:
        		part = part.split("=")
                	key = part[0]
                	try:
                		value = part[1]
                	except IndexError:
				continue
                	frappe.form_dict.data[key] = value
			frappe.form_dict[key] = value
		return frappe.handler.handle()

	elif call=="resource":
		if "run_method" in frappe.local.form_dict:
			method = frappe.local.form_dict.pop("run_method")
			doc = frappe.get_doc(doctype, name)
			doc.is_whitelisted(method)

			if frappe.local.request.method=="GET":
				if not doc.has_permission("read"):
					frappe.throw(_("Not permitted"), frappe.PermissionError)
				frappe.local.response.update({"data": doc.run_method(method, **frappe.local.form_dict)})

			if frappe.local.request.method=="POST":
				if not doc.has_permission("write"):
					frappe.throw(_("Not permitted"), frappe.PermissionError)

				frappe.local.response.update({"data": doc.run_method(method, **frappe.local.form_dict)})
				frappe.db.commit()

		else:
			if name:
				if frappe.local.request.method=="GET":
					doc = frappe.get_doc(doctype, name)
					if not doc.has_permission("read"):
						raise frappe.PermissionError
					frappe.local.response.update({"data": doc})

				if frappe.local.request.method=="PUT":
					data = json.loads(frappe.local.form_dict.data)
					doc = frappe.get_doc(doctype, name)

					if "flags" in data:
						del data["flags"]

					# Not checking permissions here because it's checked in doc.save
					doc.update(data)

					frappe.local.response.update({
						"data": doc.save().as_dict()
					})
					frappe.db.commit()

				if frappe.local.request.method=="DELETE":
					# Not checking permissions here because it's checked in delete_doc
					frappe.delete_doc(doctype, name, ignore_missing=False)
					frappe.local.response.http_status_code = 202
					frappe.local.response.message = "ok"
					frappe.db.commit()


			elif doctype:
				if frappe.local.request.method=="GET":
					if frappe.local.form_dict.get('fields'):
						frappe.local.form_dict['fields'] = json.loads(frappe.local.form_dict['fields'])
					frappe.local.form_dict.setdefault('limit_page_length', 20)
					frappe.local.response.update({
						"data":  frappe.call(frappe.client.get_list,
							doctype, **frappe.local.form_dict)})

				if frappe.local.request.method=="POST":
					data = json.loads(frappe.local.form_dict.data)
					data.update({
						"doctype": doctype
					})
					frappe.local.response.update({
						"data": frappe.get_doc(data).insert().as_dict()
					})
					frappe.db.commit()
			else:
				raise frappe.DoesNotExistError

	else:
		raise frappe.DoesNotExistError

	return build_response("json")

def validate_oauth():
	from frappe.oauth import get_url_delimiter
	form_dict = frappe.local.form_dict
	authorization_header = frappe.get_request_header("Authorization").split(" ") if frappe.get_request_header("Authorization") else None
	if authorization_header and authorization_header[0].lower() == "bearer":
		from frappe.integrations.oauth2 import get_oauth_server
		token = authorization_header[1]
		r = frappe.request
		parsed_url = urlparse(r.url)
		access_token = { "access_token": token}
		uri = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path + "?" + urlencode(access_token)
		http_method = r.method
		body = r.get_data()
		headers = r.headers

		required_scopes = frappe.db.get_value("OAuth Bearer Token", token, "scopes").split(get_url_delimiter())

		valid, oauthlib_request = get_oauth_server().verify_request(uri, http_method, body, headers, required_scopes)

		if valid:
			frappe.set_user(frappe.db.get_value("OAuth Bearer Token", token, "user"))
			frappe.local.form_dict = form_dict
