# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime, timedelta

import frappe
import math


def execute():
    employees = frappe.get_list(
        "Employee",
        fields=["user_id", "valid_upto"],
        filters=dict(),
        ignore_ifnull=True,
        ignore_permissions=True
    )
    all_users = frappe.get_all(
        "User",
        filters=dict(
            user_type="System User"
        ),
        ignore_permissions=True,
        ignore_ifnull=True
    )
    for employee in employees:
        if employee.valid_upto and datetime.strptime(
                str(employee.valid_upto)[:10],
                '%Y-%m-%d').date() > (datetime.now() - timedelta(days=28)).date():
            remained_days = int(math.ceil((datetime.strptime(
                str(employee.valid_upto)[:10],
                '%Y-%m-%d').date() - datetime.now().date()).total_seconds() / 3600 / 24))
            if remained_days % 7 != 0:
                continue
            alert = frappe.get_doc(
                doctype="Note",
                title=frappe.generate_hash("Note", 16).upper(),
                public=1,
                notify_on_login=1,
                expire_notification_on=(datetime.now() + timedelta(days=6)).date(),
                content="""<div align="right"><b><font color="#397B21">مرحبا بك</font><br>نود ثذكيرك بأن <font color="#9C0000">تاريخ صلاحية جواز السفر الخاص بك على وشك الإنتهاء</font>.. باقٍ على تاريخ إنتهائه<font color="#9C0000"> {} </font>فقط<br>الرجاء تجديد جواز سفرك وتحديث بياناتك عند الموارد البشرية<br><br>نتمنى لك يوما سعيدا<br></b></div>""".format(
                    "أقل من ({}) أسبوع".format(remained_days / 7) if remained_days != 0 else "يوم واحد"
                ),
            )
            alert.insert(ignore_permissions=True)
            alert.title = "تذكير بشأن تاريخ صلاحية جواز السفر"
            for user in all_users:
                if user.name != employee.user_id:
                    alert.append("seen_by", dict(
                        user="",

                    ))
            alert.save(ignore_permissions=True)

