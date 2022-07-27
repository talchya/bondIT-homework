import csv
from datetime import datetime

from flask import Flask, request

app = Flask(__name__)


def diff_in_minutes(departure, arrival):
    fmt = '%H:%M'
    return (datetime.strptime(departure, fmt) - datetime.strptime(arrival, fmt)).total_seconds() / 60.0


class DictReaderStrip(csv.DictReader):
    @property
    def fieldnames(self):
        if self._fieldnames is None:
            csv.DictReader.fieldnames.fget(self)
            if self._fieldnames is not None:
                self._fieldnames = [name.strip() for name in self._fieldnames]
        return self._fieldnames


@app.route("/<flight>")
def get_flight(flight):
    with open("test1.csv", "r") as f:
        csv_reader = DictReaderStrip(f)
        field_names = csv_reader.fieldnames
        records = list(csv_reader)

    for row in records:
        row['flight ID'] = row['flight ID'].strip()
        row['Arrival'] = row['Arrival'].strip()
        row['Departure'] = row['Departure'].strip()

    sorted_records = sorted(records, key=lambda d: d['Arrival'])

    for row in sorted_records:
        if row['flight ID'] == flight:
            return row

    return "flight does not exist"


@app.route("/<flight>", methods=["POST"])
def upsert_flight(flight):
    params = request.get_json()
    with open("test1.csv", "r") as f:
        csv_reader = DictReaderStrip(f)
        field_names = csv_reader.fieldnames
        records = list(csv_reader)

    for row in records:
        row['flight ID'] = row['flight ID'].strip()
        row['Arrival'] = row['Arrival'].strip()
        row['Departure'] = row['Departure'].strip()

    flag = False
    answer = ""
    for row in records:
        if row['flight ID'] == flight:
            row['Arrival'] = params['Arrival'].strip()
            row['Departure'] = params['Departure'].strip()
            row['success'] = ""
            flag = True
            answer = row

    if not flag:
        row = {"flight ID": flight, "Arrival": params['Arrival'].strip(), "Departure":
            params['Departure'].strip(), "success": ""}
        answer = row
        records.append(row)

    sorted_records = sorted(records, key=lambda d: d['Arrival'])

    last_flight_id = ""
    counter = 0
    for row in sorted_records:
        if not row['flight ID'] == last_flight_id:
            if diff_in_minutes(row['Departure'], row['Arrival']) >= 180 and counter < 20:
                row['success'] = "success"
                counter += 1
            else:
                row['success'] = "fail"
        else:
            row['success'] = ""
        last_flight_id = row['flight ID']

    with open("test1.csv", "w") as f:
        csv_writer = csv.DictWriter(f, field_names)
        csv_writer.writeheader()
        csv_writer.writerows(sorted_records)

    return answer


if __name__ == "__main__":
    app.run()
