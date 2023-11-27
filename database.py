import csv
import copy


class CSVReader:
    def __init__(self, input_file):
        self.input_file = input_file

    def read_csv(self):
        temp = []
        with open(self.input_file) as f:
            rows = csv.DictReader(f)
            for r in rows:
                temp.append(dict(r))
        return temp


class DB:
    def __init__(self):
        self.database = []

    def insert(self, table):
        self.database.append(table)

    def search(self, table_name):
        for table in self.database:
            if table.table_name == table_name:
                return table
        return None

    def get_tables(self):
        tables_dict = {}
        for table in self.database:
            tables_dict[table.table_name] = table
        return tables_dict


class Table:
    def __init__(self, table_name, table):
        self.table_name = table_name
        self.table = table

    def join(self, other_table, common_key):
        joined_table = Table(self.table_name + '_joins_' + other_table.table_name, [])
        for item1 in self.table:
            for item2 in other_table.table:
                if item1[common_key] == item2[common_key]:
                    dict1 = copy.deepcopy(item1)
                    dict2 = copy.deepcopy(item2)
                    dict1.update(dict2)
                    joined_table.table.append(dict1)
        return joined_table

    def filter(self, condition):
        filtered_table = Table(self.table_name + '_filtered', [])
        for item1 in self.table:
            if condition(item1):
                filtered_table.table.append(item1)
        return filtered_table

    def aggregate(self, function, aggregation_key):
        temps = []
        for item1 in self.table:
            temps.append(float(item1[aggregation_key]))
        return function(temps)

    def select(self, attributes_list):
        temps = []
        for item1 in self.table:
            dict_temp = {}
            for key in item1:
                if key in attributes_list:
                    dict_temp[key] = item1[key]
            temps.append(dict_temp)
        return temps

    def insert_table(self, entry):
        self.table.append(entry)

    def update(self, user_id, key, new_value):
        for data in self.table:
            if data['ID'] == user_id:
                data[key] = new_value

    def __str__(self):
        return f"{self.table_name} : {self.table}"
