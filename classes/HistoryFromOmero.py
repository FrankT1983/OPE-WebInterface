import omero

class HistoryFromOmero :
    def getHierarchyFromAllGroups(self,conn):
        startgroup = conn.getGroupFromContext().getId()

        result = {"data": []}
        groups = list(conn.getGroupsMemberOf())

        for g in groups:
            conn.SERVICE_OPTS.setOmeroGroup(g.getId())
            g_data = {"type": "group"}
            g_data["name"] = g.getName()
            g_data["children"] = []
            g_data["id"] = [g.getId()]
            result["data"].append(g_data)

            # get all images and then build tree from there ancestry
            images = list(conn.getObjects("Image"))

            DataSets = {}
            Projects = {}

            for img in images:
                ac = img.getAncestry()

                img_data = {"type": "image"}
                img_data["name"] = img.getName()
                img_data["id"] = img.getId()

                if (len(ac) == 1):
                    # belongs only to da dataset
                    ds_data, created = self.create_or_get_dataset_data(ac[0], DataSets)
                    if (created):
                        g_data["children"].append(ds_data)

                    ds_data["children"].append(img_data)

                if (len(ac) == 2):
                    # belongs only to da dataset and project

                    proj = img.getProject()
                    proj_id = proj.getId()

                    if not proj_id in Projects:
                        proj_data = {"type": "project"}
                        proj_data["name"] = proj.getName()
                        proj_data["id"] = proj_id
                        proj_data["children"] = []

                        Projects[proj_id] = proj_data
                        g_data["children"].append(proj_data)
                    else:
                        proj_data = Projects[proj_id]

                    for ac_i in range(0,len(ac)):
                        if (ac[ac_i].getName() == proj.getName and ac[ac_i].getId() == proj_id):
                            # not %100 save, but save enough for now
                            continue

                        ds_data, created = self.create_or_get_dataset_data(ac[ac_i], DataSets)
                        if (created):
                            proj_data["children"].append(ds_data)
                        ds_data["children"].append(img_data)
                        break

        conn.SERVICE_OPTS.setOmeroGroup(startgroup)
        return result

    def create_or_get_dataset_data(self,ds_wrapper, data_sets_repo):
        ancestry_data_set = ds_wrapper
        ancestry_data_set_name = ancestry_data_set.getName()
        ancestry_data_set_id = ancestry_data_set.getId()

        created = False
        if not ancestry_data_set_id in data_sets_repo:
            ds_data = {"type": "dataset"}
            ds_data["name"] = ancestry_data_set_name
            ds_data["id"] = ancestry_data_set_id
            ds_data["children"] = []
            data_sets_repo[ancestry_data_set_id] = ds_data
            created = True,
        else:
            ds_data = data_sets_repo[ancestry_data_set_id]
        return ds_data, created

    def getThumbNail(self,conn, imageId):
        return "http://omero.inf-ra.uni-jena.de:8080/webclient/render_thumbnail/size/96/" + str(imageId) + "/"