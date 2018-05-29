# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import math
from datetime import datetime, timedelta

import frappe


def execute():
    employees = frappe.get_list(
        "Employee",
        fields=[
            "user_id",
            "valid_upto",
            "alarm_passport_expiry",
            "residence_valid_to",
            "alarm_residence_expiry",
            "health_inssurance_valid_to",
            "alarm_inssurance_expiry"
        ],
        filters=dict(),
        ignore_ifnull=True,
        ignore_permissions=True
    )
    all_users = frappe.get_all(
        "User",
        fields=["name", "full_name"],
        filters=dict(
            user_type="System User"
        ),
        ignore_permissions=True,
        ignore_ifnull=True
    )
    for employee in employees:
        full_name = frappe.get_value("User", employee.user_id, "full_name")

        if employee.valid_upto and employee.alarm_passport_expiry and datetime.strptime(
                str(employee.valid_upto)[:10],
                '%Y-%m-%d').date() > (datetime.now() - timedelta(days=28)).date():
            remained_days = int(math.ceil((datetime.strptime(
                str(employee.residence_valid_to)[:10],
                '%Y-%m-%d').date() - datetime.now().date()).total_seconds() / 3600 / 24))
            alert = frappe.get_doc(
                doctype="Note",
                title=frappe.generate_hash("Note", 16).upper(),
                public=1,
                notify_on_login=1,
                notify_on_every_login=0,
                expire_notification_on=(datetime.now() + timedelta(days=1)).date(),
                content="""<div align="right"><b><font color="#397B21">مرحبا {0}</font><br>
نود ثذكيرك بأن <font color="#9C0000">
تاريخ صلاحية جواز السفر الخاص بك على وشك الإنتهاء</font>.. باقٍ على تاريخ إنتهائه<font color="#9C0000"> {1} </font>
<br>الرجاء تجديد جواز سفرك وتحديث بياناتك عند الموارد البشرية<br><br>نتمنى لك يوما سعيدا<br>
</b></div>""".format(
                    full_name,
                    "أقل من ({}) أسبوع".format(remained_days / 7) if remained_days > 0 else "(انتهى تاريخ الصلاحية)"
                ),
            )
            alert.insert(ignore_permissions=True)
            alert.title = "تذكير بشأن تاريخ صلاحية جواز السفر"
            for user in all_users:
                if user.name != employee.user_id:
                    alert.append("seen_by", dict(
                        user=user.name,
                    ))
            alert.save(ignore_permissions=True)

            ## for administrator
            alert = frappe.get_doc(
                doctype="Note",
                title=frappe.generate_hash("Note", 16).upper(),
                public=1,
                notify_on_login=1,
                notify_on_every_login=0,
                expire_notification_on=(datetime.now() + timedelta(days=1)).date(),
                content="""<div align="right"><b><font color="#397B21">الموظف {0}</font><br>.. باقٍ على تاريخ إنتهاء جواز سفره<font color="#9C0000"> {1} </font>
</b></div>""".format(
                    full_name,
                    "أقل من ({}) أسبوع".format(remained_days / 7) if remained_days > 0 else "(انتهى تاريخ الصلاحية)"
                ),
            )
            alert.insert(ignore_permissions=True)
            alert.title = "تذكير بشأن تاريخ صلاحية جواز السفر"
            for user in all_users:
                if user.name != "Administrator":
                    alert.append("seen_by", dict(
                        user=user.name,
                    ))
            alert.save(ignore_permissions=True)

        if employee.residence_valid_to and employee.alarm_residence_expiry and datetime.strptime(
                str(employee.residence_valid_to)[:10],
                '%Y-%m-%d').date() > (datetime.now() - timedelta(days=28)).date():
            remained_days = int(math.ceil((datetime.strptime(
                str(employee.residence_valid_to)[:10],
                '%Y-%m-%d').date() - datetime.now().date()).total_seconds() / 3600 / 24))

            alert = frappe.get_doc(
                doctype="Note",
                title=frappe.generate_hash("Note", 16).upper(),
                public=1,
                notify_on_login=1,
                notify_on_every_login=0,
                expire_notification_on=(datetime.now() + timedelta(days=1)).date(),
                content="""<div align="right"><b><font color="#397B21">مرحبا بك</font><br>نود ثذكيرك بأن <font color="#9C0000">إقامتك على وشك الإنتهاء</font>.. باقٍ على تاريخ إنتهائها<font color="#9C0000"> {} </font>فقط<br>الرجاء تجديد إقامتك وتحديث بياناتك عند الموارد البشرية<br><br>نتمنى لك يوما سعيدا<br></b></div>""".format(
                    "أقل من ({}) أسبوع".format(remained_days / 7) if remained_days > 0 else "(انتهى تاريخ الصلاحية)"
                ),
            )
            alert.insert(ignore_permissions=True)
            alert.title = "تذكير بشأن تاريخ إقامتك"
            for user in all_users:
                if user.name != employee.user_id:
                    alert.append("seen_by", dict(
                        user=user.name,
                    ))
            alert.save(ignore_permissions=True)
            ## for administrator
            alert = frappe.get_doc(
                doctype="Note",
                title=frappe.generate_hash("Note", 16).upper(),
                public=1,
                notify_on_login=1,
                notify_on_every_login=0,
                expire_notification_on=(datetime.now() + timedelta(days=1)).date(),
                content="""<div align="right"><b><font color="#397B21">الموظف {0}</font><br>.. باقٍ على تاريخ إنتهاء إقامته<font color="#9C0000"> {1} </font>
</b></div>""".format(
                    full_name,
                    "أقل من ({}) أسبوع".format(remained_days / 7) if remained_days > 0 else "(انتهى تاريخ الصلاحية)"
                ),
            )
            alert.insert(ignore_permissions=True)
            alert.title = "تذكير بشأن تاريخ الإقامة"
            for user in all_users:
                if user.name != "Administrator":
                    alert.append("seen_by", dict(
                        user=user.name,
                    ))
            alert.save(ignore_permissions=True)

        if employee.health_inssurance_valid_to and employee.alarm_inssurance_expiry and datetime.strptime(
                str(employee.health_inssurance_valid_to)[:10],
                '%Y-%m-%d').date() > (datetime.now() - timedelta(days=28)).date():
            alert = frappe.get_doc(
                doctype="Note",
                title=frappe.generate_hash("Note", 16).upper(),
                public=1,
                notify_on_login=1,
                notify_on_every_login=0,
                expire_notification_on=(datetime.now() + timedelta(days=1)).date(),
                content="""<div align="right"><b><font color="#397B21">مرحبا بك</font><br>نود ثذكيرك بأن <font color="#9C0000">تاريخ تأمينك الصحي على وشك الإنتهاء</font>.. باقٍ على تاريخ إنتهائه<font color="#9C0000"> {} </font><br>الرجاء تجديد تأمينك الصحي وتحديث بياناتك عند الموارد البشرية<br><br>نتمنى لك يوما سعيدا<br></b></div>""".format(
                    "أقل من ({}) أسبوع".format(remained_days / 7) if remained_days > 0 else "(انتهى تاريخ الصلاحية)"
                ),
            )
            alert.insert(ignore_permissions=True)
            alert.title = "تذكير بشأن تاريخ إنتهاء تأمينك الصحي"
            for user in all_users:
                if user.name != employee.user_id:
                    alert.append("seen_by", dict(
                        user=user.name,
                    ))
            alert.save(ignore_permissions=True)

            ## for administrator
            alert = frappe.get_doc(
                doctype="Note",
                title=frappe.generate_hash("Note", 16).upper(),
                public=1,
                notify_on_login=1,
                notify_on_every_login=0,
                expire_notification_on=(datetime.now() + timedelta(days=1)).date(),
                content="""<div align="right"><b><font color="#397B21">الموظف {0}</font><br>.. باقٍ على تاريخ إنتهاء تأمينه الصحي<font color="#9C0000"> {1} </font>
            </b></div>""".format(
                    full_name,
                    "أقل من ({}) أسبوع".format(remained_days / 7) if remained_days > 0 else "(انتهى تاريخ الصلاحية)"
                ),
            )
            alert.insert(ignore_permissions=True)
            alert.title = "تذكير بشأن تاريخ التأمين الصحي"
            for user in all_users:
                if user.name != "Administrator":
                    alert.append("seen_by", dict(
                        user=user.name,
                    ))
            alert.save(ignore_permissions=True)
