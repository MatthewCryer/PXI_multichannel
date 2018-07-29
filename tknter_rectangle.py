from tkinter import *
import itertools
import colorsys

class Pixel:
    def __init__(self, canvas, x1, y1, x2, y2, colour):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.colour = colour
        self.canvas = canvas
        self.pixel = canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=self.colour)

    def colourchange(self, colour):
        # colours = ["blue", "pink", "yellow", "green"]
        # for col in colours:
        self.canvas.itemconfigure(self.pixel, fill=colour)
            # self.canvas.update()
            # self.canvas.after(1000)

def bulkcolourchange(objectIDs):
    for col in colours:
        for i in objectIDs:
            i.colourchange(col)
        canvas.update()
        canvas.after(1000)

def bulkcolourchange2(objectIDs):
    for row in range(int(len(array))):
        for channel,ID in zip(range(1,16), objectIDs): #list has same order as channels!
            x = float(array[[row], [channel]]) #as using the normed array the value of x is between 0 and 1
            assert x <= 1, 'colour value from array > 1'
            colourtouse = ("#%s00000" % (hex(int(x//0.0625)))[2])
            ID.colourchange(colourtouse)
        canvas.update()
        canvas.after(2)
    root.destroy()

def bulkcolourchange3(objectIDs):
    for row in range(int(len(array))):
        for channel,ID in zip(range(1,16), objectIDs): #list has same order as channels!
            x = float(array[[row], [channel]]) #as using the normed array the value of x is between 0 and 1
            assert x <= 1, 'colour value from array > 1'
            hexV = (hex(int(x//0.00390625)))[2:]
            if len(hexV) == 2:
                colourtouse = ("#%s0000" % hexV)
            elif len(hexV) == 1:
                colourtouse = ("#%s00000" % hexV)
            else:
                assert len(hexV) > 2 or len(hexV) < 1, 'hex value is wrong length'
            ID.colourchange(colourtouse)
        canvas.update()
        canvas.after(1)
    root.destroy()


# initialize root Window and canvas
root = Tk()
root.title("Pixels")
root.geometry('300x300+300+300')
root.resizable(False,False)
canvas = Canvas(root, width = 300, height = 300)
canvas.pack()

pixels = []
k = range(50,250,50)
corners2d = [[(i,j) for i in k] for j in k]
corners1d = list(itertools.chain.from_iterable(corners2d))
corners1d.pop(4)
for i in corners1d:
    pix = Pixel(canvas, i[0], i[1], i[0]+50, i[1]+50, "red")
    pixels.append(pix)

#colours = ["blue", "pink", "yellow", "green"]
#bulkcolourchange(pixels)

#must have normed array from tdms_import
bulkcolourchange2(pixels)


# for pix in pixels:
#     pix.colourchange()

# pixel[4].colourchange()

root.mainloop()
