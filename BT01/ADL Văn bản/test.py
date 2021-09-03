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
    b = 0
    for line in cover_text_lines:
        stego_text += line
        if b < len(msg_bits):
            n_allowed_spaces = text_width - len(line)
            n_needed_spaces = msg_bits[b] + 1
            if n_needed_spaces <= n_allowed_spaces:
                stego_text += n_needed_spaces * ' '
                b += 1
        stego_text += '\n'
    if b < len(msg_bits):
        print('Not enough spaces to embed!')
        return False
    
    # Write stego text to file
    with open(stego_text_file, 'w') as f:
        f.write(stego_text)
    return True

embed('02_03-msg.txt', '02_03-cover.txt', 70, '02_03-stego.txt')

