import json

from courses.models import FormBuilder, FormEntry


def get_form_columns(form: FormBuilder):
    columns = ['time']
    column_names = []
    fields = form.fields.order_by("id")
    for field in fields:
        columns.append(field.label)
        column_names.append(field.internal_name)

    if len(form.register_api.all()) > 0:
        columns.append("ejudge_login")
        column_names.append("ejudge_login")
        columns.append("ejudge_password")
        column_names.append("ejudge_password")
        columns.append("ejudge_id")
        column_names.append("ejudge_id")

    return [columns, column_names]


def get_form_entry_row(entry: FormEntry, column_names):
    row = [entry.time.strftime('%d.%m.%Y %H:%M:%S')]
    entry_dict = json.loads(entry.data)

    for column in column_names:
        if column in entry_dict:
            row.append(entry_dict[column])
        else:
            row.append('')

    return row