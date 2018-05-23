
class Table:
    def __init__ (self, headers, rows, use_last_column_for_color=False):
        self.headers = headers
        self.rows = rows
        self.use_last_column_for_color = use_last_column_for_color
        self.column_count = len(self.headers)
    
    def print_table(self):
        # calculate the column widths
        widths = [len(h) for h in self.headers]
        for row in self.rows:
            for i in range(self.column_count):
                widths[i] = max(widths[i], len(str(row[i])))

        print(self.build_row(self.headers + [''], widths)) # add extra item to headers in case using last column for colors!

        for row in self.rows:
            print(self.build_row(row, widths))
        
    def build_row(self, row, widths):
        if (self.use_last_column_for_color):
            output = row[-1]
        else:
            output = ""

        for i in range(self.column_count):
            output += self.pad_and_trunc(row[i], widths[i]) + " "
        return output

    def pad_and_trunc(self, value, width):
        return str(value).ljust(width)[0:width]