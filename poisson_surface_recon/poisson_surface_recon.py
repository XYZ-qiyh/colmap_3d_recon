import os

PoissonRecon = "/mnt/A/qiyh/2021/3rd_party_lib/PoissonRecon/Bin/Linux/PoissonRecon"
SurfaceTrimmer = "/mnt/A/qiyh/2021/3rd_party_lib/PoissonRecon/Bin/Linux/SurfaceTrimmer"

if __name__ == "__main__":
    dataset_path = "/mnt/B/qiyh/DTU_dataset/OriginalData/"
    testlist = "./lists/dtu/train.txt"
   
    with open(testlist) as f:
        scans = f.readlines()
        scans = [line.rstrip() for line in scans]
        
    # scans = scans[2:]
    # scans = ["scan64", "scan65", "scan68"]
    print("len of scans: {}".format(len(scans)))
    print("scans: {}".format(scans))

    for scan in scans:
        print(scan)
        fused_ply = os.path.join(dataset_path, "{}/dense_colmap/fused.ply".format(scan))
        assert os.path.isfile(fused_ply)

        #########################################
        # PoissonRecon
        #########################################
        surface_folder = os.path.join(dataset_path, "{}/surface_poisson".format(scan))
        if not os.path.exists(surface_folder):
            os.mkdir(surface_folder)
        mesh_ply = os.path.join(dataset_path, "{}/surface_poisson/mesh.ply".format(scan))

        cmd = PoissonRecon + ' --in ' + fused_ply
        cmd = cmd + ' --out ' + mesh_ply
        cmd = cmd + ' --depth 11 '
        cmd = cmd + ' --density '
        cmd = cmd + ' --verbose '

        print(cmd)
        os.system(cmd)

        #########################################
        # SurfaceTrimmer
        #########################################
        trimmed_mesh_ply = os.path.join(dataset_path, "{}/surface_poisson/mesh_trim_9.5.ply".format(scan))
        cmd = SurfaceTrimmer + ' --in ' + mesh_ply
        cmd = cmd + ' --trim 9.5 '
        cmd = cmd + ' --out ' + trimmed_mesh_ply
        cmd = cmd + ' --verbose ' 

        print(cmd)
        os.system(cmd)

        # break
