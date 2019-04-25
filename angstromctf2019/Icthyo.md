# Icthyo - 130 points - 75 solves
## Custom steganography

We get a binary that takes a 256x256 image and a message and outputs a modified 256x256 image. Also, we get an image of dinosaurs that is probably the output of the binary on an image with the message set to the flag.

Undestandind the binary took a lot of staring at the assembly. But basically, the original image has the lsb of each pixel randomly flipped. Then the message is used to specifically set the lsb of some pixels.

Here is the code to recover the message:
```python
# icthyo.py
import numpy as np
from PIL import Image
import sys

def get_bit(i,vec):
    return (vec[i<<5]^vec[(i<<5)+1]^vec[(i<<5)+2])&1

def get_byte(im,index):
    vec = im[index,:,:].ravel()
    return chr(int(''.join(reversed([str(get_bit(3*i,vec)) for i in range(7)])),2))

def get_message(fp, length):
    im = Image.open(fp)
    im = np.array(im)
    return ''.join((get_byte(im,i) for i in range(length)))

if __name__=='__main__':
    print(get_message(sys.argv[1], int(sys.argv[2])))
```

Running on a custom image gives the correct result:
```bash
~/Desktop/ctf/angstrom/rev$ ./icthyo image.png outimage.png
message (less than 256 bytes): ABCDEFGH
~/Desktop/ctf/angstrom/rev$ python icthyo.py outimage.png 8
ABCDEFGH
```

Finally, running it on the image given by the challenge gives the flag:
```bash
~/Desktop/ctf/angstrom/rev$ python icthyo.py out.png 42
actf{lurking_in_the_depths_of_random_bits}
```
