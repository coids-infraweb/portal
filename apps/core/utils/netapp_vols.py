import subprocess
import argparse

AGGREGATE = "aggr_FSAS16T04_N3"


def comando_netapp(divisao, grupo, produto, user):
    print(f"entrou")
    try:
        volume = f"vol_int_{divisao}_{grupo}_{produto}_dados".lower()
        montagem = f"/{produto}_dados".lower()
        password = '!Net03App@#'
        vserver = "svm_int"
        policy = "policy_int_ro"
        size = '5GB'
        permissions = '2750'
        snapshot = 'default'
        percentagen_snapshot = '5'

        cmd = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {user}@150.163.161.36 'vol show -vserver {vserver} -volume {volume}'"
        output = subprocess.getstatusoutput(cmd)

        if "There are no entries matching your query." in output[1]:
            print("\n-> Volume não existe, criando...")
            cmd = f'sshpass -p "{password}" ssh {user}@150.163.161.36 "vol create -volume {volume} -aggregate {AGGREGATE} -size {size} -state online -policy {policy} -unix-permissions {permissions} -type RW -snapshot-policy {snapshot} -foreground true -vserver {vserver} -junction-path {montagem} -percent-snapshot-space {percentagen_snapshot}"'
            print("\n-> Criando volume...")
            output = subprocess.getstatusoutput(cmd)
            print(f"\n->Output 1: {output}")
            cmd = f'sshpass -p "{password}" ssh {user}@150.163.161.36 "vol snapshot autodelete modify -vserver {vserver} -volume {volume} -enabled true -commitment try -defer-delete user_created -delete-order oldest_first -target-free-space 15% -trigger volume"'
            print("\n-> Ativando autodelete...")
            output = subprocess.getstatusoutput(cmd)
            print(f"\n->Output 2: {output}")
            cmd = f'sshpass -p "{password}" ssh {user}@150.163.161.36 "vol efficiency on -vserver {vserver} -volume {volume}"'
            print("\n-> Ativando dedup...")
            output = subprocess.getstatusoutput(cmd)
            print(f"\n->Output 3: {output}")
        else:
            print(f"--> O volume {volume} já existe no NetApp... Nada a fazer.")
            return False
    except Exception as err:
        print(f'Deu erro em segundo plano?: {err}')


print("\n##### Criando volumes dirs")
    
