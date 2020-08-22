import subprocess
import re
import argparse
import sys
import os
from os import path
import time
import copy
import logging

serial_Maps = {'S286942X7B23528': ['MBM-CMM-FIO', 'UD175S000078'], 'S286942X7C19241': ['MBM-CMM-FIO', 'VD177S000027'], 'S286942X8A11629': ['MBM-CMM-FIO', 'VD186S001652'], 'S286942X8A11628': ['MBM-CMM-FIO', 'VD186S001653'], 'S286942X7B10201': ['MBM-CMM-FIO', 'VD176S002589'], 'S286942X7B10199': ['MBM-CMM-FIO', 'UD175S000042'], 'S286942X8A11636': ['MBM-CMM-FIO', 'VD186S001663'], 'S286942X8A11631': ['MBM-CMM-FIO', 'VD186S001664'], 'S286942X7C19256': ['MBM-CMM-FIO', 'VD177S000040'], 'S286942X7B23507': ['MBM-CMM-FIO', 'VD177S000156'], 'S286942X7C19236': ['MBM-CMM-FIO', 'VD177S000038'], 'S286942X7C19257': ['MBM-CMM-FIO', 'VD177S000032'], 'S286942X8A11632': ['MBM-CMM-FIO', 'VD186S001665'], 'S286942X8A11635': ['MBM-CMM-FIO', 'VD186S001662'], 'S15317606C00335': ['MBM-CMM-001', 'VD16BS017229'], 'S15317606C00339': ['MBM-CMM-001', 'VD16BS017224'], 'S15317606C00338': ['MBM-CMM-001', 'VD16BS017223'], 'S15317606C00334': ['MBM-CMM-001', 'VD16BS017230'], 'S15317606C00341': ['MBM-CMM-001', 'VD16BS017222'], 'S15317606C00336': ['MBM-CMM-001', 'VD16BS017227'], 'S15317608311982': ['MBM-CMM-001', 'VD176S000590'], 'S15317606C00340': ['MBM-CMM-001', 'VD16BS017225'], 'S286942X9714127': ['MBM-CMM-FIO', 'VD195S000423'], 'S286942X9714126': ['MBM-CMM-FIO', 'VD195S000424'], 'S286942X9714124': ['MBM-CMM-FIO', 'VD195S000425'], 'S286942X9714129': ['MBM-CMM-FIO', 'VD195S000421'], 'S286942X9918742': ['MBM-CMM-FIO', 'VD195S000497'], 'S286942X9918725': ['MBM-CMM-FIO', 'VD195S000495'], 'S286942X9918737': ['MBM-CMM-FIO', 'VD196S000049'], 'S286942X9918741': ['MBM-CMM-FIO', 'VD195S000494'], 'S286942X8A20485': ['MBM-CMM-FIO', 'VD186S001323']}
bins = {'MBM-CMM-001':'FRU_MBM_CMM_001_V102_2.bin', 'MBM-CMM-FIO':'FRU_MBM_CMM_FIO_V100_6.bin'}

inter_files = []
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO , filename='Write_CMM_FRU.log')
def create_new_bin(model, sn):
    if sys.platform.lower() == 'win32':
        bin = 'bin\\'+ bins[model]
    else:
        bin = 'bin/{}'.format(bins[model])
    # if model not in bins.keys():
    #     print("Error model name. Skip programming!!")
    #     logging.error("Error model name. Skip programming!!")
    #     return None
    # else:
    #     map = bins[model]
    if sn not in serial_Maps.keys():
        print("Can not find this serial number {} in database. Skip programming!!".format(sn))
        logging.error("Can not find this serial number {} in database. Skip programming!!".format(sn))
        return None
    else:
        bn = serial_Maps[sn][1]

    new_bin = run_ModifyFRU(bin, 'bs', bn)
    #print(new_bin)
    inter_files.append(new_bin)
    new_bin = run_ModifyFRU(new_bin, 'ps', sn)

    if sys.platform.lower() == 'win32':
        file_name = sn + '.bin'
    else:
        file_name = "bin/{}.bin".format(sn)
    #print(new_bin)

    if not path.isfile(file_name):
        try:
            #subprocess.call(['ren', new_bin, file_name])
            if sys.platform.lower() == 'win32':
                os.system('ren {} {}'.format(new_bin, file_name))
            else:
                os.system('mv {} {}'.format(new_bin, file_name))
        except Exception as e:
            print("Error has occurred. Leave program!!" + str(e))
            logging.error("Failed to rename this file {}. In create_new_bin.".format(new_bin) + str(e))
            sys.exit()

    if sys.platform.lower() == 'win32':
        inter_files.append('bin\\' + file_name)
        return 'bin\\' + file_name
    else:
        inter_files.append(file_name)
        return '{}'.format(file_name)

def run_ModifyFRU(file_name, type, serial):
    if sys.platform.lower() == 'win32':
        tool_dir = 'Windows'
        tool_cmd = f'{tool_dir}\ModifyFRU'
    else:
        tool_dir = 'Linux'
        tool_cmd = f'{tool_dir}/ModifyFRU'
    if type == 'bs':
        type = '--bs'
    if type == 'ps':
        type = '--ps'

    try:
        output = subprocess.run([tool_cmd, '-f', file_name, type, serial], stdout=subprocess.PIPE)
        # os.system(cmd)
    except Exception as e:
        print("Error has occurred in create bin with serial {}. Leave program!!".format(serial) + str(e))
        logging.error("Error has occurred in run_ModifyFRU with serial {}. ".format(serial) + str(e))
        sys.exit()
    #print(output)
    if output.returncode == 0:
        out_txt = output.stdout.decode("utf-8", errors='ignore')
        if sys.platform.lower() == 'win32':
            result = re.search(r'(bin\\.*?)$', out_txt)
            return result.group(1).rstrip()
        else:
            return "{}.new.{}".format(file_name, serial)
    else:
        print("Error has occurred in create bin with serial {}. Leave program!!".format(serial))
        logging.error("Error has occurred in run_ModifyFRU with serial {}. ".format(serial))
        sys.exit()

def Write_FRU(ip,username,passwd,bin_file,sn,slot):
    #slot_map = {'CMM':'1' ,'A1':'3', 'A2':'4', 'B1':'5', 'B2':'6', 'CMM2':'18'}
    slot_map = {'CMM': '1'}
    if sys.platform.lower() == 'win32':
        tool_dir = 'tool'
        tool_cmd = f'{tool_dir}\ipmitool.exe'
    else:
        tool_cmd = 'ipmitool'
    com = [tool_cmd,'-I', 'lanplus' , '-H', ip, '-U', username, '-P', passwd]
    c1 = copy.deepcopy(com)

    run_ipmi(c1 + ['raw', '0x30', '0x6', '0x0'])
    run_ipmi(c1 + ['fru', 'write', slot_map[slot], bin_file])
    run_ipmi(c1 + ['raw', '0x30', '0x6', '0x1'])
    (board_serial, product_serial) = get_serial(com, slot_map[slot])
    if product_serial == sn:
        if not board_serial:
            print("Board serial mismatch after programming. Failed to write board serial on {}".format(sn))
            logging.warning("Board serial mismatch after programming. Failed to write board serial on {}".format(sn))
        else:
            print("Updated FRU on {} successfully\n".format(sn))
            logging.info("Updated FRU on {} successfully.".format(sn))
    else:
        print("Product serial mismatch after programming. Failed to write product serial on {}".format(sn))
        logging.warning("Product serial mismatch after programming. Failed to write product serial on {}".format(sn))


def get_serial(com, slot):
    com = com + ['fru', 'print', slot]
    output = subprocess.run(com, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    board_number = None
    product_number = None

    if output.returncode == 0:
        out_txt = output.stdout.decode("utf-8", errors='ignore')
        result = re.search(r'Board\s+Serial\s+\:\s?(\w+)', out_txt)
        if result:
            board_number = result.group(1).rstrip().lstrip()
        result = re.search(r'Product\s+Serial\s+\:\s?(\w+)', out_txt)
        if result:
            product_number = result.group(1).rstrip().lstrip()
    else:
        print("Failed to login to CMM. Please check your user name and password")
        logging.error("Failed to login to CMM. Please check your user name and password")
        sys.exit()
    #print("{} bs {} ps {}".format(out_txt, board_number, product_number))
    return (board_number, product_number)
def run_ipmi(com):

    try:
        output = subprocess.run(com, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # os.system(cmd)
    except Exception as e:
        print("Error has occurred in updating FRU. " + str(e))
        sys.exit()
    #print(output)
def Write_device(ip, Username, Passwd, slot, model, sn):
    slot_map = {'CMM': '1'}
    if sys.platform.lower() == 'win32':
        tool_dir = 'tool'
        tool_cmd = f'{tool_dir}\ipmitool.exe'
    else:
        tool_cmd = 'ipmitool'
    com = [tool_cmd,'-I', 'lanplus', '-H', ip, '-U', Username, '-P', Passwd]
    board_serial = ''
    product_serial = ''
    (board_serial, product_serial) = get_serial(com, slot_map[slot])
    if slot == 'CMM':
        if board_serial:
            if re.search(r'^0+$', board_serial):
                board_serial = ''
        else:
            board_serial = ''
        if product_serial:
            if re.search(r'^0+$', product_serial):
                product_serial = ''
        else:
            product_serial = ''
        # if int(board_serial) == 0:
        #     board_serial = ''
        # if int(product_serial) == 0:
        #     product_serial = ''
    #print(board_serial, product_serial, slot)
    if board_serial and product_serial:
        print("There are Board Serial and Product Serial on the device. Skip programming serial numbers on this device {}.\n Please check the information via Web GUI".format(sn))
        logging.warning("There is Board Serial and Product Serial on the device. Skip programming serial numbers on this device {}.\n Please check the information via Web GUI".format(sn))
    else:
        bin_file = create_new_bin(model, sn)
        if not bin_file:
            return
        Write_FRU(ip, Username, Passwd, bin_file,sn,slot)
        while inter_files:
            bin = inter_files.pop()
            if sys.platform.lower() == 'win32':
                cmd = 'del ' + bin
            else:
                cmd = 'rm ' + bin
            os.system(cmd)

def check_connectivity(ip):
    if sys.platform.lower() == 'win32':
        res = subprocess.run(['ping','-n','3', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        res = subprocess.run(['ping', '-c', '3', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode  != 0:
        return False
    else:
        out_text = res.stdout.decode("utf-8", errors='ignore')
        #print(out_text)
        if 'Destination host unreachable' in out_text:
            return False
        else:
            return True

def main():
    data = {}
    try:
        #with open('SW_config.txt', 'r') as file:
        with open(sys.argv[1], 'r') as file:
            for line in file:
                result = re.match(r'^(\w+.*?)\:(.*?)$', line)
                if result:
                    value = result.group(2).rstrip().lstrip()
                    if value and value != '':
                        field = result.group(1).rstrip().lstrip()
                        field = re.sub(r'\(.*?\)', '', field)
                        data[field] = value
    except IOError as e:
        print("config file is not available. Please read readme file and run this program again. Leave program!")
        logging.error("config file is not available.")
        sys.exit()
    #print(data)


    if 'CMM IP' in data.keys():
        ip = data['CMM IP']
    else:
        print("CMM IP is missing. Leave program!")
        sys.exit()

    if 'CMM User Name' in data.keys():
        username = data['CMM User Name']
    else:
        print("CMM user name is missing. Leave program!")
        sys.exit()

    if 'CMM Password' in data.keys():
        password = data['CMM Password']
    else:
        print("CMM Password is missing. Leave program!")
        sys.exit()

    if 'CMM Serial Number' not in data.keys():
        print("CMM Serial Number is missing. Leave program!")
        sys.exit()

    if data['CMM Serial Number'] not in serial_Maps.keys():
        print("CMM Serial Number is invalid. Please check the serial number and run again. Leave program!")
        sys.exit()
    else:
        sn = data['CMM Serial Number']
    print("Checking connection to {}".format(ip))
    if not check_connectivity(ip):
        print("Failed to access to {}. Leave program!!".format(ip))
        sys.exit()
    #print(data)
    #devices = []
    #devices.append("CMM\t{}\t{}".format(sn, serial_Maps[sn][0]))
    print("Programming CMM FRU on {} ".format(sn))
    logging.info("Programming CMM FRU on {}".format(sn))
    Write_device(ip, username, password, 'CMM', serial_Maps[sn][0], sn)
    #print(devices)
    # for dev in devices:
    #     (slot,sn, model) = re.split(r'\t', dev)
    #     print("Programming FRU on {} in {}".format(sn,slot))
    #     logging.info("Programming FRU on {} in {}".format(sn,slot))
    #     Write_device(ip, username, password, slot, model, sn)


if __name__ == '__main__':
    main()
