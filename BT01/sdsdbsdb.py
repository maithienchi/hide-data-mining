from bitarray import bitarray
def embed(msg_file, cover_text_file, text_width, stego_text_file):
    # YOUR CODE HERE
    #raise NotImplementedError()
    b = 0 # Chỉ số duyệt từng bit của msg_bits
    l = 0 # Chỉ số duyệt từng dòng của cover_text

    # # Đọc cover text file
    # cover_text = open(cover_text_file, "r")
    # print(cover_text)

    # # Đọc msg file
    # with open(msg_file, 'r') as f:
    #     msg = f.read()
    #     print(len(msg))
    # # chuyển msg thành msg bits
    # msg_bits = bitarray()
    # msg_bits.fromstring(msg)
    # print(len(msg_bits))

def tobits(s):
    result = []
    for c in s:
        bits = bin(ord(c))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result
def frombits(bits):
    chars = []
    for b in range(len(bits) / 8):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)

def text_from_bits(bits):
    """
    >>> text_from_bits([0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1])
    'Hi'
    """
    n = int(''.join(map(str, bits)), 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
with open('msg.txt', 'r') as f:
        msg = f.read()
        print(len(msg))
# chuyển msg thành msg bits
msg_bits = bitarray()
msg_bits.frombytes(msg.encode('utf-8'))
print(msg_bits)
print(text_from_bits(msg_bits))






# embed('msg.txt', 'cover.txt', 70, 'stego.txt')