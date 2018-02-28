===========
Django Obit
===========

This Django app is in major flux, but its aim is allow area funeral homes 
to supply a given local newspaper with clean, reliable death notice and 
obituary information that can be quickly and easily formatted and distributed 
both online and in print. A few Adobe InDesign templates are included as 
examples.

Add this to your urls.py:
(r'^add/(?P<model_name>\w+)/$', 'obituary.views.add_new_model'),

Make sure you can send out an e-mail. (Elsewise, it'll bust on ``save()`` 
 To stop the email sending comment out ``.send`` lines.)

Also, add recipients to obituary_settings.py, otherwise no e-mails will go 
out.

Note to self: Run locally from virtualenv `test_root` with ssh tunnel to 
server.

===========
Immediate To Do
===========
- Finish password reset
- Preceded in death (by wife). <- create logic for; if spouse death date

===========
Other To Do
===========
- Form factory for FH index view?
- Wire up delete_old_items() in utils into cron job.
- jQuery/Ajax lookup of Death notice remembrances on Obituary onselect of 
Death notice

===========
Odd Areas
===========
- "Length of residence in Lane County area:"
- "Length of relationship:"
- What do outside-of-area folk do?

===========
Schema
===========
.. image:: https://cloud.githubusercontent.com/assets/96007/4929379/6ef1e6e8-6552-11e4-805e-530c944a6202.png
