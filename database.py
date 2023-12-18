import csv
import copy


class CSVReader:
    """
    Class for reading data from a CSV file.
    """

    def __init__(self, input_file):
        self.input_file = input_file

    def read_csv(self):
        """
        Read data from the CSV file and convert it into a list of dictionaries.
        """
        temp = []
        with open(self.input_file) as f:
            rows = csv.DictReader(f)
            for r in rows:
                temp.append(dict(r))
        return temp   # Returns a list of dict where each dict represents a row from the CSV file.


class DB:
    """
    Database class to store and manage tables.
    """
    def __init__(self):
        self.database = []

    def insert(self, table):
        """
        Insert a table into the database.
        """
        self.database.append(table)

    def search(self, table_name):
        """
        Search for a table in the database based on its name.
        """
        for table in self.database:
            if table.table_name == table_name:
                return table
        return None    # Returns the table with the specified name or None if not found.


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
        """
        Perform a filter operation based on a condition.
        """
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
        """
        Perform a select operation on specified attributes.
        """
        temps = []
        for item1 in self.table:
            dict_temp = {}
            for key in item1:
                if key in attributes_list:
                    dict_temp[key] = item1[key]
            temps.append(dict_temp)
        return temps

    def insert_table(self, entry):
        """
        Insert a new entry into the table.
        """
        self.table.append(entry)

    def update(self, check_key, check_val, check2_key, check2_val, key, new_value):
        """
        Update values in the table based on multiple conditions.

        Parameters:
        - check_key (str): The key for the first condition.
        - check_val: The value for the first condition.
        - check2_key (str): The key for the second condition.
        - check2_val: The value for the second condition.
        - key (str): The key to update.
        - new_value: The new value.
        """
        for data in self.table:
            if data[check_key] == check_val and data[check2_key] == check2_val:
                data[key] = new_value

    def update2(self, check_key, check_val, key, new_value):
        """
        Update values in the table based on a single condition.

        Parameters:
        - check_key (str): The key for the condition.
        - check_val: The value for the condition.
        - key (str): The key to update.
        - new_value: The new value.
        """
        for data in self.table:
            if data[check_key] == check_val:
                data[key] = new_value

    def __str__(self):
        return f"{self.table_name} : {self.table}"
