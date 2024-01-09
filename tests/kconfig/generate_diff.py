from tabulate import tabulate

COLUMN_WIDTH_MAX = 40
MODIF_COLUMN_WIDTH_MAX = 80

def read_data(file1):
    data = []
    with open(file1, 'r') as f1:
        data = f1.readlines()
        data = filter(lambda line: not(line.startswith('#')), data)
    
    ret = dict()
    for line in data:
        tokens = line.split('=')
        if len(tokens) == 2:
            key, val = tokens[0].strip(), tokens[-1].strip()
        ret[key] = val
    return ret

def generate_diff(file1, file2):
    data_f1 = read_data(file1)
    data_f2 = read_data(file2)
    
    additions = []
    modifications = []
    deletions = []

    for key_old, val_old in data_f1.items():
        val_new = data_f2.get(key_old, None)
        if not val_new:
            deletions.append("{}={}".format(key_old, val_old))
        elif val_old != val_new:
            modifications.append("{}={}->{}".format(key_old, val_old, val_new))
        if val_new:
            del data_f2[key_old]
    
    for key, val in data_f2.items():
        additions.append("{}={}".format(key, val))
    return additions, modifications, deletions

def restrict_column_width(lis, width):
    for i in range(0, len(lis)):
        curr_width = len(lis[i])
        new_val = ''
        num_newlines = int(curr_width/width)
        for j in range(0, num_newlines+1):
            if (j+1)*width < curr_width:
                new_val += lis[i][j*width:(j+1)*width]
                new_val += "\n"
            else:
                new_val += lis[i][j*width:]
        lis[i] = new_val

def format_diff_table(additions, modifications, deletions):
    max_len = max(len(additions), len(deletions))
    additions += [''] * (max_len - len(additions))
    deletions += [''] * (max_len - len(deletions))

    restrict_column_width(additions, COLUMN_WIDTH_MAX)
    restrict_column_width(deletions, COLUMN_WIDTH_MAX)
    restrict_column_width(modifications, MODIF_COLUMN_WIDTH_MAX)

    table_data = list(zip(additions, deletions))
    headers = ["ADDITIONS", "DELETIONS"]

    str_ = tabulate(table_data, headers=headers, tablefmt="grid")
    str_ += "\n" * 5
    str_ += tabulate(list(zip(modifications)), headers=["MODIFICATIONS"], tablefmt="grid")
    return str_

if __name__ == "__main__":
    ver1 = '5.10.0-23-2-amd64'
    ver2 = '6.1.0-11-2-amd64'
    file1 = 'config-{}'.format(ver1)
    file2 = 'config-{}'.format(ver2)

    additions, modifications, deletions = generate_diff(file1, file2)
    diff_table = format_diff_table(additions, modifications, deletions)

    metadata = {
        'name' : 'diff_{}_{}_{}_{}.txt'.format('5-10-0-23-2',  '6-1-0-11-2', 'amd64', 'mlnx-msn3420'),
        'platform' : 'x86_64-mlnx_msn3420-r0',
        'diff' : diff_table,
        'old_commit_id' : '6416e238c',
        'new_commit_id' : 'c410b18f8',
        'old_build' : '',
        'new_build' : ''
    }

    hdr_lines = []
    hdr_lines += "Platform = {}\n".format(metadata['platform'])
    hdr_lines += "Build Commit for {} = {}\n".format(ver1, metadata['old_commit_id'])
    hdr_lines += "Build Commit for {} = {}\n".format(ver2, metadata['new_commit_id'])
    hdr_lines += "\n"
    hdr_lines += "KConfig Diff b/w {} -> {}:\n\n".format(ver1, ver2)
    with open(metadata['name'], 'w') as f:
        f.write("".join(hdr_lines))
        f.write(diff_table)