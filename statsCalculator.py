# Here will be implemented the runtime stats calculators

class statsCalculator:

    # Average of file sizes that were opened, written or read. (Before write operation)
    avgFileSizes_open = 0
    open_counter = 0
    avgFileSizes_read = 0
    read_counter = 0
    avgFileSizes_write = 0
    write_counter = 0
    def avgFileSizes_update(self, filesMap, fileName, type):
        if filesMap.get(fileName):
            if type == "open":
                self.avgFileSizes_open += filesMap.get(fileName)
                self.open_counter += 1
            elif type == "read":
                self.avgFileSizes_read += filesMap.get(fileName)
                self.read_counter += 1
            elif type == "write":
                self.avgFileSizes_write += filesMap.get(fileName)
                self.write_counter += 1
    def avgFileSizes(self):
        return {"open" : 0 if self.open_counter == 0 else self.avgFileSizes_open/self.open_counter,\
                "read" : 0 if self.read_counter == 0 else self.avgFileSizes_read/self.read_counter,\
                "write" : 0 if self.write_counter == 0 else self.avgFileSizes_write/self.write_counter}
    ###################################################################################


x = statsCalculator()
print(x.avgFileSizes())