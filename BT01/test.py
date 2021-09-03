from bitarray import bitarray

def embed(msg_file, cover_text_file, text_width, stego_text_file):

    # Read cover text file
    with open(cover_text_file, 'r') as f:
        cover_text_lines = f.read().splitlines()
    
    # Read msg file
    with open(msg_file, 'r') as f:
        msg = f.read()
    
    # Convert msg to msg bits
    msg_bits = bitarray()
    msg_bits.frombytes(msg.encode('utf-8'))
    
    # Embed msg bits into cover text lines
    stego_text = ''
    b = 0 # Chỉ số duyệt từng bit của msg_bits
    l = 0 # index kiểm tra duyệt tới hàng cuối hay chưa
    checkend = 0 #bit check kiểm tra đã nhung xong hết bit chưa ?
    for line in cover_text_lines: # Chỉ số duyệt từng dòng của cover_text
        if l < len(cover_text_lines)-1: #kiểm tra có phải hàng cuối cùng hay không
            if cover_text_lines[l+1] != '':
                n=line.count(' ') #số khoảng trắng của dòng l
                m=text_width-len(line) #số khoảng trắng cần phải chèn để dòng l được căn lề
                if (line =='' or len(line)>=text_width): # kiểm tra nhúng được
                    if line =='':
                        stego_text+='\n'
                    elif len(line)>=text_width:
                        stego_text+=line+'\n'
                elif (0 < m < n):
                    tam = line.split()
                    for i in range(min(m,n-m)):
                        if(b<len(msg_bits)):
                            if(msg_bits[b]==1):
                                tam.insert(i*3+2,' ') #thêm '  ' vào 2
                            else:
                                tam.insert(i*3+1,' ') #thêm '  ' vào 1
                            b+=1 # tăng bit secret 
                        else: #thêm 1000.. vào cuối
                            if checkend == 0:
                                tam.insert(i*3+2, ' ')
                                checkend = 1
                            else:
                                tam.insert(i*3+1, ' ')
                    if min(m,n-m)==(n-m):
                            j = m-min(m,n-m)
                            while j > 0:
                                tam.insert(len(tam)-j, ' ')
                                j -= 1
                    for i in range(len(tam)):
                        stego_text += tam[i]
                        if tam[i] != ' ':
                            if i < len(tam)-1:
                                stego_text += ' '

                    stego_text +='\n'

                else: # m>=n
                    dem=0
                    tam = line.split()
                    for i in range(len(tam)):
                        stego_text += tam[i]
                        if tam[i] != ' ':
                            if i < len(tam)-1:
                                if(dem<(m-n)):
                                    x=m/n
                                    stego_text += '  '+' '*(m//n)
                                    dem+=1
                                else:
                                    stego_text += '  '
                    stego_text+='\n'
                    
                                
            else:
                stego_text += line+'\n'
        else:
            stego_text += line
        l += 1
       
        
    with open(stego_text_file, 'w') as f:
        f.write(stego_text)
    return checkend

embed('msg.txt', 'cover.txt', 70, 'stego.txt')

def extract(stego_text_file, extr_msg_file):
    
    with open(stego_text_file, 'r') as f:
        stego_text_lines = f.read().splitlines()
    
    extr_msg_bits = bitarray()
    for line in stego_text_lines:
        tam = line.split(' ') # lấy list các từ đến ký tự rỗng
        if len(tam) > 2:
            listspace = []
            for i in range(len(tam)-1):
                if tam[i] != '':
                    if tam[i+1] == '':
                        listspace.append(2)
                    else:
                        listspace.append(1)
            checkspace = [] # tạo cụm 1 2 để dễ check bit 0 1 [[1,2],[2,1],..]
            for x in range(0, len(listspace), 2):
                checkspace.append(listspace[x:x+2])
            for c in checkspace:
                if len(c) == 2:
                    if c[0] == 2 and c[1] == 1:
                        extr_msg_bits.append(0)
                    elif c[0] == 1 and c[1] == 2:
                        extr_msg_bits.append(1)

    last_index = len(extr_msg_bits)-1
    for i in reversed(range(len(extr_msg_bits))):  # duyệt index ngược để tìm vị trí cuối bit 100..
        if extr_msg_bits[i] == 1:
            last_index = i
            break #kết thúc khi tìm đc vị trí cuối
    extr_msg = extr_msg_bits[:last_index].tobytes().decode('utf-8') #cover bit to string secret message

    with open(extr_msg_file, 'w') as f:#ghi secret message cover ra file
        f.write(extr_msg)

extract('stego.txt', 'extr_msg.txt')

