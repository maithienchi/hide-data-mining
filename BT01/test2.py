from bitarray import bitarray
def embed(msg_file, cover_text_file, text_width, stego_text_file):
    
    with open(cover_text_file, 'r') as f:
        cover_text_lines = f.read().splitlines() #đọc file tex lấy đừng dòng của văn bản
    
    with open(msg_file, 'r') as f:  #đọc lấy seret text
        msg = f.read() 
    
    # msg_bits = bitarray.bitarray()
    # msg_bits.fromstring(msg)
    msg_bits = bitarray()
    msg_bits.frombytes(msg.encode('utf-8'))
    
    stego_text = '' # gán stego bằng rỗng
    b = 0 # index duyệt msgbit
    l = 0 # index duyệt của cover text
    last_bit = 1
    for line in cover_text_lines: # duyệt từng dòng file cover text
        if l < len(cover_text_lines)-1:
            if cover_text_lines[l+1] != '': # Kiểm tra phải line trống hay không?
                if len(line) < text_width: # kiểm tra có vượt qua số ký tự cho phép
                    n = line.count(' ') # số khoảng cách trong dòng line
                    m = text_width - len(line) # số khoảng trắng cần chèn vào đoạn line
                    if 0 < m < n: # kiểm tra điều kiện để nhúng 
                        words = line.split() #  lấy từng từ trong dòng line thành []
                        for i in range(min(m, n-m)): # duyệt trên số lượng cần chèn phù hợp
                            if b < len(msg_bits): # kiểm tra index msgbit chưa nhúng hết
                                if msg_bits[b] == 0:
                                    words.insert(i*3+1, ' ')
                                else:
                                    words.insert(i*3+2, ' ')
                                b += 1
                            else:
                                if last_bit == 1:
                                    words.insert(i*3+2, ' ')
                                    last_bit = 0
                                else:
                                    words.insert(i*3+1, ' ')
                                 
                        if min(m,n-m)==(n-m):
                            j = m-min(m,n-m)
                            while j > 0:
                                words.insert(len(words)-j, ' ')
                                j -= 1
                                
                        for i in range(len(words)):
                            stego_text += words[i]
                            if words[i] != ' ':
                                if i < len(words)-1:
                                    stego_text += ' '
                    else:
                        needed_spaces = m
                        text_list = list(line)
                        for i in range(int(-(-(m-n) // 1))+1):
                            for j, c in enumerate(line):
                                if needed_spaces > 0:
                                    if c == ' ':
                                        text_list[j] = ' '+' '*(i+1)
                                        needed_spaces -= 1
                        stego_text += ''.join(text_list)
                else:
                    stego_text += line
            else:
                stego_text += line
            stego_text += '\n'
        else:
            stego_text += line
        l += 1
    #print(stego_text)
    with open(stego_text_file, 'w') as f:
        f.write(stego_text)
        
    return last_bit

embed('msg.txt', 'cover.txt', 70, 'stego.txt')

def extract(stego_text_file, extr_msg_file):
    
    with open(stego_text_file, 'r') as f:
        stego_text_lines = f.read().splitlines()
    
    extr_msg_bits = bitarray()
    for line in stego_text_lines:
        words = line.split(' ')
        if len(words) > 2:
            space_list = []
            for i in range(len(words)-1):
                if words[i] != '':
                    if words[i+1] == '':
                        space_list.append('  ')
                    else:
                        space_list.append(' ')
            
            c_spaces = [space_list[x:x+2] for x in range(0, len(space_list), 2)]
            for p in c_spaces:
                if len(p) == 2:
                    if p[0] == '  ' and p[1] == ' ':
                        extr_msg_bits.append(False)
                    elif p[0] == ' ' and p[1] == '  ':
                        extr_msg_bits.append(True)

    last_index = len(extr_msg_bits)-1
    for i in reversed(range(len(extr_msg_bits))):
        if extr_msg_bits[i] == True:
            last_index = i
            break
    extr_msg = extr_msg_bits[:last_index].tobytes().decode('utf-8')
    with open(extr_msg_file, 'w') as f:
        f.write(extr_msg)

extract('stego.txt', 'extr_msg.txt')