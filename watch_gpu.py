import os
import re


def get_users():
    ''' 获取当前在线的用户

        解析who的结果：
            chenlinwei :0           2023-09-18 12:39 (:0)
            root     :1           2023-09-18 12:56 (:1)
            chenlinwei pts/9        2023-09-18 14:43 (tmux(15646).%0)
            chenlinwei pts/9        2023-09-18 14:43 (tmux(15646).%0)

        注意去重
    '''
    
    users = set()
    with os.popen("who") as f:
        lines = f.readlines()
    
    for line in lines:
        users.add(line.split(" ")[0])
    
    return users

def expand_name(query_name, usernames):
    """ 最大匹配算法 

        例：
            chenlin+ 扩展为 chenlinwei
    """
    max_len = 0
    full_name = query_name

    for username in usernames:
        min_len = min(len(query_name), len(username))
        for i in range(min_len):
            if query_name[i] == username[i]:
                if i > max_len:
                    max_len = i
                    full_name = username
            else:
                break
    
    return full_name

def get_process_infos():
    """
        获取进程信息：

        返回结果：{进程: 用户名}
    """

    # 获取在线用户
    usernames = get_users()

    # 获取进程
    with os.popen("""ps -aux | awk '{print $1 " " $2}'""") as f:
        lines = f.readlines()[1:]
    
    # 解析进程信息
    pid_2_name = dict()
    simple_name_2_full_name = dict()
    for line in lines:
        simple_username, pid = line[:-1].split(" ")
        if simple_username not in simple_name_2_full_name:
            simple_name_2_full_name[simple_username] = expand_name(simple_username, usernames)
        pid_2_name[pid] = simple_name_2_full_name[simple_username]

    return pid_2_name


if __name__ == '__main__':
    pid_2_name = get_process_infos()

    # 获取gpu信息
    with os.popen('nvidia-smi') as f:
        lines = f.readlines()
    
    # 解析使用情况
    gpu_index_pattern = re.compile(' (\d) ')
    pid_pattern = re.compile(' (\d{3,5}) ')
    size_pattern = re.compile(' (\d+)MiB ')

    out_msg = ""
    out_msg += "--------------------------------------------\n"
    out_msg += "| GPU |  PID  |    USERNAME    |    SIZE   |\n"
    out_msg += "--------------------------------------------\n"

    for line in lines:
        try:
            gpu_index = gpu_index_pattern.search(line).group(1)
            pid = pid_pattern.search(line).group(1)
            size = int(size_pattern.search(line).group(1))
            
            # 排除特别小的使用（系统调用）
            if size < 100:
                continue

            name = pid_2_name[pid]

            out_msg += f"|  {gpu_index:2} | {pid:>5} |  {name:13} |  {size:5}MiB |\n"
        except AttributeError:
            pass
    
    out_msg += "--------------------------------------------"
    print(out_msg)