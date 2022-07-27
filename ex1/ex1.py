import csv
from datetime import datetime


class DictReaderStrip(csv.DictReader):
    @property
    def fieldnames(self):
        if self._fieldnames is None:
            csv.DictReader.fieldnames.fget(self)
            if self._fieldnames is not None:
                self._fieldnames = [name.strip() for name in self._fieldnames]
        return self._fieldnames


def diff_in_minutes(departure, arrival):
    fmt = '%H:%M'
    return (datetime.strptime(departure, fmt) - datetime.strptime(arrival, fmt)).total_seconds() / 60.0


with open("test.csv", "r") as f:
    csv_reader = DictReaderStrip(f)
    field_names = csv_reader.fieldnames
    records = list(csv_reader)

for row in records:
    row['flight ID'] = row['flight ID'].strip()
    row['Arrival'] = row['Arrival'].strip()
    row['Departure'] = row['Departure'].strip()


sorted_records = sorted(records, key=lambda d: d['Arrival'])

counter = 0
last_flight_id = ""
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

with open("test.csv", "w") as f:
    csv_writer = csv.DictWriter(f, field_names)
    csv_writer.writeheader()
    csv_writer.writerows(sorted_records)
