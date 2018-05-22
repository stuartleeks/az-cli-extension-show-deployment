
class Table:
    def __init__ (self, headers, rows):
        self.headers = headers
        self.rows = rows
    
    def print_table(self):
        # calculate the column widths
        widths = [len(h) for h in self.headers]
        for row in self.rows:
            for i in range(5):
                widths[i] = max(widths[i], len(str(row[i])))

        print(self.build_row(self.headers, widths))

        for row in self.rows:
            print(self.build_row(row, widths))
        
    def build_row(self, row, widths):
        output = ""
        for i in range(len(row)):
            output += self.pad_and_trunc(row[i], widths[i]) + " "
        return output

    def pad_and_trunc(self, value, width):
        return str(value).ljust(width)[0:width]