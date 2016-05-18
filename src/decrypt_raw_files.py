import simplejson as json
from Crypto.Cipher import AES
from hashlib import md5
from basicInfo import encryption_decryption as ec


def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = ''
    while len(d) < key_length + iv_length:
        d_i = md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length + iv_length]


def decrypt_me(password, encrypted_folder, encrypted_file, folder_to_write_in, return_message_string=False):
    if '' == password:
        password = ec.password
    key_length = ec.key_length
    block_size = AES.block_size
    f = open(encrypted_folder + encrypted_file, 'rb')
    salt = f.read(block_size)[len(ec.file_prefix):]
    ekey, iv = derive_key_and_iv(password, salt, key_length, block_size)
    cipher = AES.new(ekey, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    message = ''
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(f.read(ec.block_length_bytes * block_size))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        message += chunk
    f.close()
    message = message.replace('\x00', '')
    message = message.replace('true', 'True')
    message = message.replace('false', 'False')
    if return_message_string:
        return message
    # print 'Message is : ', message
    m_eval = eval(message)
    if '' == folder_to_write_in:
        #print json.dumps(eval(message), sort_keys=True, indent=4, separators=(',', ': '))
        return m_eval
    if not '' == folder_to_write_in:
        decrypted_file = encrypted_file.replace('.encrypted', '')
        print 'writing: ', decrypted_file
        with open(folder_to_write_in + decrypted_file, 'w') as jsonFile:
            json.dump(m_eval, jsonFile)
