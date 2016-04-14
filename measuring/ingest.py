################################################################
#
#       This file contains methods for ingesting
#       the various files that the users may
#       upload into the measuring too.
#
################################################################
import re
import allometric
from mrvapi.models import Project, Parcel, Plot, Tree


class IndonesianPlotIngest(object):
    parcels = dict()
    plots = dict()
    trees = list()
    region = None

    def __init__(self, file_sk, project):
        self.file_sk = file_sk
        self.project = project

    def __call__(self):
        self.ingest()
        self.save_to_database()

    def ingest(self):
        try:
            contents = self.file_sk.read()
        except:
            raise Exception("Can't read file contents")

        line_num = 0
        if '\r\n' in contents:
            contents = contents.split('\r\n')
        else:
            contents = contents.split('\n')

        regex = re.compile('END PLOTS|END PARCELS|END TREES')
        INGESTSTATE = -1

        for line in contents:
            line_num += 1
            line = line.strip('\r')
            if not line:
                continue
            if line == "BEGIN PARCELS":
                INGESTSTATE = 0
                continue
            elif line == "BEGIN PLOTS":
                INGESTSTATE = 1
                continue
            elif line == "BEGIN TREES":
                INGESTSTATE = 2
                continue
            elif regex.match(line) is not None:
                INGESTSTATE = -1
                continue

            line = re.split(", |,", line)
            if line[0] == "id":
                continue

            if INGESTSTATE == 0:            # Parcel
                if len(line) != 3:
                    raise Exception("You did not define a parcel correctly on line %d" % line_num)
                for i in line:
                    if not i:
                        raise Exception("You cannot have an empty value on line %d" % line_num)
                self.parcels[int(line[0])] = { "name": line[1], "area_reported": float(line[2]) }
            elif INGESTSTATE == 1:          # Plot
                if len(line) != 8:
                    raise Exception("You did not define a plot correctly on line %d" % line_num)
                for i in range(0, len(line)):
                    if i != 3 and not line[i]:
                        raise Exception("You cannot have an empty value on line %d in column %d" % (line_num, i))
                self.plots[int(line[0])] = {
                    "name" : line[1],
                    "parcel_id" : int(line[2]),
                    "shape_reported": line[3],
                    "dimensions_reported" : line[4],
                    "region" : line[5],
                    "calculate_by_species" : line[6],
                    "root_shoot_ratio" : float(line[7])
                }
            elif INGESTSTATE == 2:          # Tree
                if len(line) != 5:
                    raise Exception("You did not define a tree correctly on line %d" % line_num)
                if (not line[2] or line[2] == 'None') and (line[3] != 'None' or line[3]):
                    if ' ' in line[3]:
                        s = re.split("[ \t]*", line[3])
                        line[2] = s[0]
                        line[3] = s[1]
                for i in line:
                    if not i:
                        raise Exception("You cannot have an empty value on line %d" % line_num)

                self.trees.append({
                    "id" : int(line[0]),
                    "plot_id" : int(line[1]),
                    "genus" : line[2],
                    "species" : line[3],
                    "dbh" : float(line[4])
                })


    def save_to_database(self):
        true_reg = re.compile("[Tt]rue")
        for key in self.parcels:
            p = Parcel()
            p.name = self.parcels[key]["name"]
            p.area_reported = self.parcels[key]["area_reported"]
            p.project = self.project
            p.save()
            for plot in self.plots:
                if self.plots[plot]["parcel_id"] == key:
                    self.plots[plot]["parcel_id"] = p

        for key in self.plots:
            p = Plot()
            p.name = self.plots[key]["name"]
            p.parcel = self.plots[key]["parcel_id"]
            p.project = self.project
            p.dimensions_reported = self.plots[key]["dimensions_reported"]
            p.shape_reported = self.plots[key]["shape_reported"]
            if true_reg.match(self.plots[key]["calculate_by_species"]) is not None:
                p.calculate_by_species = True
            else:
                p.calculate_by_species = False
            try:
                if self.region is not None and self.region.name.lower() == self.plots[key]["region"].lower():
                    pass
                else:
                    region = allometric.models.EquationRegion.objects.get(name__iexact=self.plots[key]["region"])
            except:
                region = None
            p.region = region
            p.root_shoot_ratio = self.plots[key]["root_shoot_ratio"]

            p.save()
            for t in self.trees:
                if t["plot_id"] == key:
                    t["plot_id"] = p
        l = list()
        for key in self.trees:
            p = Tree()
            p.plot = key["plot_id"]
            p.genus = key["genus"]
            p.species = key["species"]
            p.dbh = key["dbh"]
            l.append(p)

        Tree.objects.bulk_create(l)

